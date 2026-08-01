# Sprint 8D — Deferred-defect work block: F-Score criteria 7 and 9, and one hard-coded threshold

Status: **APPROVED BY THE OWNER, 2026-08-01. Implementable. Sections 4.1, 4.3 and 4.4 were read and accepted explicitly, including the amendment of `docs/SPEC_SPRINT_6.md` section 2.2 and the loss of a scored criterion on 8 tickers.**

Written: 2026-08-01. Repository state it was written against: `main` = `8adfefd`.
Governing rules: `AGENTS.md` sections 2, 3, 5; `docs/KNOWN_LIMITS_AND_DEFERRED_DEFECTS.md` entries DEF-3 and DEF-5.

Evaluation date for every measurement quoted below: `2026-07-20` (the `evaluation_date` recorded in `data/screener/sprint6_fscore.csv`).

---

## 1. Scope

Sprint 8D closes exactly three items and nothing else:

- **8D-1 — DEF-3.** Criterion 9 (asset turnover) must become `UNSCORED` when the year N-1 revenue that forms its comparison denominator is non-positive, matching the guard criterion 8 already has.
- **8D-2 — DEF-5.** Implement the owner's settled 1% materiality threshold for criterion 7 (share issuance), read from `config/screener.yaml`, applied to BOTH the par-capital increase and the cash proceeds. See section 4.
- **8D-2b — consequential amendment.** `docs/SPEC_SPRINT_6.md` section 2.2 currently forbids the ratio that 8D-2 now uses for gating. That sentence must be amended openly, not contradicted silently. See section 4.3.
- **8D-3 — hard-coded threshold.** Move the literal `2.0` at `src/screener/step1_pipeline.py:273` into `config/screener.yaml` under a named key, with the value unchanged. `AGENTS.md` section 5 states that hard-coding a threshold in source code is a defect.

8D-3 is bundled here rather than sent alone because on its own it would be a sub-50-line change, which `05_ANTI_SLOPPY_RULES.md` rule D2 forbids sending as a separate work block.

Files in scope: `scripts/build_sprint6_fscore.py`, `scripts/audit_sprint6_readiness.py`, `src/screener/step1_pipeline.py`, `config/screener.yaml`, `data/screener/sprint6_fscore.csv` (regenerated output), `docs/REPORT_SPRINT_6_FSCORE.md` (regenerated report), `docs/SPEC_SPRINT_6.md` (section 2.2 amendment only), `docs/KNOWN_LIMITS_AND_DEFERRED_DEFECTS.md`, `CHANGELOG.md`, `data_contract.md`, and tests.

---

## 2. Evidence base — measured, not recalled

Every number in this section was produced by reading repository artifacts on `8adfefd` and is reproducible from them.

### 2.1 DEF-3, the criterion 9 defect, stated exactly

From `data/screener/sprint6_fscore.csv`, row `HQC` (the only row where `non_positive_revenue_n_minus_1` is `True`):

| criterion | result | flag |
|---|---|---|
| 8 (gross margin) | *(empty)* | `NET_SALES_N_minus_1_NON_POSITIVE` |
| 9 (asset turnover) | `1` | *(empty)* |

Both criteria consume the same `net_sales` value for year N-1. Criterion 8 blocks on it; criterion 9 does not.

The cause is visible in `scripts/build_sprint6_fscore.py`. The gross-margin helper applies `_positive_denominator(sales, ...)`, so a non-positive `net_sales` raises a flag and the criterion goes `UNSCORED`. The criterion 9 block builds `turnover_n1 = revenue_n1 / assets_n2` and guards only `assets_n2 > 0`; it applies no sign test to `revenue_n1`. A non-positive `revenue_n1` therefore yields a non-positive `turnover_n1`, so `turnover_n > turnover_n1` passes for any ordinary positive current-year turnover. "Asset turnover improved" scores automatically against a meaningless base.

Current HQC score: `F_SCORE_POINTS = 6`, `F_SCORE_CRITERIA_SCORED = 8`, `fscore_ranking_ratio = 0.75`, `fscore_ranking_eligible = True`.

### 2.2 DEF-5, the current criterion 7 population

