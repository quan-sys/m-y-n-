from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import random
import sys
import time
from typing import Any

import pandas as pd


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.finance_client import (  # noqa: E402
    STATEMENT_BALANCE_SHEET,
    STATEMENT_CASH_FLOW,
    STATEMENT_INCOME_STATEMENT,
    FinanceClient,
)


RUN_DATE = date.today().isoformat()
EVALUATION_DATE = pd.Timestamp(RUN_DATE)
FINANCIAL_ICB2 = {"NGÂN HÀNG", "BẢO HIỂM", "DỊCH VỤ TÀI CHÍNH"}
STATEMENT_CALLS = (
    (STATEMENT_BALANCE_SHEET, "get_balance_sheet", "balance_sheet"),
    (STATEMENT_INCOME_STATEMENT, "get_income_statement", "income_statement"),
    (STATEMENT_CASH_FLOW, "get_cash_flow", "cash_flow"),
)
RUN_STATE = ROOT / "data" / "fundamentals" / "run_state" / "sprint4_annual" / RUN_DATE
PROGRESS_PATH = RUN_STATE / "progress.json"
NORMALIZED_DIR = RUN_STATE / "normalized"
REPORT_PATH = ROOT / "docs" / "COVERAGE_SPRINT_4_ANNUAL.md"

# This map expresses data presence only. It deliberately contains no formula arithmetic.
# "BOTH" means N and N−1; "N" means the current annual period only.
FORMULA_REQUIREMENTS: dict[str, tuple[tuple[str, str, str], ...]] = {
    "STA": (
        (STATEMENT_BALANCE_SHEET, "current_assets", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "cash_and_cash_equivalents", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "current_liabilities", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "short_term_borrowings", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "taxes_and_other_payable_to_state_budget", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "total_assets", "BOTH"),
        (STATEMENT_CASH_FLOW, "depreciation_and_amortization", "N"),
    ),
    "SNOA": (
        (STATEMENT_BALANCE_SHEET, "total_assets", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "cash_and_cash_equivalents", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "short_term_investments", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "short_term_borrowings", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "long_term_borrowings", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "owners_equity", "BOTH"),
    ),
    "DSRI": (
        (STATEMENT_BALANCE_SHEET, "accounts_receivable", "BOTH"),
        (STATEMENT_INCOME_STATEMENT, "net_sales", "BOTH"),
    ),
    "GMI": (
        (STATEMENT_INCOME_STATEMENT, "gross_profit", "BOTH"),
        (STATEMENT_INCOME_STATEMENT, "net_sales", "BOTH"),
    ),
    "AQI": (
        (STATEMENT_BALANCE_SHEET, "current_assets", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "tangible_fixed_assets", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "total_assets", "BOTH"),
    ),
    "SGI": ((STATEMENT_INCOME_STATEMENT, "net_sales", "BOTH"),),
    "DEPI": (
        (STATEMENT_CASH_FLOW, "depreciation_and_amortization", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "tangible_fixed_assets", "BOTH"),
    ),
    "SGAI": (
        (STATEMENT_INCOME_STATEMENT, "selling_expenses", "BOTH"),
        (STATEMENT_INCOME_STATEMENT, "general_and_admin_expenses", "BOTH"),
        (STATEMENT_INCOME_STATEMENT, "net_sales", "BOTH"),
    ),
    "LVGI": (
        (STATEMENT_BALANCE_SHEET, "current_liabilities", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "long_term_liabilities", "BOTH"),
        (STATEMENT_BALANCE_SHEET, "total_assets", "BOTH"),
    ),
    "TATA": (
        (STATEMENT_INCOME_STATEMENT, "net_profit_loss_after_tax", "N"),
        (
            STATEMENT_CASH_FLOW,
            "net_cash_inflows_outflows_from_operating_activities",
            "N",
        ),
        (STATEMENT_BALANCE_SHEET, "total_assets", "N"),
    ),
}
M_SCORE_INDICES = ("DSRI", "GMI", "AQI", "SGI", "DEPI", "SGAI", "TATA", "LVGI")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sprint 4 Step 0 annual fundamentals coverage")
    parser.add_argument("--mode", choices=("fetch", "report"), required=True)
    parser.add_argument("--max-tickers", type=int)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--batch-pause", type=float, default=5.0)
    parser.add_argument("--min-sleep", type=float, default=2.8)
    parser.add_argument("--max-sleep", type=float, default=3.6)
    args = parser.parse_args(argv)
    if args.max_tickers is not None and args.max_tickers < 1:
        parser.error("--max-tickers must be positive")
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")
    if args.batch_pause < 0 or args.min_sleep < 0 or args.max_sleep < args.min_sleep:
        parser.error("invalid sleep bounds")
    return args


