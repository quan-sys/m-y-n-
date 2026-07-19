from __future__ import annotations

import pandas as pd
import pytest

from scripts.audit_sprint5_readiness import (
    classify_price_adjustment,
    component_present_at_quarter,
    item_present_for_quarters,
    quarter_ordinal,
    rows_available_by,
    select_latest_four_quarters,
)


def quarter_rows(*periods: tuple[str, str]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "period_type": "QUARTER",
                "report_period": period,
                "period_end": f"{period[:4]}-03-31",
                "available_from": available_from,
                "item_id": "operating_profit_loss",
                "value": index + 1,
            }
            for index, (period, available_from) in enumerate(periods)
        ]
    )


def test_quarter_ordinal_handles_year_boundary() -> None:
    assert quarter_ordinal("2025Q4") + 1 == quarter_ordinal("2026Q1")
    assert quarter_ordinal("2025-Q4") == quarter_ordinal("2025Q4")
    with pytest.raises(ValueError, match="invalid quarter"):
        quarter_ordinal("2025Q5")


def test_selects_latest_four_consecutive_eligible_quarters() -> None:
    rows = quarter_rows(
        ("2025Q2", "2025-07-30"),
        ("2025Q3", "2025-10-30"),
        ("2025Q4", "2026-03-31"),
        ("2026Q1", "2026-04-30"),
    )
    selection = select_latest_four_quarters(rows, "2026-07-18")
    assert selection.selected_quarters == ("2026Q1", "2025Q4", "2025Q3", "2025Q2")
    assert selection.four_consecutive is True
    assert selection.missing_quarter_count == 0


def test_future_row_is_excluded_without_hiding_eligible_positive_control() -> None:
    rows = quarter_rows(
        ("2025Q3", "2025-10-30"),
        ("2025Q4", "2026-03-31"),
        ("2026Q1", "2026-04-30"),
        ("2026Q2", "2026-08-30"),
    )
    before_release = select_latest_four_quarters(rows, "2026-07-18")
    after_release = select_latest_four_quarters(rows, "2026-09-01")
    assert before_release.selected_quarters == ("2026Q1", "2025Q4", "2025Q3")
    assert before_release.future_period_exclusion_count == 1
    assert before_release.future_row_exclusion_count == 1
    assert after_release.selected_quarters == ("2026Q2", "2026Q1", "2025Q4", "2025Q3")
    assert after_release.four_consecutive is True
    assert after_release.future_row_exclusion_count == 0


@pytest.mark.parametrize(
    ("periods", "missing_one", "missing_two_plus"),
    [
        (("2026Q1", "2025Q4", "2025Q3"), True, False),
        (("2026Q1", "2025Q3"), False, True),
    ],
)
def test_missing_quarter_buckets(
    periods: tuple[str, ...], missing_one: bool, missing_two_plus: bool
) -> None:
    rows = quarter_rows(*((period, "2026-04-30") for period in periods))
    selection = select_latest_four_quarters(rows, "2026-07-18")
    assert (selection.missing_quarter_count == 1) is missing_one
    assert (selection.missing_quarter_count >= 2) is missing_two_plus


def test_duplicate_period_is_reported() -> None:
    rows = quarter_rows(("2026Q1", "2026-04-30"), ("2026Q1", "2026-04-30"))
    assert select_latest_four_quarters(rows, "2026-07-18").duplicate_period_case is True


@pytest.mark.parametrize(
    ("metadata", "source_exists", "expected"),
    [
        ({"price_adjustment_status": "RAW"}, True, "RAW_UNADJUSTED"),
        ({"price_adjustment_status": "UNADJUSTED"}, True, "RAW_UNADJUSTED"),
        ({"price_adjustment_status": "ADJUSTED_OBSERVED"}, True, "ADJUSTED"),
        ({}, True, "UNKNOWN_BLOCKED"),
        (None, False, "NO_CACHED_PRICE_SOURCE"),
    ],
)
def test_price_adjustment_requires_explicit_raw_evidence(
    metadata: dict[str, str] | None, source_exists: bool, expected: str
) -> None:
    assert classify_price_adjustment(metadata, source_exists) == expected


def test_item_presence_requires_four_unique_non_null_quarters() -> None:
    rows = quarter_rows(
        ("2025Q2", "2025-07-30"),
        ("2025Q3", "2025-10-30"),
        ("2025Q4", "2026-03-31"),
        ("2026Q1", "2026-04-30"),
    )
    quarters = ("2026Q1", "2025Q4", "2025Q3", "2025Q2")
    assert item_present_for_quarters(rows, "operating_profit_loss", quarters) is True
    rows.loc[rows["report_period"].eq("2025Q2"), "value"] = None
    assert item_present_for_quarters(rows, "operating_profit_loss", quarters) is False


def test_component_presence_requires_one_non_null_latest_quarter_value() -> None:
    rows = pd.DataFrame(
        [
            {
                "report_period": "2026Q1",
                "item_id": "short_term_borrowings",
                "value": 123,
            }
        ]
    )
    assert component_present_at_quarter(rows, "short_term_borrowings", "2026Q1") is True
    assert component_present_at_quarter(rows, "long_term_borrowings", "2026Q1") is False


def test_component_future_row_is_not_available_at_evaluation_date() -> None:
    rows = pd.DataFrame(
        [
            {
                "report_period": "2026Q1",
                "available_from": "2026-08-01",
                "item_id": "cash_and_cash_equivalents",
                "value": 123,
            }
        ]
    )
    before_release = rows_available_by(rows, "2026-07-18")
    after_release = rows_available_by(rows, "2026-08-02")
    assert component_present_at_quarter(before_release, "cash_and_cash_equivalents", "2026Q1") is False
    assert component_present_at_quarter(after_release, "cash_and_cash_equivalents", "2026Q1") is True
