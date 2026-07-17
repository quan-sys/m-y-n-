from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import sys
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
    REQUIRED_ITEMS,
    _compact_json,
    _escape,
    _resolved_values,
    _source_rows,
)
from src.data.finance_client import (  # noqa: E402
    STATEMENT_BALANCE_SHEET,
    STATEMENT_CASH_FLOW,
    STATEMENT_INCOME_STATEMENT,
    FinanceClient,
)


TICKERS = (
    "FPT",
    "CSM",
    "DVP",
    "C32",
    "VOS",
    "PHR",
    "DP3",
    "DHC",
    "DRC",
    "VCS",
    "TLH",
    "HID",
)
FINANCIAL_ICB2 = {"NGÂN HÀNG", "BẢO HIỂM", "DỊCH VỤ TÀI CHÍNH"}
STATEMENT_CALLS = (
    (STATEMENT_BALANCE_SHEET, "get_balance_sheet"),
    (STATEMENT_INCOME_STATEMENT, "get_income_statement"),
    (STATEMENT_CASH_FLOW, "get_cash_flow"),
)
REPORT_MD = ROOT / "docs" / "VALIDATE_REQUIRED_ITEMS_V1_LIVE_12_SPRINT_3.md"
REPORT_CSV = ROOT / "docs" / "VALIDATE_REQUIRED_ITEMS_V1_LIVE_12_SPRINT_3.csv"
FETCH_STATUS_CSV = ROOT / "docs" / "VALIDATE_REQUIRED_ITEMS_V1_LIVE_12_FETCH_STATUS.csv"


def _validate_selection() -> list[dict[str, str]]:
    universe = pd.read_csv(ROOT / "data" / "universe.csv")
    selected = universe.loc[universe["ticker"].astype(str).isin(TICKERS)].copy()
    found = set(selected["ticker"].astype(str))
    missing = sorted(set(TICKERS) - found)
    if missing:
        raise ValueError(f"selected tickers missing from universe: {missing}")
    invalid = selected.loc[
        ~selected["status"].astype(str).eq("ACCEPTED")
        | selected["icb2"].astype(str).isin(FINANCIAL_ICB2)
    ]
    if not invalid.empty:
        raise ValueError(
            "selection contains non-ACCEPTED or financial tickers: "
            + _compact_json(invalid[["ticker", "status", "icb2"]].to_dict("records"))
        )
    by_ticker = selected.set_index("ticker")
    return [
        {
            "ticker": ticker,
            "status": str(by_ticker.at[ticker, "status"]),
            "exchange": str(by_ticker.at[ticker, "exchange"]),
            "icb2": str(by_ticker.at[ticker, "icb2"]),
        }
        for ticker in TICKERS
    ]


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


def _classification(
    *,
    statement_type: str,
    raw_count: int,
    normalized: pd.DataFrame,
    item_id: str,
) -> tuple[str, str]:
    if raw_count == 0:
        return "MISSING", "ITEM_ID_ABSENT_IN_LIVE_RAW"
    if raw_count == 1:
        return "PRESENT_UNIQUE", "ONE_LIVE_RAW_ROW"
    if statement_type == STATEMENT_BALANCE_SHEET:
        normalized_has_item = (
            not normalized.empty
            and normalized["item_id"].astype(str).eq(item_id).any()
        )
        if normalized_has_item:
            return "PRESENT_UNIQUE", "DUPLICATE_RESOLVED_BY_APPROVED_BALANCE_RULE"
    return "DUPLICATED", "NO_NEW_RULE_AUTHORIZED"


def _markdown_fetch_table(records: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| ticker | statement | ok | data_status | cache_state | raw shape | periods | observation | error |",
        "| --- | --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in records:
        lines.append(
            f"| {row['ticker']} | {row['statement_type']} | {row['ok']} | "
            f"{row['data_status']} | {row['cache_state']} | "
            f"`{_compact_json(row['raw_shape'])}` | {row['returned_period_count']} | "
            f"{_escape(row['observation_path'])} | {_escape(row['error'])} |"
        )
    return lines


def _markdown_item_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| ticker | statement | item_id | classification | raw count | verbatim raw rows | normalized values | evidence |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['ticker']} | {row['statement_type']} | {row['item_id']} | "
            f"{row['classification']} | {row['raw_count']} | "
            f"`{_escape(_compact_json(row['raw_rows']))}` | "
            f"`{_escape(_compact_json(row['normalized_values']))}` | "
            f"{row['evidence_note']} |"
        )
    return lines