def _load_nonfinancial_universe() -> pd.DataFrame:
    universe = pd.read_csv(ROOT / "data" / "universe.csv")
    accepted = universe.loc[universe["status"].astype(str).eq("ACCEPTED")].copy()
    nonfinancial = accepted.loc[~accepted["icb2"].astype(str).isin(FINANCIAL_ICB2)].copy()
    nonfinancial["ticker"] = nonfinancial["ticker"].astype(str).str.strip().str.upper()
    nonfinancial = nonfinancial.sort_values("ticker", kind="stable").reset_index(drop=True)
    if nonfinancial["ticker"].duplicated().any():
        duplicates = sorted(
            nonfinancial.loc[nonfinancial["ticker"].duplicated(False), "ticker"].unique()
        )
        raise ValueError(f"duplicate non-financial ACCEPTED tickers: {duplicates}")
    return nonfinancial


def _load_progress() -> dict[str, Any]:
    if not PROGRESS_PATH.exists():
        return {"run_date": RUN_DATE, "period": "year", "tickers": {}}
    state = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
    if state.get("run_date") != RUN_DATE or state.get("period") != "year":
        raise ValueError("Sprint 4 annual progress metadata does not match this run")
    return state


def _write_progress(state: dict[str, Any]) -> None:
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = PROGRESS_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(PROGRESS_PATH)


def _write_normalized_copy(ticker: str, statement_dir: str, data: pd.DataFrame) -> Path:
    output = NORMALIZED_DIR / ticker / f"{statement_dir}.parquet"
    output.parent.mkdir(parents=True, exist_ok=True)
    data.to_parquet(output, index=False)
    return output


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _audit_annual_rows(data: pd.DataFrame) -> dict[str, int]:
    if data.empty:
        return {
            "normalized_rows": 0,
            "annual_periods": 0,
            "missing_report_period": 0,
            "missing_available_from": 0,
            "nonannual_rows": 0,
            "lag_mismatches": 0,
        }
    missing_period = int(data["report_period"].isna().sum())
    missing_available = int(data["available_from"].isna().sum())
    nonannual = int(data["period_type"].astype(str).ne("ANNUAL").sum())
    expected = pd.to_datetime(data["period_end"], errors="coerce") + pd.Timedelta(days=90)
    actual = pd.to_datetime(data["available_from"], errors="coerce")
    lag_mismatches = int((expected.dt.normalize() != actual.dt.normalize()).sum())
    return {
        "normalized_rows": int(len(data)),
        "annual_periods": int(data["report_period"].nunique()),
        "missing_report_period": missing_period,
        "missing_available_from": missing_available,
        "nonannual_rows": nonannual,
        "lag_mismatches": lag_mismatches,
    }


def _record_complete(record: dict[str, Any]) -> bool:
    path_text = str(record.get("normalized_path") or "")
    return bool(record.get("complete")) and bool(path_text) and (ROOT / path_text).exists()


