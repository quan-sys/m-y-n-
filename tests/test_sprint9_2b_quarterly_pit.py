from __future__ import annotations

from datetime import timedelta

import pandas as pd

from scripts.build_sprint9_2b_quarterly_pit import (
    OUTPUT_COLUMNS,
    assemble_output,
    derive_available_from,
    internal_gap_quarters,
    select_key_item_rows,
)
from src.data.finance_client import LAG_QUARTER, NORMALIZED_COLUMNS


def _normalized_rows(rows: list[dict[str, object]]) -> pd.DataFrame:
    defaults: dict[str, object] = {
        "ticker": "TST",
        "company_type": "NON_FINANCIAL",
        "statement_type": "INCOME_STATEMENT",
        "period_type": "QUARTER",
        "report_period": "2024Q1",
        "period_end": "2024-03-31",
        "available_from": "2024-04-30",
        "item_id": "net_accounting_profit_loss_before_tax",
        "item": "Synthetic fixture item",
        "item_en": "Synthetic fixture item",
        "value": 2_000_000_000,
        "currency": "VND",
        "source": "synthetic_fixture",
        "as_of": "2026-07-26",
        "data_status": "OK",
    }
    return pd.DataFrame(
        [{**defaults, **row} for row in rows],
        columns=NORMALIZED_COLUMNS,
    )


def test_available_from_uses_imported_quarter_lag_for_31_and_30_day_months() -> None:
    for period_end in ("2024-03-31", "2024-06-30"):
        expected = (
            pd.Timestamp(period_end).date() + timedelta(days=LAG_QUARTER)
        ).isoformat()
        assert derive_available_from(period_end) == expected

    assert derive_available_from("2024-03-31") == "2024-04-30"
    assert derive_available_from("2024-06-30") == "2024-07-30"


def test_internal_gap_detector_flags_middle_gap_but_not_late_start() -> None:
    assert internal_gap_quarters(["2023Q4", "2024Q2"]) == ["2024Q1"]
    assert internal_gap_quarters(["2024Q2", "2024Q3", "2024Q4"]) == []


def test_absent_item_emits_no_row_instead_of_zero() -> None:
    income = _normalized_rows(
        [
            {
                "item_id": "interest_expenses",
                "value": -1_500_000_000,
            }
        ]
    )

    output = select_key_item_rows(
        {
            "income_statement": income,
            "balance_sheet": pd.DataFrame(columns=NORMALIZED_COLUMNS),
        }
    )

    assert output["item_id"].tolist() == ["interest_expenses"]
    assert (
        "net_accounting_profit_loss_before_tax"
        not in output["item_id"].tolist()
    )
    assert output["value"].tolist() == [-1_500_000_000]


def test_output_columns_and_sort_order_are_exact() -> None:
    aaa = _normalized_rows(
        [
            {
                "ticker": "AAA",
                "report_period": "2024Q2",
                "period_end": "2024-06-30",
                "available_from": "2024-07-30",
                "item_id": "interest_expenses",
            },
            {
                "ticker": "AAA",
                "report_period": "2024Q1",
                "item_id": "net_accounting_profit_loss_before_tax",
            },
        ]
    )
    zzz = _normalized_rows(
        [
            {
                "ticker": "ZZZ",
                "report_period": "2024Q1",
                "item_id": "financial_expenses",
            }
        ]
    )

    output = assemble_output(
        ["ZZZ", "AAA"],
        {
            "AAA": {
                "income_statement": aaa,
                "balance_sheet": pd.DataFrame(columns=NORMALIZED_COLUMNS),
                "cash_flow": pd.DataFrame(columns=NORMALIZED_COLUMNS),
            },
            "ZZZ": {
                "income_statement": zzz,
                "balance_sheet": pd.DataFrame(columns=NORMALIZED_COLUMNS),
                "cash_flow": pd.DataFrame(columns=NORMALIZED_COLUMNS),
            },
        },
    )

    assert tuple(output.columns) == OUTPUT_COLUMNS
    assert output.loc[:, ["ticker", "quarter", "item_id"]].values.tolist() == [
        ["AAA", "2024Q1", "net_accounting_profit_loss_before_tax"],
        ["AAA", "2024Q2", "interest_expenses"],
        ["ZZZ", "2024Q1", "financial_expenses"],
    ]
