from __future__ import annotations

import pandas as pd
import pytest

from scripts.build_sprint9_5b_walk_forward import (
    ALL_DATES,
    IN_WINDOW,
    SAMPLE_TOO_SMALL,
    _metrics_row,
    build_eligibility_frame,
    resolve_execution_date,
    resolve_execution_dates,
    window_details,
)
from src.backtest.engine import EngineConfig, run_engine
from src.backtest.metrics import metrics_from_value_series


def _config(*, min_sessions: int = 1) -> EngineConfig:
    return EngineConfig(
        min_traded_sessions_12m=min_sessions,
        ticker_identity_gap_days=180,
        brokerage_fee_pct_per_side=0.003,
        sell_tax_pct=0.001,
        settlement_lag_days=2,
        min_candidate_pool_multiple=1.5,
        selection_ratio_report_threshold=0.70,
    )


def _value_rows(count: int) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "execution_date": pd.date_range("2020-03-31", periods=count, freq="QE-DEC").date.astype(str),
            "portfolio_value": [100.0 + float(index) for index in range(count)],
        }
    )


def test_execution_date_resolver_moves_sunday_and_keeps_session_date() -> None:
    prices = pd.DataFrame(
        {
            "date": ["2024-03-29", "2024-04-01", "2024-04-02"],
            "volume": [1, 1, 1],
        }
    )
    resolved = resolve_execution_dates(["2024-03-31", "2024-04-01"], prices)
    assert resolved == {"2024-03-31": "2024-04-01", "2024-04-01": "2024-04-01"}


def test_execution_date_resolver_skips_multi_day_market_closure() -> None:
    prices = pd.DataFrame(
        {
            "date": ["2022-12-30", "2023-01-03"],
            "volume": [1, 1],
        }
    )
    assert resolve_execution_dates(["2022-12-31"], prices) == {"2022-12-31": "2023-01-03"}


def test_held_ticker_delays_execution_until_it_trades() -> None:
    prices = pd.DataFrame(
        {
            "ticker": ["AAA", "HELD", "AAA", "HELD", "AAA", "HELD"],
            "date": [
                "2024-03-31",
                "2024-03-31",
                "2024-04-01",
                "2024-04-01",
                "2024-04-02",
                "2024-04-02",
            ],
            "close_adjusted": ["10", "", "10", "", "10", "10"],
            "volume": ["1", "0", "1", "0", "1", "1"],
        }
    )
    resolution = resolve_execution_date("2024-03-31", prices, {"HELD"})
    assert resolution.execution_date == "2024-04-02"
    assert resolution.sessions_delayed == 2
    assert resolution.blocking_tickers == ("HELD",)


def test_execution_date_resolver_stops_after_eight_advances_without_held_price() -> None:
    sessions = pd.date_range("2024-01-01", periods=10, freq="D").date.astype(str)
    prices = pd.DataFrame(
        {
            "ticker": ["AAA"] * 10 + ["HELD"] * 10,
            "date": list(sessions) * 2,
            "close_adjusted": ["10"] * 10 + [""] * 9 + ["10"],
            "volume": ["1"] * 10 + ["0"] * 9 + ["1"],
        }
    )
    with pytest.raises(RuntimeError, match="within 8 advances"):
        resolve_execution_date("2024-01-01", prices, {"HELD"})


def test_newly_selected_unpriced_name_does_not_delay_or_prevent_portfolio_value() -> None:
    held_and_selected = [f"TICKER{index:02d}" for index in range(19)]
    prices = pd.DataFrame(
        {
            "ticker": held_and_selected,
            "date": ["2024-03-31"] * len(held_and_selected),
            "close_adjusted": ["10"] * len(held_and_selected),
            "volume": ["1"] * len(held_and_selected),
        }
    )
    resolution = resolve_execution_date("2024-03-31", prices, {"TICKER00"})
    assert resolution.execution_date == "2024-03-31"
    tickers = [*held_and_selected, "NEW"]
    eligibility = pd.DataFrame(
        {
            "ticker": tickers,
            "eligible": [True] * len(tickers),
            "traded_sessions_12m": [1] * len(tickers),
            "reason": [""] * len(tickers),
            "segment_flag": [""] * len(tickers),
        }
    )
    result = run_engine(
        prices,
        {"2024-03-31": {ticker: 1 / len(tickers) for ticker in tickers}},
        {"2024-03-31": eligibility},
        config=_config(),
        initial_value=100.0,
        candidate_pool_sizes_by_rebalance={"2024-03-31": 20},
        portfolio_size=20,
    )
    assert result.trade_log.loc[result.trade_log["status"].eq("PRICE_UNAVAILABLE"), "ticker"].tolist() == ["NEW"]
    assert len(result.trade_log.loc[result.trade_log["side"].eq("BUY")]) == 19
    assert len(result.value_series) == 1
    assert float(result.value_series.loc[0, "portfolio_value"]) > 0