From `data/screener/sprint6_fscore.csv`, 156 rows, tallied directly:

`criterion_7_branch`: `SCORE_1` 72 · `SCORE_0` 55 · `SHARE_INCREASE_NO_CASH_SUSPECTED` 28 · `MISSING_INPUT_UNSCORED` 1.
`criterion_7_settled_case`: `NO_SHARE_INCREASE_CASH_POSITIVE_SCORE_0` 20.

These four counts and the count of 20 match `docs/KNOWN_LIMITS_AND_DEFERRED_DEFECTS.md` entry DEF-5 exactly.

### 2.3 DEF-5, the counterfactual DEF-5 says has never been measured

DEF-5 records that the number of tickers whose score would change is `UNCLEAR` and "must not be stated as a fact until it is measured". It has now been measured, by replaying `classify_criterion7_branch` over the `criterion7_common_shares_n_value`, `criterion7_common_shares_n_minus_1_value` and `criterion7_issue_proceeds_n_value` columns of `data/screener/sprint6_readiness_audit.csv`.

**Reproduction control:** replaying the current, unmodified branch rules over those three columns reproduces the stored `criterion_7_branch` for **156 of 156 rows, 0 mismatches**. The counterfactuals below rest on that control.

64 of 156 tickers show any increase in `common_shares`. Exactly four increase by less than 1%: `MSN` 0.500%, `DGW` 0.912%, `PNJ` 0.959%, `DBD` 0.999%.

**Applying the 1% threshold to the `common_shares` comparison alone changes 0 of 156 rows.** All four sub-1% tickers also have positive `proceeds_from_issue_of_shares_N`, so declaring their share increase immaterial moves them from the first branch to the fourth, and the fourth branch scores 0 as well. The threshold, read the narrow way, is inert.

If the same 1% is also applied to `proceeds_from_issue_of_shares_N / common_shares_N`, **21 of 156 rows change**: 13 go `SCORE_0` to `SCORE_1` (`AGG`, `API`, `DBD`, `DGW`, `DHA`, `DXP`, `GVR`, `KSV`, `PVD`, `SBG`, `TCO`, `TV2`, `VNM`) and 8 go `SCORE_0` to `UNSCORED` with `SHARE_INCREASE_NO_CASH_SUSPECTED` (`ASM`, `CMG`, `HDG`, `HPG`, `IDC`, `ITD`, `SHI`, `SIP`).

The second group is the economically interesting one. `HPG` shows a 19.999% rise in `common_shares` against cash proceeds worth 0.896% of par capital; `IDC` and `SIP` show 15.0% against 0.529% and 0.929%. A near-20% rise in par capital funded by cash worth under 1% of it is the shape of a bonus issue or stock dividend, which is exactly the case the third branch was written for in `docs/SPEC_SPRINT_6.md` section 2.2, and which the current implementation misses because it tests `proceeds > 0` rather than `proceeds` being material.

### 2.4 The hard-coded threshold

`src/screener/step1_pipeline.py:273` reads `"review_flag": ratio > 2.0`. Consumers are `scripts/run_sprint4_step1_cleaning.py` lines 65 and 166, which put the flagged sector list into report metadata only. No ticker is removed by this flag.

---

## 3. SETTLED — 8D-1, the criterion 9 guard

Criterion 9 must produce `UNSCORED` with flag `REVENUE_N_MINUS_1_NON_POSITIVE` when `revenue_n1` is present, numeric, and less than or equal to zero. The flag name follows the existing `NET_SALES_N_minus_1_NON_POSITIVE` pattern produced by `_positive_denominator`; the exact final string is settled here so that Codex does not invent one.

`revenue_n` receives the same treatment for the same reason: a non-positive current-year revenue makes `turnover_n` meaningless in the same way. Flag `REVENUE_N_NON_POSITIVE`.

No other criterion changes. No threshold is involved: zero is not a tunable parameter, it is the point at which the ratio stops carrying economic meaning.

