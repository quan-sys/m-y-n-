from decimal import Decimal

import pandas as pd
import pytest

from scripts import build_sprint9_3_historical_valuation as valuation


OVERRIDE_COLUMNS = [
    "ticker",
    "quarter",
    "raw_interest_expenses",
    "override_action",
    "status",
    "evidence_url",
    "published_date",
    "recorded_at",
    "note",
]


def _hag_2024_03_31_inputs():
    fundamentals, market_cap = valuation.load_inputs()
    hag_fundamentals = fundamentals.loc[fundamentals["ticker"].eq("HAG")].copy()
    hag_market = market_cap.loc[
        market_cap["ticker"].eq("HAG")
        & market_cap["measurement_date"].eq("2024-03-31")
    ]
    assert len(hag_market) == 1
    return hag_market.iloc[0].to_dict(), hag_fundamentals


def _force_override_file(monkeypatch, tmp_path, rows):
    path = tmp_path / "interest_sign_overrides.csv"
    pd.DataFrame(rows, columns=OVERRIDE_COLUMNS).to_csv(path, index=False)
    monkeypatch.setattr(valuation, "OVERRIDES_PATH", path, raising=False)


def test_zero_subtract_overrides_keep_current_hag_ebit_behavior(monkeypatch, tmp_path):
    _force_override_file(monkeypatch, tmp_path, [])
    market_row, hag_fundamentals = _hag_2024_03_31_inputs()

    row = valuation.build_valuation_row(
        market_row,
        hag_fundamentals,
        run_date="2026-07-26",
    )

    assert row["ebit_proxy_vas"] == Decimal("3435428780000")
    assert row.get("interest_override_applied") == ""


def test_hag_2023q4_subtract_override_changes_hag_ebit_and_ebit_tev(
    monkeypatch,
    tmp_path,
):
    _force_override_file(
        monkeypatch,
        tmp_path,
        [
            {
                "ticker": "HAG",
                "quarter": "2023Q4",
                "raw_interest_expenses": "951800507000.0",
                "override_action": "SUBTRACT",
                "status": "VERIFIED_INCOME",
                "evidence_url": "",
                "published_date": "",
                "recorded_at": "2026-07-29",
                "note": "test fixture",
            }
        ],
    )
    market_row, hag_fundamentals = _hag_2024_03_31_inputs()

    row = valuation.build_valuation_row(
        market_row,
        hag_fundamentals,
        run_date="2026-07-26",
    )

    assert row["ebit_proxy_vas"] == Decimal("1531827766000")
    assert abs(
        row["ebit_tev"] - Decimal("0.0754962391960831511771912")
    ) <= Decimal("1e-12")
    assert row.get("interest_override_applied") == "HAG:2023Q4"


def test_data_contract_output_columns_match_valuation_output_columns():
    contract = (valuation.ROOT / "data_contract.md").read_text(encoding="utf-8")
    sprint_section = contract.split(
        "## Sprint 9-3 historical valuation diagnostics", 1
    )[1].split("\n## ", 1)[0]
    column_block = sprint_section.split(
        "The exact column order is:\n\n```text\n", 1
    )[1].split("\n```", 1)[0]

    assert tuple(column_block.splitlines()) == valuation.OUTPUT_COLUMNS


def test_subtract_override_rejects_negative_raw_interest(monkeypatch, tmp_path):
    _force_override_file(
        monkeypatch,
        tmp_path,
        [
            {
                "ticker": "AAA",
                "quarter": "2024Q1",
                "raw_interest_expenses": "-5000",
                "override_action": "SUBTRACT",
                "status": "VERIFIED_INCOME",
                "evidence_url": "",
                "published_date": "",
                "recorded_at": "2026-07-29",
                "note": "test fixture",
            }
        ],
    )

    with pytest.raises(ValueError, match="AAA"):
        valuation.load_interest_overrides()


def test_subtract_override_returns_hag_key(monkeypatch, tmp_path):
    _force_override_file(
        monkeypatch,
        tmp_path,
        [
            {
                "ticker": "HAG",
                "quarter": "2023Q4",
                "raw_interest_expenses": "951800507000.0",
                "override_action": "SUBTRACT",
                "status": "VERIFIED_INCOME",
                "evidence_url": "",
                "published_date": "",
                "recorded_at": "2026-07-29",
                "note": "test fixture",
            }
        ],
    )

    assert valuation.load_interest_overrides() == frozenset({("HAG", "2023Q4")})


def test_hag_2026q1_subtract_changes_ttm_ending_2026q1():
    fundamentals, _ = valuation.load_inputs()
    hag_fundamentals = fundamentals.loc[fundamentals["ticker"].eq("HAG")]
    quarters = ("2025Q2", "2025Q3", "2025Q4", "2026Q1")

    current_behavior = valuation._sum_item(
        hag_fundamentals,
        quarters,
        "interest_expenses",
        absolute=True,
        interest_overrides=frozenset(),
    )
    subtract_override = valuation._sum_item(
        hag_fundamentals,
        quarters,
        "interest_expenses",
        absolute=True,
        interest_overrides=frozenset({("HAG", "2026Q1")}),
    )

    assert current_behavior == Decimal("1182251572000")
    assert subtract_override == Decimal("16549240000")
    assert current_behavior - subtract_override == 2 * Decimal("582851166000")


def test_committed_overrides_contain_both_hag_subtract_keys():
    assert valuation.load_interest_overrides() == frozenset(
        {("HAG", "2023Q4"), ("HAG", "2026Q1")}
    )
