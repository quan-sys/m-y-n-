"""Local-only Sprint 6 quality-input readiness audit; computes no quality score."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SURVIVORS_PATH = ROOT / "data" / "screener" / "step1_survivors.csv"
FUNDAMENTALS_ROOT = ROOT / "data" / "fundamentals"
OUTPUT_PATH = ROOT / "data" / "screener" / "sprint6_readiness_audit.csv"
REPORT_PATH = ROOT / "docs" / "SPRINT_6_DATA_READINESS.md"
EVALUATION_DATE = "2026-07-20"
EXPECTED_SURVIVORS = 156
PROPOSED_FRANCHISE_MIN_YEARS = 3

NET_INCOME_ITEM = "net_profit_loss_after_tax"
CFO_ITEM = "net_cash_inflows_outflows_from_operating_activities"
TOTAL_ASSETS_ITEM = "total_assets"
LONG_TERM_DEBT_ITEM = "long_term_borrowings"
CURRENT_ASSETS_ITEM = "current_assets"
CURRENT_LIABILITIES_ITEM = "current_liabilities"
REVENUE_ITEM = "net_sales"
GROSS_PROFIT_ITEM = "gross_profit"
COGS_ITEM = "cost_of_sales"
ISSUE_PROCEEDS_ITEM = "proceeds_from_issue_of_shares"
COMMON_SHARES_ITEM = "common_shares"

ROC_INCOME_ITEMS = (
    "net_accounting_profit_loss_before_tax",
    "interest_expenses",
)
ROC_BALANCE_ITEMS = (
    "owners_equity",
    "short_term_borrowings",
    "long_term_borrowings",
    "cash_and_cash_equivalents",
)


def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "ticker",
            "statement_type",
            "period_type",
            "report_period",
            "available_from",
            "item_id",
            "value",
            "data_status",
        ]
    )


def latest_annual_frame(
    ticker: str, statement: str, fundamentals_root: Path = FUNDAMENTALS_ROOT
) -> tuple[pd.DataFrame, str, bool]:
    root = fundamentals_root / ticker / statement / "year"
    candidates = sorted(root.glob("*/*/normalized.parquet"))
    if not candidates:
        return _empty_frame(), "", False
    path = candidates[-1]
    frame = pd.read_parquet(
        path,
        columns=[
            "ticker",
            "statement_type",
            "period_type",
            "report_period",
            "available_from",
            "item_id",
            "value",
            "data_status",
        ],
    )
    required = {"report_period", "available_from", "item_id", "value"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{path} missing normalized columns: {missing}")
    return frame, path.relative_to(ROOT).as_posix(), True


def eligible_annual_rows(frame: pd.DataFrame, evaluation_date: str) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    available = pd.to_datetime(frame["available_from"], errors="coerce")
    annual_label = frame["report_period"].astype(str).str.fullmatch(r"\d{4}")
    return frame.loc[
        annual_label & available.notna() & available.le(pd.Timestamp(evaluation_date))
    ].copy()


def item_available(frame: pd.DataFrame, item_id: str, year: int) -> bool:
    if frame.empty:
        return False
    matches = frame.loc[
        frame["item_id"].astype(str).eq(item_id)
        & frame["report_period"].astype(str).eq(str(year)),
        "value",
    ]
    if len(matches) != 1:
        return False
    return bool(pd.to_numeric(matches, errors="coerce").notna().all())


def years_in(frame: pd.DataFrame) -> set[int]:
    if frame.empty:
        return set()
    return {
        int(value)
        for value in frame["report_period"].astype(str).unique()
        if str(value).isdigit() and len(str(value)) == 4
    }


def select_annual_pair(
    row: dict[str, Any], income: pd.DataFrame, balance: pd.DataFrame
) -> tuple[int, int, bool, str]:
    try:
        requested_n = int(row["annual_n"])
        requested_n1 = int(row["annual_n_minus_1"])
    except (KeyError, TypeError, ValueError):
        requested_n = 0
        requested_n1 = 0
    common = years_in(income) & years_in(balance)
    requested_valid = (
        requested_n1 == requested_n - 1
        and requested_n in common
        and requested_n1 in common
    )
    if requested_valid:
        return requested_n, requested_n1, True, "STEP1_PAIR_REUSED"
    for year in sorted(common, reverse=True):
        if year - 1 in common:
            return year, year - 1, False, "LATEST_LOCAL_CONSECUTIVE_FALLBACK"
    return requested_n, requested_n1, False, "NO_VALID_CONSECUTIVE_PAIR"


def _gross_margin_inputs_available(income: pd.DataFrame, year: int) -> bool:
    return item_available(income, REVENUE_ITEM, year) and (
        item_available(income, GROSS_PROFIT_ITEM, year)
        or item_available(income, COGS_ITEM, year)
    )


def _share_signal_available(
    cash_flow: pd.DataFrame, balance: pd.DataFrame, year: int
) -> bool:
    return (
        item_available(cash_flow, ISSUE_PROCEEDS_ITEM, year)
        and item_available(balance, COMMON_SHARES_ITEM, year)
        and item_available(balance, COMMON_SHARES_ITEM, year - 1)
    )


def _roc_inputs_available(
    income: pd.DataFrame, balance: pd.DataFrame, year: int
) -> bool:
    return all(item_available(income, item, year) for item in ROC_INCOME_ITEMS) and all(
        item_available(balance, item, balance_year)
        for balance_year in (year, year - 1)
        for item in ROC_BALANCE_ITEMS
    )


def _franchise_years(
    income: pd.DataFrame, balance: pd.DataFrame
) -> tuple[int, int, int, tuple[int, ...]]:
    candidate_years = sorted(years_in(income) & years_in(balance))
    roc_years = tuple(
        year for year in candidate_years if _roc_inputs_available(income, balance, year)
    )
    margin_years = tuple(
        year for year in candidate_years if _gross_margin_inputs_available(income, year)
    )
    common = tuple(year for year in roc_years if year in set(margin_years))
    return len(roc_years), len(margin_years), len(common), common


def audit_ticker_from_frames(
    row: dict[str, Any],
    income_frame: pd.DataFrame,
    balance_frame: pd.DataFrame,
    cash_flow_frame: pd.DataFrame,
    *,
    evaluation_date: str = EVALUATION_DATE,
    income_path: str = "",
    balance_path: str = "",
    cash_flow_path: str = "",
    income_file_exists: bool = True,
    balance_file_exists: bool = True,
    cash_flow_file_exists: bool = True,
) -> dict[str, Any]:
    ticker = str(row["ticker"]).strip().upper()
    income = eligible_annual_rows(income_frame, evaluation_date)
    balance = eligible_annual_rows(balance_frame, evaluation_date)
    cash_flow = eligible_annual_rows(cash_flow_frame, evaluation_date)
    annual_n, annual_n1, pair_reused, pair_status = select_annual_pair(
        row, income, balance
    )
    annual_n2 = annual_n1 - 1

    result: dict[str, Any] = {
        "ticker": ticker,
        "exchange": row.get("exchange", ""),
        "icb2": row.get("icb2", ""),
        "evaluation_date": evaluation_date,
        "annual_n": annual_n,
        "annual_n_minus_1": annual_n1,
        "annual_n_minus_2": annual_n2,
        "step1_annual_pair_reused": pair_reused,
        "annual_pair_status": pair_status,
        "income_annual_dataset_exists": income_file_exists,
        "balance_annual_dataset_exists": balance_file_exists,
        "cash_flow_annual_dataset_exists": cash_flow_file_exists,
        "income_annual_dataset_has_eligible_rows": not income.empty,
        "balance_annual_dataset_has_eligible_rows": not balance.empty,
        "cash_flow_annual_dataset_has_eligible_rows": not cash_flow.empty,
        "income_annual_source_path": income_path,
        "balance_annual_source_path": balance_path,
        "cash_flow_annual_source_path": cash_flow_path,
    }

    specifications = {
        "net_income_n_available": (income, NET_INCOME_ITEM, annual_n),
        "net_income_n_minus_1_available": (income, NET_INCOME_ITEM, annual_n1),
        "cfo_n_available": (cash_flow, CFO_ITEM, annual_n),
        "cfo_n_minus_1_available": (cash_flow, CFO_ITEM, annual_n1),
        "total_assets_n_available": (balance, TOTAL_ASSETS_ITEM, annual_n),
        "total_assets_n_minus_1_available": (balance, TOTAL_ASSETS_ITEM, annual_n1),
        "total_assets_n_minus_2_available": (balance, TOTAL_ASSETS_ITEM, annual_n2),
        "long_term_debt_n_available": (balance, LONG_TERM_DEBT_ITEM, annual_n),
        "long_term_debt_n_minus_1_available": (balance, LONG_TERM_DEBT_ITEM, annual_n1),
        "current_assets_n_available": (balance, CURRENT_ASSETS_ITEM, annual_n),
        "current_assets_n_minus_1_available": (balance, CURRENT_ASSETS_ITEM, annual_n1),
        "current_liabilities_n_available": (balance, CURRENT_LIABILITIES_ITEM, annual_n),
        "current_liabilities_n_minus_1_available": (balance, CURRENT_LIABILITIES_ITEM, annual_n1),
        "revenue_n_available": (income, REVENUE_ITEM, annual_n),
        "revenue_n_minus_1_available": (income, REVENUE_ITEM, annual_n1),
        "gross_profit_n_available": (income, GROSS_PROFIT_ITEM, annual_n),
        "gross_profit_n_minus_1_available": (income, GROSS_PROFIT_ITEM, annual_n1),
        "cogs_n_available": (income, COGS_ITEM, annual_n),
        "cogs_n_minus_1_available": (income, COGS_ITEM, annual_n1),
        "issue_proceeds_n_available": (cash_flow, ISSUE_PROCEEDS_ITEM, annual_n),
        "issue_proceeds_n_minus_1_available": (cash_flow, ISSUE_PROCEEDS_ITEM, annual_n1),
        "common_shares_n_available": (balance, COMMON_SHARES_ITEM, annual_n),
        "common_shares_n_minus_1_available": (balance, COMMON_SHARES_ITEM, annual_n1),
        "common_shares_n_minus_2_available": (balance, COMMON_SHARES_ITEM, annual_n2),
    }
    for column, (frame, item_id, year) in specifications.items():
        result[column] = item_available(frame, item_id, year)

    result["gross_margin_inputs_n_available"] = _gross_margin_inputs_available(
        income, annual_n
    )
    result["gross_margin_inputs_n_minus_1_available"] = _gross_margin_inputs_available(
        income, annual_n1
    )
    result["share_issuance_signal_n_available"] = _share_signal_available(
        cash_flow, balance, annual_n
    )
    result["share_issuance_signal_n_minus_1_available"] = _share_signal_available(
        cash_flow, balance, annual_n1
    )

    criteria = {
        "criterion_1_inputs_available": result["net_income_n_available"]
        and result["total_assets_n_minus_1_available"],
        "criterion_2_inputs_available": result["cfo_n_available"]
        and result["total_assets_n_minus_1_available"],
        "criterion_3_inputs_available": result["net_income_n_available"]
        and result["net_income_n_minus_1_available"]
        and result["total_assets_n_minus_1_available"]
        and result["total_assets_n_minus_2_available"],
        "criterion_4_inputs_available": result["cfo_n_available"]
        and result["net_income_n_available"]
        and result["total_assets_n_minus_1_available"],
        "criterion_5_inputs_available": result["long_term_debt_n_available"]
        and result["long_term_debt_n_minus_1_available"]
        and result["total_assets_n_available"]
        and result["total_assets_n_minus_1_available"]
        and result["total_assets_n_minus_2_available"],
        "criterion_6_inputs_available": result["current_assets_n_available"]
        and result["current_assets_n_minus_1_available"]
        and result["current_liabilities_n_available"]
        and result["current_liabilities_n_minus_1_available"],
        "criterion_7_inputs_available": result["share_issuance_signal_n_available"],
        "criterion_8_inputs_available": result["gross_margin_inputs_n_available"]
        and result["gross_margin_inputs_n_minus_1_available"],
        "criterion_9_inputs_available": result["revenue_n_available"]
        and result["revenue_n_minus_1_available"]
        and result["total_assets_n_minus_1_available"]
        and result["total_assets_n_minus_2_available"],
    }
    result.update(criteria)
    result["fscore_criteria_inputs_available_count"] = sum(criteria.values())

    complete_columns = [
        "net_income_n_available",
        "net_income_n_minus_1_available",
        "cfo_n_available",
        "cfo_n_minus_1_available",
        "total_assets_n_available",
        "total_assets_n_minus_1_available",
        "total_assets_n_minus_2_available",
        "long_term_debt_n_available",
        "long_term_debt_n_minus_1_available",
        "current_assets_n_available",
        "current_assets_n_minus_1_available",
        "current_liabilities_n_available",
        "current_liabilities_n_minus_1_available",
        "revenue_n_available",
        "revenue_n_minus_1_available",
        "gross_margin_inputs_n_available",
        "gross_margin_inputs_n_minus_1_available",
        "share_issuance_signal_n_available",
        "share_issuance_signal_n_minus_1_available",
    ]
    result["complete_fscore_inputs_both_years"] = all(
        bool(result[column]) for column in complete_columns
    )

    common_history = years_in(income) & years_in(balance)
    roc_depth, margin_depth, years_used, franchise_years = _franchise_years(
        income, balance
    )
    result["annual_history_depth"] = len(common_history)
    result["annual_history_years"] = "|".join(str(year) for year in sorted(common_history))
    result["franchise_roc_years_available"] = roc_depth
    result["franchise_margin_years_available"] = margin_depth
    result["franchise_years_used"] = years_used
    result["franchise_year_labels"] = "|".join(str(year) for year in franchise_years)
    result["franchise_minimum_years_proposed"] = PROPOSED_FRANCHISE_MIN_YEARS
    result["franchise_history_status"] = (
        "READY"
        if years_used >= PROPOSED_FRANCHISE_MIN_YEARS
        else "INSUFFICIENT_HISTORY"
    )
    result["source"] = "existing local normalized annual fundamentals only"
    result["data_status"] = "READINESS_AUDIT_ONLY"
    return result


def audit_survivor(
    row: dict[str, Any], fundamentals_root: Path = FUNDAMENTALS_ROOT
) -> dict[str, Any]:
    ticker = str(row["ticker"]).strip().upper()
    frames: dict[str, pd.DataFrame] = {}
    paths: dict[str, str] = {}
    exists: dict[str, bool] = {}
    for statement in ("income_statement", "balance_sheet", "cash_flow"):
        frame, path, file_exists = latest_annual_frame(
            ticker, statement, fundamentals_root
        )
        frames[statement] = frame
        paths[statement] = path
        exists[statement] = file_exists
    return audit_ticker_from_frames(
        row,
        frames["income_statement"],
        frames["balance_sheet"],
        frames["cash_flow"],
        income_path=paths["income_statement"],
        balance_path=paths["balance_sheet"],
        cash_flow_path=paths["cash_flow"],
        income_file_exists=exists["income_statement"],
        balance_file_exists=exists["balance_sheet"],
        cash_flow_file_exists=exists["cash_flow"],
    )


def run_audit(
    survivors_path: Path = SURVIVORS_PATH,
    fundamentals_root: Path = FUNDAMENTALS_ROOT,
) -> pd.DataFrame:
    survivors = pd.read_csv(survivors_path)
    tickers = survivors["ticker"].astype(str).str.strip().str.upper()
    if len(survivors) != EXPECTED_SURVIVORS or tickers.nunique() != EXPECTED_SURVIVORS:
        raise ValueError(
            f"expected {EXPECTED_SURVIVORS} unique survivors; "
            f"rows={len(survivors)} unique={tickers.nunique()}"
        )
    survivors = survivors.copy()
    survivors["ticker"] = tickers
    audited = pd.DataFrame(
        audit_survivor(row, fundamentals_root)
        for row in survivors.to_dict("records")
    )
    if len(audited) != EXPECTED_SURVIVORS or audited["ticker"].nunique() != EXPECTED_SURVIVORS:
        raise AssertionError("audit output is not exactly one row per survivor")
    return audited


def render_report(audited: pd.DataFrame) -> str:
    cash_files = int(audited["cash_flow_annual_dataset_exists"].sum())
    cash_rows = int(audited["cash_flow_annual_dataset_has_eligible_rows"].sum())
    complete = int(audited["complete_fscore_inputs_both_years"].sum())
    labels = Counter(int(value) for value in audited["franchise_years_used"])
    special = audited.loc[audited["ticker"].isin(["NTC", "TRC", "DBC"])].copy()
    special["_order"] = special["ticker"].map({"NTC": 0, "TRC": 1, "DBC": 2})
    special = special.sort_values("_order")

    availability_columns = [
        column
        for column in audited.columns
        if column.endswith("_available")
        and pd.api.types.is_bool_dtype(audited[column])
    ]
    lines = [
        "# Sprint 6 local data-readiness audit",
        "",
        f"- Evaluation date: `{EVALUATION_DATE}`.",
        f"- Survivor rows: `{len(audited)}`; unique tickers: `{audited['ticker'].nunique()}`.",
        "- Network/API calls: `0`; production F-Scores: `0`; production Franchise Power scores: `0`; production composite-quality scores: `0`.",
        "",
        "## 1. Cash-flow dataset existence — answered first",
        "",
        f"**YES.** A local normalized annual cash-flow file exists for `{cash_files}/{len(audited)}` survivors; `{cash_rows}/{len(audited)}` contain at least one annual row available by the evaluation date.",
        f"The proposed CFO field `net_cash_inflows_outflows_from_operating_activities` is available for year N in `{int(audited['cfo_n_available'].sum())}/{len(audited)}` rows and year N-1 in `{int(audited['cfo_n_minus_1_available'].sum())}/{len(audited)}` rows.",
        "",
        "## 2. Exact input availability counts",
        "",
        "| availability flag | available | missing |",
        "|---|---:|---:|",
    ]
    for column in availability_columns:
        count = int(audited[column].sum())
        lines.append(f"| `{column}` | {count} | {len(audited) - count} |")
    lines.extend(
        [
            "",
            "## 3. F-Score build readiness",
            "",
            f"- Complete proposed F-Score inputs for both N and N-1, including required N-2 denominators/signals: `{complete}/{len(audited)}`.",
            f"- All nine criteria have their required inputs available: `{int(audited['fscore_criteria_inputs_available_count'].eq(9).sum())}/{len(audited)}`.",
            f"- Sprint 4 annual pair reused without fallback: `{int(audited['step1_annual_pair_reused'].sum())}/{len(audited)}`.",
            "- This is availability evidence only. No criterion was evaluated and no F-Score was computed.",
            "",
            "## 4. Franchise Power history depth",
            "",
            f"- Proposed minimum usable years: `{PROPOSED_FRANCHISE_MIN_YEARS}`.",
            f"- READY: `{int(audited['franchise_history_status'].eq('READY').sum())}/{len(audited)}`.",
            f"- INSUFFICIENT_HISTORY: `{int(audited['franchise_history_status'].eq('INSUFFICIENT_HISTORY').sum())}/{len(audited)}`.",
            "",
            "| franchise_years_used | ticker count |",
            "|---:|---:|",
        ]
    )
    for depth in sorted(labels):
        lines.append(f"| {depth} | {labels[depth]} |")
    lines.extend(
        [
            "",
            "The local cache exposes at most four annual report periods per ticker. ROC needs both a current and a prior invested-capital observation, so the observed maximum usable ROC/margin overlap is three years. The proposed minimum of three uses the full locally available comparable window; rows below it remain visible with `INSUFFICIENT_HISTORY` rather than being excluded.",
            "",
            "## 5. NTC, TRC, and DBC explicit rows",
            "",
            "| ticker | annual_n | annual_n_minus_1 | cash_flow annual file | nine criteria inputs available | complete F-Score inputs both years | franchise_years_used | franchise_history_status |",
            "|---|---:|---:|---|---:|---|---:|---|",
        ]
    )
    for row in special.itertuples(index=False):
        lines.append(
            f"| {row.ticker} | {row.annual_n} | {row.annual_n_minus_1} | "
            f"{row.cash_flow_annual_dataset_exists} | {row.fscore_criteria_inputs_available_count} | "
            f"{row.complete_fscore_inputs_both_years} | {row.franchise_years_used} | "
            f"{row.franchise_history_status} |"
        )
    entirely_absent = [
        column
        for column in availability_columns
        if int(audited[column].sum()) == 0
    ]
    partially_missing = [
        column
        for column in availability_columns
        if 0 < int(audited[column].sum()) < len(audited)
    ]
    lines.extend(
        [
            "",
            "## 6. Build-phase prerequisites",
            "",
        ]
    )
    if entirely_absent:
        lines.append(
            "Entirely absent local input classes: "
            + ", ".join(f"`{column}`" for column in entirely_absent)
            + ". They must be sourced and audited in a later owner-approved build phase; this audit does not fetch them."
        )
    else:
        lines.append(
            "Entirely absent local input classes: `NONE`."
        )
    if partially_missing:
        lines.append(
            "Partially missing availability flags: "
            + ", ".join(f"`{column}`" for column in partially_missing)
            + ". Any affected future criterion must stay UNSCORED."
        )
    else:
        lines.append("Partially missing audited availability flags: `NONE`.")
    lines.extend(
        [
            "",
            "Production quality computation remains **FORBIDDEN** until the owner approves `docs/SPEC_SPRINT_6.md`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    audited = run_audit()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    audited.to_csv(OUTPUT_PATH, index=False, lineterminator="\n")
    REPORT_PATH.write_text(render_report(audited), encoding="utf-8")
    print(f"cash_flow_files={int(audited['cash_flow_annual_dataset_exists'].sum())}")
    print(
        "cash_flow_eligible_rows="
        f"{int(audited['cash_flow_annual_dataset_has_eligible_rows'].sum())}"
    )
    print(f"rows={len(audited)}; unique={audited['ticker'].nunique()}")
    print(
        "complete_fscore_inputs_both_years="
        f"{int(audited['complete_fscore_inputs_both_years'].sum())}"
    )
    print(
        "all_nine_criteria_inputs="
        f"{int(audited['fscore_criteria_inputs_available_count'].eq(9).sum())}"
    )
    print(
        "franchise_history="
        f"ready={int(audited['franchise_history_status'].eq('READY').sum())};"
        f"insufficient={int(audited['franchise_history_status'].eq('INSUFFICIENT_HISTORY').sum())};"
        f"depths={dict(sorted(Counter(int(value) for value in audited['franchise_years_used']).items()))}"
    )
    print("network_calls=0; production_scores=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
