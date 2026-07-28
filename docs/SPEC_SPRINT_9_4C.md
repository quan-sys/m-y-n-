9-4C-1 REUSE, DO NOT REIMPLEMENT. Every gate formula already exists in the repository as an
importable pure function. This sprint IMPORTS and CALLS them; it does not rewrite, reimplement,
inline, copy, or "simplify" any of them:
  `src/screener/step1_cleaning.py` — calculate_sta, calculate_snoa, calculate_dsri, calculate_gmi,
      calculate_aqi, calculate_sgi, calculate_depi, calculate_sgai, calculate_lvgi, calculate_tata,
      calculate_m_score, calculate_simple_distress
  `scripts/build_sprint6_fscore.py` — compute_ticker, criterion7_score, finalize_scores
  `scripts/build_sprint6_franchise.py` — compute_roc_series, summarize_roc, compute_margin_series,
      summarize_margin
If a function cannot be imported without triggering a side effect, extract it into an importable
module WITHOUT changing a single line of its arithmetic, and say in the report exactly what moved.
Do NOT re-derive or recall any formula from memory.

9-4C-2 INPUTS. Read-only, all already committed:
(a) `data/fundamentals/annual_pit/2026-07-26/annual_items_point_in_time.csv.gz` (32 items)
(b) `data/valuation/2026-07-26/historical_valuation_point_in_time.csv.gz` (for clause 9-4C-8 only)
(c) `data/screener/step1_survivors.csv`, `data/screener/sprint6_fscore.csv`,
    `data/screener/sprint6_franchise_quality.csv` (for the reconciliation in STEP 4 only)
No provider call. No input modified.

9-4C-3 UNIT WARNING FOR common_shares. In the VCI data, `common_shares` is SHARE CAPITAL denominated
in VND at a par value of 10,000 VND, NOT a share count. Verified cross-check: VNM fiscal 2024
`common_shares` = 20,899,554,450,000, which divided by 10,000 equals 2,089,955,445, exactly the
`shares_issued_derived` value for VNM 2024Q4 in `data/market_cap/2026-07-24/market_cap_point_in_time.csv`.
Piotroski criterion 7 compares year N against N-1, so a consistent VND-at-par unit is valid for that
comparison. Do NOT divide it, do NOT relabel it a share count, and do NOT mix it with
`shares_issued_derived`.

9-4C-4 EVALUATION GRID. The 28 quarter-end dates from 2019-03-31 to 2025-12-31, identical to the
Sprint 9-4a grid, PLUS one extra RECONCILIATION-ONLY date 2026-07-20 which is flagged
`grid_role = RECONCILIATION` and is excluded from every walk-forward summary. All other rows carry
`grid_role = WALK_FORWARD`.

9-4C-5 ANNUAL SELECTION IS AS-OF. For each (evaluation_date, ticker), the usable annual years are
exactly those with `available_from <= evaluation_date`. `annual_n` is the latest such year,
`annual_n_minus_1` the one before it, `annual_n_minus_2` the one before that. The pair or triple must
be CONSECUTIVE fiscal years; if a required year is missing the gate is UNSCORED with a named reason.
Never pad, never skip a year to reach the required count, never reuse a year twice.

9-4C-6 PERCENTILES ARE WITHIN-DATE. Every percentile and every relative flag is computed across the
tickers eligible AT THAT evaluation_date only. Pooling all dates into one population would rank a
2019 ticker against 2025 data, which is look-ahead. Use the Sprint 6 convention verbatim: a
rank-based percentile computed with the average rank for tied values, scaled to [0, 1], formed only
over tickers with a usable value, and tickers missing the value are excluded from the population
rather than placed at the bottom.

9-4C-7 US THRESHOLDS ARE HYPOTHESES, SO EMIT BOTH. `MSCORE_THRESHOLD` and `ACCRUAL_WORST_PCT` are
IMPORTED from `config/screener.yaml`; do NOT hard-type -1.78 or 0.10 and do NOT change them. For each
of these, emit BOTH the absolute-threshold flag AND the within-date percentile of the raw value, so a
later sprint can sweep the threshold without recomputing. State that these coefficients were
calibrated on United States data and remain hypotheses on the Vietnamese market.

9-4C-8 TEV-COLLAPSE FLAG — FLAG ONLY, NEVER DROP. When enterprise value is netted down close to zero
by a large cash balance, EBIT/TEV and E/P explode and the name occupies rank 1 for a reason that is
about the balance sheet rather than about operating cheapness. Measured example already in the repo:
PVS at evaluation date 2020-03-31 has cash 6,949,114,784,400 VND against market cap 5,049,466,799,623
VND plus debt 1,355,547,170,485 VND, leaving TEV 161,241,212,328 VND, that is 3.2 percent of market
cap, and EBIT/TEV 8.49. Emit `tev_to_market_cap` and a boolean `tev_collapse_flag` set when
`tev_to_market_cap < TEV_MIN_FRACTION_OF_MARKET_CAP`, a NEW key added to `config/screener.yaml` with
value 0.20. Justification to record verbatim: below that level more than 80 percent of enterprise
value is netted away by cash, and for Vietnamese non-financial companies a large share of reported
cash is working capital and customer advances rather than distributable excess cash, so the yield
describes the cash position rather than the operating business. This threshold was chosen on
economic grounds; it was NOT selected by searching the observed distribution for a convenient gap.
The flag NEVER removes a row and NEVER changes any existing metric.

9-4C-9 OUT OF SCOPE. No portfolio, no weights, no holdings, no returns, no trading costs, no
rebalance simulation, no momentum, no composite score combining value with quality, no change to any
Sprint 9-4a ranking. Those belong to Sprint 9-5.

9-4C-10 DISTRESS SCORES FROM TWO FINANCIAL-STATEMENT SIGNALS. The distress gate is scored from
accumulated loss and negative equity alone. The HoSE warning list remains a recognised third
signal that can convict a ticker whenever its value is supplied, but its absence no longer
blocks a verdict. Reason: the warning list is a manual input, `manual_inputs/` has never held
data, and no reconstruction exists for the 2019-2025 history, so requiring it left the gate
permanently unscored. Every row scored without warning data carries
`distress_confidence = NO_WARNING_DATA` and must be read as a weaker acquittal than a row
carrying `FULL`: a company already on the HoSE warning list for a reason not visible in
retained earnings or equity will be acquitted by this gate. This is a change to the gate
DEFINITION, approved by the repository owner on 2026-07-27, and it is confined to the
point-in-time path; the Step 1 production pipeline keeps the three-signal requirement through
the `require_hose_warning=True` default.

9-4C-11 NO THRESHOLD ON F-SCORE OR FRANCHISE. The owner decided on 2026-07-28 NOT to impose a
Piotroski or Franchise threshold at this stage, because those cut-offs were calibrated on United
States data and the master plan requires Vietnamese walk-forward evidence before any threshold is
fixed. The decision is deferred to Sprint 9-5B, which will run both baskets in parallel.
