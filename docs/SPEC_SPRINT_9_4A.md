9-4A-1 SCOPE SPLIT AND WHY. Sprint 9-4 is split. Sprint 9-4a ranks the VALUATION metrics only.
Sprint 9-4b will apply the Step 1 cleaning gates (accruals, M-Score, distress) and the Step 3
quality gates (F-Score, Franchise Power). 9-4b is deferred because both need ANNUAL point-in-time
fundamentals for the 243 screener-relevant tickers, which do not exist in the repo: only the
quarterly table from Sprint 9-2b exists, and the Sprint 6 annual work covers only the 156 survivors
frozen at the single date 2026-07-17, so reusing it for past quarters would reintroduce look-ahead
and survivorship. Every output of 9-4a therefore carries the label: "VALUE-ONLY BASKET — no fraud,
distress or quality gate has been applied; this is NOT the final screener basket."

9-4A-2 INPUT. Exactly one committed file, read-only:
`data/valuation/2026-07-26/historical_valuation_point_in_time.csv.gz`. No provider call, no other
input, and the file must not be modified.

9-4A-3 REBALANCE GRID. One ranking per distinct `evaluation_date` in the input where at least one
row is eligible. The earliest such date is 2019-03-31, because Sprint 9-3 measured zero computable
rows in calendar 2018: point-in-time share count for 2018 quarters requires the FY2017 annual report
and annual history begins in 2018. The grid is never moved forward or backward to produce a nicer
window; choosing a window by what happened afterwards is look-ahead.

9-4A-4 DIRECTION OF CHEAPNESS. `ebit_tev` and `e_p` are YIELDS: a HIGHER value means CHEAPER. The
cheap set is therefore the TOP fraction by metric value, never the bottom. Rank 1 is the highest
metric value and the cheapest name.

9-4A-5 ELIGIBILITY. A row enters a ranking only when `valuation_status == "OK"` and the
corresponding eligibility flag (`ebit_tev_eligible` or `e_p_eligible`) is True. Rows excluded by the
Sprint 9-3 rule (negative EBIT, non-positive TEV, negative earnings) are never ranked and never
silently converted to a bottom rank.

9-4A-6 FOUR POPULATIONS. Every ranking is computed independently inside each of these four
populations, identified by `population_id`:
  ALL                      — every eligible row at that date
  ALL_EX_UPPER_BOUND       — excludes rows with market_cap_status == "UPPER_BOUND"
  PRICE_OK                 — only rows with price_confidence == "OK"
  PRICE_OK_EX_UPPER_BOUND  — both restrictions
Reason to state: Sprint 9-3 measured that 32.9 percent of OK rows carry an UPPER_BOUND market cap,
whose EBIT/TEV and E/P are therefore LOWER bounds, so those names are pushed down the cheapness
ordering by a data limitation rather than by valuation. The two EX_UPPER_BOUND populations measure
how much that limitation moves the basket.

9-4A-7 PERCENTILE CONVENTION (verbatim from SPEC_SPRINT_6.md section on component percentiles):
"a rank-based percentile computed with the average rank for tied values, so that tied tickers
receive an identical percentile; it is scaled to [0, 1] and formed only over tickers that have a
usable value for that component. Tickers missing that component are excluded from that ranking
population rather than being placed at the bottom."
Percentile 1.0 is the cheapest end.

9-4A-8 CHEAP CUT. `in_cheap_set` is True when `percentile >= 1 - VALUE_CHEAPEST_PCT`, with
`VALUE_CHEAPEST_PCT` IMPORTED from `config/screener.yaml`. Do NOT hard-type 0.30. The full ranking
is emitted for every eligible row regardless of the cut, so a later sprint can sweep the threshold
without refetching or recomputing.

9-4A-9 POOL DEPTH DIAGNOSTICS. For every (evaluation_date, metric, population), compute and report
`cheap_set_size`, plus `selection_ratio = target_size / cheap_set_size` for `target_size` of 20 and
of 25. Flag `LOW_SELECTIVITY` when the ratio exceeds `SELECTION_RATIO_REPORT_THRESHOLD` and
`THIN_CANDIDATE_POOL` when `cheap_set_size < 20 * MIN_CANDIDATE_POOL_MULTIPLE`. Both constants are
IMPORTED from `config/screener.yaml`; do NOT hard-type 0.70 or 1.5, and do NOT change them.

9-4A-10 OUT OF SCOPE. No portfolio weights, no holdings, no returns, no trading costs, no rebalance
simulation, no momentum, no F-Score, no M-Score, no accruals, no distress gate, no composite score.
Those belong to Sprint 9-4b and Sprint 9-5.
