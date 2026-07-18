from __future__ import annotations

import pandas as pd
import pytest

from scripts.run_sprint4_annual_coverage import (
    FORMULA_REQUIREMENTS,
    STATEMENT_BALANCE_SHEET,
    _formula_missing,
)


@pytest.fixture
def snoa_balance_sheet() -> pd.DataFrame:
    required_items = (
        "total_assets",
        "cash_and_cash_equivalents",
        "short_term_investments",
        "short_term_borrowings",
        "long_term_borrowings",
        "owners_equity",
    )
    return pd.DataFrame(
        [
            {
                "item_id": item_id,
                "report_period": str(year),
                "available_from": f"{year + 1}-03-31",
                "value": float(position + year),
            }
            for year in (2025, 2024)
            for position, item_id in enumerate(required_items)
        ]
    )


def test_snoa_coverage_ignores_minority_and_preferred_fields(
    snoa_balance_sheet: pd.DataFrame,
) -> None:
    expected_requirements = {
        "total_assets",
        "cash_and_cash_equivalents",
        "short_term_investments",
        "short_term_borrowings",
        "long_term_borrowings",
        "owners_equity",
    }
    actual_requirements = {
        item_id for _, item_id, _ in FORMULA_REQUIREMENTS["SNOA"]
    }
    assert actual_requirements == expected_requirements

    without_optional_fields = {STATEMENT_BALANCE_SHEET: snoa_balance_sheet}
    baseline = _formula_missing(without_optional_fields, "SNOA", (2025, 2024))
    assert baseline == []

    garbage_rows = pd.DataFrame(
        [
            {
                "item_id": item_id,
                "report_period": str(year),
                "available_from": f"{year + 1}-03-31",
                "value": garbage_value,
            }
            for year in (2025, 2024)
            for item_id, garbage_value in (
                ("minority_interests", 10**30),
                ("preferred_shares", -(10**30)),
            )
        ]
    )
    with_changed_optional_fields = {
        STATEMENT_BALANCE_SHEET: pd.concat(
            [snoa_balance_sheet, garbage_rows], ignore_index=True
        )
    }
    assert _formula_missing(
        with_changed_optional_fields, "SNOA", (2025, 2024)
    ) == baseline
