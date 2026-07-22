from __future__ import annotations

import pandas as pd

from scripts.probe_share_count_history import (
    DERIVATION_STATUSES,
    _crosscheck,
    derive_annual_shares,
    extract_annual_rows,
    provider_field_records,
)


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


def test_derived_series_preserves_missing_and_flags_treasury() -> None:
    raw = pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "year": "2024",
                "charter_capital_raw": "100000",
                "treasury_shares_raw": "0",
                "fetch_status": "OK",
            },
            {
                "ticker": "AAA",
                "year": "2025",
                "charter_capital_raw": "200000",
                "treasury_shares_raw": "-5000",
                "fetch_status": "OK",
            },
            {
                "ticker": "BBB",
                "year": "2025",
                "charter_capital_raw": "",
                "treasury_shares_raw": "",
                "fetch_status": "OK",
            },
            {
                "ticker": "CCC",
                "year": "",
                "charter_capital_raw": "",
                "treasury_shares_raw": "",
                "fetch_status": "NOT_ATTEMPTED",
            },
        ]
    )

    derived = derive_annual_shares(raw)

    assert derived["shares_issued_derived"].tolist() == ["10", "20", "", ""]
    assert derived["treasury_present"].tolist() == ["false", "true", "false", "false"]
    assert derived["derivation_status"].tolist() == list(DERIVATION_STATUSES)
    assert derived.loc[derived["paid_in_capital_vnd"] == "", "shares_issued_derived"].eq("").all()


def test_crosscheck_splits_signed_deviation(tmp_path) -> None:
    tickers = [f"T{index:03d}" for index in range(156)]
    market = pd.DataFrame(
        [{"ticker": ticker, "shares_outstanding": 100} for ticker in tickers]
        + [{"ticker": "NO_SHARES", "shares_outstanding": None}]
    )
    market_path = tmp_path / "market.csv"
    market.to_csv(market_path, index=False)
    capital_by_ticker = {
        "T001": "900000",
        "T002": "1100000",
        "T155": "",
    }
    results = pd.DataFrame(
        [
            {
                "ticker": ticker,
                "year": "2025",
                "charter_capital_raw": capital_by_ticker.get(ticker, "1000000"),
                "treasury_shares_raw": "-1" if ticker == "T002" else "0",
                "fetch_status": "OK",
            }
            for ticker in tickers
        ]
    )

    crosscheck = _crosscheck(results, market_path)

    assert crosscheck["computed"] == 155
    assert len(crosscheck["group_a"]) == 153
    assert [item["ticker"] for item in crosscheck["group_b"]] == ["T001"]
    assert crosscheck["group_b"][0]["nearest_fraction"] == "10/9"
    assert crosscheck["group_b"][0]["approximation_relative_error"] == 0
    assert [item["ticker"] for item in crosscheck["group_c"]] == ["T002"]
    assert crosscheck["group_c"][0]["treasury_present"] is True
