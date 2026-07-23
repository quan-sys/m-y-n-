from __future__ import annotations

from math import sqrt

import pandas as pd
import pytest

from src.backtest.metrics import (
    MIN_METRIC_PERIODS,
    OK,
    UNDEFINED_FLAT,
    UNDEFINED_NONPOSITIVE_VALUE,
    UNDEFINED_TOO_SHORT,
    bias_checklist,
    metrics_from_value_series,
)


def _series(values: list[float], dates: list[str]) -> pd.Series:
    return pd.Series(values, index=pd.to_datetime(dates), dtype=float)


def test_cagr_uses_elapsed_calendar_time() -> None:
    nav = _series([100, 200], ["2019-01-01 00:00", "2020-12-31 12:00"])

    result = metrics_from_value_series(nav, periods_per_year=1)

    assert result.cagr == pytest.approx(2**0.5 - 1)
    assert result.statuses["cagr"] == OK


def test_maximum_drawdown_and_magnitude() -> None:
    nav = _series(
        [100, 120, 90, 150],
        ["2020-01-01", "2020-04-01", "2020-07-01", "2020-10-01"],
    )

    result = metrics_from_value_series(nav, periods_per_year=4)

    assert result.max_drawdown == pytest.approx(90 / 120 - 1)
    assert result.max_drawdown_magnitude == pytest.approx(0.25)
    assert result.statuses["max_drawdown"] == OK


def test_volatility_sharpe_and_sortino_match_hand_computation() -> None:
    returns = [0.10, -0.05, 0.02, -0.01]
    values = [100.0]
    for periodic_return in returns:
        values.append(values[-1] * (1 + periodic_return))
    nav = _series(
        values,
        ["2020-01-01", "2020-04-01", "2020-07-01", "2020-10-01", "2021-01-01"],
    )
    mean_return = sum(returns) / len(returns)
    sample_standard_deviation = sqrt(
        sum((value - mean_return) ** 2 for value in returns) / (len(returns) - 1)
    )
    downside_deviation = sqrt(
        sum(min(value, 0) ** 2 for value in returns) / len(returns)
    )

    result = metrics_from_value_series(nav, periods_per_year=4)

    assert result.n_periods == 4
    assert result.mean_period_return == pytest.approx(mean_return)
    assert result.sample_standard_deviation == pytest.approx(sample_standard_deviation)
    assert result.annualised_volatility == pytest.approx(sample_standard_deviation * 2)
    assert result.downside_deviation == pytest.approx(downside_deviation)
    assert result.sharpe == pytest.approx(
        (mean_return * 4) / (sample_standard_deviation * 2)
    )
    assert result.sortino == pytest.approx(
        (mean_return * 4) / (downside_deviation * 2)
    )
    assert result.diagnostic_only is True
    assert MIN_METRIC_PERIODS == 8


def test_flat_nav_reports_undefined_ratios_without_raising() -> None:
    nav = _series(
        [100, 100, 100],
        ["2020-01-01", "2020-04-01", "2020-07-01"],
    )

    result = metrics_from_value_series(nav, periods_per_year=4)

    assert result.annualised_volatility == 0
    assert result.sharpe is None
    assert result.sortino is None
    assert result.statuses["sharpe"] == UNDEFINED_FLAT
    assert result.statuses["sortino"] == UNDEFINED_FLAT


def test_one_point_series_is_too_short() -> None:
    result = metrics_from_value_series(
        _series([100], ["2020-01-01"]),
        periods_per_year=4,
    )

    assert result.n_periods == 0
    assert all(status == UNDEFINED_TOO_SHORT for status in result.statuses.values())


@pytest.mark.parametrize("invalid_value", [0, -1])
def test_nonpositive_value_is_reported_not_raised(invalid_value: float) -> None:
    result = metrics_from_value_series(
        _series([100, invalid_value, 110], ["2020-01-01", "2020-04-01", "2020-07-01"]),
        periods_per_year=4,
    )

    assert all(
        status == UNDEFINED_NONPOSITIVE_VALUE for status in result.statuses.values()
    )
    assert result.cagr is None
    assert result.max_drawdown is None


def test_engine_value_series_dataframe_adapter() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2020-01-01", "2021-01-01"],
            "portfolio_value": [100, 110],
            "cash": [0, 0],
        }
    )

    result = metrics_from_value_series(frame, periods_per_year=1)

    assert result.n_periods == 1
    assert result.periodic_returns == pytest.approx((0.1,))


def test_bias_checklist_is_nonempty_and_has_no_blank_entries() -> None:
    checklist = bias_checklist()

    assert checklist
    assert all(entry.strip() for entry in checklist)
