from __future__ import annotations

import pandas as pd
import pytest

from src.backtest.eligibility import compute_eligibility
from src.backtest.engine import EngineConfig, PRICE_UNAVAILABLE, run_engine


CONFIG = EngineConfig(
    min_traded_sessions_12m=2,
    ticker_identity_gap_days=180,
    brokerage_fee_pct_per_side=0.01,
    sell_tax_pct=0.02,
    settlement_lag_days=2,
)


def test_eligibility_rejects_rows_on_or_after_rebalance_date() -> None:
    rows = pd.DataFrame([{"ticker": "AAA", "date": "2020-01-02", "volume": 100}])

    with pytest.raises(ValueError, match="date >= rebalance"):
        compute_eligibility(
            rows,
            "2020-01-02",
            min_traded_sessions_12m=1,
            ticker_identity_gap_days=180,
        )


def test_ticker_can_fail_then_later_pass_without_universe_deletion() -> None:
    full = pd.DataFrame(
        [
            {"ticker": "AAA", "date": "2020-01-02", "volume": 100},
            {"ticker": "AAA", "date": "2020-01-03", "volume": 100},
        ]
    )
    early = compute_eligibility(
        full[full["date"] < "2020-01-03"],
        "2020-01-03",
        min_traded_sessions_12m=2,
        ticker_identity_gap_days=180,
        universe_tickers=["AAA"],
    )
    later = compute_eligibility(
        full[full["date"] < "2020-01-04"],
        "2020-01-04",
        min_traded_sessions_12m=2,
        ticker_identity_gap_days=180,
        universe_tickers=["AAA"],
    )

    assert bool(early.loc[0, "eligible"]) is False
    assert early.loc[0, "reason"] == "INSUFFICIENT_TRADED_SESSIONS"
    assert bool(later.loc[0, "eligible"]) is True


def test_zero_volume_session_does_not_count_for_b1() -> None:
    rows = pd.DataFrame(
        [
            {"ticker": "AAA", "date": "2020-01-02", "volume": 100},
            {"ticker": "AAA", "date": "2020-01-03", "volume": 0},
        ]
    )

    result = compute_eligibility(
        rows,
        "2020-01-04",
        min_traded_sessions_12m=2,
        ticker_identity_gap_days=180,
    )

    assert result.loc[0, "traded_sessions_12m"] == 1
    assert bool(result.loc[0, "eligible"]) is False


def test_engine_reports_missing_exact_price_without_filling_gap() -> None:
    prices = pd.DataFrame(
        [
            {"ticker": "AAA", "date": "2020-01-02", "close_adjusted": 10.0, "volume": 100},
            {"ticker": "AAA", "date": "2020-01-04", "close_adjusted": 12.0, "volume": 100},
        ]
    )
    eligibility = pd.DataFrame(
        [{"ticker": "AAA", "eligible": True, "traded_sessions_12m": 200, "reason": "", "segment_flag": ""}]
    )

    result = run_engine(
        prices,
        {"2020-01-03": ["AAA"]},
        {"2020-01-03": eligibility},
        config=CONFIG,
        initial_value=1000.0,
    )

    assert result.trade_log.loc[0, "status"] == PRICE_UNAVAILABLE
    assert result.rebalance_log.loc[0, "status"] == PRICE_UNAVAILABLE
    assert result.trade_log.loc[0, "entry_price"] == ""


def test_cost_arithmetic_for_hand_checkable_buy_then_sell() -> None:
    prices = pd.DataFrame(
        [
            {"ticker": "AAA", "date": "2020-01-02", "close_adjusted": 10.0, "volume": 100},
            {"ticker": "AAA", "date": "2020-01-06", "close_adjusted": 20.0, "volume": 100},
        ]
    )
    eligibility = pd.DataFrame(
        [{"ticker": "AAA", "eligible": True, "traded_sessions_12m": 200, "reason": "", "segment_flag": ""}]
    )

    result = run_engine(
        prices,
        {"2020-01-02": ["AAA"], "2020-01-06": []},
        {"2020-01-02": eligibility, "2020-01-06": eligibility},
        config=CONFIG,
        initial_value=1010.0,
    )

    buy = result.trade_log.iloc[0]
    sell = result.trade_log.iloc[1]
    assert buy["side"] == "BUY"
    assert buy["gross_value"] == pytest.approx(1000.0)
    assert buy["cost_paid"] == pytest.approx(10.0)
    assert buy["shares"] == pytest.approx(100.0)
    assert buy["settlement_date"] == "2020-01-06"
    assert sell["side"] == "SELL"
    assert sell["gross_value"] == pytest.approx(2000.0)
    assert sell["cost_paid"] == pytest.approx(60.0)
    assert sell["settlement_date"] == "2020-01-08"
    assert result.ending_value == pytest.approx(1940.0)
