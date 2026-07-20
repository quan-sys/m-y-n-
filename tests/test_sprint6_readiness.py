from __future__ import annotations

import pandas as pd

from scripts.audit_sprint6_readiness import audit_ticker_from_frames


def annual_rows(
    statement_type: str,
    items: tuple[str, ...],
    years: tuple[int, ...] = (2022, 2023, 2024, 2025),
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "statement_type": statement_type,
                "period_type": "YEAR",
                "report_period": str(year),
                "available_from": f"{year + 1}-03-31",
                "item_id": item,
                "value": year * 100 + index,
                "data_status": "OK",
            }
            for year in years
            for index, item in enumerate(items)
        ]
    )


def complete_frames(
    years: tuple[int, ...] = (2022, 2023, 2024, 2025),
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    income = annual_rows(
        "INCOME_STATEMENT",
        (
            "net_profit_loss_after_tax",
            "net_sales",
            "gross_profit",
            "cost_of_sales",
            "net_accounting_profit_loss_before_tax",
            "interest_expenses",
        ),
        years,
    )
    balance = annual_rows(
        "BALANCE_SHEET",
        (
            "total_assets",
            "long_term_borrowings",
            "current_assets",
            "current_liabilities",
            "common_shares",
            "owners_equity",
            "short_term_borrowings",
            "cash_and_cash_equivalents",
        ),
        years,
    )
    cash_flow = annual_rows(
        "CASH_FLOW",
        (
            "net_cash_inflows_outflows_from_operating_activities",
            "proceeds_from_issue_of_shares",
        ),
        years,
    )
    return income, balance, cash_flow


def survivor() -> dict[str, object]:
    return {
        "ticker": "AAA",
        "exchange": "HOSE",
        "icb2": "TEST",
        "annual_n": 2025,
        "annual_n_minus_1": 2024,
    }


def test_complete_ticker_has_all_fscore_inputs_and_three_franchise_years() -> None:
    income, balance, cash_flow = complete_frames()
    result = audit_ticker_from_frames(survivor(), income, balance, cash_flow)
    assert result["step1_annual_pair_reused"] is True
    assert result["fscore_criteria_inputs_available_count"] == 9
    assert result["complete_fscore_inputs_both_years"] is True
    assert result["franchise_years_used"] == 3
    assert result["franchise_history_status"] == "READY"


def test_ticker_missing_one_input_keeps_the_gap_explicit() -> None:
    income, balance, cash_flow = complete_frames()
    cash_flow = cash_flow.loc[
        ~(
            cash_flow["item_id"].eq(
                "net_cash_inflows_outflows_from_operating_activities"
            )
            & cash_flow["report_period"].eq("2025")
        )
    ].copy()
    result = audit_ticker_from_frames(survivor(), income, balance, cash_flow)
    assert result["cfo_n_available"] is False
    assert result["criterion_2_inputs_available"] is False
    assert result["criterion_4_inputs_available"] is False
    assert result["complete_fscore_inputs_both_years"] is False


def test_ticker_with_short_history_is_flagged_without_exclusion() -> None:
    income, balance, cash_flow = complete_frames((2024, 2025))
    result = audit_ticker_from_frames(survivor(), income, balance, cash_flow)
    assert result["annual_history_depth"] == 2
    assert result["franchise_years_used"] == 1
    assert result["franchise_history_status"] == "INSUFFICIENT_HISTORY"