def test_configurations_with_different_held_names_resolve_different_dates() -> None:
    prices = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB", "AAA", "BBB"],
            "date": ["2024-03-31", "2024-03-31", "2024-04-01", "2024-04-01"],
            "close_adjusted": ["10", "", "10", "10"],
            "volume": ["1", "0", "1", "1"],
        }
    )
    first = resolve_execution_date("2024-03-31", prices, {"AAA"})
    second = resolve_execution_date("2024-03-31", prices, {"BBB"})
    assert first.execution_date == "2024-03-31"
    assert second.execution_date == "2024-04-01"


def test_eligibility_excludes_a_row_on_the_evaluation_date() -> None:
    prices = pd.DataFrame(
        {
            "ticker": ["AAA"],
            "date": ["2024-03-31"],
            "volume": [1],
        }
    )
    eligibility = build_eligibility_frame(prices, "2024-03-31", ["AAA"], _config())
    assert bool(eligibility.loc[0, "eligible"]) is False
    assert int(eligibility.loc[0, "traded_sessions_12m"]) == 0


def test_in_window_is_false_before_start_and_true_from_start() -> None:
    start, flags = window_details(
        [
            ("2019-03-31", 29),
            ("2019-06-30", 30),
            ("2019-09-30", 29),
        ],
        _config(),
    )
    assert start == "2019-06-30"
    assert flags == {
        "2019-03-31": False,
        "2019-06-30": True,
        "2019-09-30": True,
    }


def test_missing_execution_price_is_recorded_without_dropping_rebalance() -> None:
    prices = pd.DataFrame(
        {
            "ticker": ["AAA"],
            "date": ["2024-03-31"],
            "close_adjusted": ["10"],
            "volume": ["1"],
        }
    )
    eligibility = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB"],
            "eligible": [True, True],
            "traded_sessions_12m": [1, 1],
            "reason": ["", ""],
            "segment_flag": ["", ""],
        }
    )
    result = run_engine(
        prices,
        {"2024-03-31": {"AAA": 0.5, "BBB": 0.5}},
        {"2024-03-31": eligibility},
        config=_config(),
        initial_value=100.0,
        candidate_pool_sizes_by_rebalance={"2024-03-31": 2},
        portfolio_size=2,
    )
    assert len(result.rebalance_log) == 1
    assert int(result.rebalance_log.loc[0, "selected_count"]) == 2
    unavailable = result.trade_log.loc[
        result.trade_log["status"].eq("PRICE_UNAVAILABLE")
    ]
    assert unavailable["ticker"].tolist() == ["BBB"]


def test_short_metric_sample_has_the_required_flag_and_long_sample_does_not() -> None:
    short_row = _metrics_row(
        config_id="SHORT",
        scope=ALL_DATES,
        window_start_date="2024-03-31",
        values=_value_rows(8),
    )
    long_row = _metrics_row(
        config_id="LONG",
        scope=IN_WINDOW,
        window_start_date="2019-03-31",
        values=_value_rows(28),
    )
    assert short_row["n_periods"] == 7
    assert short_row["sample_flag"] == SAMPLE_TOO_SMALL
    assert long_row["n_periods"] == 27
    assert long_row["sample_flag"] == ""


def test_emitted_cagr_comes_from_imported_metrics_function() -> None:
    values = _value_rows(28)
    emitted = _metrics_row(
        config_id="CHECK",
        scope=ALL_DATES,
        window_start_date="2019-03-31",
        values=values,
    )
    imported = metrics_from_value_series(
        values.rename(columns={"execution_date": "date"}),
        periods_per_year=4,
        rf_annual=0.0,
    )
    assert emitted["cagr"] == pytest.approx(imported.cagr)