def fetch(args: argparse.Namespace) -> int:
    universe = _load_nonfinancial_universe()
    if args.max_tickers is not None:
        universe = universe.head(args.max_tickers).copy()
    state = _load_progress()
    client = FinanceClient(
        cache_dir=ROOT / "data" / "fundamentals",
        provider="VCI",
        source="vnstock_VCI_financial",
        min_sleep_seconds=args.min_sleep,
        max_sleep_seconds=args.max_sleep,
        use_cache=True,
    )
    processed = 0
    live_calls = 0
    cached_calls = 0
    total = len(universe)

    for position, (_, row) in enumerate(universe.iterrows(), start=1):
        ticker = str(row["ticker"])
        ticker_state = state["tickers"].setdefault(
            ticker,
            {
                "exchange": str(row["exchange"]),
                "icb2": str(row["icb2"]),
                "source": "vnstock_VCI_financial",
                "as_of": RUN_DATE,
                "data_status": "IN_PROGRESS",
                "statements": {},
            },
        )
        if all(
            _record_complete(ticker_state["statements"].get(statement_type, {}))
            for statement_type, _, _ in STATEMENT_CALLS
        ):
            print(f"[{position}/{total}] {ticker}: annual statements already complete; skip", flush=True)
            continue

        for statement_type, method_name, statement_dir in STATEMENT_CALLS:
            existing = ticker_state["statements"].get(statement_type, {})
            if _record_complete(existing):
                continue
            result = getattr(client, method_name)(ticker, "year", company_type="NON_FINANCIAL")
            data = result.data if isinstance(result.data, pd.DataFrame) else pd.DataFrame()
            metadata = result.metadata or {}
            cache_hit = bool(metadata.get("cache_hit"))
            cached_calls += int(cache_hit)
            live_calls += int(not cache_hit)
            normalized_path = _write_normalized_copy(ticker, statement_dir, data)
            audit = _audit_annual_rows(data)
            complete = bool(result.ok)
            ticker_state["statements"][statement_type] = {
                "complete": complete,
                "source_mode": "ANNUAL_CACHE" if cache_hit else "ANNUAL_LIVE_FETCH",
                "source": str(result.source),
                "as_of": str(result.as_of),
                "data_status": str(result.status),
                "error": str(result.error or ""),
                "normalized_path": _relative(normalized_path),
                **audit,
            }
            ticker_state["as_of"] = str(result.as_of)
            ticker_state["data_status"] = str(result.status)
            _write_progress(state)
            print(
                f"[{position}/{total}] {ticker} {statement_type}: "
                f"mode={'CACHE' if cache_hit else 'LIVE'}; status={result.status}; "
                f"annual_periods={audit['annual_periods']}; rows={audit['normalized_rows']}; "
                f"lag_mismatches={audit['lag_mismatches']}; error={result.error or ''}",
                flush=True,
            )
            if not result.ok:
                print(
                    f"STOP: annual API call failed verbatim: {result.error or result.status}",
                    file=sys.stderr,
                    flush=True,
                )
                return 2

        statuses = [
            str(record.get("data_status") or "UNKNOWN")
            for record in ticker_state["statements"].values()
        ]
        ticker_state["data_status"] = "OK" if all(status == "OK" for status in statuses) else "+".join(statuses)
        _write_progress(state)
        processed += 1
        if processed % args.batch_size == 0:
            print(
                f"BATCH COMPLETE: tickers={processed}; live statements={live_calls}; "
                f"cached statements={cached_calls}",
                flush=True,
            )
            if args.batch_pause > 0 and live_calls > 0:
                time.sleep(args.batch_pause + random.random())

    print(
        f"ANNUAL FETCH COMPLETE: non-financial ACCEPTED tickers={total}; "
        f"live statements={live_calls}; cached statements={cached_calls}; "
        f"progress={PROGRESS_PATH.resolve()}",
        flush=True,
    )
    return 0


def _load_normalized(record: dict[str, Any]) -> pd.DataFrame:
    path_text = str(record.get("normalized_path") or "")
    if not path_text:
        return pd.DataFrame()
    path = ROOT / path_text
    return pd.read_parquet(path) if path.exists() else pd.DataFrame()


def _eligible_periods(frames: dict[str, pd.DataFrame]) -> list[int]:
    periods: set[int] = set()
    for frame in frames.values():
        if frame.empty:
            continue
        eligible = frame.loc[
            frame["period_type"].astype(str).eq("ANNUAL")
            & (pd.to_datetime(frame["available_from"], errors="coerce") <= EVALUATION_DATE)
        ]
        periods.update(
            int(value) for value in eligible["report_period"].dropna().astype(str) if str(value).isdigit()
        )
    return sorted(periods, reverse=True)


def _latest_consecutive_pair(periods: list[int]) -> tuple[int, int] | None:
    available = set(periods)
    for year in periods:
        if year - 1 in available:
            return year, year - 1
    return None