Expected effect, stated as a prediction to be verified against the regenerated output rather than assumed: `HQC` moves to `F_SCORE_POINTS = 5`, `F_SCORE_CRITERIA_SCORED = 7`, `fscore_ranking_ratio = 5/7 = 0.7142857142857143`. Because `MIN_SCORED_CRITERIA = 7`, HQC stays `fscore_ranking_eligible = True` and keeps its row. No other of the 156 rows is expected to change, because `non_positive_revenue_n_minus_1` is `True` for HQC alone. If the regenerated output disagrees with this prediction in any row, that is a STOP condition, not something to reconcile silently.

DEF-3's downstream instruction stands unchanged: for Franchise Power margin stability, HQC's affected year is DROPPED, never treated as a gross margin of zero.

---

## 4. SETTLED — 8D-2, the criterion 7 materiality threshold

DEF-5 recorded that the owner settled "a materiality threshold of 1%" without recording which quantity the 1% measures. Section 2.3 showed the two readings are not close variants: one is inert, the other rewrites 21 rows. The owner closed the question on 2026-08-01.

### 4.1 The owner's decision and its stated reason

**Option B: the 1% applies to BOTH tests.** Owner's reason, to be recorded in `CHANGELOG.md`: an increase that is too small is not material on either side of the criterion — a par-capital figure that only nudges is not real dilution, and cash proceeds that only trickle are not a real capital raise.

The decision was made on which quantity the threshold describes, NOT on the measured row counts. The counterfactual in section 2.3 exists to make the consequence visible before committing, not to select the rule. Selecting a rule by the output it produces is the data-mining DEF-5 warns against.

### 4.2 The settled rule

One configuration key governs both tests:

```yaml
CRITERION_7_MATERIALITY_PCT: 0.01
```

It is defined in exactly one place, is never hard-coded, and is deliberately NOT split into two independent keys. Two keys would be two tuning dials, and each extra dial is another way to fit the rule to the data after the fact. One key forces both sides to move together.

Test one, par-capital increase, replaces the plain `common_shares_N > common_shares_N-1`:

```text
material_share_increase =
    (common_shares_N - common_shares_N_minus_1) / common_shares_N_minus_1
    > CRITERION_7_MATERIALITY_PCT
```

Test two, cash proceeds, replaces the plain `proceeds_from_issue_of_shares_N > 0`:

```text
material_issue_proceeds =
    proceeds_from_issue_of_shares_N / common_shares_N
    > CRITERION_7_MATERIALITY_PCT
```

Both comparisons are strictly greater-than, so a value of exactly 1% is immaterial. Both denominators are non-zero by the existing input checks; a zero or missing denominator keeps the row `MISSING_INPUT_UNSCORED` exactly as today and must not be routed into a materiality branch.

The four settled branches of `docs/SPEC_SPRINT_6.md` section 2.2 keep their meaning, their names, and their order. Only the two boolean tests feeding them change. No fifth branch is created and no branch label is renamed.

**Test two introduces no new formula.** `proceeds_from_issue_of_shares_N / common_shares_N` is the ratio already defined and already computed as `issue_proceeds_to_common_shares_ratio` in `docs/SPEC_SPRINT_6.md` section 2.2. Its definition is reused verbatim; only its role changes. It must now be computed for every row rather than only for fourth-branch rows.

### 4.3 REQUIRED consequential amendment to `docs/SPEC_SPRINT_6.md`

Section 2.2 of that file currently states that `issue_proceeds_to_common_shares_ratio` "must NEVER gate, threshold, or alter any score". Option B gates on exactly that ratio. The sentence must therefore be amended in the same change set, with the amendment visible in the diff and its reason recorded in `CHANGELOG.md`.

Implementing 8D-2 while leaving that sentence in place would put the repository in direct self-contradiction, which is worse than either rule alone. Silently deleting the sentence is equally forbidden: the amendment must read as a dated owner decision that supersedes the earlier one, so that a later reader can see the rule changed and why.

### 4.4 Consequence the owner has accepted

Of the 21 rows that change, 8 move from a scored 0 to `UNSCORED` (`ASM`, `CMG`, `HDG`, `HPG`, `IDC`, `ITD`, `SHI`, `SIP`). Those tickers lose a data point rather than gain one: their `F_SCORE_CRITERIA_SCORED` falls by one, which moves them one step closer to the `MIN_SCORED_CRITERIA = 7` boundary and the `LOW_CONFIDENCE_SCORED_DENOMINATOR` flag. This is the intended behaviour of the third branch — refusing to score is the honest answer when the evidence points at a bonus issue — and is not to be "fixed" by lowering `MIN_SCORED_CRITERIA`.

