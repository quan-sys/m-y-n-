from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.vnstock_client import FetchResult
from src.weekly import (
    BANNED_REPORT_PHRASES,
    INDEX_SOURCE_PROXY,
    MISSING,
    breadth_ma_pct,
    build_run_metadata,
    build_sector_daily_returns,
    build_sector_index,
    build_weekly_outputs,
    calc_distance_from_52w_low,
    calc_drawdown_from_52w_high,
    calc_liquidity_trend_4w,
    calc_return,
    calc_volatility_20d,
    cap_weighted_return_or_missing,
    compute_confidence_lite,
    coverage_status_for,
    render_weekly_report,
)


def test_return_1w_1m_3m_windows():
    price = _price_frame(90, start=100, step=1)

    assert calc_return(price, 5) == price.iloc[-1]["close"] / price.iloc[-6]["close"] - 1
    assert calc_return(price, 21) == price.iloc[-1]["close"] / price.iloc[-22]["close"] - 1
    assert calc_return(price, 63) == price.iloc[-1]["close"] / price.iloc[-64]["close"] - 1


def test_equal_weight_sector_return_is_mean_of_valid_ticker_returns():
    universe = _universe([("AAA", "BANKS", 100), ("BBB", "BANKS", 300)])
    prices = {
        "AAA": FetchResult(True, _price_frame_from_closes([100] * 70 + [110]), source="fixture"),
        "BBB": FetchResult(True, _price_frame_from_closes([200] * 70 + [220]), source="fixture"),
    }
    result = build_weekly_outputs(universe, prices, _index_result())
    row = result.indicators.iloc[0]

    assert round(row["sector_return_1w_equal_weight"], 6) == 0.1
    assert round(row["sector_return_1m_equal_weight"], 6) == 0.1


def test_cap_weighted_sector_return_when_market_cap_is_complete():
    universe = _universe([("AAA", "BANKS", 100), ("BBB", "BANKS", 300)])
    returns = {"AAA": 0.10, "BBB": 0.20}

    assert cap_weighted_return_or_missing(universe, returns) == 0.175


def test_cap_weighted_sector_return_missing_when_market_cap_is_missing():
    universe = _universe([("AAA", "BANKS", ""), ("BBB", "BANKS", 300)])
    returns = {"AAA": 0.10, "BBB": 0.20}

    assert cap_weighted_return_or_missing(universe, returns) == MISSING


def test_breadth_ma50_pct():
    histories = {
        "AAA": _price_frame(80, start=100, step=1),
        "BBB": _price_frame(80, start=100, step=-0.1),
    }

    assert breadth_ma_pct(histories, 50) == 0.5


def test_breadth_ma200_is_missing_when_history_is_short():
    universe = _universe([("AAA", "BANKS", 100)])
    prices = {"AAA": FetchResult(True, _price_frame(100, start=100, step=1), source="fixture")}
    result = build_weekly_outputs(universe, prices, _index_result())

    assert result.indicators.iloc[0]["breadth_ma200_pct"] == MISSING


def test_drawdown_from_52w_high():
    index = pd.Series([1, 1.2, 0.9], index=pd.date_range("2026-01-01", periods=3))

    assert round(calc_drawdown_from_52w_high(index), 6) == -0.25


def test_distance_from_52w_low():
    index = pd.Series([1, 0.8, 1.0], index=pd.date_range("2026-01-01", periods=3))

    assert calc_distance_from_52w_low(index) == 0.25


def test_volatility_20d_uses_sector_daily_returns_not_annualized():
    returns = pd.Series([0.01, -0.01] * 15)

    assert calc_volatility_20d(returns) == returns.tail(20).std(ddof=0)


def test_liquidity_trend_4w_uses_value_or_close_volume_proxy():
    close = [10] * 20 + [20] * 20
    volume = [100] * 40
    price = _price_frame_from_closes(close, volume=volume, include_value=False)

    assert calc_liquidity_trend_4w(price) == 1.0


def test_confidence_lite_drops_for_missing_data():
    score = compute_confidence_lite(
        accepted_ticker_count=2,
        valid_price_count=1,
        cap_weight_missing=True,
        core_missing_count=2,
        vnindex_missing=True,
        stale_price_data=True,
    )

    assert score == 0


def test_low_coverage_for_sector_with_less_than_three_tickers():
    assert coverage_status_for(2, 2) == "LOW_COVERAGE"


def test_report_does_not_contain_banned_trading_wording():
    universe = _universe([("AAA", "BANKS", 100), ("BBB", "BANKS", 200), ("CCC", "BANKS", 300)])
    prices = {
        "AAA": FetchResult(True, _price_frame(260, start=100, step=1), source="fixture"),
        "BBB": FetchResult(True, _price_frame(260, start=100, step=0.5), source="fixture"),
        "CCC": FetchResult(True, _price_frame(260, start=100, step=-0.1), source="fixture"),
    }
    result = build_weekly_outputs(universe, prices, _index_result())
    metadata = _metadata(len(universe))
    report = render_weekly_report(result.indicators, result.summary, result.data_quality, metadata)
    lowered = report.lower()

    assert all(phrase not in lowered for phrase in BANNED_REPORT_PHRASES)


