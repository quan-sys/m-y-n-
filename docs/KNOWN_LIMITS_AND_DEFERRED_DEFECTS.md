# Known limits and deferred defects

This registry lists decisions that are DELIBERATE. Every entry below is a thing
this repository does not do on purpose. None of them is a bug waiting to be
tidied up by whoever reads this next.

Rule: do not "fix" any entry here without an explicit owner decision recorded in
`CHANGELOG.md`. Silently closing one of these is a defect, not an improvement.

Uncertainty labels: OK verified from a repository artifact named in the entry;
EST estimate or secondary source; UNCLEAR unverified.

## LIM-1 — The PFD_HIGH_RISK warning gate mixes three unrelated reason types

Status: ACCEPTED LIMIT, gate stays as built. Owner decision 2026-07-31.

The exchange "special monitoring" lists feed a single boolean into
`PFD_HIGH_RISK`, whose name means financial distress. Those lists in fact mix at
least three unrelated reason types: financial (accumulated losses, negative
equity), disclosure (late statements), and GOVERNANCE.

Evidence (OK): DGC was removed by this gate. Its published reason, read from
https://www.hsx.vn/vi/theo-doi-dac-biet effective 2026-07-09, is failure to hold
the annual general meeting within six months of financial year end. That is a
governance failure, not insolvency. DGC was profitable and operating normally.

Run of record (OK, `CHANGELOG.md` entry 2026-07-31): survivors 156 -> 153,
`PFD_HIGH_RISK` 10 -> 13, the three tickers removed by the warning signal alone
being API, DGC and IDJ; the other four filters moved by zero tickers.

Owner decision: KEEP THE GATE, WITH NO PER-TICKER EXCEPTIONS. Reason: carving
out an exception for an individual ticker puts subjective judgement back into
the screener, which is the exact thing this project exists to remove. The cost
is accepted and recorded here rather than paid by a hand-made exception list.

Not measured (UNCLEAR): what share of flagged tickers is governance rather than
financial. `manual_inputs/hose_warning/warnings.csv` has 65 rows and its header
is `ticker,status,effective_date,lifted_date,source_url,published_date,recorded_at,note`
— there is NO reason column. Measuring this requires re-collecting a reason for
every row from the exchanges.

## DEF-1 — The TEV collapse flag is diagnostic only and gates nothing

Status: DEFERRED, no gating behaviour to be added without an owner decision.

`config/screener.yaml` sets `TEV_MIN_FRACTION_OF_MARKET_CAP: 0.20`. A row whose
`tev_to_market_cap` falls below it receives `tev_collapse_flag`. The flag is
recorded and reported; it does not remove the row from any ranking.

Evidence (OK), `docs/REPORT_SPRINT_9_4C_GATES_AS_OF.md`, flagged-row table and
the sentence immediately below it, "No row was dropped for tev_collapse_flag":
seven rows are flagged. Five carry a NEGATIVE ratio (SRA at 2019-06-30,
2019-09-30 and 2019-12-31; TIP at 2022-09-30 and 2022-12-31) and a negative
ratio sorts as most expensive, so those never reach a portfolio. Two are
positive but tiny: PVS 2020-03-31 at 0.031932324486197386 and VTO 2025-12-31 at
0.142624831676547.

Do NOT change `TEV_MIN_FRACTION_OF_MARKET_CAP` and do NOT make the flag drop
rows as part of any unrelated change.

## DEF-2 — VHM is a confirmed ticker-reuse case

Status: DEFERRED, handled by flag only.

The daily price series for VHM contains a long flat zero-volume stretch followed
by a gap and a discontinuous jump, i.e. two different companies share one
ticker string. The repository marks the earlier stretch rather than deleting or
patching it: the flag constant `PRE_GAP_SEGMENT_UNVERIFIED` is defined in
`src/backtest/eligibility.py` and is also referenced in `docs/SPEC_SPRINT_8B.md`.
The gap width parameter is `TICKER_IDENTITY_GAP_DAYS: 180` in
`config/screener.yaml`.

Filling price gaps is banned. Nine further tickers have gaps over thirty days
(EST, not re-counted in this document). Do not change
`TICKER_IDENTITY_GAP_DAYS` to make a flag disappear.

## DEF-3 — HQC has non-positive FY2024 revenue and criterion 9 still scores it

Status: DEFERRED to the Sprint 8D work block.

Evidence (OK), `data/screener/sprint6_fscore.csv` read directly: the column
`non_positive_revenue_n_minus_1` is True for exactly one ticker, HQC. The
distribution of `F_SCORE_CRITERIA_SCORED` is 9 for 126 tickers and 8 for 30
tickers. HQC is one of the 30: its gross-margin criterion is correctly UNSCORED.

What is NOT handled: HQC's `criterion_9_result` is 1, i.e. the asset-turnover
criterion still scores despite resting on the same meaningless denominator, so
"turnover improved" passes close to automatically. This is tracked by the
diagnostic column only and is deferred.

