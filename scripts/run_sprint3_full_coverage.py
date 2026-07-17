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

from scripts.verify_required_items_v1_sample_sprint3 import (  # noqa: E402
    HELPER_ITEM,
    REQUIRED_ITEMS,
    _compact_json,
)
from src.data.finance_client import (  # noqa: E402
    STATEMENT_BALANCE_SHEET,
    STATEMENT_CASH_FLOW,
    STATEMENT_INCOME_STATEMENT,
    FinanceClient,
    normalize_financial_statement,
)


RUN_DATE = date.today().isoformat()
FINANCIAL_ICB2 = {"NGÂN HÀNG", "BẢO HIỂM", "DỊCH VỤ TÀI CHÍNH"}
STATEMENT_CALLS = (
    (STATEMENT_BALANCE_SHEET, "get_balance_sheet", "balance_sheet"),
    (STATEMENT_INCOME_STATEMENT, "get_income_statement", "income_statement"),
    (STATEMENT_CASH_FLOW, "get_cash_flow", "cash_flow"),
)
LAGS = {"QUARTER": 30, "SEMIANNUAL": 60, "ANNUAL": 90}
RUN_STATE = ROOT / "data" / "fundamentals" / "run_state" / RUN_DATE
PROGRESS_PATH = RUN_STATE / "progress.json"
NORMALIZED_DIR = RUN_STATE / "normalized"
REPORT_MD = ROOT / "docs" / "COVERAGE_SPRINT_3_FULL_UNIVERSE.md"
TICKER_CSV = ROOT / "docs" / "COVERAGE_SPRINT_3_FULL_UNIVERSE.csv"
ITEM_CSV = ROOT / "docs" / "COVERAGE_SPRINT_3_FULL_UNIVERSE_ITEMS.csv"
FETCH_CSV = ROOT / "docs" / "FETCH_STATUS_SPRINT_3_FULL_UNIVERSE.csv"
SNAPSHOT_DIR = ROOT / "data" / "snapshots" / RUN_DATE


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sprint 3 full-universe fundamentals coverage")
    parser.add_argument("--mode", choices=("fetch", "finalize"), required=True)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--batch-pause", type=float, default=5.0)
    parser.add_argument("--min-sleep", type=float, default=2.8)
    parser.add_argument("--max-sleep", type=float, default=3.6)
    parser.add_argument("--max-tickers", type=int)
    parser.add_argument("--pytest-exit-code", type=int)
    parser.add_argument("--pytest-output", type=Path)
    args = parser.parse_args(argv)
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")
    if args.batch_pause < 0 or args.min_sleep < 0 or args.max_sleep < args.min_sleep:
        parser.error("invalid sleep bounds")
    if args.mode == "finalize" and args.pytest_exit_code is None:
        parser.error("--pytest-exit-code is required in finalize mode")
    return args


def _load_universe() -> pd.DataFrame:
    universe = pd.read_csv(ROOT / "data" / "universe.csv")
    accepted = universe.loc[universe["status"].astype(str).eq("ACCEPTED")].copy()
    accepted["ticker"] = accepted["ticker"].astype(str).str.strip().str.upper()
    accepted = accepted.sort_values("ticker", kind="stable").reset_index(drop=True)
    if accepted["ticker"].duplicated().any():
        duplicates = sorted(accepted.loc[accepted["ticker"].duplicated(False), "ticker"].unique())
        raise ValueError(f"duplicate ACCEPTED universe tickers: {duplicates}")
    return accepted


def _scope(row: pd.Series) -> str:
    return "FINANCIAL_RAW_FETCH_ONLY" if str(row["icb2"]) in FINANCIAL_ICB2 else "NON_FINANCIAL"


def _company_type(row: pd.Series) -> str:
    sector = str(row["icb2"])
    if sector == "NGÂN HÀNG":
        return "BANK"
    if sector == "BẢO HIỂM":
        return "INSURANCE"
    if sector == "DỊCH VỤ TÀI CHÍNH":
        return "FINANCIAL_SERVICES"
    return "NON_FINANCIAL"


