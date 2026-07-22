C1. Candidate pool definition, single and binding. The candidate pool at a
rebalance date is the value-cut list for that portfolio AFTER the Sprint 7 S2
gate has removed every ticker whose `franchise_history_status` is not `READY`.
`franchise_history_status` does NOT exist in
`data/screener/step2_candidates_*.csv`; it must be joined on `ticker` from
`data/screener/sprint6_franchise_quality.csv`. On the 2026-07-20 evaluation date
this yields 44 for the EBIT/TEV portfolio and 43 for the E/P portfolio; the raw
candidate files hold 45 and 44 rows respectively and those raw counts are NOT
the candidate pool.

C2. Backtest start is computed by rule, never chosen by hand. During a
walk-forward run the engine advances through rebalance dates in chronological
order and begins recording at the first date whose candidate pool size is
greater than or equal to `ceil(MIN_CANDIDATE_POOL_MULTIPLE * portfolio_size)`,
using only data dated strictly before that date. The start date is an output of
the run, never an input, and no scan of later periods may influence it. As of
2026-07-22 this rule cannot yet be evaluated on historical quarters: the
screener has only ever been run for the single evaluation date 2026-07-20, and
`data/market_cap/2026-07-19/universe_market_cap.csv` holds one `shares_outstanding`
value per ticker rather than a time series, so historical market capitalisation,
and therefore historical EBIT/TEV and E/P, do not exist in this repository.
Pairing today's share count with a past price would be look-ahead and is
forbidden. The rule is implemented and tested here; it is first evaluated on
real data only after a point-in-time share-count series exists.

C3. A later thin period does not stop the run. If the candidate pool falls below
the C2 threshold at any rebalance after the start date, the run continues and
that period is flagged `THIN_CANDIDATE_POOL` in the rebalance log. Periods are
never dropped, and the start date is never moved backwards or forwards to
produce an uninterrupted window, because selecting a window on the basis of what
happened afterwards is look-ahead.

C4. `selection_ratio` is printed every period. `selection_ratio =
selected_count / candidate_pool_size`, written for every rebalance row. Any
period whose `selection_ratio` exceeds `SELECTION_RATIO_REPORT_THRESHOLD` is
flagged `LOW_SELECTIVITY` and must be listed explicitly in the report, because
at that point the screener is barely discriminating and the period's result says
more about pool scarcity than about the strategy.

C5. Thresholds are configuration chosen by economic meaning, not by data. Both
`MIN_CANDIDATE_POOL_MULTIPLE` and `SELECTION_RATIO_REPORT_THRESHOLD` live in
`config/screener.yaml`. `MIN_CANDIDATE_POOL_MULTIPLE = 1.5` was chosen because
picking 20 names from a pool of 30 still discards a third of the pool and
therefore still constitutes selection; it was deliberately NOT chosen by looking
for a gap in the observed per-period counts, which would be data mining. Every
report prints both values it ran with.

The headline result is the full window starting at the C2 date. The sub-window
restricted to periods whose candidate pool reaches twice the portfolio size is
reported alongside it as a robustness check. This two-window split is declared
here, before the first run, and neither window may be promoted or demoted after
the results are seen.

An `assert` is removed by the interpreter when Python runs with `-O`, so the
only look-ahead guard in the engine would silently disappear in an optimised
run. A `raise` cannot be stripped.
