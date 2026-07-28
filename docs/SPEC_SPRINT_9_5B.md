# Sprint 9-5B — Walk-forward

9-5B-1 SCOPE. This sprint runs the existing Sprint 8B engine and the existing Sprint 8C metrics
over the eight configurations built by Sprint 9-5A, and reports the result. It writes no new
financial formula. Every number it produces is DIAGNOSTIC ONLY and is never an expected return.

9-5B-2 INPUTS, READ-ONLY, ALL ALREADY COMMITTED.
(a) `data/screener/targets_pit/2026-07-28/rebalance_targets_point_in_time.csv.gz`
(b) `data/price_history/2026-07-22/daily_close.csv.gz`
No provider call. No input modified. No re-selection of any basket: the 20 tickers and their
weights come from (a) exactly as committed and are never recomputed, re-ranked or re-filtered.

9-5B-3 EXECUTION DATE MUST PRICE THE PORTFOLIO. A market session is a date on which at least one
ticker has volume strictly greater than zero. For an evaluation date `t` and a configuration,
the execution date is the FIRST market session on or after `t` on which EVERY ticker currently
held by that configuration has a traded price. Holdings are the positions carried in from the
previous rebalance; at the first rebalance of a configuration the set is empty and the execution
date is simply the first market session on or after `t`. The search advances at most 8 sessions;
if no qualifying session exists within 8, STOP the run and report rather than proceeding.
Rationale, to record: a session on which a held name did not trade is a session on which the
portfolio cannot be valued, so trading there would delete the period rather than measure it.
Waiting conditions only on assets already owned and on information observable that same session,
so it introduces no look-ahead; it does assume execution at the close of the first day on which
every holding traded, and that assumption is stated in every report. The execution date is
therefore CONFIGURATION-SPECIFIC, not a single market-wide map, and both the evaluation date and
the configuration's own execution date appear in every output row.

9-5B-4 ELIGIBILITY IS MEASURED AT THE EVALUATION DATE, NOT THE EXECUTION DATE. `compute_eligibility`
is called with the EVALUATION date, identical to Sprint 9-5A, so the eligible set the engine
sees is exactly the eligible set 9-5A selected from. The resulting frame is then keyed under the
EXECUTION date because that is the key the engine matches against its targets. Consequence to
verify, not to assume: `selected_count` in the engine rebalance log must equal 20 at every date
of every configuration, because no name 9-5A selected can be excluded by a differently-measured
eligibility test.

9-5B-5 MISSING PRICE IS REPORTED, NEVER FILLED. Sprint 8B clause B3 stands: no interpolation, no
forward fill, no substitution, and no change to `src/backtest/engine.py`. Clause 9-5B-3 removes
the case where a HELD name cannot be priced. The remaining case is a NEWLY SELECTED name that
does not trade on the execution date; the engine excludes it, the position is not opened, and its
intended weight stays in cash for that period. Measured before the run: exactly 7 target rows
fall in this case. Each is listed in the report with configuration, evaluation date, execution
date and ticker, and the affected rebalances are reported as holding 19 names plus residual cash
rather than 20.

9-5B-6 THE BACKTEST WINDOW IS NOT THE TARGET TABLE. `compute_backtest_window` is imported and
run per configuration on the `candidate_pool_size` series from (a). Periods before the window
starts are NOT performance periods. Metrics are computed TWICE for every configuration: once
over all emitted dates, and once restricted to dates from the window start onward. Both are
reported side by side and neither is presented as the answer.

9-5B-7 METRICS ARE IMPORTED. `metrics_from_value_series` from `src/backtest/metrics.py` is
called with `periods_per_year = 4` because the grid is quarterly, and `rf_annual = 0.0`. The
zero risk-free rate is an unverified placeholder, not a market observation, and every Sharpe
and Sortino figure is labelled accordingly. Do NOT compute CAGR, volatility, Sharpe, Sortino or
drawdown by hand anywhere in this sprint.

9-5B-8 SAMPLE SIZE DISCLOSURE IS MANDATORY. Every metrics table states `n_periods` beside every
ratio. A configuration whose in-window `n_periods` is below 12 carries the literal flag
`SAMPLE_TOO_SMALL_FOR_INFERENCE` in its row, and the report states that a Sharpe ratio computed
from fewer than 12 quarterly returns cannot distinguish skill from noise.

9-5B-9 WHAT THIS RUN MAY NOT DECIDE. Per Sprint 8B clause B8, this engine may NOT settle the
choice between EBIT/TEV and E/P, and may NOT settle the momentum question. It also may not
settle whether the six gates help, because the gated configurations cover a far shorter period
than the ungated ones and the two are therefore not comparable on return. The gate comparison
this sprint CAN make is confined to dates where both configurations are live.

9-5B-10 OUT OF SCOPE. No new factor, no momentum, no sector cap, no threshold on F-Score or
Franchise, no parameter sweep, no optimisation of any kind, no change to any Sprint 9-4 or
9-5A number, and no recommendation to buy or sell anything.
