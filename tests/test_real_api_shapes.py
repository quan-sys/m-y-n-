from __future__ import annotations

import builtins
from pathlib import Path

import pandas as pd

from src.data.vnstock_client import FetchResult
from src.universe import (
    _extract_market_cap,
    _extract_market_cap_with_source,
    _normalize_icb,
    _normalize_symbols,
    build_universe,
)


class VciShapeClient:
    source = "fixture_vci_shape"

    def list_symbols(self) -> FetchResult:
        return FetchResult(
            True,
            pd.DataFrame(
                [
                    {"symbol": "AAA", "exchange": "HSX", "type": "STOCK"},
                    {"symbol": "BBB", "exchange": "HNX", "type": "STOCK"},
                    {"symbol": "BOND1", "exchange": "BOND", "type": "BOND"},
                    {"symbol": "CW1", "exchange": "HSX", "type": "CW"},
                    {"symbol": "ETF1", "exchange": "HSX", "type": "ETF"},
                ]
            ),
            source=self.source,
        )

    def get_icb_classification(self, tickers=None) -> FetchResult:
        return FetchResult(
            True,
            pd.DataFrame(
                [
                    {"symbol": "AAA", "icb_level": 1, "icb_code": "1000", "icb_name": "ROOT_A"},
                    {"symbol": "AAA", "icb_level": 2, "icb_code": "1300", "icb_name": "MATERIALS"},
                    {"symbol": "AAA", "icb_level": 3, "icb_code": "1350", "icb_name": "CHEMICALS"},
                    {"symbol": "AAA", "icb_level": 4, "icb_code": "1353", "icb_name": "SPECIALTY_CHEMICALS"},
                    {"symbol": "BBB", "icb_level": 2, "icb_code": "8300", "icb_name": "BANKS"},
                    {"symbol": "BBB", "icb_level": 3, "icb_code": "8350", "icb_name": "BANKS_L3"},
                    {"symbol": "BBB", "icb_level": 4, "icb_code": "8355", "icb_name": "BANKS_L4"},
                ]
            ),
            source=self.source,
        )

    def get_price_history(self, ticker: str, months: int = 6) -> FetchResult:
        return FetchResult(True, _price_fixture(), source=self.source, as_of="2026-06-30")

    def get_market_cap(self, ticker: str) -> FetchResult:
        return FetchResult(
            True,
            pd.DataFrame([{"symbol": ticker, "issue_share": 100_000_000, "last_close": 10_000}]),
            source=self.source,
        )


def test_vci_icb_long_format_pivots_to_wide_icb_columns():
    frame = pd.DataFrame(
        [
            {"symbol": "AAA", "icb_level": 1, "icb_code": "1000", "icb_name": "ROOT_A"},
            {"symbol": "AAA", "icb_level": 2, "icb_code": "1300", "icb_name": "MATERIALS"},
            {"symbol": "AAA", "icb_level": 3, "icb_code": "1350", "icb_name": "CHEMICALS"},
            {"symbol": "AAA", "icb_level": 4, "icb_code": "1353", "icb_name": "SPECIALTY_CHEMICALS"},
        ]
    )
    result = _normalize_icb(frame)

    assert result.loc[0, "ticker"] == "AAA"
    assert result.loc[0, "icb2"] == "MATERIALS"
    assert result.loc[0, "icb3"] == "CHEMICALS"
    assert result.loc[0, "icb4"] == "SPECIALTY_CHEMICALS"


def test_listing_shape_filters_to_stock_only():
    frame = pd.DataFrame(
        [
            {"symbol": "AAA", "exchange": "HSX", "type": "STOCK"},
            {"symbol": "BOND1", "exchange": "BOND", "type": "BOND"},
            {"symbol": "CW1", "exchange": "HSX", "type": "CW"},
            {"symbol": "ETF1", "exchange": "HSX", "type": "ETF"},
        ]
    )
    result = _normalize_symbols(frame)

    assert result["ticker"].tolist() == ["AAA"]
    assert result["exchange"].tolist() == ["HOSE"]


def test_unknown_stock_board_is_rejected_as_unsupported_exchange():
    client = UnsupportedExchangeClient()
    result = build_universe(client=client, write_outputs=False, min_adtv_20d=0)

    assert result.accepted.empty
    assert result.rejects.iloc[0]["ticker"] == "ZZZ"
    assert result.rejects.iloc[0]["reject_reason"] == "UNSUPPORTED_EXCHANGE"


def test_market_cap_proxy_uses_issue_share_times_last_close_with_source_marker():
    overview = pd.DataFrame([{"symbol": "AAA", "issue_share": 100_000_000, "last_close": 12_500}])

    value, source = _extract_market_cap_with_source(overview)

    assert _extract_market_cap(overview) == 1_250_000_000_000
    assert value == 1_250_000_000_000
    assert source == "mktcap_shares_x_close_proxy"


def test_valid_long_icb_shape_does_not_mass_reject_missing_icb():
    result = build_universe(client=VciShapeClient(), write_outputs=False, min_adtv_20d=0)

    assert len(result.accepted) == 2
    assert "MISSING_ICB_CLASSIFICATION" not in set(result.rejects["reject_reason"])
    assert set(result.accepted["icb2"]) == {"MATERIALS", "BANKS"}
    assert result.accepted["source"].str.contains("mktcap_shares_x_close_proxy").all()


def test_shape_tests_do_not_import_real_vnstock(monkeypatch):
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "vnstock" or name.startswith("vnstock."):
            raise AssertionError("shape unit tests must not import vnstock")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    result = build_universe(client=VciShapeClient(), write_outputs=False, min_adtv_20d=0)
    assert len(result.accepted) == 2


class UnsupportedExchangeClient(VciShapeClient):
    def list_symbols(self) -> FetchResult:
        return FetchResult(
            True,
            pd.DataFrame([{"symbol": "ZZZ", "exchange": "OTC", "type": "STOCK"}]),
            source=self.source,
        )


def _price_fixture() -> pd.DataFrame:
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "prices" / "AAA.csv"
    return pd.read_csv(fixture_path)
