from __future__ import annotations

import pandas as pd

from scripts.build_sprint8a3b_treasury_bound import classify_treasury_year


def _prices(close: object, volume: object) -> pd.DataFrame:
    return pd.DataFrame([{"close": close, "volume": volume}])


def test_caller_classifies_bound_ok() -> None:
    row = classify_treasury_year("AAA", "2024", "100000", "-1000", _prices(10.0, 100))

    assert row["reason"] == "BOUND_OK"
    assert row["upper_bound_fraction"] == "0.01"
    assert row["below_par_excluded"] == "false"


def test_caller_classifies_below_par_excluded() -> None:
    row = classify_treasury_year("AAA", "2024", "100000", "-1000", _prices(9.9, 100))

    assert row["reason"] == "BELOW_PAR_EXCLUDED"
    assert row["upper_bound_fraction"] == ""
    assert row["below_par_excluded"] == "true"


def test_caller_classifies_prices_missing() -> None:
    row = classify_treasury_year("AAA", "2024", "100000", "-1000", _prices(None, 100))

    assert row["reason"] == "PRICES_MISSING"
    assert row["upper_bound_fraction"] == ""
    assert row["below_par_excluded"] == "false"


def test_caller_classifies_paid_in_capital_missing_before_price_checks() -> None:
    row = classify_treasury_year("AAA", "2024", "", "-1000", _prices(9.9, 100))

    assert row["reason"] == "PAID_IN_CAPITAL_MISSING"
    assert row["upper_bound_fraction"] == ""
    assert row["below_par_excluded"] == "false"
