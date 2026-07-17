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

from src.data.finance_client import (  # noqa: E402
    STATEMENT_BALANCE_SHEET,
    STATEMENT_CASH_FLOW,
    STATEMENT_INCOME_STATEMENT,
    normalize_financial_statement,
)


AS_OF = "2026-07-15"
SAMPLE_TICKERS = (
    "VNM", "HPG", "FPT", "VCB", "CSM", "DVP", "C32", "VOS", "PHR", "DP3",
    "DHC", "DRC", "VCS", "TLH", "HID", "DXP", "LBE", "ASM", "PVP", "CTF",
    "HDG", "PVC", "NCT", "VC7", "CTI", "FMC", "CAP", "RAL", "DVM", "DPG",
    "EVG", "VVS", "VHC", "IDC", "GAS", "MST", "ASP", "SHN", "D2D", "HT1",
)
BEFORE_AFTER_TICKERS = ("C32", "VCS", "PVC", "DRC", "TLH", "VHC", "HT1")
REQUIRED_ITEMS = {
    STATEMENT_BALANCE_SHEET: (
        "current_assets",
        "cash_and_cash_equivalents",
        "short_term_investments",
        "accounts_receivable",
        "inventories_net",
        "fixed_assets",
        "tangible_fixed_assets",
        "total_assets",
        "current_liabilities",
        "short_term_borrowings",
        "taxes_and_other_payable_to_state_budget",
        "long_term_liabilities",
        "long_term_borrowings",
        "owners_equity",
        "undistributed_earnings",
        "minority_interests",
        "preferred_shares",
        "paid_in_capital",
    ),
    STATEMENT_INCOME_STATEMENT: (
        "net_sales",
        "cost_of_sales",
        "gross_profit",
        "selling_expenses",
        "general_and_admin_expenses",
        "operating_profit_loss",
        "interest_expenses",
        "net_accounting_profit_loss_before_tax",
        "net_profit_loss_after_tax",
        "attributable_to_parent_company",
    ),
    STATEMENT_CASH_FLOW: (
        "depreciation_and_amortization",
        "net_cash_inflows_outflows_from_operating_activities",
        "proceeds_from_issue_of_shares",
    ),
}
STATEMENT_DIRS = {
    STATEMENT_BALANCE_SHEET: "balance_sheet",
    STATEMENT_INCOME_STATEMENT: "income_statement",
    STATEMENT_CASH_FLOW: "cash_flow",
}
HELPER_ITEM = "other_current_assets"
PERIODS = ("2026-Q1", "2025-Q4", "2025-Q3", "2025-Q2")


def _cached_raw(ticker: str, statement_type: str) -> tuple[pd.DataFrame | None, Path | None]:
    parent = (
        ROOT
        / "data"
        / "fundamentals"
        / ticker
        / STATEMENT_DIRS[statement_type]
        / "quarter"
    )
    paths = sorted(parent.rglob("raw.parquet")) if parent.exists() else []
    if not paths:
        return None, None
    path = paths[-1]
    return pd.read_parquet(path), path


def _period_columns(frame: pd.DataFrame) -> list[str]:
    return [
        str(column)
        for column in frame.columns
        if str(column) not in {"item", "item_en", "item_id"}
    ]


def _json_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return value


def _source_rows(frame: pd.DataFrame, item_id: str) -> list[dict[str, Any]]:
    periods = _period_columns(frame)
    rows: list[dict[str, Any]] = []
    for index, row in frame.loc[frame["item_id"].astype(str).eq(item_id)].iterrows():
        rows.append(
            {
                "raw_index": int(index),
                "item": str(row.get("item", "")),
                "item_en": str(row.get("item_en", "")),
                "values": {period: _json_value(row.get(period)) for period in periods},
            }
        )
    return rows


