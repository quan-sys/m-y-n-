from __future__ import annotations

import pandas as pd
import pytest

from scripts.build_historical_market_cap import build_historical_market_cap


def _prices() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["TST", "TST", "TST"],
            "date": ["2024-03-28", "2024-04-01", "2024-06-28"],
            "raw_close": [12.5, 13.0, 15.0],
            "cumulative_factor": [1.0, 1.0, 1.0],
            "adjustment_confidence": ["LOW", "OK", "OK"],
        }
    )


def _shares(
    *,
    quarter: str = "2024Q1",
    measurement_date: str = "2024-03-31",
    shares: object = 100.0,
    status: str = "PIT_ISSUED_OK",
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["TST"],
            "quarter": [quarter],
            "measurement_date": [measurement_date],
            "source_fiscal_year": [2023],
            "available_from": ["2024-03-01"],
            "shares_issued_derived": [shares],
            "staleness_days": [30],
            "status": [status],
        }
    )


def test_market_cap_product_preserves_thousand_vnd_unit() -> None:
    result = build_historical_market_cap(_shares(), _prices()).iloc[0]
    assert result["raw_close"] == pytest.approx(12.5)
    assert result["shares_issued_derived"] == pytest.approx(100.0)
    assert result["market_cap_thousand_vnd"] == pytest.approx(1_250.0)


def test_weekend_quarter_end_uses_last_trading_day_on_or_before() -> None:
    result = build_historical_market_cap(_shares(), _prices()).iloc[0]
    assert result["measurement_date"] == "2024-03-31"
    assert result["price_date_used"] == "2024-03-28"


def test_price_confidence_is_specific_to_selected_price_row() -> None:
    share_rows = pd.concat(
        [
            _shares(),
            _shares(quarter="2024Q2", measurement_date="2024-06-30"),
        ],
        ignore_index=True,
    )
    result = build_historical_market_cap(share_rows, _prices())
    assert result["price_confidence"].tolist() == ["LOW", "OK"]


def test_treasury_present_maps_to_upper_bound() -> None:
    result = build_historical_market_cap(
        _shares(status="PIT_TREASURY_PRESENT"), _prices()
    ).iloc[0]
    assert result["market_cap_status"] == "UPPER_BOUND"
    assert result["market_cap_thousand_vnd"] == pytest.approx(1_250.0)


def test_no_available_annual_maps_to_null_market_cap() -> None:
    result = build_historical_market_cap(
        _shares(shares=None, status="NO_AVAILABLE_ANNUAL"), _prices()
    ).iloc[0]
    assert result["market_cap_status"] == "NO_SHARE_COUNT"
    assert pd.isna(result["market_cap_thousand_vnd"])
