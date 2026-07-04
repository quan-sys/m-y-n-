from __future__ import annotations

import builtins
from pathlib import Path

import pandas as pd
import pytest

from src.data.vnstock_client import FetchResult
from src.universe import OUTPUT_COLUMNS, REQUIRED_COLUMNS, build_universe


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class FixtureClient:
    source = "fixture"

    def __init__(self, root: Path = FIXTURES) -> None:
        self.root = root

    def list_symbols(self) -> FetchResult:
        return FetchResult(True, pd.read_csv(self.root / "symbols.csv"), source=self.source)

    def get_icb_classification(self, tickers=None) -> FetchResult:
        frame = pd.read_csv(self.root / "icb.csv")
        if tickers is not None:
            frame = frame[frame["ticker"].isin(tickers)]
        return FetchResult(True, frame, source=self.source)

    def get_price_history(self, ticker: str, months: int = 6) -> FetchResult:
        path = self.root / "prices" / f"{ticker}.csv"
        if not path.exists():
            return FetchResult(False, pd.DataFrame(), status="API_ERROR", source=self.source)
        return FetchResult(True, pd.read_csv(path), source=self.source)

    def get_market_cap(self, ticker: str) -> FetchResult:
        frame = pd.read_csv(self.root / "market_caps.csv")
        return FetchResult(True, frame[frame["ticker"] == ticker], source=self.source)


@pytest.fixture()
def result():
    return build_universe(client=FixtureClient(), write_outputs=False)


def test_output_schema_has_required_columns(result):
    for frame in (result.accepted, result.rejects):
        assert set(REQUIRED_COLUMNS).issubset(frame.columns)
        assert list(frame.columns) == OUTPUT_COLUMNS


def test_low_liquidity_symbol_is_rejected(result):
    row = _row(result.rejects, "BBB")
    assert row["status"] == "REJECTED"
    assert row["reject_reason"] == "LOW_LIQUIDITY"


def test_missing_six_month_price_history_is_rejected(result):
    row = _row(result.rejects, "CCC")
    assert row["reject_reason"] in {"MISSING_PRICE_6M", "INSUFFICIENT_PRICE_HISTORY"}


def test_rejected_symbols_always_have_reject_reason(result):
    assert not result.rejects.empty
    assert result.rejects["reject_reason"].notna().all()
    assert (result.rejects["reject_reason"].astype(str).str.len() > 0).all()


def test_valid_symbol_is_accepted(result):
    row = _row(result.accepted, "AAA")
    assert row["status"] == "ACCEPTED"
    assert row["reject_reason"] == ""
    assert row["as_of"] == "2026-06-30"
    assert row["source"]


def test_no_real_api_import_is_needed_for_fixture_build(monkeypatch):
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "vnstock" or name.startswith("vnstock."):
            raise AssertionError("unit tests must not import vnstock")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    result = build_universe(client=FixtureClient(), write_outputs=False)
    assert "AAA" in set(result.accepted["ticker"])


def test_build_universe_end_to_end_writes_outputs(tmp_path):
    result = build_universe(client=FixtureClient(), output_dir=tmp_path, write_outputs=True)

    universe_path = tmp_path / "universe.csv"
    rejects_path = tmp_path / "universe_rejects.csv"
    assert universe_path.exists()
    assert rejects_path.exists()

    accepted = pd.read_csv(universe_path)
    rejects = pd.read_csv(rejects_path)
    assert len(accepted) == len(result.accepted)
    assert len(rejects) == len(result.rejects)
    assert set(REQUIRED_COLUMNS).issubset(accepted.columns)
    assert set(REQUIRED_COLUMNS).issubset(rejects.columns)


def test_proxy_adtv_uses_fixture_prices_without_fabricating_values(result):
    row = _row(result.accepted, "EEE")
    assert row["status"] == "ACCEPTED"
    assert row["adtv_20d"] == 1_000_000_000
    assert "adtv_close_x_volume_proxy" in row["source"]


def _row(frame: pd.DataFrame, ticker: str) -> pd.Series:
    match = frame[frame["ticker"] == ticker]
    assert not match.empty
    return match.iloc[0]