def main() -> int:
    selection = _validate_selection()
    client = FinanceClient(
        cache_dir=ROOT / "data" / "fundamentals",
        provider="VCI",
        source="vnstock_VCI_financial",
        min_sleep_seconds=2.8,
        max_sleep_seconds=3.6,
        use_cache=False,
    )
    fetch_records: list[dict[str, Any]] = []
    item_rows: list[dict[str, Any]] = []

    for ticker in TICKERS:
        for statement_type, method_name in STATEMENT_CALLS:
            method = getattr(client, method_name)
            result = method(ticker, "quarter", company_type="NON_FINANCIAL")
            metadata = result.metadata or {}
            raw, raw_path = _raw_from_result(result)
            record = {
                "ticker": ticker,
                "statement_type": statement_type,
                "ok": bool(result.ok),
                "data_status": str(result.status),
                "cache_state": str(metadata.get("cache_state") or ""),
                "raw_shape": metadata.get("raw_shape") or [int(raw.shape[0]), int(raw.shape[1])],
                "returned_period_count": int(
                    metadata.get("returned_period_count")
                    or len([column for column in raw.columns if column not in {"item", "item_en", "item_id"}])
                ),
                "observation_path": str(raw_path.relative_to(ROOT)) if raw_path else "",
                "error": str(result.error or ""),
            }
            fetch_records.append(record)
            print(
                f"{ticker} {statement_type}: status={record['data_status']}; "
                f"cache_state={record['cache_state']}; raw_shape={record['raw_shape']}; "
                f"periods={record['returned_period_count']}; error={record['error']}",
                flush=True,
            )

            for item_id in REQUIRED_ITEMS[statement_type]:
                source_rows = _source_rows(raw, item_id) if not raw.empty else []
                classification, note = _classification(
                    statement_type=statement_type,
                    raw_count=len(source_rows),
                    normalized=result.data,
                    item_id=item_id,
                )
                item_rows.append(
                    {
                        "ticker": ticker,
                        "statement_type": statement_type,
                        "item_id": item_id,
                        "classification": classification,
                        "raw_count": len(source_rows),
                        "raw_rows": source_rows,
                        "normalized_values": _resolved_values(result.data, item_id),
                        "evidence_note": note,
                    }
                )

    client.write_fetch_status(FETCH_STATUS_CSV)
    csv_frame = pd.DataFrame(item_rows).copy()
    csv_frame["raw_rows"] = csv_frame["raw_rows"].map(_compact_json)
    csv_frame["normalized_values"] = csv_frame["normalized_values"].map(_compact_json)
    csv_frame.to_csv(REPORT_CSV, index=False, encoding="utf-8-sig")

    focus_rows = [
        row
        for row in item_rows
        if row["statement_type"] in {STATEMENT_INCOME_STATEMENT, STATEMENT_CASH_FLOW}
    ]
    focus_missing = [row for row in focus_rows if row["classification"] == "MISSING"]
    focus_duplicates = [row for row in focus_rows if row["classification"] == "DUPLICATED"]
    focus_present = [row for row in focus_rows if row["classification"] == "PRESENT_UNIQUE"]
    all_missing = [row for row in item_rows if row["classification"] == "MISSING"]
    all_duplicates = [row for row in item_rows if row["classification"] == "DUPLICATED"]
    fresh_ok = [
        row
        for row in fetch_records
        if row["ok"] and row["data_status"] == "OK" and row["cache_state"] == "FETCHED"
    ]
    passed = (
        len(fresh_ok) == len(TICKERS) * len(STATEMENT_CALLS)
        and not all_missing
        and not all_duplicates
    )

    selection_lines = [
        "| ticker | universe status | exchange | ICB2 |",
        "| --- | --- | --- | --- |",
        *[
            f"| {row['ticker']} | {row['status']} | {row['exchange']} | {row['icb2']} |"
            for row in selection
        ],
    ]
    focus_issue_lines = [
        "| ticker | statement | item_id | classification | raw rows |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in [*focus_missing, *focus_duplicates]:
        focus_issue_lines.append(
            f"| {row['ticker']} | {row['statement_type']} | {row['item_id']} | "
            f"{row['classification']} | `{_escape(_compact_json(row['raw_rows']))}` |"
        )
    if not focus_missing and not focus_duplicates:
        focus_issue_lines.append("| NONE | NONE | NONE | NONE | `[]` |")

    document = "\n".join(
        [
            "# Sprint 3 — controlled live validation of REQUIRED_ITEMS v1 on 12 tickers",
            "",
            f"Run date: `{date.today().isoformat()}`",
            "Provider/interface: supported public `vnstock.api.Finance`, provider `VCI`.",
            "Mode: quarterly; exactly 12 existing sample tickers × 3 statements = 36 live requests.",
            "Polite sleep: random 2.8–3.6 seconds before each provider call; retries remain the FinanceClient defaults.",
            "Cache policy: live calls forced with `use_cache=False`; every returned raw observation is content-addressed under `data/fundamentals`.",
            "Threshold changes: `NONE`.",
            "Full-universe run: `NOT RUN`. Sprint 4: `NOT STARTED`. PR #1: `UNMERGED`.",
            "",
            "## Tóm tắt đơn giản cho chủ project",
            "",
            f"- Đã tải có kiểm soát {len(fetch_records)} báo cáo cho đúng 12 mã, gồm bảng cân đối, báo cáo thu nhập và luồng tiền. Có {len(fresh_ok)}/{len(fetch_records)} lượt tải mới thành công đầy đủ.",
            f"- Trọng tâm 13 mục từng chưa có cache: {len(focus_present)}/{len(focus_rows)} mục theo mã đều có đúng một dòng; thiếu {len(focus_missing)}, trùng {len(focus_duplicates)}.",
            f"- Toàn bộ 31 mục theo 12 mã: thiếu {len(all_missing)}, trùng chưa xử lý {len(all_duplicates)}.",
            "- `PRESENT_UNIQUE` nghĩa là tìm thấy đúng một dòng dùng được sau các quy tắc đã duyệt. `MISSING` là không thấy mã mục trong dữ liệu thật. `DUPLICATED` là nhà cung cấp trả nhiều dòng cùng mã mục và hệ thống không được tự đoán.",
            "- Ý nghĩa thực tế: "
            + (
                "mẫu nhỏ đã chứng minh đủ cả 31 mục, bao gồm 13 mục thu nhập/luồng tiền trước đây chỉ thiếu vì chưa tải."
                if passed
                else "mẫu nhỏ chưa đủ sạch để xin phép chạy toàn thị trường; các dòng lỗi bên dưới cần chủ project xem trước."
            ),
            "- Việc còn lại: "
            + (
                "chủ project duyệt báo cáo này; chỉ một prompt sau mới được phép chạy độ phủ toàn thị trường."
                if passed
                else "dừng tại đây, không thêm quy tắc và chờ quyết định của chủ project."
            ),
            "",
            "## Selected ACCEPTED non-financial tickers",
            "",
            *selection_lines,
            "",
            "## Fetch results",
            "",
            *_markdown_fetch_table(fetch_records),
            "",
            "## Income-statement and cash-flow issues",
            "",
            *focus_issue_lines,
            "",
            "## Verbatim per-ticker × per-item table (31 items each)",
            "",
            *_markdown_item_table(item_rows),
            "",
            "## Stop condition",
            "",
            (
                "All 12 tickers have all 31 REQUIRED_ITEMS v1 present and unique. This report stops before the full-universe run as ordered."
                if passed
                else "At least one live request, required item, or uniqueness check failed. No new rule was applied; stop for owner review."
            ),
            "",
        ]
    )
    REPORT_MD.write_text(document, encoding="utf-8")
    print(f"Report: {REPORT_MD.resolve()}")
    print(f"CSV evidence: {REPORT_CSV.resolve()}")
    print(f"Fetch status: {FETCH_STATUS_CSV.resolve()}")
    print(
        f"Focus result: present={len(focus_present)}/{len(focus_rows)}; "
        f"missing={len(focus_missing)}; duplicated={len(focus_duplicates)}",
        flush=True,
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
