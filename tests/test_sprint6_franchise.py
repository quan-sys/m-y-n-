from __future__ import annotations

import math

import pandas as pd

from scripts.build_sprint6_franchise import (
    composite_value,
    compute_margin_series,
    compute_roc_series,
    rank_percentile,
    summarize_margin,
    summarize_roc,
)


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


def test_nonpositive_average_invested_capital_makes_roc_year_unavailable() -> None:
    income = _frame(
        "INCOME_STATEMENT",
        {
            "net_accounting_profit_loss_before_tax": {2025: 10},
            "interest_expenses": {2025: -2},
        },
    )
    balance = _frame(
        "BALANCE_SHEET",
        {
            "owners_equity": {2024: 10, 2025: 10},
            "short_term_borrowings": {2024: 0, 2025: 0},
            "long_term_borrowings": {2024: 0, 2025: 0},
            "cash_and_cash_equivalents": {2024: 20, 2025: 20},
        },
    )
    usable, dropped = compute_roc_series(income, balance, (2025,))
    assert usable == []
    assert dropped == [(2025, "NON_POSITIVE_AVERAGE_INVESTED_CAPITAL")]


def test_nonpositive_net_sales_year_is_dropped_not_zero_filled() -> None:
    income = _frame(
        "INCOME_STATEMENT",
        {
            "net_sales": {2024: 0, 2025: 100},
            "gross_profit": {2024: 20, 2025: 30},
        },
    )
    usable, dropped = compute_margin_series(income, (2024, 2025))
    assert [item.year for item in usable] == [2025]
    assert [item.gross_margin for item in usable] == [0.3]
    assert dropped == [(2024, "NON_POSITIVE_NET_SALES")]


def test_one_usable_margin_year_has_missing_stability_not_zero_std() -> None:
    mean, population_std, stability, flag = summarize_margin([0.25])
    assert mean == 0.25
    assert population_std is None
    assert stability is None
    assert flag == "FEWER_THAN_TWO_USABLE_MARGIN_YEARS"


def test_tied_values_receive_identical_rank_percentile() -> None:
    percentiles = rank_percentile(pd.Series([1.0, 1.0, 2.0]))
    assert percentiles.iloc[0] == percentiles.iloc[1]
    assert percentiles.iloc[2] == 1.0


def test_missing_component_shrinks_composite_denominator_without_zero() -> None:
    composite, components = composite_value((0.2, None, 0.8))
    assert components == 2
    assert composite == 0.5


def test_margin_uses_population_not_sample_standard_deviation() -> None:
    mean, population_std, stability, flag = summarize_margin([0.2, 0.4])
    assert math.isclose(mean or 0, 0.3)
    assert math.isclose(population_std or 0, 0.1)
    assert math.isclose(stability or 0, 3.0)
    assert not math.isclose(population_std or 0, math.sqrt(0.02))
    assert flag == ""


def test_zero_variance_margin_gets_maximum_percentile_without_infinity() -> None:
    mean, population_std, stability, flag = summarize_margin([0.3, 0.3])
    assert mean == 0.3
    assert population_std == 0
    assert stability is None
    assert flag == "ZERO_MARGIN_VARIANCE"
    percentiles = rank_percentile(
        pd.Series([stability, 2.0]),
        maximum_mask=pd.Series([flag == "ZERO_MARGIN_VARIANCE", False]),
    )
    assert percentiles.iloc[0] == 1.0
    assert not math.isinf(percentiles.iloc[0])


def test_nonpositive_mean_margin_is_missing_not_negative_ratio() -> None:
    mean, population_std, stability, flag = summarize_margin([-0.2, -0.4])
    assert math.isclose(mean or 0, -0.3)
    assert population_std is not None
    assert stability is None
    assert flag == "NON_POSITIVE_MEAN_GROSS_MARGIN"


def test_nonpositive_roc_blocks_geometric_but_keeps_arithmetic_mean() -> None:
    arithmetic, geometric, flag = summarize_roc([0.2, -0.1, 0.3])
    assert math.isclose(arithmetic or 0, 0.4 / 3)
    assert geometric is None
    assert flag == "NON_POSITIVE_ROC_YEAR_PRESENT"
