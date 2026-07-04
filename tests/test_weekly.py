from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from src.weekly import (
    MISSING,
    build_run_metadata,
    build_weekly_outputs,
    calc_breadth_ma_pct,
    calc_drawdown_52w,
    calc_return,
    calc_volatility_20d,
    calculate_sector_indicators,
    compute_confidence_lite,
    render_weekly_report,
)


def test_return_1w_and_1m():
    prices = _prices([100.0] * 9 + [105.0] * 16 + [110.0])
    assert calc_return(prices, 5) == 110.0 / 105.0 - 1
    assert calc_return(prices, 21) == 110.0 / 100.0 - 1


def test_equal_weight_sector_return():
    universe = _universe([("AAA", "BANKS", 100), ("BBB", "BANKS", 100)])
    histories = {
        "AAA": _return_price(base=100, latest=110, length=22),
        "BBB": _return_price(base=100, latest=90, length=22),
    }
    row = calculate_sector_indicators("BANKS", universe, histories)
    assert abs(row["sector_return_1m_equal_weight"] - 0.0) < 1e-12


def test_cap_weight_sector_return_with_market_cap():
    universe = _universe([("AAA", "BANKS", 300), ("BBB", "BANKS", 100)])
    histories = {
        "AAA": _return_price(base=100, latest=110, length=22),
        "BBB": _return_price(base=100, latest=90, length=22),
    }
    row = calculate_sector_indicators("BANKS", universe, histories)
    assert abs(row["sector_return_1m_cap_weight"] - 0.05) < 1e-12


def test_cap_weight_returns_missing_data_when_market_cap_missing():
    universe = _universe([("AAA", "BANKS", ""), ("BBB", "BANKS", 100)])
    histories = {
        "AAA": _return_price(base=100, latest=110, length=22),
        "BBB": _return_price(base=100, latest=90, length=22),
    }
    row = calculate_sector_indicators("BANKS", universe, histories)
    assert row["sector_return_1m_cap_weight"] == MISSING


def test_breadth_ma50():
    histories = {
        "AAA": _prices([100.0] * 49 + [120.0]),
        "BBB": _prices([100.0] * 49 + [80.0]),
    }
    assert calc_breadth_ma_pct(histories, 50) == 0.5


def test_drawdown_52w():
    prices = _prices([100.0] * 250 + [200.0, 150.0])
    assert calc_drawdown_52w(prices) == -0.25


def test_volatility_20d():
    closes = [100.0]
    for idx in range(20):
        closes.append(closes[-1] * (1.01 if idx % 2 == 0 else 0.99))
    expected = pd.Series(closes).pct_change().dropna().tail(20).std(ddof=0)
    assert abs(calc_volatility_20d(_prices(closes)) - expected) < 1e-15


def test_confidence_lite_decreases_when_data_missing():
    full = compute_confidence_lite(
        ticker_count=10,
        valid_price_count=10,
        missing_market_cap=False,
        stale_price_data=False,
        missing_indicator_count=0,
    )
    weak = compute_confidence_lite(
        ticker_count=10,
        valid_price_count=6,
        missing_market_cap=True,
        stale_price_data=True,
        missing_indicator_count=2,
    )
    assert full == 100
    assert weak < full


def test_report_has_no_trade_recommendation_keywords(tmp_path):
    universe = _universe([("AAA", "BANKS", 100), ("BBB", "BANKS", 100)])
    histories = {
        "AAA": _return_price(base=100, latest=110, length=260),
        "BBB": _return_price(base=100, latest=105, length=260),
    }
    outputs = build_weekly_outputs(universe, histories, _return_price(base=100, latest=101, length=260))
    metadata = build_run_metadata(tmp_path / "universe.csv", universe, "2026-06-30", "fixture")
    report = render_weekly_report(outputs["indicators"], outputs["summary"], outputs["data_quality"], metadata)
    banned = ["nên mua", "nên bán", "khuyến nghị", "target price", "buy", "sell"]
    lowered = report.lower()
    assert not any(re.search(rf"\b{re.escape(word)}\b", lowered) for word in banned)


def test_missing_data_is_explicit():
    universe = _universe([("AAA", "BANKS", "")])
    histories = {"AAA": _prices([100.0, 101.0, 102.0])}
    outputs = build_weekly_outputs(universe, histories, None)
    row = outputs["indicators"].iloc[0]
    assert row["sector_return_1m_cap_weight"] == MISSING
    assert row["breadth_ma50_pct"] == MISSING
    assert MISSING in render_weekly_report(
        outputs["indicators"],
        outputs["summary"],
        outputs["data_quality"],
        build_run_metadata(Path("missing.csv"), universe, "2026-06-30", "fixture"),
    )


def _prices(closes: list[float]) -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=len(closes), freq="D")
    return pd.DataFrame(
        {
            "date": dates,
            "close": closes,
            "volume": [1000] * len(closes),
            "trading_value": [close * 1000 for close in closes],
        }
    )


def _return_price(base: float, latest: float, length: int) -> pd.DataFrame:
    closes = [base] * max(length - 1, 1) + [latest]
    return _prices(closes)


def _universe(rows: list[tuple[str, str, object]]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": [row[0] for row in rows],
            "exchange": ["HOSE"] * len(rows),
            "icb2": [row[1] for row in rows],
            "icb3": ["BANKS"] * len(rows),
            "icb4": ["COMMERCIAL_BANKS"] * len(rows),
            "market_cap": [row[2] for row in rows],
            "adtv_20d": [1_000_000_000] * len(rows),
            "status": ["ACCEPTED"] * len(rows),
            "reject_reason": [""] * len(rows),
            "as_of": ["2026-06-30"] * len(rows),
            "source": ["fixture"] * len(rows),
            "data_status": ["OK"] * len(rows),
        }
    )