def _load_progress() -> dict[str, Any]:
    if not PROGRESS_PATH.exists():
        return {"run_date": RUN_DATE, "tickers": {}}
    state = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
    if state.get("run_date") != RUN_DATE:
        raise ValueError(f"progress run date mismatch: {state.get('run_date')}")
    return state


def _write_progress(state: dict[str, Any]) -> None:
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = PROGRESS_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(PROGRESS_PATH)


def _latest_cached_raw(ticker: str, statement_dir: str) -> Path | None:
    parent = ROOT / "data" / "fundamentals" / ticker / statement_dir / "quarter"
    if not parent.exists():
        return None
    paths = list(parent.rglob("raw.parquet")) + list(parent.rglob("raw.csv"))
    return max(paths, key=lambda path: path.stat().st_mtime) if paths else None


def _load_frame(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path) if path.suffix.lower() == ".parquet" else pd.read_csv(path)


def _relative(path: Path | None) -> str:
    return str(path.relative_to(ROOT)) if path is not None else ""


def _raw_from_result(result: Any) -> tuple[pd.DataFrame, Path | None]:
    metadata = result.metadata or {}
    observation = Path(str(metadata.get("observation_path") or ""))
    parquet_path = observation / "raw.parquet"
    csv_path = observation / "raw.csv"
    if parquet_path.exists():
        return pd.read_parquet(parquet_path), parquet_path
    if csv_path.exists():
        return pd.read_csv(csv_path), csv_path
    return pd.DataFrame(), None


def _write_normalized_run_copy(
    ticker: str, statement_dir: str, normalized: pd.DataFrame
) -> Path:
    output = NORMALIZED_DIR / ticker / f"{statement_dir}.parquet"
    output.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_parquet(output, index=False)
    return output


def _audit_point_in_time(normalized: pd.DataFrame) -> dict[str, int]:
    if normalized.empty:
        return {
            "normalized_rows": 0,
            "missing_report_period": 0,
            "missing_available_from": 0,
            "lag_mismatches": 0,
        }
    report_missing = int(normalized["report_period"].isna().sum())
    available_missing = int(normalized["available_from"].isna().sum())
    mismatch = 0
    for _, row in normalized.iterrows():
        period_type = str(row["period_type"])
        lag = LAGS.get(period_type)
        if lag is None or pd.isna(row["period_end"]) or pd.isna(row["available_from"]):
            mismatch += 1
            continue
        expected = (pd.Timestamp(str(row["period_end"])) + pd.Timedelta(days=lag)).date().isoformat()
        if str(row["available_from"]) != expected:
            mismatch += 1
    return {
        "normalized_rows": int(len(normalized)),
        "missing_report_period": report_missing,
        "missing_available_from": available_missing,
        "lag_mismatches": mismatch,
    }


def _record_is_complete(record: dict[str, Any]) -> bool:
    raw_path = ROOT / str(record.get("raw_path") or "")
    normalized_path = ROOT / str(record.get("normalized_path") or "")
    return bool(record.get("complete")) and raw_path.exists() and normalized_path.exists()


