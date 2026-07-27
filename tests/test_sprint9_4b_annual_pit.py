from datetime import date, timedelta

import pandas as pd
import pytest

from scripts.build_sprint9_4b_annual_pit import (
    OUTPUT_COLUMNS,
    assemble_output,
    derive_annual_dates,
    emitted_item_ids,
    gate_buildability,
    internal_gap_years,
    select_required_item_rows,
    validate_gate_items_in_emitted_set,
)
from src.data.finance_client import LAG_ANNUAL, NORMALIZED_COLUMNS


def annual_row(
    *,
    ticker="AAA",
    year=2024,
    statement_type="BALANCE_SHEET",
    item_id="current_assets",
    value=100,
):
    period_end = date(year, 12, 31)
    return {
        "ticker": ticker,
        "company_type": "NON_FINANCIAL",
        "statement_type": statement_type,
        "period_type": "ANNUAL",
        "report_period": str(year),
        "period_end": period_end.isoformat(),
        "available_from": (
            period_end + timedelta(days=LAG_ANNUAL)
        ).isoformat(),
        "item_id": item_id,
        "item": "",
        "item_en": "",
        "value": value,
        "currency": "VND",
        "source": "fixture",
        "as_of": "2026-07-26",
        "data_status": "OK",
    }


def normalized_frame(rows):
    return pd.DataFrame(rows, columns=NORMALIZED_COLUMNS)


def empty_normalized_frame():
    return pd.DataFrame(columns=NORMALIZED_COLUMNS)


def test_annual_dates_use_imported_lag_and_december_year_end():
    period_end, available_from = derive_annual_dates(2024)

    assert period_end == "2024-12-31"
    assert date.fromisoformat(available_from) == (
        date.fromisoformat(period_end) + timedelta(days=LAG_ANNUAL)
    )


def test_absent_required_item_produces_no_zero_row():
    frames = {
        "balance_sheet": normalized_frame(
            [annual_row(item_id="current_assets")]
        ),
        "income_statement": empty_normalized_frame(),
        "cash_flow": empty_normalized_frame(),
    }

    output = select_required_item_rows(frames)

    assert set(output["item_id"]) == {"current_assets"}
    assert "cash_and_cash_equivalents" not in set(output["item_id"])
    assert len(output) == 1


def test_internal_gap_detector_ignores_late_start_but_flags_middle_gap():
    assert internal_gap_years([2021, 2022, 2023]) == []
    assert internal_gap_years([2020, 2022, 2023]) == [2021]


def test_gate_buildability_requires_every_item_for_ticker_year():
    rows = pd.DataFrame(
        [
            {"ticker": "AAA", "report_period": "2023", "item_id": "a", "value": 1},
            {"ticker": "AAA", "report_period": "2023", "item_id": "b", "value": 2},
            {"ticker": "AAA", "report_period": "2024", "item_id": "a", "value": 3},
        ]
    )
    definitions = {
        "FIXTURE_GATE": {
            "roles": {"a": {0}, "b": {0}},
            "source": "fixture",
            "history": "N only",
        }
    }

    measured, _ = gate_buildability(
        rows, ["AAA"], definitions=definitions
    )
    by_year = measured.set_index("fiscal_year")["buildable"].to_dict()

    assert bool(by_year[2023])
    assert not bool(by_year[2024])


def test_output_columns_and_sort_order_are_exact():
    frames = {
        "AAA": {
            "balance_sheet": normalized_frame(
                [
                    annual_row(year=2024, item_id="total_assets"),
                    annual_row(year=2023, item_id="current_assets"),
                    annual_row(year=2023, item_id="cash_and_cash_equivalents"),
                ]
            ),
            "income_statement": empty_normalized_frame(),
            "cash_flow": empty_normalized_frame(),
        }
    }

    output = assemble_output(["AAA"], frames)

    assert tuple(output.columns) == OUTPUT_COLUMNS
    assert output[["ticker", "fiscal_year", "item_id"]].values.tolist() == [
        ["AAA", "2023", "cash_and_cash_equivalents"],
        ["AAA", "2023", "current_assets"],
        ["AAA", "2024", "total_assets"],
    ]


def test_common_shares_is_in_the_emitted_item_set():
    assert "common_shares" in emitted_item_ids()


def test_gate_item_guard_raises_when_an_emitted_item_is_missing():
    definitions = {
        "FIXTURE_GATE": {
            "roles": {"not_emitted": {0}},
            "source": "fixture",
            "history": "N only",
        }
    }

    with pytest.raises(RuntimeError, match="emitted item set omits gate inputs"):
        validate_gate_items_in_emitted_set(
            definitions, emitted_items=("current_assets",)
        )
