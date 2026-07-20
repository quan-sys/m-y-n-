"""Checkpointed VCI annual-history fetch for the 156 Sprint 4 survivors."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.probe_annual_history_sources import is_rate_limit_response
from src.data.finance_client import FinanceClient


SURVIVORS_PATH = ROOT / "data" / "screener" / "step1_survivors.csv"
FUNDAMENTALS_ROOT = ROOT / "data" / "fundamentals"
RUN_DATE = "2026-07-20"
RUN_ROOT = FUNDAMENTALS_ROOT / "sprint6_annual_history" / RUN_DATE
CHECKPOINT_PATH = RUN_ROOT / "checkpoint.csv"
SUMMARY_PATH = RUN_ROOT / "summary.json"
BASELINE_HASH_PATH = RUN_ROOT / "protected_baseline_sha256.json"
EXPECTED_SURVIVORS = 156
STATEMENTS = (
    ("balance_sheet", "get_balance_sheet"),
    ("income_statement", "get_income_statement"),
    ("cash_flow", "get_cash_flow"),
)
CHECKPOINT_COLUMNS = (
    "ticker",
    "statement",
    "status",
    "periods",
    "period_count",
    "error",
    "observation_path",
    "completed",
)
PROTECTED_SCREENER_FILES = (
    "step1_rejects.csv",
    "step1_survivors.csv",
    "sprint5_readiness_audit.csv",
    "step2_candidates_ebit_tev.csv",
    "step2_candidates_ep.csv",
    "step2_valuation_all.csv",
)


class StopOnFirstErrorFinanceClient(FinanceClient):
    """Use the production call once so an outer rate-limit stop is immediate."""

    def _fetch_statement(self, ticker: str, period: str, statement_type: str) -> pd.DataFrame:
        wrapped = getattr(FinanceClient._fetch_statement, "__wrapped__", None)
        if wrapped is None:
            raise RuntimeError("FinanceClient._fetch_statement retry wrapper is unavailable")
        return wrapped(self, ticker, period, statement_type)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def protected_paths() -> list[Path]:
    paths = [ROOT / "data" / "screener" / name for name in PROTECTED_SCREENER_FILES]
    paths.extend(
        sorted(
            path
            for path in FUNDAMENTALS_ROOT.glob("*/*/year/2026-07-17/**/*")
            if path.is_file()
        )
    )
    return paths


def hash_manifest(paths: list[Path]) -> dict[str, str]:
    return {
        path.relative_to(ROOT).as_posix(): sha256_file(path)
        for path in paths
    }


def ensure_baseline() -> dict[str, str]:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    current = hash_manifest(protected_paths())
    if BASELINE_HASH_PATH.exists():
        baseline = json.loads(BASELINE_HASH_PATH.read_text(encoding="utf-8"))
        if current != baseline:
            raise RuntimeError("protected Sprint 4/Sprint 5 or 2026-07-17 cache hash mismatch")
        return baseline
    BASELINE_HASH_PATH.write_text(
        json.dumps(current, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return current


def verify_baseline(baseline: dict[str, str]) -> bool:
    return hash_manifest(protected_paths()) == baseline


def load_survivors(path: Path = SURVIVORS_PATH) -> list[str]:
    frame = pd.read_csv(path)
    if "ticker" not in frame.columns:
        raise ValueError("survivor input is missing ticker")
    tickers = frame["ticker"].astype(str).str.strip().str.upper().tolist()
    if len(tickers) != EXPECTED_SURVIVORS or len(set(tickers)) != EXPECTED_SURVIVORS:
        raise ValueError(
            f"expected {EXPECTED_SURVIVORS} unique survivors; "
            f"rows={len(tickers)} unique={len(set(tickers))}"
        )
    return tickers


def write_checkpoint(rows: list[dict[str, Any]], tickers: list[str]) -> None:
    order = {(ticker, statement): index for index, (ticker, statement) in enumerate(
        (pair for ticker in tickers for pair in ((ticker, name) for name, _ in STATEMENTS))
    )}
    frame = pd.DataFrame(rows, columns=CHECKPOINT_COLUMNS)
    if not frame.empty:
        frame = frame.drop_duplicates(["ticker", "statement"], keep="last")
        frame["_order"] = [order[(row.ticker, row.statement)] for row in frame.itertuples()]
        frame = frame.sort_values("_order").drop(columns="_order")
    temporary = CHECKPOINT_PATH.with_suffix(".tmp")
    frame.to_csv(temporary, index=False, lineterminator="\n")
    temporary.replace(CHECKPOINT_PATH)


def load_checkpoint() -> list[dict[str, Any]]:
    if not CHECKPOINT_PATH.exists():
        return []
    frame = pd.read_csv(CHECKPOINT_PATH, keep_default_na=False)
    missing = sorted(set(CHECKPOINT_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"checkpoint missing columns: {missing}")
    return frame[list(CHECKPOINT_COLUMNS)].to_dict("records")


def result_record(ticker: str, statement: str, result: Any) -> dict[str, Any]:
    data = result.data if isinstance(result.data, pd.DataFrame) else pd.DataFrame()
    periods = sorted(
        {
            str(value)
            for value in data.get("report_period", pd.Series(dtype=str)).astype(str)
            if str(value).isdigit() and len(str(value)) == 4
        }
    )
    return {
        "ticker": ticker,
        "statement": statement,
        "status": str(result.status),
        "periods": "|".join(periods),
        "period_count": len(periods),
        "error": str(result.error or ""),
        "observation_path": str((result.metadata or {}).get("observation_path", "")),
        "completed": True,
    }


def run_fetch(
    *,
    client: FinanceClient | None = None,
    on_progress: Callable[[dict[str, Any], int, int], None] | None = None,
) -> dict[str, Any]:
    baseline = ensure_baseline()
    tickers = load_survivors()
    rows = load_checkpoint()
    completed = {
        (str(row["ticker"]), str(row["statement"]))
        for row in rows
        if str(row.get("completed", "")).lower() in {"true", "1"}
    }
    client = client or StopOnFirstErrorFinanceClient(
        cache_dir=RUN_ROOT,
        provider="VCI",
        min_sleep_seconds=2.8,
        max_sleep_seconds=3.6,
        use_cache=False,
    )
    total = len(tickers) * len(STATEMENTS)
    rate_limit_error = ""
    for ticker in tickers:
        for statement, method_name in STATEMENTS:
            if (ticker, statement) in completed:
                continue
            result = getattr(client, method_name)(
                ticker,
                "year",
                company_type="NON_FINANCIAL",
            )
            record = result_record(ticker, statement, result)
            rows.append(record)
            completed.add((ticker, statement))
            write_checkpoint(rows, tickers)
            if on_progress is not None:
                on_progress(record, len(completed), total)
            if is_rate_limit_response(record["error"]):
                rate_limit_error = record["error"]
                break
        if rate_limit_error:
            break
    if not verify_baseline(baseline):
        raise RuntimeError("protected files changed during fetch")
    remaining = total - len(completed)
    summary = {
        "status": "STOPPED_RATE_LIMIT" if rate_limit_error else ("OK" if remaining == 0 else "INCOMPLETE"),
        "completed_calls": len(completed),
        "remaining_calls": remaining,
        "completed_tickers": sum(
            all((ticker, statement) in completed for statement, _ in STATEMENTS)
            for ticker in tickers
        ),
        "remaining_tickers": sum(
            not all((ticker, statement) in completed for statement, _ in STATEMENTS)
            for ticker in tickers
        ),
        "rate_limit_error": rate_limit_error,
        "checkpoint": CHECKPOINT_PATH.relative_to(ROOT).as_posix(),
        "run_root": RUN_ROOT.relative_to(ROOT).as_posix(),
        "protected_files_byte_identical": True,
    }
    SUMMARY_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--verify-protected", action="store_true")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    if args.verify_protected:
        if not BASELINE_HASH_PATH.exists():
            raise FileNotFoundError(f"baseline hash manifest missing: {BASELINE_HASH_PATH}")
        baseline = json.loads(BASELINE_HASH_PATH.read_text(encoding="utf-8"))
        identical = verify_baseline(baseline)
        print(
            "every Sprint 4 and Sprint 5 output file is byte-identical="
            f"{str(identical).upper()}"
        )
        print(f"protected_file_count={len(baseline)}")
        return 0 if identical else 4

    def progress(record: dict[str, Any], completed: int, total: int) -> None:
        print(
            f"completed={completed}/{total} ticker={record['ticker']} "
            f"statement={record['statement']} status={record['status']} "
            f"periods={record['periods'] or 'ABSENT'}",
            flush=True,
        )

    summary = run_fetch(on_progress=progress)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if summary["status"] == "OK" else 3


if __name__ == "__main__":
    raise SystemExit(main())
