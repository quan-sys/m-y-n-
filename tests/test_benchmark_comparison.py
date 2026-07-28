from __future__ import annotations

import pandas as pd
import pytest

from scripts.build_benchmark_comparison import (
    BenchmarkComparisonError,
    build_benchmark_comparison,
    resolve_nominal_session,
)


def _value_series(rows: list[tuple[str, str, str, str]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "config_id": config_id,
                "evaluation_date": evaluation_date,
                "execution_date": execution_date,
                "portfolio_value": portfolio_value,
                "cash": "0",
                "status": "OK",
                "missing_tickers": "",
                "in_window": "True",
            }
            for config_id, evaluation_date, execution_date, portfolio_value in rows
        ]
    )


def _benchmark_history(rows: list[tuple[str, str]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ticker": "VNINDEX",
                "date": date,
                "close_adjusted": close,
                "close_adjusted_unit": "INDEX_POINTS",
                "volume": "1",
                "source": "saved_real_provider_shape",
                "as_of": "2026-07-28",
                "data_status": "OK",
            }
            for date, close in rows
        ]
    )


def test_cumulative_excess_is_geometric_not_sum_of_period_excess() -> None:
    values = _value_series(
        [
            ("CFG", "2020-03-31", "2020-03-31", "100"),
            ("CFG", "2020-06-30", "2020-06-30", "110"),
            ("CFG", "2020-09-30", "2020-09-30", "104.5"),
        ]
    )
    benchmark = _benchmark_history(
        [("2020-03-31", "100"), ("2020-06-30", "105"), ("2020-09-30", "105")]
    )

    result = build_benchmark_comparison(
        values, benchmark, run_date="2026-07-28", source="fixture"
    )

    period_excess_sum = float(result.comparison["excess_return"].sum())
    cumulative_excess = float(result.summary.loc[0, "cumulative_excess"])
    assert period_excess_sum == pytest.approx(0.0)
    assert cumulative_excess == pytest.approx((1.045 / 1.05) - 1.0)
    assert cumulative_excess != pytest.approx(period_excess_sum)


def test_weekend_nominal_date_resolves_to_last_observed_index_session() -> None:
    sessions = pd.DatetimeIndex(["2024-03-29", "2024-04-01"])

    resolved = resolve_nominal_session("2024-03-31", sessions)

    assert resolved == pd.Timestamp("2024-03-29")


def test_missing_execution_index_session_stops_with_configuration_and_date() -> None:
    values = _value_series(
        [
            ("CFG", "2020-03-31", "2020-03-31", "100"),
            ("CFG", "2020-06-30", "2020-07-01", "110"),
        ]
    )
    benchmark = _benchmark_history([("2020-03-31", "100"), ("2020-06-30", "105")])

    with pytest.raises(
        BenchmarkComparisonError,
        match=r"CFG: VNINDEX is missing observed execution session 2020-07-01",
    ):
        build_benchmark_comparison(values, benchmark, run_date="2026-07-28", source="fixture")
