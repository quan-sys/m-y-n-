from __future__ import annotations

import argparse
from datetime import date
from importlib.metadata import version
import json
from pathlib import Path
import sys


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.finance_client import FinanceClient  # noqa: E402


STATEMENT_CALLS = (
    ("BALANCE_SHEET", "get_balance_sheet"),
    ("INCOME_STATEMENT", "get_income_statement"),
    ("CASH_FLOW", "get_cash_flow"),
)
PERIODS = ("quarter", "year")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the explicit live vnstock finance smoke test.")
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=["VNM", "FPT", "VCB"],
        help="At least three tickers. Defaults to VNM, FPT, and VCB.",
    )
    parser.add_argument(
        "--bank-tickers",
        nargs="*",
        default=["VCB"],
        help="Tickers whose provider schema must be labeled BANK.",
    )
    parser.add_argument("--provider", default="VCI", help="Public vnstock.api Finance provider.")
    parser.add_argument("--min-sleep", type=float, default=2.8)
    parser.add_argument("--max-sleep", type=float, default=3.6)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "smoke_output" / "finance" / date.today().isoformat(),
    )
    args = parser.parse_args(argv)
    args.tickers = list(dict.fromkeys(str(ticker).strip().upper() for ticker in args.tickers if str(ticker).strip()))
    args.bank_tickers = {
        str(ticker).strip().upper() for ticker in args.bank_tickers if str(ticker).strip()
    }
    if len(args.tickers) < 3:
        parser.error("--tickers must contain at least three unique tickers")
    if args.min_sleep < 0 or args.max_sleep < args.min_sleep:
        parser.error("sleep bounds must satisfy 0 <= min_sleep <= max_sleep")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    client = FinanceClient(
        cache_dir=ROOT / "data" / "fundamentals",
        provider=args.provider,
        source=f"vnstock_{args.provider.upper()}_financial",
        min_sleep_seconds=args.min_sleep,
        max_sleep_seconds=args.max_sleep,
        use_cache=False,
    )

    results: list[dict[str, object]] = []
    for ticker in args.tickers:
        company_type = "BANK" if ticker in args.bank_tickers else "NON_FINANCIAL"
        for statement_type, method_name in STATEMENT_CALLS:
            method = getattr(client, method_name)
            for period in PERIODS:
                result = method(
                    ticker,
                    period,
                    company_type=company_type,
                    expect_large_company_scale=True,
                )
                metadata = result.metadata or {}
                returned_period_count = int(metadata.get("returned_period_count") or 0)
                raw_shape = metadata.get("raw_shape") or []
                row_count = 0
                if hasattr(result.data, "columns"):
                    row_count = len(result.data)
                    if returned_period_count == 0 and "report_period" in result.data.columns:
                        returned_period_count = int(result.data["report_period"].nunique())
                record = {
                    "ticker": ticker,
                    "company_type": company_type,
                    "statement_type": statement_type,
                    "period": period,
                    "ok": result.ok,
                    "data_status": result.status,
                    "returned_period_count": returned_period_count,
                    "raw_shape": raw_shape,
                    "normalized_row_count": row_count,
                    "source": result.source,
                    "as_of": result.as_of,
                    "error": result.error or "",
                }
                results.append(record)
                print(
                    f"{ticker} {statement_type} {period}: "
                    f"status={result.status}; periods={returned_period_count}; "
                    f"raw_shape={raw_shape}; rows={row_count}; "
                    f"error={result.error or ''}",
                    flush=True,
                )

    status_path = client.write_fetch_status(args.output_dir / "fetch_status.csv")
    successful = sum(1 for result in results if result["ok"] and result["data_status"] == "OK")
    summary = {
        "run_date": date.today().isoformat(),
        "vnstock_version": version("vnstock"),
        "provider": args.provider.upper(),
        "tickers": args.tickers,
        "request_count": len(results),
        "successful_request_count": successful,
        "more_than_four_periods_confirmed": any(
            int(result["returned_period_count"]) > 4 for result in results
        ),
        "price_adjustment_status": "ADJUSTED_OBSERVED",
        "price_adjustment_probe_performed_by_this_script": False,
        "price_adjustment_reason": (
            "The documented manual VNM 2020 corporate-action comparison in data_contract.md v2 "
            "shows retroactively adjusted VCI history; this finance-only command does not repeat "
            "the quote-history probe"
        ),
        "status_path": str(status_path.resolve()),
        "results": results,
    }
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Finance smoke summary: {summary_path.resolve()}")

    if successful != len(results):
        print(
            f"FINANCE SMOKE TEST FAILED: {successful}/{len(results)} requests returned OK",
            file=sys.stderr,
        )
        return 1
    print("FINANCE SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
