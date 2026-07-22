from __future__ import annotations

import pandas as pd

from scripts.probe_share_count_history import extract_annual_rows, provider_field_records


def _saved_vnm_shape() -> pd.DataFrame:
    # Exact field/period shape and values saved from the live VNM VCI response on 2026-07-22.
    return pd.DataFrame(
        [
            {
                "item": "Vốn góp",
                "item_en": "Paid-in capital",
                "item_id": "paid_in_capital",
                "2018": 17416877930000.0,
                "2019": 17416877930000.0,
                "2020": 20899554450000.0,
                "2021": 20899554450000.0,
                "2022": 20899554450000.0,
                "2023": 20899554450000.0,
                "2024": 20899554450000.0,
                "2025": 20899554450000.0,
            },
            {
                "item": "Cổ phiếu quỹ",
                "item_en": "Treasury shares",
                "item_id": "treasury_shares",
                "2018": -10485707360.0,
                "2019": -11644956120.0,
                "2020": -11644956120.0,
                "2021": 0.0,
                "2022": 0.0,
                "2023": 0.0,
                "2024": 0.0,
                "2025": 0.0,
            },
            {
                "item": "Cổ phiếu ưu đãi",
                "item_en": "Preferred shares",
                "item_id": "preferred_shares",
                **{str(year): 0.0 for year in range(2018, 2026)},
            },
            {
                "item": "Cổ phiếu phổ thông",
                "item_en": "Common shares",
                "item_id": "common_shares",
                "2018": 17416877930000.0,
                "2019": 17416877930000.0,
                "2020": 20899554450000.0,
                "2021": 20899554450000.0,
                "2022": 20899554450000.0,
                "2023": 20899554450000.0,
                "2024": 20899554450000.0,
                "2025": 20899554450000.0,
            },
        ]
    )


def test_extracts_exact_provider_fields_and_all_returned_years() -> None:
    raw = _saved_vnm_shape()

    rows = extract_annual_rows("VNM", raw)

    assert len(rows) == 8
    assert rows[0]["year"] == "2018"
    assert rows[-1]["year"] == "2025"
    assert rows[0]["charter_capital_raw"] == "17416877930000.0"
    assert rows[0]["treasury_shares_raw"] == "-10485707360.0"
    assert rows[0]["field_name_used"] == "Paid-in capital"
    assert len(provider_field_records(raw)) == 4


def test_missing_exact_fields_stay_missing() -> None:
    raw = pd.DataFrame(
        [
            {
                "item": "TỔNG CỘNG TÀI SẢN",
                "item_en": "Total Assets",
                "item_id": "total_assets",
                "2024": 100.0,
                "2025": 120.0,
            }
        ]
    )

    rows = extract_annual_rows("AAA", raw)

    assert [row["charter_capital_raw"] for row in rows] == ["", ""]
    assert [row["treasury_shares_raw"] for row in rows] == ["", ""]
    assert [row["field_name_used"] for row in rows] == ["", ""]
