from __future__ import annotations

import pandas as pd
import pytest

from scripts.audit_sprint6_readiness import (
    CRITERION7_MISSING_INPUT,
    CRITERION7_SCORE_0,
    CRITERION7_SCORE_1,
    CRITERION7_SHARE_INCREASE_NO_CASH,
)
from scripts.build_sprint6_fscore import (
    MIN_SCORED_CRITERIA,
    CriterionResult,
    compute_ticker,
    criterion7_score,
    finalize_scores,
)


@pytest.mark.parametrize(
    ("common_n", "common_n1", "proceeds_n", "branch", "result", "ratio"),
    (
        (110.0, 100.0, 5.0, CRITERION7_SCORE_0, 0, None),
        (100.0, 100.0, 0.0, CRITERION7_SCORE_1, 1, None),
        (110.0, 100.0, 0.0, CRITERION7_SHARE_INCREASE_NO_CASH, None, None),
        (100.0, 100.0, 5.0, CRITERION7_SCORE_0, 0, 0.05),
    ),
)
def test_criterion7_settled_cases(
    common_n: float,
    common_n1: float,
    proceeds_n: float,
    branch: str,
    result: int | None,
    ratio: float | None,
) -> None:
    scored, actual_branch, actual_ratio = criterion7_score(
        common_n, common_n1, proceeds_n
    )
    assert actual_branch == branch
    assert scored.result == result
    assert actual_ratio == ratio


def test_criterion7_missing_input_is_unscored() -> None:
    scored, branch, ratio = criterion7_score(
        None,
        100.0,
        0.0,
        common_n_status="MISSING",
    )
    assert branch == CRITERION7_MISSING_INPUT
    assert scored.result is None
    assert scored.flag == "COMMON_SHARES_N_MISSING"
    assert ratio is None


def test_unscored_criterion_does_not_collapse_to_zero() -> None:
    results = [CriterionResult(1, "", ()) for _ in range(8)]
    results.append(CriterionResult(None, "INPUT_MISSING", ()))
    summary = finalize_scores(results)
    assert summary["F_SCORE_POINTS"] == 8
    assert summary["F_SCORE_CRITERIA_SCORED"] == 8
    assert summary["F_SCORE_CRITERIA_UNSCORED"] == 1
    assert summary["fscore_ranking_ratio"] == 1.0
    assert summary["fscore_ranking_eligible"] is (8 >= MIN_SCORED_CRITERIA)


def _frame(statement_type: str, values: dict[str, dict[int, float]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "statement_type": statement_type,
                "period_type": "YEAR",
                "report_period": str(year),
                "available_from": f"{year + 1}-03-31",
                "item_id": item_id,
                "value": value,
                "data_status": "OK",
            }
            for item_id, yearly in values.items()
            for year, value in yearly.items()
        ]
    )


@pytest.fixture
def complete_ticker_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    years = (2023, 2024, 2025)
    income = _frame(
        "INCOME_STATEMENT",
        {
            "net_profit_loss_after_tax": {2024: 10, 2025: 12},
            "attributable_to_parent_company": {2025: 11},
            "net_sales": {2024: 80, 2025: 100},
            "gross_profit": {2024: 24, 2025: 35},
            "cost_of_sales": {2024: -56, 2025: -65},
        },
    )
    balance = _frame(
        "BALANCE_SHEET",
        {
            "total_assets": dict(zip(years, (90, 100, 110))),
            "long_term_borrowings": {2024: 20, 2025: 18},
            "current_assets": {2024: 40, 2025: 50},
            "current_liabilities": {2024: 25, 2025: 25},
            "common_shares": {2024: 100, 2025: 100},
        },
    )
    cash_flow = _frame(
        "CASH_FLOW",
        {
            "net_cash_inflows_outflows_from_operating_activities": {2025: 15},
            "proceeds_from_issue_of_shares": {2025: 0},
        },
    )
    return income, balance, cash_flow


@pytest.mark.parametrize("bad_denominator", (0.0, -1.0))
def test_nonpositive_current_liabilities_block_current_ratio_criterion(
    complete_ticker_frames: tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame],
    bad_denominator: float,
) -> None:
    income, balance, cash_flow = complete_ticker_frames
    balance = balance.copy()
    mask = balance["item_id"].eq("current_liabilities") & balance[
        "report_period"
    ].eq("2025")
    balance.loc[mask, "value"] = bad_denominator
    _, results, _ = compute_ticker(
        {
            "ticker": "AAA",
            "exchange": "HOSE",
            "icb2": "TEST",
            "annual_n": 2025,
            "annual_n_minus_1": 2024,
        },
        income,
        balance,
        cash_flow,
    )
    assert results[6].result is None
    assert "CURRENT_LIABILITIES_N_NON_POSITIVE" in results[6].flag


def test_nonpositive_prior_revenue_is_diagnostic_and_only_blocks_margin(
    complete_ticker_frames: tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame],
) -> None:
    income, balance, cash_flow = complete_ticker_frames
    baseline_row, baseline_results, _ = compute_ticker(
        {
            "ticker": "AAA",
            "exchange": "HOSE",
            "icb2": "TEST",
            "annual_n": 2025,
            "annual_n_minus_1": 2024,
        },
        income,
        balance,
        cash_flow,
    )
    income = income.copy()
    mask = income["item_id"].eq("net_sales") & income["report_period"].eq("2024")
    income.loc[mask, "value"] = -80.0
    row, results, _ = compute_ticker(
        {
            "ticker": "AAA",
            "exchange": "HOSE",
            "icb2": "TEST",
            "annual_n": 2025,
            "annual_n_minus_1": 2024,
        },
        income,
        balance,
        cash_flow,
    )
    assert baseline_row["non_positive_revenue_n_minus_1"] is False
    assert row["non_positive_revenue_n_minus_1"] is True
    assert results[8].result is None
    assert "NET_SALES_N_minus_1_NON_POSITIVE" in results[8].flag
    assert {
        number: result.result for number, result in results.items() if number != 8
    } == {
        number: result.result
        for number, result in baseline_results.items()
        if number != 8
    }


def test_scored_and_unscored_sum_to_nine() -> None:
    for scored_count in range(10):
        results = [CriterionResult(1, "", ()) for _ in range(scored_count)]
        results.extend(
            CriterionResult(None, "INPUT_MISSING", ())
            for _ in range(9 - scored_count)
        )
        summary = finalize_scores(results)
        assert (
            summary["F_SCORE_CRITERIA_SCORED"]
            + summary["F_SCORE_CRITERIA_UNSCORED"]
            == 9
        )


def test_ranking_ratio_is_empty_when_scored_denominator_is_zero() -> None:
    summary = finalize_scores([CriterionResult(None, "INPUT_MISSING", ())] * 9)
    assert summary["F_SCORE_POINTS"] == 0
    assert summary["F_SCORE_CRITERIA_SCORED"] == 0
    assert summary["fscore_ranking_ratio"] is None
    assert summary["fscore_ranking_eligible"] is False
