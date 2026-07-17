from __future__ import annotations

import builtins
from pathlib import Path

import pandas as pd
import pytest

from src.data.vnstock_client import FetchResult, VnstockClient
from src.universe import OUTPUT_COLUMNS, REQUIRED_COLUMNS, build_universe, write_universe_snapshot


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


class CountingMarketCapClient(FixtureClient):
    def __init__(self, root: Path = FIXTURES) -> None:
        super().__init__(root)
        self.market_cap_calls: list[str] = []

    def get_market_cap(self, ticker: str) -> FetchResult:
        self.market_cap_calls.append(ticker)
        return super().get_market_cap(ticker)


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


def test_market_cap_fetch_requires_an_explicit_batch_limit():
    with pytest.raises(ValueError, match="market_cap_limit is required"):
        build_universe(client=FixtureClient(), write_outputs=False, fetch_market_cap=True)


def test_market_cap_fetch_respects_controlled_batch_limit():
    client = CountingMarketCapClient()
    result = build_universe(
        client=client,
        write_outputs=False,
        fetch_market_cap=True,
        market_cap_limit=1,
    )

    assert len(client.market_cap_calls) == 1
    assert result.summary["market_cap_fetch_count"] == 1
    assert result.summary["market_cap_fetch_limit"] == 1
    skipped = result.accepted[result.accepted["market_cap"].isna()]
    assert skipped["source"].str.contains("market_cap_not_fetched_batch_limit").all()


def test_market_cap_cache_freshness_is_exactly_seven_days(monkeypatch, tmp_path):
    client = VnstockClient(cache_dir=tmp_path, use_cache=True)
    cache_path = client._cache_path("market_cap", "VNM")
    pd.DataFrame([{"market_cap": 1_000_000_000}]).to_parquet(cache_path, index=False)
    observed_max_age: list[int] = []

    def fake_is_fresh(path, max_age_days):
        assert path == cache_path
        observed_max_age.append(max_age_days)
        return True

    monkeypatch.setattr(client, "_is_fresh", fake_is_fresh)
    result = client.get_market_cap("VNM")

    assert result.ok
    assert result.metadata["cache_state"] == "CACHED"
    assert observed_max_age == [7]


def test_universe_snapshot_writes_exact_schema_and_is_idempotent(result, tmp_path):
    snapshot_dir = write_universe_snapshot(
        result.accepted,
        result.rejects,
        tmp_path,
        run_date="2026-07-14",
    )
    repeated = write_universe_snapshot(
        result.accepted,
        result.rejects,
        tmp_path,
        run_date="2026-07-14",
    )

    assert repeated == snapshot_dir
    accepted = pd.read_csv(snapshot_dir / "universe.csv")
    rejects = pd.read_csv(snapshot_dir / "universe_rejects.csv")
    assert list(accepted.columns) == OUTPUT_COLUMNS
    assert list(rejects.columns) == OUTPUT_COLUMNS
    assert accepted["status"].eq("ACCEPTED").all()
    assert rejects["status"].eq("REJECTED").all()
    assert rejects["reject_reason"].astype(str).str.len().gt(0).all()


def test_universe_snapshot_refuses_same_day_data_conflict(result, tmp_path):
    write_universe_snapshot(result.accepted, result.rejects, tmp_path, run_date="2026-07-14")
    changed = result.accepted.copy()
    changed.loc[changed.index[0], "source"] = "changed_source"

    with pytest.raises(FileExistsError, match="snapshot conflict"):
        write_universe_snapshot(changed, result.rejects, tmp_path, run_date="2026-07-14")


def test_universe_snapshot_rejects_invalid_row_statuses(result, tmp_path):
    invalid_accepted = result.accepted.copy()
    invalid_accepted.loc[invalid_accepted.index[0], "status"] = "REJECTED"

    with pytest.raises(ValueError, match="non-ACCEPTED"):
        write_universe_snapshot(invalid_accepted, result.rejects, tmp_path, run_date="2026-07-14")

    invalid_rejects = result.rejects.copy()
    invalid_rejects.loc[invalid_rejects.index[0], "reject_reason"] = ""
    with pytest.raises(ValueError, match="empty reject_reason"):
        write_universe_snapshot(result.accepted, invalid_rejects, tmp_path, run_date="2026-07-14")


def _row(frame: pd.DataFrame, ticker: str) -> pd.Series:
    match = frame[frame["ticker"] == ticker]
    assert not match.empty
    return match.iloc[0]
