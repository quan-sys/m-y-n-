from __future__ import annotations

import pandas as pd
import pytest

from scripts.build_sprint5_valuation import (
    PBT_ITEM,
    calculate_ebit_proxy_vas,
    calculate_tev,
    ebit_tev_exclusion_reason,
    ep_exclusion_reason,
    select_cheapest,
    select_ttm_window,
)


def real_shape_rows(periods: list[tuple[str, str]], *, duplicate_period: str = "") -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for index, (period, available_from) in enumerate(periods):
        records.append(
            {
                "ticker": "AAA",
                "company_type": "NON_FINANCIAL",
                "statement_type": "INCOME_STATEMENT",
                "period_type": "QUARTER",
                "report_period": period,
                "period_end": f"{period[:4]}-03-31",
                "available_from": available_from,
                "item_id": PBT_ITEM,
                "item": "Lợi nhuận kế toán trước thuế",
                "item_en": "Net accounting profit before tax",
                "value": 100 + index,
                "currency": "VND",
                "source": "vnstock_VCI_financial",
                "as_of": "2026-07-17",
                "data_status": "OK",
            }
        )
    if duplicate_period:
        records.append(dict(next(row for row in records if row["report_period"] == duplicate_period)))
    return pd.DataFrame(records)


def test_ttm_window_records_a_missing_quarter_without_filling_it() -> None:
    rows = real_shape_rows(
        [
            ("2026Q1", "2026-04-30"),
            ("2025Q4", "2026-01-30"),
            ("2025Q2", "2025-07-30"),
        ]
    )
    window = select_ttm_window(rows, "2026-07-20", (PBT_ITEM,))
    assert window.periods == ("2026Q1", "2025Q4", "2025Q3", "2025Q2")
    assert window.missing_periods == ("2025Q3",)
    assert window.complete is False


def test_ttm_window_records_a_duplicate_quarter_without_double_counting() -> None:
    rows = real_shape_rows(
        [
            ("2026Q1", "2026-04-30"),
            ("2025Q4", "2026-01-30"),
            ("2025Q3", "2025-10-30"),
            ("2025Q2", "2025-07-30"),
        ],
        duplicate_period="2025Q4",
    )
    window = select_ttm_window(rows, "2026-07-20", (PBT_ITEM,))
    assert window.duplicate_entries == (
        "2025Q4:net_accounting_profit_loss_before_tax",
    )
    assert window.complete is False


def test_ttm_window_crosses_a_year_boundary() -> None:
    rows = real_shape_rows(
        [
            ("2026Q1", "2026-04-30"),
            ("2025Q4", "2026-01-30"),
            ("2025Q3", "2025-10-30"),
            ("2025Q2", "2025-07-30"),
        ]
    )
    window = select_ttm_window(rows, "2026-07-20", (PBT_ITEM,))
    assert window.periods == ("2026Q1", "2025Q4", "2025Q3", "2025Q2")
    assert window.complete is True


def test_ebit_proxy_uses_absolute_interest_expense_per_quarter() -> None:
    ttm_pbt, ttm_interest, ebit = calculate_ebit_proxy_vas(
        (100, 200, 300, 400), (-10, 20, -30, 40)
    )
    assert ttm_pbt == 1_000
    assert ttm_interest == 100
    assert ebit == 1_100


def test_cheap_set_includes_every_tie_at_the_30_percent_boundary() -> None:
    values = pd.Series([10.0, 9.0, 8.0, 8.0, 1.0])
    result = select_cheapest(values, pd.Series([True] * 5), 0.60)
    assert result.eligible_count == 5
    assert result.target_count == 3
    assert result.cutoff == 8.0
    assert result.flags.tolist() == [True, True, True, True, False]
    assert result.actual_count == 4


@pytest.mark.parametrize(
    ("ebit", "tev", "expected"),
    [
        (None, 100, "MISSING_EBIT"),
        (100, None, "MISSING_TEV"),
        (-1, 100, "NEGATIVE_EBIT"),
        (100, 0, "NON_POSITIVE_TEV"),
        (100, -1, "NON_POSITIVE_TEV"),
        (100, 100, ""),
    ],
)
def test_each_ebit_tev_exclusion_rule(
    ebit: int | None, tev: int | None, expected: str
) -> None:
    assert ebit_tev_exclusion_reason(ebit, tev) == expected


@pytest.mark.parametrize(
    ("earnings", "market_cap", "expected"),
    [
        (None, 100, "MISSING_EARNINGS"),
        (100, None, "MISSING_MARKET_CAP"),
        (-1, 100, "NEGATIVE_EARNINGS"),
        (0, 100, ""),
        (100, 100, ""),
    ],
)
def test_each_ep_exclusion_rule(
    earnings: int | None, market_cap: int | None, expected: str
) -> None:
    assert ep_exclusion_reason(earnings, market_cap) == expected


def test_tev_includes_an_explicit_minority_interest() -> None:
    result = calculate_tev(100, 20, 30, 10, 5)
    assert result.value == 145
    assert result.status == "OK"
    assert result.minority_treatment == "INCLUDED_EXPLICIT_VALUE"


def test_tev_omits_unavailable_minority_interest_without_fabricating_zero() -> None:
    result = calculate_tev(100, 20, 30, 10, None)
    assert result.value == 140
    assert result.status == "OK"
    assert result.minority_treatment == "OMITTED_EXPLICITLY_UNAVAILABLE"
