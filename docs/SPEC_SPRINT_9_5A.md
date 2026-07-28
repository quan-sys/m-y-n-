# Sprint 9-5A — Rebalance targets

9-5A-1 SCOPE SPLIT. Sprint 9-5 is split in two. 9-5A produces the point-in-time rebalance
target table and nothing else: no prices, no returns, no portfolio value, no metrics, no
engine call. 9-5B feeds this table into the Sprint 8B engine and the Sprint 8C metrics. This
split was approved by the repository owner on 2026-07-28.

9-5A-2 INPUTS, READ-ONLY, ALL ALREADY COMMITTED.
(a) `data/screener/candidates_pit/2026-07-26/value_candidates_point_in_time.csv.gz`
(b) `data/screener/gates_pit/2026-07-27/gate_values_point_in_time.csv.gz`
(c) `data/price_history/2026-07-22/daily_close.csv.gz` — used ONLY to compute B1 eligibility
    session counts. No price is written to the output and no return is computed.
No provider call. No input file modified.

9-5A-3 GRID. The 28 quarter-end dates 2019-03-31 to 2025-12-31, identical to Sprint 9-4a and to
the WALK_FORWARD rows of Sprint 9-4c. The Sprint 9-4c RECONCILIATION row dated 2026-07-20 is
excluded.

9-5A-4 CONFIGURATION GRID. Eight configurations, the cross product of:
  populations `ALL` and `PRICE_OK`;
  metrics `ebit_tev` and `e_p`;
  gate settings `VALUE_ONLY` and `VALUE_PLUS_GATES`.
`config_id` is the three joined by a double underscore, for example
`ALL__ebit_tev__VALUE_PLUS_GATES`. Both metrics are carried because Sprint 8B clause B8
forbids this engine from deciding between EBIT/TEV and E/P; carrying both keeps the question
open rather than answering it.

9-5A-5 CANDIDATE SET PER CONFIGURATION. Start from the rows of input (a) with
`in_cheap_set` true for that population and metric at that date. For `VALUE_PLUS_GATES`,
intersect with the tickers that satisfy the Sprint 9-4c `_all_six_pass` predicate at the same
date — import that predicate, do NOT restate it. For `VALUE_ONLY`, no gate filter is applied.

9-5A-6 ELIGIBILITY BEFORE SELECTION. A ticker is eligible at rebalance date `t` only if,
within the 365 calendar days strictly before `t`, it has at least `MIN_TRADED_SESSIONS_12M`
sessions with volume strictly greater than zero, exactly as Sprint 8B clause B1 defines it.
Eligibility is applied BEFORE the top-N cut, and the count of candidates dropped for
ineligibility is recorded per configuration per date with reason
`INSUFFICIENT_TRADED_SESSIONS`. Sessions with zero volume are not counted, per B2.

9-5A-7 SELECTION IS TOP-N BY EXISTING RANK, DETERMINISTIC. Sort the eligible candidates by
`rank_in_population` ascending, breaking ties by ticker in ascending alphabetical order, and
take the first `HOLDING_COUNT` names. `rank_in_population` is already computed within date and
within population by Sprint 9-4a; do NOT recompute a ranking, do NOT re-derive a percentile.
If fewer than `HOLDING_COUNT` eligible candidates exist at a date, take all of them and set
`SHORT_BASKET` true for that configuration and date rather than padding from outside the
candidate set.

9-5A-8 WEIGHTS ARE EQUAL, NO SECTOR CAP AT THIS STAGE. Each selected name receives weight
`1 / (number of names selected at that date)`. The Sprint 7 function `select_portfolio` is
deliberately NOT reused: it ranks on `composite_quality` and requires `adtv_20d` and
`franchise_history_status`, none of which exist as point-in-time series, and its sector cap
keys on `icb2` which exists only as a snapshot taken today, so applying it to 2019 would inject
look-ahead. Record this as a deliberate simplification, not an oversight; the sector cap
remains an open question for a later sprint.

9-5A-9 THIN POOL IS FLAGGED, NEVER PADDED. For each configuration and date, record the
candidate pool size after eligibility, the threshold `ceil(MIN_CANDIDATE_POOL_MULTIPLE *
HOLDING_COUNT)`, and whether the pool meets it, by importing `compute_backtest_window` from
`src/backtest/window.py`. Do NOT restate its arithmetic, do NOT drop a date because it is thin.

9-5A-10 OUT OF SCOPE. No price is written, no return, no portfolio value, no CAGR, Sharpe,
Sortino or drawdown, no trading cost, no benchmark, no momentum, no threshold on F-Score or
Franchise, and no change to any Sprint 9-4a or 9-4c number.
