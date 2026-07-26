from decimal import Decimal

import pandas as pd

from scripts.build_sprint9_3_historical_valuation import (
    build_valuation_row,
    calculate_tev,
    market_cap_to_vnd,
    select_ttm_quarters,
)


FLOW_VALUES = {
    "net_accounting_profit_loss_before_tax": "10",
    "interest_expenses": "-2",
    "attributable_to_parent_company": "8",
}
STOCK_VALUES = {
    "short_term_borrowings": "20",
    "long_term_borrowings": "30",
    "cash_and_cash_equivalents": "10",
    "minority_interests": "5",
}


def fundamentals_fixture(
    quarters=("2023Q4", "2024Q1", "2024Q2", "2024Q3"),
    *,
    available_from=None,
    include_minority=True,
    pbt="10",
):
    rows = []
    for quarter in quarters:
        values = {**FLOW_VALUES, **STOCK_VALUES}
        values["net_accounting_profit_loss_before_tax"] = pbt
        if not include_minority:
            values.pop("minority_interests")
        for item_id, value in values.items():
            rows.append(
                {
                    "ticker": "AAA",
                    "quarter": quarter,
                    "available_from": (available_from or {}).get(
                        quarter, "2024-01-01"
                    ),
                    "item_id": item_id,
                    "value": value,
                }
            )
    return pd.DataFrame(rows)


def market_row(**overrides):
    row = {
        "ticker": "AAA",
        "quarter": "2024Q4",
        "measurement_date": "2024-12-31",
        "market_cap_thousand_vnd": "1",
        "price_confidence": "OK",
        "market_cap_status": "OK",
    }
    row.update(overrides)
    return row


def test_unit_bridge_and_hand_calculated_tev():
    market_cap_vnd = market_cap_to_vnd(Decimal("1"))

    assert market_cap_vnd == Decimal("1000")
    assert calculate_tev(
        market_cap_vnd,
        Decimal("20"),
        Decimal("30"),
        Decimal("10"),
        Decimal("5"),
    ) == Decimal("1045")


def test_ttm_uses_prior_four_when_evaluation_quarter_is_not_yet_available():
    fundamentals = fundamentals_fixture(
        quarters=("2023Q4", "2024Q1", "2024Q2", "2024Q3", "2024Q4"),
        available_from={"2024Q4": "2025-01-30"},
    )

    assert select_ttm_quarters(fundamentals, "2024-12-31") == (
        "2023Q4",
        "2024Q1",
        "2024Q2",
        "2024Q3",
    )


def test_stock_items_come_from_latest_single_quarter_not_a_sum():
    fundamentals = fundamentals_fixture()
    fundamentals.loc[
        (fundamentals["quarter"] == "2024Q3")
        & (fundamentals["item_id"] == "short_term_borrowings"),
        "value",
    ] = "77"

    row = build_valuation_row(market_row(), fundamentals, run_date="2026-07-26")

    assert row["stock_quarter"] == "2024Q3"
    assert row["short_term_borrowings"] == Decimal("77")


def test_absent_minority_is_unavailable_and_omitted_from_tev():
    row = build_valuation_row(
        market_row(),
        fundamentals_fixture(include_minority=False),
        run_date="2026-07-26",
    )

    assert row["minority_interests"] is None
    assert row["minority_interest_status"] == "UNAVAILABLE"
    assert row["tev"] == Decimal("1040")


def test_negative_ebit_remains_visible_but_is_ineligible():
    row = build_valuation_row(
        market_row(),
        fundamentals_fixture(pbt="-10"),
        run_date="2026-07-26",
    )

    assert row["ebit_proxy_vas"] == Decimal("-32")
    assert row["ebit_tev"] is not None
    assert row["ebit_tev_eligible"] is False


def test_only_three_available_quarters_is_insufficient_ttm():
    row = build_valuation_row(
        market_row(),
        fundamentals_fixture(quarters=("2024Q1", "2024Q2", "2024Q3")),
        run_date="2026-07-26",
    )

    assert row["valuation_status"] == "INSUFFICIENT_TTM"
    assert row["ttm_quarters"] == ""
    assert row["ebit_proxy_vas"] is None
    assert row["tev"] is None
    assert row["ebit_tev"] is None
    assert row["e_p"] is None
