from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Final

import numpy as np
import pandas as pd

from src.backtest.engine import KNOWN_BIASES


OK: Final = "OK"
UNDEFINED_FLAT: Final = "UNDEFINED_FLAT"
UNDEFINED_TOO_SHORT: Final = "UNDEFINED_TOO_SHORT"
UNDEFINED_NONPOSITIVE_VALUE: Final = "UNDEFINED_NONPOSITIVE_VALUE"
METRIC_STATUSES: Final = (
    OK,
    UNDEFINED_FLAT,
    UNDEFINED_TOO_SHORT,
    UNDEFINED_NONPOSITIVE_VALUE,
)
MIN_METRIC_PERIODS: Final = 8
METRIC_NAMES: Final = (
    "periodic_returns",
    "cagr",
    "annualised_volatility",
    "sharpe",
    "sortino",
    "max_drawdown",
    "max_drawdown_magnitude",
)


@dataclass(frozen=True)
class MetricsResult:
    periodic_returns: tuple[float, ...]
    cagr: float | None
    annualised_volatility: float | None
    sharpe: float | None
    sortino: float | None
    max_drawdown: float | None
    max_drawdown_magnitude: float | None
    n_periods: int
    mean_period_return: float | None
    sample_standard_deviation: float | None
    downside_deviation: float | None
    periods_per_year: float
    rf_annual: float
    mar_period: float
    diagnostic_only: bool
    statuses: dict[str, str]


def metrics_from_value_series(
    value_series: pd.Series | pd.DataFrame,
    periods_per_year: float,
    rf_annual: float = 0.0,
    mar_period: float = 0.0,
) -> MetricsResult:
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive")
    values = _normalise_value_series(value_series)
    n_periods = max(len(values) - 1, 0)
    if len(values) < 2:
        return _undefined_result(
            UNDEFINED_TOO_SHORT,
            n_periods,
            periods_per_year,
            rf_annual,
            mar_period,
        )
    if values.isna().any() or not np.isfinite(values.to_numpy(dtype=float)).all():
        return _undefined_result(
            UNDEFINED_NONPOSITIVE_VALUE,
            n_periods,
            periods_per_year,
            rf_annual,
            mar_period,
        )
    if bool((values <= 0).any()):
        return _undefined_result(
            UNDEFINED_NONPOSITIVE_VALUE,
            n_periods,
            periods_per_year,
            rf_annual,
            mar_period,
        )

    returns = values.div(values.shift(1)).sub(1).iloc[1:]
    mean_return = float(returns.mean())
    return_values = tuple(float(value) for value in returns)
    statuses = {name: OK for name in METRIC_NAMES}

    first_date = pd.Timestamp(values.index[0])
    last_date = pd.Timestamp(values.index[-1])
    elapsed_days = (last_date - first_date) / pd.Timedelta(days=1)
    years = float(elapsed_days) / 365.25
    if years <= 0:
        cagr = None
        statuses["cagr"] = UNDEFINED_TOO_SHORT
    else:
        cagr = float((values.iloc[-1] / values.iloc[0]) ** (1 / years) - 1)

    if n_periods < 2:
        sample_standard_deviation = None
        annualised_volatility = None
        sharpe = None
        statuses["annualised_volatility"] = UNDEFINED_TOO_SHORT
        statuses["sharpe"] = UNDEFINED_TOO_SHORT
    else:
        sample_standard_deviation = float(returns.std(ddof=1))
        annualised_volatility = sample_standard_deviation * sqrt(periods_per_year)
        if sample_standard_deviation == 0:
            sharpe = None
            statuses["sharpe"] = UNDEFINED_FLAT
        else:
            sharpe = (
                mean_return * periods_per_year - rf_annual
            ) / annualised_volatility

    downside_terms = np.minimum(returns.to_numpy(dtype=float) - mar_period, 0.0)
    downside_deviation = float(sqrt(float(np.mean(downside_terms**2))))
    if downside_deviation == 0:
        sortino = None
        statuses["sortino"] = UNDEFINED_FLAT
    else:
        sortino = (
            mean_return * periods_per_year - rf_annual
        ) / (downside_deviation * sqrt(periods_per_year))

    peaks = values.cummax()
    drawdowns = values.div(peaks).sub(1)
    max_drawdown = float(drawdowns.min())
    max_drawdown_magnitude = abs(max_drawdown)
    return MetricsResult(
        periodic_returns=return_values,
        cagr=cagr,
        annualised_volatility=annualised_volatility,
        sharpe=sharpe,
        sortino=sortino,
        max_drawdown=max_drawdown,
        max_drawdown_magnitude=max_drawdown_magnitude,
        n_periods=n_periods,
        mean_period_return=mean_return,
        sample_standard_deviation=sample_standard_deviation,
        downside_deviation=downside_deviation,
        periods_per_year=float(periods_per_year),
        rf_annual=float(rf_annual),
        mar_period=float(mar_period),
        diagnostic_only=n_periods < MIN_METRIC_PERIODS,
        statuses=statuses,
    )


def bias_checklist() -> tuple[str, ...]:
    checklist = (
        *KNOWN_BIASES,
        "SURVIVORSHIP: the universe is today's listings only.",
        "POINT_IN_TIME_FUNDAMENTALS: Sprint 3-7 fundamentals are restated, not point-in-time.",
        "ANNUAL_PUBLICATION_LAG: LAG_ANNUAL is assumed to be 90 days and is ESTIMATE_UNVERIFIED.",
        "TREASURY_SHARES: the treasury-share fraction is only a below-par-excluded one-sided upper bound.",
        "TRADING_FRICTIONS: the brokerage fee, sell tax, and settlement lag are ESTIMATE_UNVERIFIED.",
        "INTERPRETATION: results are for RELATIVE comparison only, never an expected return.",
    )
    if not checklist or any(not entry.strip() for entry in checklist):
        raise ValueError("bias checklist must be non-empty and contain no blank entries")
    return checklist


def _normalise_value_series(value_series: pd.Series | pd.DataFrame) -> pd.Series:
    if isinstance(value_series, pd.DataFrame):
        required = {"date", "portfolio_value"}
        missing = sorted(required.difference(value_series.columns))
        if missing:
            raise ValueError("value_series missing columns: " + ", ".join(missing))
        dates = pd.to_datetime(value_series["date"], errors="coerce")
        values = pd.to_numeric(value_series["portfolio_value"], errors="coerce")
        series = pd.Series(values.to_numpy(), index=dates)
    elif isinstance(value_series, pd.Series):
        dates = pd.to_datetime(value_series.index, errors="coerce")
        values = pd.to_numeric(value_series, errors="coerce")
        series = pd.Series(values.to_numpy(), index=dates)
    else:
        raise TypeError("value_series must be a pandas Series or DataFrame")
    return series.sort_index(kind="stable")


def _undefined_result(
    status: str,
    n_periods: int,
    periods_per_year: float,
    rf_annual: float,
    mar_period: float,
) -> MetricsResult:
    return MetricsResult(
        periodic_returns=(),
        cagr=None,
        annualised_volatility=None,
        sharpe=None,
        sortino=None,
        max_drawdown=None,
        max_drawdown_magnitude=None,
        n_periods=n_periods,
        mean_period_return=None,
        sample_standard_deviation=None,
        downside_deviation=None,
        periods_per_year=float(periods_per_year),
        rf_annual=float(rf_annual),
        mar_period=float(mar_period),
        diagnostic_only=True,
        statuses={name: status for name in METRIC_NAMES},
    )
