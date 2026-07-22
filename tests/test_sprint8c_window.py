from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from src.backtest.eligibility import compute_eligibility
from src.backtest.engine import EngineConfig, run_engine
from src.backtest.window import compute_backtest_window


def _eligibility_rows(date_value: str) -> pd.DataFrame:
    return pd.DataFrame([{"ticker": "AAA", "date": date_value, "volume": 100}])


def test_eligibility_guard_rejects_date_equal_to_rebalance() -> None:
    with pytest.raises(ValueError, match="date >= rebalance"):
        compute_eligibility(
            _eligibility_rows("2020-01-02"),
            "2020-01-02",
            min_traded_sessions_12m=1,
            ticker_identity_gap_days=180,
        )


def test_eligibility_guard_rejects_date_after_rebalance() -> None:
    with pytest.raises(ValueError, match="date >= rebalance"):
        compute_eligibility(
            _eligibility_rows("2020-01-03"),
            "2020-01-02",
            min_traded_sessions_12m=1,
            ticker_identity_gap_days=180,
        )


def test_eligibility_guard_survives_optimised_python_mode() -> None:
    script = """
import pandas as pd
from src.backtest.eligibility import compute_eligibility

compute_eligibility(
    pd.DataFrame([{"ticker": "AAA", "date": "2020-01-02", "volume": 100}]),
    "2020-01-02",
    min_traded_sessions_12m=1,
    ticker_identity_gap_days=180,
)
"""
    completed = subprocess.run(
        [sys.executable, "-O", "-c", script],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "ValueError: eligibility input contains date >= rebalance date" in completed.stderr


def test_start_date_is_unchanged_when_later_periods_are_appended() -> None:
    initial = [("2020-03-31", 20), ("2020-06-30", 30)]
    appended = initial + [("2020-09-30", 10), ("2020-12-31", 40)]

    initial_start, _ = compute_backtest_window(initial, portfolio_size=20, multiple=1.5)
    appended_start, _ = compute_backtest_window(appended, portfolio_size=20, multiple=1.5)

    assert initial_start == pd.Timestamp("2020-06-30")
    assert appended_start == initial_start


def test_later_thin_period_is_flagged_without_truncating_series() -> None:
    periods = [("2020-03-31", 30), ("2020-06-30", 29), ("2020-09-30", 35)]

    start_date, frame = compute_backtest_window(periods, portfolio_size=20, multiple=1.5)

    assert start_date == pd.Timestamp("2020-03-31")
    assert frame["rebalance_date"].tolist() == [pd.Timestamp(day) for day, _ in periods]
    assert frame["THIN_CANDIDATE_POOL"].tolist() == [False, True, False]


def test_engine_rebalance_log_carries_pool_ratio_and_period_flags() -> None:
    prices = pd.DataFrame(
        [
            {"ticker": "AAA", "date": "2020-01-02", "close_adjusted": 10.0, "volume": 100},
            {"ticker": "AAA", "date": "2020-01-06", "close_adjusted": 10.0, "volume": 100},
        ]
    )
    eligibility = pd.DataFrame(
        [{"ticker": "AAA", "eligible": True, "traded_sessions_12m": 200, "reason": "", "segment_flag": ""}]
    )
    config = EngineConfig(
        min_traded_sessions_12m=200,
        ticker_identity_gap_days=180,
        brokerage_fee_pct_per_side=0.0,
        sell_tax_pct=0.0,
        settlement_lag_days=2,
        min_candidate_pool_multiple=1.5,
        selection_ratio_report_threshold=0.40,
    )

    result = run_engine(
        prices,
        {"2020-01-02": ["AAA"], "2020-01-06": ["AAA"]},
        {"2020-01-02": eligibility, "2020-01-06": eligibility},
        config=config,
        initial_value=1000.0,
        candidate_pool_sizes_by_rebalance={"2020-01-02": 4, "2020-01-06": 2},
        portfolio_size=2,
    )

    assert result.rebalance_log["candidate_pool_size"].tolist() == [4, 2]
    assert result.rebalance_log["selection_ratio"].tolist() == [0.25, 0.5]
    assert result.rebalance_log["period_flags"].tolist() == [
        "",
        "THIN_CANDIDATE_POOL|LOW_SELECTIVITY",
    ]


def test_engine_does_not_invent_pool_size_when_none_was_supplied() -> None:
    from src.backtest.engine import load_engine_config

    prices = pd.DataFrame(
        [
            {"ticker": "AAA", "date": "2020-01-02", "close_adjusted": 10.0, "volume": 100},
            {"ticker": "BBB", "date": "2020-01-02", "close_adjusted": 20.0, "volume": 100},
        ]
    )
    eligibility = pd.DataFrame(
        [
            {"ticker": ticker, "eligible": True, "traded_sessions_12m": 200, "reason": "", "segment_flag": ""}
            for ticker in ("AAA", "BBB")
        ]
    )
    config = load_engine_config(Path(__file__).resolve().parents[1] / "config" / "screener.yaml")

    result = run_engine(
        prices,
        {"2020-01-02": ["AAA", "BBB"]},
        {"2020-01-02": eligibility},
        config=config,
        initial_value=1000.0,
    )

    row = result.rebalance_log.iloc[0]
    assert row["candidate_pool_size"] == ""
    assert row["selection_ratio"] == ""
    assert row["period_flags"] == "POOL_SIZE_NOT_SUPPLIED"


def test_engine_and_window_thresholds_agree_at_required_portfolio_sizes() -> None:
    from src.backtest.engine import load_engine_config

    prices = pd.DataFrame(
        [
            {"ticker": "AAA", "date": "2020-01-02", "close_adjusted": 10.0, "volume": 100},
            {"ticker": "AAA", "date": "2020-01-06", "close_adjusted": 10.0, "volume": 100},
        ]
    )
    eligibility = pd.DataFrame(
        [{"ticker": "AAA", "eligible": True, "traded_sessions_12m": 200, "reason": "", "segment_flag": ""}]
    )
    config = load_engine_config(Path(__file__).resolve().parents[1] / "config" / "screener.yaml")

    for portfolio_size in (1, 2, 19, 20, 21):
        _, boundary = compute_backtest_window(
            [("2020-01-02", 1000)],
            portfolio_size=portfolio_size,
            multiple=1.5,
        )
        threshold = int(boundary.loc[0, "threshold"])
        _, window_frame = compute_backtest_window(
            [("2020-01-02", threshold), ("2020-01-06", threshold - 1)],
            portfolio_size=portfolio_size,
            multiple=1.5,
        )
        result = run_engine(
            prices,
            {"2020-01-02": ["AAA"], "2020-01-06": ["AAA"]},
            {"2020-01-02": eligibility, "2020-01-06": eligibility},
            config=config,
            initial_value=1000.0,
            candidate_pool_sizes_by_rebalance={
                "2020-01-02": threshold,
                "2020-01-06": threshold - 1,
            },
            portfolio_size=portfolio_size,
        )

        assert window_frame["threshold"].tolist() == [threshold, threshold]
        assert "THIN_CANDIDATE_POOL" not in result.rebalance_log.loc[0, "period_flags"]
        assert "THIN_CANDIDATE_POOL" in result.rebalance_log.loc[1, "period_flags"]
