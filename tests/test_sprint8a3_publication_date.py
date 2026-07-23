from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pandas as pd

from scripts.build_sprint8a3_point_in_time_shares import (
    attach_availability,
    build_point_in_time,
    treasury_fraction_upper_bound,
)
from src.data.finance_client import LAG_ANNUAL


def test_availability_is_fiscal_year_end_plus_imported_lag() -> None:
    annual = pd.DataFrame(
        [{"ticker": "AAA", "year": "2023", "derivation_status": "ISSUED_OK"}]
    )

    available = attach_availability(annual)

    expected = date(2023, 12, 31) + timedelta(days=LAG_ANNUAL)
    assert available.loc[0, "available_from"] == expected.isoformat()
    assert available.columns.tolist() == [*annual.columns, "available_from"]


def test_point_in_time_selects_latest_available_annual_figure() -> None:
    available = pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "year": "2022",
                "shares_issued_derived": "10",
                "derivation_status": "ISSUED_OK",
                "available_from": "2023-03-31",
            },
            {
                "ticker": "AAA",
                "year": "2023",
                "shares_issued_derived": "20",
                "derivation_status": "OUTSTANDING_UNKNOWN_TREASURY_PRESENT",
                "available_from": "2024-03-30",
            },
        ]
    )

    result = build_point_in_time(available, ["AAA"])
    selected = result[result["quarter"] == "2024Q1"].iloc[0]

    assert selected["source_fiscal_year"] == "2023"
    assert selected["available_from"] == "2024-03-30"
    assert selected["shares_issued_derived"] == "20"
    assert selected["staleness_days"] == "1"
    assert selected["status"] == "PIT_TREASURY_PRESENT"


def test_point_in_time_is_empty_when_no_annual_figure_is_available() -> None:
    available = pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "year": "2018",
                "shares_issued_derived": "10",
                "derivation_status": "ISSUED_OK",
                "available_from": "2019-03-31",
            }
        ]
    )

    result = build_point_in_time(available, ["AAA"])
    unavailable = result[result["quarter"] == "2018Q4"].iloc[0]

    assert unavailable["status"] == "NO_AVAILABLE_ANNUAL"
    assert unavailable["source_fiscal_year"] == ""
    assert unavailable["shares_issued_derived"] == ""


def test_treasury_bound_excludes_any_fiscal_year_traded_below_par() -> None:
    prices = pd.DataFrame(
        [
            {"close": 10.5, "volume": 100},
            {"close": 9.9, "volume": 100},
            {"close": 8.0, "volume": 0},
        ]
    )

    result = treasury_fraction_upper_bound("1000000", "-200000", prices)

    assert result.value is None
    assert result.below_par_excluded is True

    valid_prices = pd.DataFrame([{"close": 10.0, "volume": 100}])
    valid = treasury_fraction_upper_bound("1000000", "-200000", valid_prices)
    assert valid.value == Decimal("0.2")
    assert valid.below_par_excluded is False