The implementation must report, for each of those 8 tickers, whether the row crosses that boundary. If any of the 21 rows differs from the itemised list in section 2.3, that is a STOP condition: it means the implemented rule is not the rule specified here.

---

## 5. SETTLED — 8D-3, externalise the sector review threshold

Add `SECTOR_REJECT_RATIO_REVIEW_THRESHOLD: 2.0` to `config/screener.yaml`. `src/screener/step1_pipeline.py` reads it instead of the literal. The value is unchanged and the flag condition is unchanged.

The owner decision of 2026-07-31 stands: the `BÁN LẺ` flag is a false alarm, the flag's firing condition is NOT to be altered, and no per-sector exception is to be created. This item is a code-hygiene move only. If moving the constant changes which sectors are flagged for the 2026-07-18 run, that is a STOP condition.

---

## 6. Data Rules

- Never fabricate financial data. No value may be invented to make a criterion scoreable.
- `UNSCORED` is never silently converted to `0`. This is restated because 8D-1 and 8D-2 both create new `UNSCORED` rows.
- Every regenerated output row keeps `source`, `as_of` / `evaluation_date`, and `data_status` as it already carries them.
- Point-in-time discipline is unchanged: `available_from <= 2026-07-20`. No new fetch, no network call, no new dependency.
- The formulas in `docs/SPEC_SPRINT_6.md` sections 2 and 2.2 are copied verbatim into the implementation prompt. No variant may be recalled from memory.

---

## 7. Required Output Schema

`data/screener/sprint6_fscore.csv` keeps all 37 existing columns in their existing order and gains, appended at the end:

```text
non_positive_revenue_n              # bool, mirrors the existing non_positive_revenue_n_minus_1
common_shares_growth_pct            # float, (N - N_minus_1) / N_minus_1, the test-one quantity
criterion_7_materiality_applied     # bool, True when either materiality test changed this row's branch
criterion_7_branch_before_materiality  # the branch the pre-8D rules would have produced
```

`criterion_9_flag` gains the two new values `REVENUE_N_NON_POSITIVE` and `REVENUE_N_MINUS_1_NON_POSITIVE`. `criterion_7_branch` gains no new values; the threshold changes which existing branch a row lands in. `issue_proceeds_to_common_shares_ratio` already exists and keeps its name and formula, but is now populated for every row rather than only for fourth-branch rows, and is no longer diagnostic-only.

`criterion_7_branch_before_materiality` exists so that the 21 changed rows are auditable directly from the output file, without re-deriving them.

Any schema change requires a `data_contract.md` update in the same change set, per `AGENTS.md` section 7.

---

## 8. Required Local Checks

```bash
python -m py_compile scripts/build_sprint6_fscore.py scripts/audit_sprint6_readiness.py src/screener/step1_pipeline.py
python -m pytest -q
python scripts/build_sprint6_fscore.py
python scripts/run_sprint4_step1_cleaning.py
```

The full suite is 493 tests on `8adfefd` and must not fall below that count.

Mandatory number table, per `05_ANTI_SLOPPY_RULES.md` rule D4: the implementation must print, verbatim, every intermediate term for `HQC` criterion 9 (`revenue_N`, `revenue_N_minus_1`, `total_assets_N_minus_1`, `total_assets_N_minus_2`, `asset_turnover_N`, `asset_turnover_N_minus_1`) and for `VNM` and `HPG` criterion 7 (`common_shares_N`, `common_shares_N_minus_1`, `proceeds_from_issue_of_shares_N`, the two ratios, branch before and branch after). Results only, without the intermediate terms, make the diff unreviewable.

New tests required, each with hand-computed expected values, per `AGENTS.md` section 5:

