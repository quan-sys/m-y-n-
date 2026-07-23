8C2-1 PERIODIC RETURNS. Given a value series NAV indexed by date with n+1 points NAV_0..NAV_n, the per-period simple return is r_t = NAV_t / NAV_{t-1} - 1 for t = 1..n. A value <= 0 anywhere in the series makes returns undefined and the metrics must report a status, not a number.

8C2-2 CAGR. CAGR = (NAV_last / NAV_first) ** (1 / years) - 1, where years = (last_date - first_date).days / 365.25. CAGR uses elapsed calendar time, NOT the count of periods. If years <= 0 or fewer than 2 points, CAGR is undefined.

8C2-3 ANNUALISED VOLATILITY. Let m = arithmetic mean of r_t and s = sample standard deviation of r_t with ddof = 1. annualised_volatility = s * sqrt(periods_per_year). Requires at least 2 returns; with fewer, volatility is undefined.

8C2-4 SHARPE. sharpe = (m * periods_per_year - rf_annual) / (s * sqrt(periods_per_year)), with rf_annual defaulting to 0.0. Label rf_annual = 0 as an ESTIMATE simplification requiring a real Vietnamese risk-free rate later. If s = 0 the ratio is undefined and must be reported as a status, never as infinity or a crash.

8C2-5 SORTINO. Let downside_deviation = sqrt( mean over ALL n periods of min(r_t - MAR_period, 0) ** 2 ), with MAR_period (minimum acceptable return per period) defaulting to 0. The mean divides by n, the total number of periods, NOT by the count of negative periods. sortino = (m * periods_per_year - rf_annual) / (downside_deviation * sqrt(periods_per_year)). If downside_deviation = 0 the ratio is undefined and reported as a status.

8C2-6 MAXIMUM DRAWDOWN. Let peak_t = running maximum of NAV_0..NAV_t. drawdown_t = NAV_t / peak_t - 1. max_drawdown = min over t of drawdown_t, a non-positive number. Report its magnitude too. Also emit n_periods with every metric set, and state that any Sharpe or Sortino computed from fewer than MIN_METRIC_PERIODS periods is diagnostic only and not statistically meaningful; set MIN_METRIC_PERIODS = 8 as a configuration constant chosen by economic meaning (at least two years of quarterly data), not by data mining.
