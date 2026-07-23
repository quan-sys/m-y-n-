# Sprint 8C-2 Synthetic Metric Fixtures

Every performance number in this report comes from a synthetic fixture. No real portfolio series exists and no real strategy performance was computed.

## N1 — CAGR

- NAV: `100.0 -> 200.0`
- first timestamp: `2019-01-01 00:00`
- last timestamp: `2020-12-31 12:00`
- elapsed days: `730.5`
- elapsed years: `2.0`
- computed CAGR: `0.41421356237309515`
- expected `2 ** 0.5 - 1`: `0.41421356237309515`

## N2 — Maximum drawdown

- NAV: `(100.0, 120.0, 90.0, 150.0)`
- running peaks: `(100.0, 120.0, 120.0, 150.0)`
- per-point drawdowns: `(0.0, 0.0, -0.25, 0.0)`
- computed max_drawdown: `-0.25`
- computed max_drawdown_magnitude: `0.25`

## N3 — Return-vector intermediates

- chosen return vector: `(0.10, -0.05, 0.02, -0.01)`
- computed periodic returns: `(0.10000000000000009, -0.050000000000000044, 0.020000000000000018, -0.010000000000000009)`
- n_periods: `4`
- count of negative periods: `2`
- downside-deviation divisor: `4` (all n_periods), NOT `2` (the count of negative periods)
- m: `0.015000000000000013`
- s with ddof=1: `0.06350852961085889`
- annualised_volatility: `0.12701705922171777`
- downside_deviation: `0.025495097567963948`
- Sharpe numerator `m * periods_per_year - rf_annual`: `0.06000000000000005`
- Sortino numerator `m * periods_per_year - rf_annual`: `0.06000000000000005`
- Sharpe: `0.4723774929733302`
- Sortino: `1.176696810829104`
- diagnostic_only: `True` because `n_periods=4 < MIN_METRIC_PERIODS=8`
- `rf_annual=0.0` is an ESTIMATE simplification requiring a real Vietnamese risk-free rate later.

## N4 — Undefined cases

- flat NAV Sharpe status: `UNDEFINED_FLAT`
- flat NAV Sortino status: `UNDEFINED_FLAT`
- one-point series statuses: `{'periodic_returns': 'UNDEFINED_TOO_SHORT', 'cagr': 'UNDEFINED_TOO_SHORT', 'annualised_volatility': 'UNDEFINED_TOO_SHORT', 'sharpe': 'UNDEFINED_TOO_SHORT', 'sortino': 'UNDEFINED_TOO_SHORT', 'max_drawdown': 'UNDEFINED_TOO_SHORT', 'max_drawdown_magnitude': 'UNDEFINED_TOO_SHORT'}`
- neither case raises.

## Bias checklist

- The universe contains only companies listed today, so companies delisted before today are absent and those are disproportionately the worst performers.
- All fundamentals from Sprint 3-7 are restated data and are not point-in-time.
- Results are usable only for RELATIVE comparison between configurations sharing the same bias, never as an expected return.
- SURVIVORSHIP: the universe is today's listings only.
- POINT_IN_TIME_FUNDAMENTALS: Sprint 3-7 fundamentals are restated, not point-in-time.
- ANNUAL_PUBLICATION_LAG: LAG_ANNUAL is assumed to be 90 days and is ESTIMATE_UNVERIFIED.
- TREASURY_SHARES: the treasury-share fraction is only a below-par-excluded one-sided upper bound.
- TRADING_FRICTIONS: the brokerage fee, sell tax, and settlement lag are ESTIMATE_UNVERIFIED.
- INTERPRETATION: results are for RELATIVE comparison only, never an expected return.