- criterion 9 `UNSCORED` on non-positive `revenue_n1`, and separately on non-positive `revenue_n`;
- criterion 9 unchanged when both revenues are positive, proving the guard did not widen;
- criterion 7, one test per branch, driven by the materiality tests rather than the old plain comparisons, with at least one fixture just below 1% and one just above on each of the two tests;
- criterion 7 boundary test: exactly 1% on either test is IMMATERIAL, proving the comparison is strictly greater-than;
- criterion 7 regression test proving a missing or zero denominator still yields `MISSING_INPUT_UNSCORED` and never enters a materiality branch;
- a lock test asserting `CRITERION_7_MATERIALITY_PCT == 0.01` and `SECTOR_REJECT_RATIO_REVIEW_THRESHOLD == 2.0` in `config/screener.yaml`, in the style of the existing `tests/test_repo_decision_guards.py` locks, and asserting they are two entries governed by one value each rather than one key split into two;
- a test asserting no numeric threshold literal remains on the `review_flag` line.

Full-population reconciliation, required before the PR is opened: the regenerated `data/screener/sprint6_fscore.csv` must show exactly 21 rows where `criterion_7_materiality_applied` is `True`, and those 21 tickers must match the two lists in section 2.3 exactly — 13 to `SCORE_1` and 8 to `SHARE_INCREASE_NO_CASH_SUSPECTED`. Any other count, or any other ticker, is a STOP condition.

Known line-number side effect to check, not to ignore: `docs/REPORT_SPRINT_9_4B_ANNUAL_PIT.md` line 340 records the provenance string `scripts/build_sprint6_fscore.py:54-65,153-446`, and `scripts/build_sprint9_4b_annual_pit.py` builds the `153-446` half from a hard-coded literal. Editing `build_sprint6_fscore.py` shifts those line numbers and makes the recorded provenance stale. It is a documentation-accuracy defect, not a crash. The change set must either update the literal and regenerate the report, or record in `CHANGELOG.md` that it is knowingly stale.

---

## 9. Must NOT Include

- Any change to `MSCORE_THRESHOLD`, `ACCRUAL_WORST_PCT`, `VALUE_CHEAPEST_PCT`, `TEV_MIN_FRACTION_OF_MARKET_CAP`, `TICKER_IDENTITY_GAP_DAYS`, `DISTRESS_REQUIRE_HOSE_WARNING`, or `MIN_SCORED_CRITERIA`.
- Any implementation of `NET_DEBT_EBITDA_CAP`. DEF-4 blocks it and `tests/test_repo_decision_guards.py` fails if the key appears.
- Any change to the `review_flag` firing condition, any per-sector exception, or any new column in the sector diagnostic table.
- Any change to LIM-1, DEF-1, DEF-2, or DEF-4.
- Any splitting of `CRITERION_7_MATERIALITY_PCT` into two keys, or any second threshold value anywhere in criterion 7.
- Any edit to `docs/SPEC_SPRINT_6.md` beyond the single section 2.2 amendment described in section 4.3, and no silent deletion of the superseded sentence.
- Any lowering of `MIN_SCORED_CRITERIA` to compensate for the 8 rows that become `UNSCORED`.
- Any change to `data/forward_test/snapshots/2026-07-21/`, to `reports/2026-07-20/`, or to any Sprint 4, 5, 7, 8 or 9 output beyond the F-Score artifacts named in section 1.
- Any recomputation of Franchise Power, composite quality, percentiles, or portfolio construction.
- Any network call, any new dependency, any deletion or rename of an existing file, any modification or skipping of an existing test.
- Any momentum, shorting, dashboard, or refactor of untouched code.

---

## 10. Approval gate

Cleared by the owner on 2026-08-01: sections 3, 4, 5, 7 and 8 as written, section 4.3 (the `docs/SPEC_SPRINT_6.md` amendment), and section 4.4 (8 rows lose a scored criterion).

Remaining before any code may be written:

1. this file is committed to the repository as `docs/SPEC_SPRINT_8D.md`;
2. `CHANGELOG.md` carries an entry recording the Option B decision and the owner's reason from section 4.1.

The implementing prompt must carry the `05_ANTI_SLOPPY_RULES.md` Part F six components and pass the twelve-item gate in Part G before it is sent. The prompt must reference this file by path rather than restating its rules, so that there is exactly one copy of the specification.

---

*Research and education only. Nothing here is investment advice.*