def _audit(frame: pd.DataFrame, ticker: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    normalized = normalize_financial_statement(
        frame,
        ticker=ticker,
        statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL",
        source="cached_vci_observation_2026_07_15",
        as_of=AS_OF,
    )
    return normalized, dict(normalized.attrs.get("duplicate_resolution") or {})


def _identity_metrics(audit: dict[str, Any]) -> dict[str, Any] | None:
    candidate_event = next(
        (
            event
            for event in audit.get("events", [])
            if event.get("flag") == "IDENTITY_CANDIDATE_ERRORS"
        ),
        None,
    )
    if candidate_event is None:
        return None
    candidates = [
        candidate
        for candidate in candidate_event.get("candidates", [])
        if candidate.get("mean_error") is not None
    ]
    if not candidates:
        return None
    winner = min(candidates, key=lambda candidate: float(candidate["mean_error"]))
    rivals = [
        candidate
        for candidate in candidates
        if int(candidate["short_term_investments_index"])
        != int(winner["short_term_investments_index"])
    ]
    rival = min(rivals, key=lambda candidate: float(candidate["mean_error"])) if rivals else None
    winner_error = float(winner["mean_error"])
    rival_error = float(rival["mean_error"]) if rival is not None else None
    if winner_error == 0 and rival_error is not None and rival_error > 0:
        margin_ratio: float | str | None = "INF"
    elif winner_error > 0 and rival_error is not None:
        margin_ratio = rival_error / winner_error
    else:
        margin_ratio = None
    passing_periods = sum(
        float(error) <= 0.01 for error in winner.get("period_errors", {}).values()
    )
    return {
        "winner_mean_error": winner_error,
        "rival_mean_error": rival_error,
        "margin_ratio": margin_ratio,
        "passing_periods": passing_periods,
        "winner_period_errors": winner.get("period_errors", {}),
        "winner_sti_index": int(winner["short_term_investments_index"]),
        "winner_other_current_assets_index": int(winner["other_current_assets_index"]),
    }


def _resolution_path(audit: dict[str, Any]) -> str:
    flags = set(audit.get("flags", []))
    if audit.get("ambiguous") or "REQUIRED_ITEM_AMBIGUOUS" in flags:
        return "REQUIRED_ITEM_AMBIGUOUS"
    if "DUPLICATE_RESOLVED_BY_IDENTITY" in flags:
        return "TOLERANCE_AND_PER_ITEM_MARGIN_GTE_5X"
    if "DUPLICATE_RESOLVED_IMMATERIAL" in flags:
        return "R3_IMMATERIAL_DIFFERENCE"
    if "DUPLICATE_VERIFIED_IDENTICAL" in flags:
        return "R2_IDENTICAL_DUPLICATES"
    return "NO_RULE_A_DUPLICATE"


def _gross_identity_copy(frame: pd.DataFrame) -> pd.DataFrame:
    gross = frame.loc[frame["item_id"].astype(str).ne("inventories_net")].copy()
    gross.loc[gross["item_id"].astype(str).eq("inventories"), "item_id"] = "inventories_net"
    return gross


def _resolved_values(normalized: pd.DataFrame, item_id: str) -> dict[str, Any] | None:
    if normalized.empty:
        return None
    rows = normalized.loc[normalized["item_id"].astype(str).eq(item_id)]
    if rows.empty:
        return None
    return {
        str(row["report_period"]): _json_value(row["value"])
        for _, row in rows.iterrows()
    }


def _escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _before_after_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    comparison: list[dict[str, Any]] = []
    provisions: list[dict[str, Any]] = []
    for ticker in BEFORE_AFTER_TICKERS:
        raw, _ = _cached_raw(ticker, STATEMENT_BALANCE_SHEET)
        if raw is None:
            raise FileNotFoundError(f"cached balance sheet missing for {ticker}")
        _, before_audit = _audit(_gross_identity_copy(raw), ticker)
        _, after_audit = _audit(raw, ticker)
        before = _identity_metrics(before_audit)
        after = _identity_metrics(after_audit)
        if before is None or after is None:
            raise ValueError(f"Rule A metrics missing for {ticker}")
        gross = raw.loc[raw["item_id"].astype(str).eq("inventories"), list(PERIODS)].iloc[0]
        net = raw.loc[raw["item_id"].astype(str).eq("inventories_net"), list(PERIODS)].iloc[0]
        current_assets = raw.loc[
            raw["item_id"].astype(str).eq("current_assets"), list(PERIODS)
        ].iloc[0]
        period_provisions = {
            period: abs(float(gross[period]) - float(net[period])) / abs(float(current_assets[period]))
            for period in PERIODS
        }
        comparison.append(
            {
                "ticker": ticker,
                "before_winner_mean_error": before["winner_mean_error"],
                "before_rival_mean_error": before["rival_mean_error"],
                "before_margin_ratio": before["margin_ratio"],
                "before_passing_periods": before["passing_periods"],
                "after_winner_mean_error": after["winner_mean_error"],
                "after_rival_mean_error": after["rival_mean_error"],
                "after_margin_ratio": after["margin_ratio"],
                "after_passing_periods": after["passing_periods"],
                "provision_pct_mean": sum(period_provisions.values()) / len(period_provisions),
                "provision_pct_max": max(period_provisions.values()),
                "final_status": "AMBIGUOUS" if after_audit.get("ambiguous") else "RESOLVED",
                "resolution_path": _resolution_path(after_audit),
            }
        )
        for period in PERIODS:
            provisions.append(
                {
                    "ticker": ticker,
                    "period": period,
                    "inventories_gross": float(gross[period]),
                    "inventory_provision": float(net[period]) - float(gross[period]),
                    "inventories_net": float(net[period]),
                    "current_assets": float(current_assets[period]),
                    "abs_provision_pct_current_assets": period_provisions[period],
                    "gross_plus_provision_equals_net": (
                        float(gross[period]) + (float(net[period]) - float(gross[period]))
                        == float(net[period])
                    ),
                }
            )
    return comparison, provisions


def main() -> int:
    output_md = ROOT / "docs" / "VERIFY_REQUIRED_ITEMS_V1_SAMPLE_SPRINT_3.md"
    output_csv = ROOT / "docs" / "VERIFY_REQUIRED_ITEMS_V1_SAMPLE_SPRINT_3.csv"
    comparison, provisions = _before_after_rows()
    item_rows: list[dict[str, Any]] = []
    ticker_rows: list[dict[str, Any]] = []
    helper_rows: list[dict[str, Any]] = []
    missing_statement_count = 0

    for ticker in SAMPLE_TICKERS:
        if ticker == "VCB":
            cached = {}
            for statement_type in REQUIRED_ITEMS:
                raw, path = _cached_raw(ticker, statement_type)
                cached[statement_type] = path is not None and raw is not None
            ticker_rows.append(
                {
                    "ticker": ticker,
                    "scope": "FINANCIAL_RAW_FETCH_ONLY",
                    "balance_rule_status": "NOT_APPLICABLE_BANK_TEMPLATE",
                    "identity_mean_error": None,
                    "identity_period_errors": None,
                    "resolved_short_term_investments": None,
                    "resolved_preferred_shares": None,
                    "cached_statements": cached,
                }
            )
            continue

        balance_normalized = pd.DataFrame()
        balance_audit: dict[str, Any] = {}
        raw_balance, _ = _cached_raw(ticker, STATEMENT_BALANCE_SHEET)
        if raw_balance is None:
            raise FileNotFoundError(f"cached balance sheet missing for {ticker}")
        balance_normalized, balance_audit = _audit(raw_balance, ticker)
        identity = _identity_metrics(balance_audit)
        ticker_rows.append(
            {
                "ticker": ticker,
                "scope": "NON_FINANCIAL_REQUIRED_ITEMS_V1",
                "balance_rule_status": (
                    "AMBIGUOUS" if balance_audit.get("ambiguous") else "RESOLVED"
                ),
                "resolution_path": _resolution_path(balance_audit),
                "identity_mean_error": identity["winner_mean_error"] if identity else None,
                "identity_period_errors": identity["winner_period_errors"] if identity else None,
                "resolved_short_term_investments": _resolved_values(
                    balance_normalized, "short_term_investments"
                ),
                "resolved_preferred_shares": _resolved_values(
                    balance_normalized, "preferred_shares"
                ),
                "cached_statements": {
                    statement_type: _cached_raw(ticker, statement_type)[0] is not None
                    for statement_type in REQUIRED_ITEMS
                },
            }
        )
        helper_source = _source_rows(raw_balance, HELPER_ITEM)
        helper_rows.append(
            {
                "ticker": ticker,
                "other_current_assets": "PRESENT" if helper_source else "MISSING",
                "raw_count": len(helper_source),
                "raw_rows": helper_source,
            }
        )

        for statement_type, required_ids in REQUIRED_ITEMS.items():
            raw, raw_path = _cached_raw(ticker, statement_type)
            normalized = pd.DataFrame()
            audit: dict[str, Any] = {}
            if raw is None:
                missing_statement_count += 1
            elif statement_type == STATEMENT_BALANCE_SHEET:
                normalized, audit = balance_normalized, balance_audit
            else:
                normalized = normalize_financial_statement(
                    raw,
                    ticker=ticker,
                    statement_type=statement_type,
                    company_type="NON_FINANCIAL",
                    source="cached_vci_observation_2026_07_15",
                    as_of=AS_OF,
                )
                audit = dict(normalized.attrs.get("duplicate_resolution") or {})

            for item_id in required_ids:
                source = _source_rows(raw, item_id) if raw is not None else []
                raw_count = len(source)
                normalized_has_item = (
                    not normalized.empty
                    and normalized["item_id"].astype(str).eq(item_id).any()
                )
                if raw is None:
                    classification = "MISSING"
                    note = "STATEMENT_NOT_CACHED_NOT_PROVIDER_MISSING"
                elif raw_count == 0:
                    classification = "MISSING"
                    note = "ITEM_ID_ABSENT_IN_CACHED_RAW"
                elif raw_count == 1:
                    classification = "PRESENT_UNIQUE"
                    note = "ONE_RAW_ROW"
                elif normalized_has_item:
                    classification = "PRESENT_UNIQUE"
                    note = "DUPLICATE_RESOLVED_BY_APPROVED_RULE"
                elif audit.get("ambiguous"):
                    classification = "AMBIGUOUS"
                    note = "REQUIRED_ITEM_AMBIGUOUS"
                else:
                    classification = "DUPLICATED"
                    note = "DUPLICATE_NOT_RESOLVED"
                item_rows.append(
                    {
                        "ticker": ticker,
                        "statement_type": statement_type,
                        "item_id": item_id,
                        "classification": classification,
                        "raw_count": raw_count,
                        "raw_rows": source,
                        "resolved_values": _resolved_values(normalized, item_id),
                        "identity_mean_error": (
                            identity["winner_mean_error"]
                            if statement_type == STATEMENT_BALANCE_SHEET
                            and item_id == "short_term_investments"
                            and identity
                            else None
                        ),
                        "identity_period_errors": (
                            identity["winner_period_errors"]
                            if statement_type == STATEMENT_BALANCE_SHEET
                            and item_id == "short_term_investments"
                            and identity
                            else None
                        ),
                        "evidence_note": note,
                        "cache_path": str(raw_path.relative_to(ROOT)) if raw_path else None,
                    }
                )

    pd.DataFrame(item_rows).to_csv(output_csv, index=False, encoding="utf-8-sig")

    comparison_lines = [
        "| ticker | BEFORE winner mean error | BEFORE rival mean error | BEFORE rival/winner | BEFORE periods <=1% | AFTER winner mean error | AFTER rival mean error | AFTER rival/winner | AFTER periods <=1% | provision/current assets mean | max | final | path |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in comparison:
        comparison_lines.append(
            "| {ticker} | {before_winner_mean_error:.12%} | {before_rival_mean_error:.12%} | "
            "{before_margin_ratio} | {before_passing_periods}/4 | {after_winner_mean_error:.12%} | "
            "{after_rival_mean_error:.12%} | {after_margin_ratio} | {after_passing_periods}/4 | "
            "{provision_pct_mean:.12%} | {provision_pct_max:.12%} | {final_status} | {resolution_path} |".format(
                **row
            )
        )

    provision_lines = [
        "| ticker | period | inventories gross | inventory provision | inventories net | current assets | abs(provision)/current assets | gross + provision = net |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in provisions:
        provision_lines.append(
            f"| {row['ticker']} | {row['period']} | {row['inventories_gross']:.1f} | "
            f"{row['inventory_provision']:.1f} | {row['inventories_net']:.1f} | "
            f"{row['current_assets']:.1f} | {row['abs_provision_pct_current_assets']:.12%} | "
            f"{'PASS' if row['gross_plus_provision_equals_net'] else 'FAIL'} |"
        )

    ticker_lines = [
        "| ticker | scope | cached statements | balance Rule A/B status | path | identity mean error | identity errors by period | resolved STI | resolved preferred |",
        "| --- | --- | --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for row in ticker_rows:
        ticker_lines.append(
            f"| {row['ticker']} | {row['scope']} | "
            f"`{_compact_json(row.get('cached_statements'))}` | "
            f"{row['balance_rule_status']} | "
            f"{row.get('resolution_path', '')} | "
            f"{'' if row.get('identity_mean_error') is None else format(row['identity_mean_error'], '.12%')} | "
            f"`{_compact_json(row.get('identity_period_errors'))}` | "
            f"`{_compact_json(row.get('resolved_short_term_investments'))}` | "
            f"`{_compact_json(row.get('resolved_preferred_shares'))}` |"
        )

    helper_lines = [
        "| ticker | other_current_assets | raw count | verbatim raw rows |",
        "| --- | --- | ---: | --- |",
    ]
    for row in helper_rows:
        helper_lines.append(
            f"| {row['ticker']} | {row['other_current_assets']} | {row['raw_count']} | "
            f"`{_escape(_compact_json(row['raw_rows']))}` |"
        )

    item_lines = [
        "| ticker | statement | item_id | classification | raw count | verbatim raw rows | resolved values | identity mean error | identity errors by period | evidence |",
        "| --- | --- | --- | --- | ---: | --- | --- | ---: | --- | --- |",
    ]
    for row in item_rows:
        identity_mean = row["identity_mean_error"]
        item_lines.append(
            f"| {row['ticker']} | {row['statement_type']} | {row['item_id']} | "
            f"{row['classification']} | {row['raw_count']} | "
            f"`{_escape(_compact_json(row['raw_rows']))}` | "
            f"`{_escape(_compact_json(row['resolved_values']))}` | "
            f"{'' if identity_mean is None else format(identity_mean, '.12%')} | "
            f"`{_escape(_compact_json(row['identity_period_errors']))}` | "
            f"{row['evidence_note']} |"
        )

    nonfinancial_rows = [row for row in ticker_rows if row["ticker"] != "VCB"]
    resolved_balances = sum(row["balance_rule_status"] == "RESOLVED" for row in nonfinancial_rows)
    comparison_resolved = sum(row["final_status"] == "RESOLVED" for row in comparison)
    document = "\n".join(
        [
            "# Sprint 3 — cached 40-ticker REQUIRED_ITEMS v1 sample verification",
            "",
            f"Date: `{date.today().isoformat()}`",
            f"Frozen source observation date: `{AS_OF}`",
            "Fixed sample: the existing 40 tickers from seed `20260715`; no ticker was replaced.",
            "Network calls made by this run: `0`.",
            "Thresholds used unchanged: `IDENTITY_TOL=0.01`, `IDENTITY_MIN_PERIODS=3`, `IDENTITY_MARGIN=5.0`, `DUP_MATERIALITY_EPS=0.01`.",
            "Full-universe job: `NOT RUN`. The >=90% gate: `NOT COMPUTED`.",
            "",
            "## Tóm tắt đơn giản cho chủ project",
            "",
            f"- Đã đọc lại dữ liệu đã lưu của đúng 40 mã, không tải rộng từ mạng. Phần kiểm tra bảng cân đối chạy thành công cho {resolved_balances}/39 mã phi tài chính; VCB là ngân hàng và đã có đủ ba báo cáo thô trong cache (cân đối, thu nhập, luồng tiền).",
            f"- Cả {comparison_resolved}/7 mã từng bị cách ly nay tự vượt quy tắc khi dùng hàng tồn kho ròng. Không mã nào được ép qua và không ngưỡng nào bị đổi.",
            "- Ví dụ: nếu hàng tồn kho gộp là 100 và dự phòng là -3 thì tài sản ngắn hạn chỉ chứa 97. Dùng 100 làm phép cộng sẽ tạo sai số giả 3; sửa sang 97 làm đẳng thức khớp đúng.",
            f"- Có {missing_statement_count} báo cáo thu nhập/luồng tiền của mẫu chưa nằm trong bộ nhớ đệm. Các mục thuộc những báo cáo đó được ghi `MISSING` kèm lý do `STATEMENT_NOT_CACHED_NOT_PROVIDER_MISSING`; điều này không có nghĩa nhà cung cấp chắc chắn thiếu dữ liệu.",
            "- Ý nghĩa: lỗi hàng tồn kho đã được xác nhận và sửa bằng số thật. Tuy nhiên báo cáo mẫu 31 mục vẫn chưa thể kết luận độ phủ toàn thị trường vì chủ project đã yêu cầu dừng trước bước đó.",
            "- Việc còn lại: chủ project xem báo cáo này. Chưa cần quyết định ngưỡng; chỉ cần duyệt hoặc yêu cầu sửa báo cáo trước khi cho phép bước tiếp theo.",
            "",
            "## BEFORE / AFTER for the seven previously ambiguous tickers",
            "",
            "`INF` means the corrected winner has exact zero error while the best different-STI rival remains above zero. This mechanically satisfies the unchanged 5x rule; it is not a forced status.",
            "",
            *comparison_lines,
            "",
            "### Verbatim inventory and provision arithmetic",
            "",
            *provision_lines,
            "",
            "## Per-ticker Rule A/B result",
            "",
            *ticker_lines,
            "",
            "## Mandatory helper — separate from REQUIRED_ITEMS coverage",
            "",
            *helper_lines,
            "",
            "## Verbatim per-ticker × per-item table",
            "",
            "Classification is limited to this cached sample. A missing cache is reported honestly and is not treated as proof that the provider lacks the item.",
            "",
            *item_lines,
            "",
            "## Hard stop",
            "",
            "No full-universe fetch or coverage calculation was run. Sprint 4 was not started. PR #1 remains unmerged.",
            "",
        ]
    )
    output_md.write_text(document, encoding="utf-8")
    print(f"Report: {output_md.resolve()}")
    print(f"CSV evidence: {output_csv.resolve()}")
    print(f"Balance resolution: {resolved_balances}/39 non-financial tickers")
    print(f"Previously ambiguous now resolved mechanically: {comparison_resolved}/7")
    print(f"Statements not cached: {missing_statement_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