def fetch(args: argparse.Namespace) -> int:
    universe = _load_universe()
    if args.max_tickers is not None:
        universe = universe.head(args.max_tickers).copy()
    state = _load_progress()
    client = FinanceClient(
        cache_dir=ROOT / "data" / "fundamentals",
        provider="VCI",
        source="vnstock_VCI_financial",
        min_sleep_seconds=args.min_sleep,
        max_sleep_seconds=args.max_sleep,
        use_cache=False,
    )
    processed_this_run = 0
    live_calls = 0
    cached_calls = 0
    total = len(universe)

    for position, (_, universe_row) in enumerate(universe.iterrows(), start=1):
        ticker = str(universe_row["ticker"])
        ticker_state = state["tickers"].setdefault(
            ticker,
            {
                "scope": _scope(universe_row),
                "company_type": _company_type(universe_row),
                "icb2": str(universe_row["icb2"]),
                "exchange": str(universe_row["exchange"]),
                "statements": {},
            },
        )
        if all(
            _record_is_complete(ticker_state["statements"].get(statement_type, {}))
            for statement_type, _, _ in STATEMENT_CALLS
        ):
            print(f"[{position}/{total}] {ticker}: already complete; resume skip", flush=True)
            continue

        for statement_type, method_name, statement_dir in STATEMENT_CALLS:
            existing = ticker_state["statements"].get(statement_type, {})
            if _record_is_complete(existing):
                continue
            source_mode = "CACHED_RAW_RENORMALIZED"
            raw_path = _latest_cached_raw(ticker, statement_dir)
            result_status = "OK"
            result_error = ""
            fetch_ok = True
            if raw_path is not None:
                raw = _load_frame(raw_path)
                cached_calls += 1
            else:
                source_mode = "LIVE_FETCHED"
                method = getattr(client, method_name)
                result = method(
                    ticker,
                    "quarter",
                    company_type=str(ticker_state["company_type"]),
                )
                live_calls += 1
                raw, raw_path = _raw_from_result(result)
                result_status = str(result.status)
                result_error = str(result.error or "")
                fetch_ok = bool(result.ok) and raw_path is not None and not raw.empty

            audit: dict[str, Any] = {}
            normalized = pd.DataFrame()
            normalization_error = ""
            if raw_path is not None and not raw.empty:
                try:
                    normalized = normalize_financial_statement(
                        raw,
                        ticker=ticker,
                        statement_type=statement_type,
                        company_type=str(ticker_state["company_type"]),
                        source="vnstock_VCI_financial",
                        as_of=RUN_DATE,
                    )
                    audit = dict(normalized.attrs.get("duplicate_resolution") or {})
                    if audit.get("ambiguous"):
                        result_status = "REQUIRED_ITEM_AMBIGUOUS"
                except BaseException as exc:  # noqa: BLE001 - preserve the exact local failure.
                    normalization_error = f"{type(exc).__name__}: {exc}"
                    result_status = "NORMALIZATION_ERROR"
            else:
                fetch_ok = False
                if result_status == "OK":
                    result_status = "MISSING_DATA"
                    result_error = "raw statement is empty or absent"

            normalized_path = _write_normalized_run_copy(ticker, statement_dir, normalized)
            point_in_time = _audit_point_in_time(normalized)
            provider_missing = result_status == "MISSING_DATA" and raw_path is not None
            record = {
                "complete": bool(raw_path is not None and (not raw.empty or provider_missing)),
                "source_mode": source_mode,
                "fetch_ok": fetch_ok,
                "data_status": result_status,
                "error": result_error,
                "normalization_error": normalization_error,
                "raw_path": _relative(raw_path),
                "raw_shape": [int(raw.shape[0]), int(raw.shape[1])],
                "normalized_path": _relative(normalized_path),
                "duplicate_resolution": audit,
                **point_in_time,
            }
            ticker_state["statements"][statement_type] = record
            _write_progress(state)
            print(
                f"[{position}/{total}] {ticker} {statement_type}: mode={source_mode}; "
                f"status={result_status}; raw={record['raw_shape']}; "
                f"rows={point_in_time['normalized_rows']}; "
                f"available_missing={point_in_time['missing_available_from']}; "
                f"error={result_error or normalization_error}",
                flush=True,
            )
            if source_mode == "LIVE_FETCHED" and not fetch_ok and not provider_missing:
                print("STOP: live fetch failed; rerun the same command to resume.", file=sys.stderr)
                return 2

        processed_this_run += 1
        if processed_this_run % args.batch_size == 0:
            print(
                f"BATCH COMPLETE: {processed_this_run} tickers this run; "
                f"live statements={live_calls}; cached statements={cached_calls}",
                flush=True,
            )
            if args.batch_pause > 0 and live_calls > 0:
                time.sleep(args.batch_pause + random.random())

    print(
        f"FETCH COMPLETE: accepted tickers={total}; live statements={live_calls}; "
        f"cached statements={cached_calls}; progress={PROGRESS_PATH.resolve()}",
        flush=True,
    )
    return 0