def test_run_metadata_has_required_keys(tmp_path):
    universe_path = tmp_path / "universe.csv"
    universe = _universe([("AAA", "BANKS", 100)])
    universe.to_csv(universe_path, index=False)
    metadata = build_run_metadata(universe_path, universe, "2026-07-03", "fixture", tmp_path / "reports")

    assert {
        "run_id",
        "generated_at",
        "as_of",
        "git_commit_if_available",
        "python_version",
        "package_versions",
        "universe_row_count",
        "universe_hash",
        "source",
        "output_dir",
    }.issubset(metadata)


def test_missing_data_is_rendered_as_na_missing_data():
    universe = _universe([("AAA", "BANKS", "")])
    prices = {"AAA": FetchResult(True, pd.DataFrame(), source="fixture")}
    result = build_weekly_outputs(universe, prices, FetchResult(False, pd.DataFrame(), status="API_ERROR"))

    assert MISSING in result.indicators.iloc[0].to_string()
    assert result.data_quality.iloc[0]["missing_indicator_count"] > 0


def test_sector_index_is_equal_weight_from_daily_returns():
    histories = {
        "AAA": _price_frame_from_closes([100, 110, 121]),
        "BBB": _price_frame_from_closes([100, 90, 81]),
    }
    returns = build_sector_daily_returns(histories)
    index = build_sector_index(returns)

    assert round(float(returns.iloc[0]), 6) == 0.0
    assert round(float(index.iloc[-1]), 6) == 1.0


def test_proxy_index_fills_relative_strength_when_index_fetch_fails():
    universe = _universe([("AAA", "BANKS", 100), ("BBB", "BANKS", 200), ("CCC", "BANKS", 300)])
    prices = {
        "AAA": FetchResult(True, _price_frame(90, start=100, step=1), source="fixture"),
        "BBB": FetchResult(True, _price_frame(90, start=100, step=0.5), source="fixture"),
        "CCC": FetchResult(True, _price_frame(90, start=100, step=-0.1), source="fixture"),
    }
    result = build_weekly_outputs(universe, prices, FetchResult(False, pd.DataFrame(), status="API_ERROR"))
    row = result.indicators.iloc[0]

    assert row["relative_strength_1m_vs_vnindex"] != MISSING
    assert result.data_quality.iloc[0]["index_source"] == INDEX_SOURCE_PROXY


def test_data_quality_tracks_cache_stale_api_and_cap_weight():
    universe = _universe([("AAA", "BANKS", 100), ("BBB", "BANKS", 200), ("CCC", "BANKS", 300)])
    prices = {
        "AAA": FetchResult(
            True,
            _price_frame(90, start=100, step=1),
            source="fixture",
            metadata={"cache_state": "CACHED"},
        ),
        "BBB": FetchResult(
            True,
            _price_frame(90, start=100, step=0.5),
            status="STALE_DATA",
            source="fixture",
            metadata={"cache_state": "STALE_DATA"},
        ),
        "CCC": FetchResult(False, pd.DataFrame(), status="API_ERROR", source="fixture"),
    }
    result = build_weekly_outputs(universe, prices, _index_result())
    row = result.data_quality.iloc[0]

    assert row["valid_price_count"] == 2
    assert row["cached_price_count"] == 1
    assert row["stale_price_count"] == 1
    assert row["api_error_count"] == 1
    assert row["api_error_tickers"] == "CCC"
    assert row["cap_weight_available"] == "yes"


def test_report_mentions_sprint_2_1_quality_context():
    universe = _universe([("AAA", "BANKS", 100), ("BBB", "BANKS", 200), ("CCC", "BANKS", 300)])
    prices = {
        "AAA": FetchResult(True, _price_frame(90, start=100, step=1), source="fixture"),
        "BBB": FetchResult(True, _price_frame(90, start=100, step=0.5), source="fixture"),
        "CCC": FetchResult(True, _price_frame(90, start=100, step=-0.1), source="fixture"),
    }
    result = build_weekly_outputs(universe, prices, FetchResult(False, pd.DataFrame(), status="API_ERROR"))
    report = render_weekly_report(result.indicators, result.summary, result.data_quality, _metadata(len(universe)))

    assert "Index source" in report
    assert INDEX_SOURCE_PROXY in report
    assert "Cap-weight available" in report


def _universe(rows: list[tuple[str, str, object]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ticker": ticker,
                "exchange": "HOSE",
                "icb2": icb2,
                "icb3": "",
                "icb4": "",
                "market_cap": market_cap,
                "adtv_20d": 1_000_000_000,
                "status": "ACCEPTED",
                "reject_reason": "",
                "as_of": "2026-07-03",
                "source": "fixture",
                "data_status": "OK",
            }
            for ticker, icb2, market_cap in rows
        ]
    )


def _price_frame(days: int, start: float, step: float) -> pd.DataFrame:
    closes = [start + index * step for index in range(days)]
    return _price_frame_from_closes(closes)


def _price_frame_from_closes(
    closes: list[float],
    volume: list[int] | None = None,
    include_value: bool = True,
) -> pd.DataFrame:
    dates = pd.bdate_range("2025-01-01", periods=len(closes))
    volume = volume or [1000] * len(closes)
    frame = pd.DataFrame({"date": dates, "close": closes, "volume": volume})
    if include_value:
        frame["value"] = frame["close"] * frame["volume"]
    return frame


def _index_result() -> FetchResult:
    return FetchResult(True, _price_frame(260, start=100, step=0.1), source="fixture_index")


def _metadata(universe_rows: int) -> dict[str, object]:
    return {
        "generated_at": "2026-07-04T00:00:00+00:00",
        "as_of": "2026-07-03",
        "universe_row_count": universe_rows,
    }