def _latest_consecutive_count(periods: list[int]) -> int:
    if not periods:
        return 0
    count = 1
    for previous, current in zip(periods, periods[1:]):
        if previous - 1 != current:
            break
        count += 1
    return count


def _formula_missing(
    frames: dict[str, pd.DataFrame], formula: str, pair: tuple[int, int] | None
) -> list[str]:
    if pair is None:
        return ["ANNUAL_PAIR:N_AND_N_MINUS_1"]
    year_n, year_previous = pair
    missing: list[str] = []
    for statement_type, item_id, period_rule in FORMULA_REQUIREMENTS[formula]:
        required_years = (year_n, year_previous) if period_rule == "BOTH" else (year_n,)
        frame = frames.get(statement_type, pd.DataFrame())
        for year in required_years:
            present = False
            if not frame.empty:
                rows = frame.loc[
                    frame["item_id"].astype(str).eq(item_id)
                    & frame["report_period"].astype(str).eq(str(year))
                    & (pd.to_datetime(frame["available_from"], errors="coerce") <= EVALUATION_DATE)
                ]
                present = not rows.empty and bool(pd.to_numeric(rows["value"], errors="coerce").notna().any())
            if not present:
                missing.append(f"{statement_type}:{year}:{item_id}")
    return missing


def _status(missing: list[str], formula: str) -> str:
    return "USABLE" if not missing else f"INSUFFICIENT_DATA_FOR_{formula}"


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        values = [str(value).replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return lines


def report() -> int:
    universe = _load_nonfinancial_universe()
    state = _load_progress()
    missing_fetches: list[str] = []
    rows: list[dict[str, Any]] = []

    for _, universe_row in universe.iterrows():
        ticker = str(universe_row["ticker"])
        ticker_state = state.get("tickers", {}).get(ticker, {})
        statement_records = ticker_state.get("statements", {})
        for statement_type, _, _ in STATEMENT_CALLS:
            if not _record_complete(statement_records.get(statement_type, {})):
                missing_fetches.append(f"{ticker}:{statement_type}")
        frames = {
            statement_type: _load_normalized(statement_records.get(statement_type, {}))
            for statement_type, _, _ in STATEMENT_CALLS
        }
        periods = _eligible_periods(frames)
        pair = _latest_consecutive_pair(periods)
        missing_by_formula = {
            formula: _formula_missing(frames, formula, pair) for formula in FORMULA_REQUIREMENTS
        }
        m_score_missing = sorted(
            {missing for formula in M_SCORE_INDICES for missing in missing_by_formula[formula]}
        )
        statuses = {
            formula: _status(missing, formula) for formula, missing in missing_by_formula.items()
        }
        statuses["FULL_M_SCORE"] = _status(m_score_missing, "FULL_M_SCORE")
        all_missing = [
            f"{formula}=" + ",".join(missing)
            for formula, missing in missing_by_formula.items()
            if missing
        ]
        statement_statuses = [
            str(statement_records.get(statement_type, {}).get("data_status") or "NOT_FETCHED")
            for statement_type, _, _ in STATEMENT_CALLS
        ]
        rows.append(
            {
                "ticker": ticker,
                "exchange": str(universe_row["exchange"]),
                "icb2": str(universe_row["icb2"]),
                "periods": ",".join(str(year) for year in periods),
                "pair": f"{pair[0]}/{pair[1]}" if pair else "NONE",
                "consecutive_count": _latest_consecutive_count(periods),
                "balance_periods": int(frames[STATEMENT_BALANCE_SHEET]["report_period"].nunique()) if not frames[STATEMENT_BALANCE_SHEET].empty else 0,
                "income_periods": int(frames[STATEMENT_INCOME_STATEMENT]["report_period"].nunique()) if not frames[STATEMENT_INCOME_STATEMENT].empty else 0,
                "cashflow_periods": int(frames[STATEMENT_CASH_FLOW]["report_period"].nunique()) if not frames[STATEMENT_CASH_FLOW].empty else 0,
                **statuses,
                "missing": "; ".join(all_missing),
                "source": str(ticker_state.get("source") or "vnstock_VCI_financial"),
                "as_of": str(ticker_state.get("as_of") or RUN_DATE),
                "data_status": "+".join(statement_statuses),
            }
        )

    if missing_fetches:
        print(
            "STOP: annual fetch is incomplete; missing records: " + ", ".join(missing_fetches),
            file=sys.stderr,
        )
        return 2

    frame = pd.DataFrame(rows)
    total = len(frame)
    sta_usable = int(frame["STA"].eq("USABLE").sum())
    snoa_usable = int(frame["SNOA"].eq("USABLE").sum())
    mscore_usable = int(frame["FULL_M_SCORE"].eq("USABLE").sum())
    no_pair = frame.loc[frame["pair"].eq("NONE"), "ticker"].tolist()
    audit_totals = {
        key: sum(
            int(record.get(key) or 0)
            for ticker_state in state["tickers"].values()
            for record in ticker_state.get("statements", {}).values()
        )
        for key in (
            "normalized_rows",
            "missing_report_period",
            "missing_available_from",
            "nonannual_rows",
            "lag_mismatches",
        )
    }

    lines = [
        "# Sprint 4 Step 0 — Annual Fundamentals Coverage",
        "",
        f"Run date / evaluation date: {RUN_DATE}.",
        "",
        "Coverage mode: annual balance sheet + income statement + cash flow for the non-financial ACCEPTED universe.",
        "",
        "Point-in-time rule: only annual rows with `available_from <= evaluation date`; annual lag is 90 days. The latest consecutive eligible pair is N/N−1.",
        "",
        "Restatement caveat: vnstock annual data is restated. This coverage is acceptable for a live screen today, not for a clean historical backtest.",
        "",
        "## Summary",
        "",
        f"- Non-financial ACCEPTED tickers: {total}.",
        f"- Usable N/N−1 pair for STA: {sta_usable}/{total} ({sta_usable / total:.2%}).",
        f"- Usable N/N−1 pair for SNOA: {snoa_usable}/{total} ({snoa_usable / total:.2%}).",
        f"- Usable N/N−1 pair for full M-Score: {mscore_usable}/{total} ({mscore_usable / total:.2%}).",
        f"- Tickers with no consecutive eligible annual pair at all: {len(no_pair)}.",
        f"- Point-in-time audit: rows={audit_totals['normalized_rows']}; missing report_period={audit_totals['missing_report_period']}; missing available_from={audit_totals['missing_available_from']}; non-annual rows={audit_totals['nonannual_rows']}; 90-day lag mismatches={audit_totals['lag_mismatches']}.",
        "",
        "## Tickers with no usable annual pair",
        "",
        ", ".join(no_pair) if no_pair else "None.",
        "",
        "## Per-ticker formula coverage",
        "",
    ]
    columns = [
        "ticker", "exchange", "icb2", "periods", "pair", "consecutive_count",
        "balance_periods", "income_periods", "cashflow_periods", "STA", "SNOA",
        "DSRI", "GMI", "AQI", "SGI", "DEPI", "SGAI", "TATA", "LVGI",
        "FULL_M_SCORE", "missing", "source", "as_of", "data_status",
    ]
    lines.extend(_markdown_table(columns, frame[columns].values.tolist()))
    lines.extend(["", "## Insufficient-data detail", ""])
    insufficient = frame.loc[frame["missing"].astype(str).ne(""), ["ticker", "missing", "source", "as_of", "data_status"]]
    if insufficient.empty:
        lines.append("None.")
    else:
        lines.extend(_markdown_table(list(insufficient.columns), insufficient.values.tolist()))
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"ANNUAL COVERAGE: STA={sta_usable}/{total} ({sta_usable / total:.2%})")
    print(f"ANNUAL COVERAGE: SNOA={snoa_usable}/{total} ({snoa_usable / total:.2%})")
    print(f"ANNUAL COVERAGE: FULL_M_SCORE={mscore_usable}/{total} ({mscore_usable / total:.2%})")
    print(f"NO CONSECUTIVE ANNUAL PAIR ({len(no_pair)}): {', '.join(no_pair) if no_pair else 'None'}")
    print(f"REPORT WRITTEN: {REPORT_PATH.resolve()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return fetch(args) if args.mode == "fetch" else report()


if __name__ == "__main__":
    raise SystemExit(main())