Consequence to respect elsewhere: when computing margin stability for Franchise
Power, that year must be DROPPED for HQC, never treated as a gross margin of
zero. HQC survives Sprint 4 cleaning but appears in no candidate list under
either EBIT/TEV or E/P, so it currently affects no ranking.

## DEF-4 — NET_DEBT_EBITDA_CAP is blocked by owner decision, and now locked

Status: BLOCKED BY OWNER DECISION. This is not an oversight.

The block itself is not new and this registry is not its first record. It is
already stated twice in the specifications (OK, verified by reading both files):
`docs/SPEC_SPRINT_4.md` line 104 gives the reason — `PLAN_quant_screener_myn.md`
contains no owner-approved cap, so under the no-invention rule the sub-signal is
deferred until the owner sets the value explicitly — and line 140 records that
the key is intentionally absent rather than left as an empty placeholder.
`docs/SPEC_SPRINT_7.md` line 78 restates that it remains BLOCKED.

What is verified about the config (OK): the key `NET_DEBT_EBITDA_CAP` does NOT
appear in `config/screener.yaml`, which is the only file where a threshold takes
effect. The three specification mentions above are prose recording the decision,
not a live setting.

Consequence: the distress filter ships on three threshold-free signals only —
accumulated losses below zero, negative shareholders' equity below zero, and
exchange warning-list membership.

What IS new here: until now nothing in the repository would fail if someone
added a plausible-looking number for this key. Prose cannot refuse a value.
`tests/test_repo_decision_guards.py` now fails if the key ever appears in
`config/screener.yaml`. Adding a number for it is a data-mining decision
requiring an owner decision recorded in `CHANGELOG.md`, not a bug fix.

## DEF-5 — The 1% materiality threshold for criterion 7 is not implemented

Status: DEFERRED to the Sprint 8D work block.

Evidence (OK), `data/screener/sprint6_fscore.csv` read directly, column
`criterion_7_branch`: SCORE_1 72, SCORE_0 55, SHARE_INCREASE_NO_CASH_SUSPECTED
28, MISSING_INPUT_UNSCORED 1. The column `criterion_7_settled_case` further
shows NO_SHARE_INCREASE_CASH_POSITIVE_SCORE_0 for 20 tickers.

The owner has settled a materiality threshold of 1% for this criterion, chosen
on ECONOMIC grounds and deliberately NOT cut at the gap observed in the data,
because cutting at an observed gap is data-mining. The number of tickers whose


## DEF-6 — Seven scripts assert a literal survivor population of 156
 
Status: OPEN. Specification approved 2026-08-01 as `docs/SPEC_SPRINT_8E_POPULATION.md`.
Implementation not started.
 
Evidence (OK), measured on `main` = `86c2bc2`: `data/screener/step1_survivors.csv`
holds 153 rows and 153 unique tickers after the 2026-07-31 HoSE/HNX warning-gate
run, while `data/screener/sprint6_fscore.csv`, `sprint6_readiness_audit.csv`,
`sprint6_annual_history_coverage.csv` and `step2_valuation_all.csv` each hold 156.
The 153 are a strict subset of the 156; the difference is exactly API, DGC and IDJ,
the three tickers the warning gate removed. Running `scripts/build_sprint6_fscore.py`
raises `ValueError: expected 156 unique survivors; rows=153 unique=153` at line 493.
 
The literal 156 gates seven scripts: `audit_sprint6_readiness.py` (lines 21, 502,
513), `build_sprint6_fscore.py` (41, 491, 521), `build_sprint6_franchise.py` (49,
377, 379, 507), `build_sprint5_valuation.py` (26, 390), `fetch_sprint6_annual_history.py`
(29, 116), `analyze_sprint6_annual_history.py` (19, 120, 237) and
`fetch_sprint5_market_cap.py` (325, 338, the default `expected_count` that `main()`
does not override). Both the Sprint 5 valuation layer and the Sprint 6 quality layer
are blocked, not only the F-Score build.
 
Evidence (OK) that the guard is untested: setting the constant to a value that makes
every guard raise unconditionally still leaves the nine test files that import these
scripts passing, 77 passed 0 failed. No test exercises the guard.
 
The owner's decision is to REMOVE the constant, not to change 156 to 153, because 153
is another ghost number that the 2026-09-30 rebalance would break again. Do not
"fix" this entry by introducing `EXPECTED_SURVIVORS = 153`, a `MIN_SURVIVORS`, or any
other expected-count constant.
 
Out of scope, and deliberately so: `scripts/probe_share_count_history.py` lines
205-207 and 250-252 gate `data/market_cap/2026-07-19/universe_market_cap.csv`, a
frozen 157-row probe artifact. That is a different number that merely looks like
this one.
 
score would change is UNCLEAR — it is not recorded in any artifact in this
repository and must not be stated as a fact until it is measured.

Nothing about this threshold is implemented. Do not implement it as a side
effect of another change.
