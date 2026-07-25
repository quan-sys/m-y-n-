from __future__ import annotations

from datetime import timedelta

import pandas as pd
import pytest

from scripts.probe_fundamentals_coverage import (
    classify_universe,
    count_missing_gap_quarters,
    derive_available_from,
    measure_key_item_availability,
)
from src.data.finance_client import LAG_QUARTER, NORMALIZED_COLUMNS


def _normalized_fixture(rows: list[dict[str, object]]) -> pd.DataFrame:
    """Mimic the exact normalized FinanceClient return shape with synthetic values."""
    defaults: dict[str, object] = {
        "ticker": "TST",
        "company_type": "NON_FINANCIAL",
        "statement_type": "INCOME_STATEMENT",
        "period_type": "QUARTER",
        "report_period": "2024Q1",
        "period_end": "2024-03-31",
        "available_from": "2024-04-30",
        "item_id": "net_accounting_profit_loss_before_tax",
        "item": "Synthetic item",
        "item_en": "Synthetic item",
        "value": 2_000_000_000,
        "currency": "VND",
        "source": "synthetic_fixture_mimicking_finance_client",
        "as_of": "2026-07-24",
        "data_status": "OK",
    }
    return pd.DataFrame(
        [{**defaults, **row} for row in rows],
        columns=NORMALIZED_COLUMNS,
    )


def test_available_from_uses_imported_lag_quarter() -> None:
    period_end = pd.Timestamp("2024-03-31")
    assert derive_available_from(period_end.date()) == (
        period_end + timedelta(days=LAG_QUARTER)
    ).date().isoformat()
    assert derive_available_from(period_end.date()) == "2024-04-30"


@pytest.mark.parametrize(
    ("periods", "expected"),
    [
        (["2024Q1"], 0),
        (["2023Q4", "2024Q1", "2024Q2"], 0),
        (["2023Q4", "2024Q2"], 1),
        (["2023Q2", "2024Q2"], 3),
    ],
)
def test_gap_counting_between_earliest_and_latest_quarter(
    periods: list[str], expected: int
) -> None:
    assert count_missing_gap_quarters(periods) == expected


def test_key_item_presence_counter_uses_ticker_quarter_values() -> None:
    income = _normalized_fixture(
        [
            {},
            {
                "report_period": "2024Q2",
                "period_end": "2024-06-30",
                "available_from": "2024-07-30",
                "value": pd.NA,
                "data_status": "MISSING_DATA",
            },
            {
                "item_id": "interest_expenses",
                "report_period": "2024Q1",
                "value": -1_500_000_000,
            },
            {
                "item_id": "interest_expenses",
                "report_period": "2024Q2",
                "period_end": "2024-06-30",
                "available_from": "2024-07-30",
                "value": -1_600_000_000,
            },
        ]
    )

    availability, anomalies = measure_key_item_availability(
        {"income_statement": income, "balance_sheet": pd.DataFrame()}
    )
    pbt = availability.loc[
        availability["item_id"].eq("net_accounting_profit_loss_before_tax")
    ].iloc[0]
    interest = availability.loc[
        availability["item_id"].eq("interest_expenses")
    ].iloc[0]

    assert pbt["n_ticker_quarters_present"] == 1
    assert pbt["n_ticker_quarters_total"] == 2
    assert pbt["pct_present"] == pytest.approx(50.0)
    assert interest["n_ticker_quarters_present"] == 2
    assert interest["pct_present"] == pytest.approx(100.0)
    assert anomalies.empty


def test_sector_classification_financial_precedes_upcom() -> None:
    universe = pd.DataFrame(
        {
            "ticker": ["BNK", "INS", "SEC", "UPC", "REL"],
            "exchange": ["HOSE", "HNX", "UPCOM", "UPCOM", "HOSE"],
            "icb2": [
                "NGÂN HÀNG",
                "BẢO HIỂM",
                "DỊCH VỤ TÀI CHÍNH",
                "HÓA CHẤT",
                "HÓA CHẤT",
            ],
        }
    )

    result = classify_universe(universe)
    assert result["sector_class"].tolist() == [
        "FINANCIAL",
        "FINANCIAL",
        "FINANCIAL",
        "UPCOM",
        "SCREENER_RELEVANT",
    ]