def _item_classification(
    *,
    raw: pd.DataFrame,
    normalized: pd.DataFrame,
    statement_type: str,
    item_id: str,
) -> tuple[str, int]:
    raw_count = int(raw["item_id"].astype(str).eq(item_id).sum()) if not raw.empty else 0
    normalized_has = (
        not normalized.empty and normalized["item_id"].astype(str).eq(item_id).any()
    )
    if raw_count == 0:
        return "MISSING", raw_count
    if raw_count == 1 and normalized_has:
        return "PRESENT_UNIQUE", raw_count
    if raw_count > 1 and statement_type == STATEMENT_BALANCE_SHEET and normalized_has:
        return "PRESENT_UNIQUE", raw_count
    if raw_count > 1:
        return "DUPLICATED", raw_count
    return "UNAVAILABLE_AFTER_NORMALIZATION", raw_count


def _markdown_table(headers: list[str], rows: list[list[Any]], align: set[int] | None = None) -> list[str]:
    align = align or set()
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---:" if index in align else "---" for index in range(len(headers))) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value).replace("|", "\\|").replace("\n", " ") for value in row) + " |")
    return lines


def finalize(args: argparse.Namespace) -> int:
    universe = _load_universe()
    state = _load_progress()
    nonfinancial = universe.loc[~universe["icb2"].astype(str).isin(FINANCIAL_ICB2)].copy()
    financial = universe.loc[universe["icb2"].astype(str).isin(FINANCIAL_ICB2)].copy()
    ticker_rows: list[dict[str, Any]] = []
    item_rows: list[dict[str, Any]] = []
    fetch_rows: list[dict[str, Any]] = []
    total_normalized_rows = 0
    missing_report_period = 0
    missing_available_from = 0
    lag_mismatches = 0

    for _, universe_row in universe.iterrows():
        ticker = str(universe_row["ticker"])
        ticker_state = state.get("tickers", {}).get(ticker, {})
        scope = _scope(universe_row)
        reasons: list[str] = []
        helper_status = "NOT_APPLICABLE"
        statement_statuses: dict[str, str] = {}
        source_modes: dict[str, str] = {}
        raw_success = True

        for statement_type, _, _ in STATEMENT_CALLS:
            record = ticker_state.get("statements", {}).get(statement_type)
            if not record:
                raw_success = False
                statement_statuses[statement_type] = "NOT_FETCHED"
                reasons.append(f"{statement_type}:NOT_FETCHED")
                continue
            raw_path = ROOT / str(record.get("raw_path") or "")
            normalized_path = ROOT / str(record.get("normalized_path") or "")
            raw = _load_frame(raw_path) if raw_path.exists() else pd.DataFrame()
            normalized = _load_frame(normalized_path) if normalized_path.exists() else pd.DataFrame()
            status = str(record.get("data_status") or "UNKNOWN")
            statement_statuses[statement_type] = status
            source_modes[statement_type] = str(record.get("source_mode") or "")
            statement_raw_success = raw_path.exists() and not raw.empty
            raw_success = raw_success and statement_raw_success
            fetch_rows.append(
                {
                    "ticker": ticker,
                    "scope": scope,
                    "statement_type": statement_type,
                    "source_mode": record.get("source_mode"),
                    "raw_fetch_success": statement_raw_success,
                    "data_status": status,
                    "raw_shape": _compact_json(record.get("raw_shape")),
                    "normalized_rows": int(record.get("normalized_rows") or 0),
                    "missing_report_period": int(record.get("missing_report_period") or 0),
                    "missing_available_from": int(record.get("missing_available_from") or 0),
                    "lag_mismatches": int(record.get("lag_mismatches") or 0),
                    "error": record.get("error") or record.get("normalization_error") or "",
                }
            )
            total_normalized_rows += int(record.get("normalized_rows") or 0)
            missing_report_period += int(record.get("missing_report_period") or 0)
            missing_available_from += int(record.get("missing_available_from") or 0)
            lag_mismatches += int(record.get("lag_mismatches") or 0)

            if scope == "FINANCIAL_RAW_FETCH_ONLY":
                if not statement_raw_success:
                    reasons.append(f"{statement_type}:{status}")
                continue

            if status not in {"OK", "REQUIRED_ITEM_AMBIGUOUS"}:
                reasons.append(f"{statement_type}:{status}")
            if status == "REQUIRED_ITEM_AMBIGUOUS":
                reasons.append(f"{statement_type}:REQUIRED_ITEM_AMBIGUOUS")

            if statement_type == STATEMENT_BALANCE_SHEET:
                helper_count = int(raw["item_id"].astype(str).eq(HELPER_ITEM).sum()) if not raw.empty else 0
                helper_status = "PRESENT" if helper_count > 0 else "MISSING"

            for item_id in REQUIRED_ITEMS[statement_type]:
                classification, raw_count = _item_classification(
                    raw=raw,
                    normalized=normalized,
                    statement_type=statement_type,
                    item_id=item_id,
                )
                item_rows.append(
                    {
                        "ticker": ticker,
                        "statement_type": statement_type,
                        "item_id": item_id,
                        "classification": classification,
                        "raw_count": raw_count,
                        "data_status": status,
                    }
                )
                if classification != "PRESENT_UNIQUE":
                    reasons.append(f"{statement_type}:{item_id}:{classification}")

        if scope == "NON_FINANCIAL":
            ticker_items = [row for row in item_rows if row["ticker"] == ticker]
            covered = (
                len(ticker_items) == 31
                and all(row["classification"] == "PRESENT_UNIQUE" for row in ticker_items)
                and not any("REQUIRED_ITEM_AMBIGUOUS" in reason for reason in reasons)
                and raw_success
            )
            coverage_status = "PASS" if covered else "FAIL"
        else:
            covered = False
            coverage_status = "EXCLUDED_FINANCIAL_RAW_OK" if raw_success else "EXCLUDED_FINANCIAL_RAW_FAIL"
        ticker_rows.append(
            {
                "ticker": ticker,
                "exchange": str(universe_row["exchange"]),
                "icb2": str(universe_row["icb2"]),
                "scope": scope,
                "coverage_status": coverage_status,
                "data_status_reason": ";".join(dict.fromkeys(reasons)) or "OK",
                "other_current_assets": helper_status,
                "statement_statuses": _compact_json(statement_statuses),
                "source_modes": _compact_json(source_modes),
            }
        )

    ticker_frame = pd.DataFrame(ticker_rows)
    item_frame = pd.DataFrame(item_rows)
    fetch_frame = pd.DataFrame(fetch_rows)
    ticker_frame.to_csv(TICKER_CSV, index=False, encoding="utf-8-sig")
    item_frame.to_csv(ITEM_CSV, index=False, encoding="utf-8-sig")
    fetch_frame.to_csv(FETCH_CSV, index=False, encoding="utf-8-sig")

    denominator = len(nonfinancial)
    numerator = int(
        ticker_frame.loc[ticker_frame["scope"].eq("NON_FINANCIAL"), "coverage_status"].eq("PASS").sum()
    )
    coverage = numerator / denominator if denominator else 0.0
    failed = ticker_frame.loc[
        ticker_frame["scope"].eq("NON_FINANCIAL") & ticker_frame["coverage_status"].eq("FAIL")
    ]
    financial_failed = ticker_frame.loc[
        ticker_frame["scope"].eq("FINANCIAL_RAW_FETCH_ONLY")
        & ticker_frame["coverage_status"].eq("EXCLUDED_FINANCIAL_RAW_FAIL")
    ]
    snapshot_universe = SNAPSHOT_DIR / "universe.csv"
    snapshot_rejects = SNAPSHOT_DIR / "universe_rejects.csv"
    snapshot_ok = snapshot_universe.exists() and snapshot_rejects.exists()
    snapshot_root = ROOT / "data" / "snapshots"
    complete_snapshot_dirs = sorted(
        path
        for path in snapshot_root.iterdir()
        if path.is_dir()
        and (path / "universe.csv").exists()
        and (path / "universe_rejects.csv").exists()
    )
    first_snapshot_dir = complete_snapshot_dirs[0] if complete_snapshot_dirs else SNAPSHOT_DIR
    pytest_green = args.pytest_exit_code == 0
    pytest_text = ""
    if args.pytest_output and args.pytest_output.exists():
        pytest_text = args.pytest_output.read_text(encoding="utf-8", errors="replace").strip()
    dod = {
        "coverage_gte_90": coverage >= 0.90,
        "zero_missing_available_from": missing_available_from == 0,
        "zero_missing_report_period": missing_report_period == 0,
        "zero_lag_mismatches": lag_mismatches == 0,
        "snapshot_written": snapshot_ok,
        "pytest_green": pytest_green,
    }

    failure_rows = [
        [row.ticker, row.exchange, row.icb2, row.data_status_reason, row.other_current_assets]
        for row in failed.itertuples(index=False)
    ] or [["NONE", "", "", "", ""]]
    financial_failure_rows = [
        [row.ticker, row.icb2, row.data_status_reason]
        for row in financial_failed.itertuples(index=False)
    ] or [["NONE", "", ""]]
    dod_rows = [[key, "PASS" if value else "FAIL"] for key, value in dod.items()]
    source_counts = fetch_frame.groupby("source_mode").size().to_dict() if not fetch_frame.empty else {}

    document = "\n".join(
        [
            "# Sprint 3 — full ACCEPTED universe REQUIRED_ITEMS v1 coverage",
            "",
            f"Run date: `{RUN_DATE}`",
            "Coverage mode: quarterly balance sheet + income statement + cash flow.",
            "Point-in-time rule: every normalized row uses its parsed `report_period` and `available_from = period_end + LAG`; quarter=30, semiannual=60, annual=90 days.",
            "Threshold changes: `NONE`. Full PR merge: `NO`. Sprint 4: `NOT STARTED`.",
            "",
            "## Tóm tắt đơn giản cho chủ project",
            "",
            f"- Đã kiểm tra toàn bộ {len(universe)} mã ACCEPTED: {denominator} mã phi tài chính dùng để tính độ phủ và {len(financial)} mã tài chính chỉ kiểm tra dữ liệu thô.",
            f"- Độ phủ chính xác: {numerator}/{denominator} = {coverage:.6%}. Mốc yêu cầu là 90%: {'ĐẠT' if coverage >= 0.90 else 'CHƯA ĐẠT'}.",
            f"- Có {len(failed)} mã phi tài chính dưới chuẩn; lý do cụ thể nằm trong bảng bên dưới. Có {len(financial_failed)} mã tài chính tải thô chưa đạt.",
            f"- Đã kiểm tra {total_normalized_rows} dòng tài chính đã chuẩn hóa: thiếu `report_period` {missing_report_period}, thiếu `available_from` {missing_available_from}, sai độ trễ {lag_mismatches}.",
            f"- Snapshot đầu tiên: {'đã ghi' if complete_snapshot_dirs else 'chưa ghi'} tại `{first_snapshot_dir.relative_to(ROOT)}/`.",
            f"- Snapshot của lần chạy này: {'đã ghi' if snapshot_ok else 'chưa ghi'} tại `{SNAPSHOT_DIR.relative_to(ROOT)}/`.",
            f"- Pytest: {'GREEN' if pytest_green else 'RED'} (exit code {args.pytest_exit_code}).",
            "- Ý nghĩa: báo cáo này chỉ đo dữ liệu đầu vào của Sprint 3. Nó chưa chấm điểm cổ phiếu, chưa loại mã tài chính khỏi universe và chưa bắt đầu Sprint 4.",
            "- Việc còn lại: dừng để chủ project và mentor duyệt con số độ phủ cùng các mã lỗi; không tự đổi ngưỡng hay tự sửa mapping.",
            "",
            "## Definition of Done",
            "",
            *_markdown_table(["check", "result"], dod_rows),
            "",
            "## Coverage result",
            "",
            f"- Numerator: `{numerator}`",
            f"- Denominator: `{denominator}`",
            f"- Exact coverage: `{coverage:.12%}`",
            f"- Required gate: `>=90%`",
            f"- Gate result: `{'PASS' if coverage >= 0.90 else 'FAIL'}`",
            f"- Source modes: `{_compact_json(source_counts)}`",
            "",
            "## Non-financial tickers below the bar",
            "",
            *_markdown_table(
                ["ticker", "exchange", "ICB2", "data_status reason", "other_current_assets"],
                failure_rows,
            ),
            "",
            "## Financial-sector raw-fetch failures (excluded from coverage %)",
            "",
            *_markdown_table(["ticker", "ICB2", "data_status reason"], financial_failure_rows),
            "",
            "## Point-in-time audit",
            "",
            f"- Normalized rows audited: `{total_normalized_rows}`",
            f"- Missing report_period: `{missing_report_period}`",
            f"- Missing available_from: `{missing_available_from}`",
            f"- Lag mismatches: `{lag_mismatches}`",
            "- Quarterly live data in this run uses +30 days. The same production parser and fixture tests enforce +60 for semiannual and +90 for annual labels.",
            "",
            "## Pytest output (verbatim)",
            "",
            "```text",
            pytest_text or "PYTEST OUTPUT FILE NOT PROVIDED",
            "```",
            "",
            "## Outputs",
            "",
            f"- Per-ticker coverage: `{TICKER_CSV.relative_to(ROOT)}`",
            f"- Per-item classifications: `{ITEM_CSV.relative_to(ROOT)}`",
            f"- Per-statement fetch/PIT audit: `{FETCH_CSV.relative_to(ROOT)}`",
            f"- Snapshot universe: `{snapshot_universe.relative_to(ROOT)}`",
            f"- Snapshot rejects: `{snapshot_rejects.relative_to(ROOT)}`",
            "",
            "## Hard stop",
            "",
            "No threshold was changed. PR #1 remains unmerged. Sprint 4 was not started. Stop for owner + mentor review.",
            "",
        ]
    )
    REPORT_MD.write_text(document, encoding="utf-8")
    print(f"Coverage: {numerator}/{denominator} = {coverage:.12%}")
    print(f"Non-financial failures: {len(failed)}")
    print(f"Financial raw failures: {len(financial_failed)}")
    print(
        f"Point-in-time: rows={total_normalized_rows}; missing_report_period={missing_report_period}; "
        f"missing_available_from={missing_available_from}; lag_mismatches={lag_mismatches}"
    )
    print(f"Definition of Done: {_compact_json(dod)}")
    print(f"Report: {REPORT_MD.resolve()}")
    return 0 if all(dod.values()) else 2


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.mode == "fetch":
        return fetch(args)
    return finalize(args)


if __name__ == "__main__":
    raise SystemExit(main())
