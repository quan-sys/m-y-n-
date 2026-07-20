# Sprint 6 Step 3 — Binding quality specification

Status: **SPECIFICATION, LOCAL READINESS AUDIT, AND INVESTIGATION ONLY. PRODUCTION QUALITY COMPUTATION IS FORBIDDEN PENDING OWNER APPROVAL.**

Evaluation date for the reproducible audit: `2026-07-20`.

## 1. Scope and ranking contract

- Sprint 6 is Step 3 **QUALITY** in `PLAN.md`.
- Quality inputs and component evidence are prepared for all `156` Sprint 4 survivors in `data/screener/step1_survivors.csv`.
- After an owner-approved production build, quality ranking is applied separately inside `data/screener/step2_candidates_ebit_tev.csv` and inside `data/screener/step2_candidates_ep.csv`.
- Component percentiles are computed across all eligible Sprint 4 survivors before the two candidate-list-specific quality ranks are assigned.
- There is no combined value+quality score and no winner metric. Winner selection belongs to Sprint 8.
- Sprint 6 does not change the Sprint 5 candidate lists or any Sprint 4 output.

## 2. Settled Piotroski F-Score definition

Annual year N is compared with year N-1. Both years must be point-in-time published with `available_from <= evaluation date`. The build must reuse the `annual_n` / `annual_n_minus_1` pairing already recorded in `data/screener/step1_survivors.csv` where that pair remains consecutive, locally present, and eligible by the evaluation date.

The nine binary criteria, one point each, F-Score = sum (0-9):

1. ROA > 0, where ROA = net_income_N / total_assets at end of N-1
2. CFO > 0, where CFO = cash flow from operations_N / total_assets at end of N-1
3. delta ROA > 0 (ROA_N > ROA_N-1)
4. CFO (scaled as in 2) > ROA (accrual criterion)
5. long-term leverage decreased: long_term_debt / average total assets,
   ratio_N < ratio_N-1
6. current ratio increased: (current assets / current liabilities),
   ratio_N > ratio_N-1
7. no new common shares issued during year N
8. gross margin increased: gross_margin_N > gross_margin_N-1
9. asset turnover increased: (revenue_N / total_assets at end of N-1) >
   (revenue_N-1 / total_assets at end of N-2)

`total_assets` at end of N-2 is required for criteria 3, 5, and 9. It remains subject to the same point-in-time rule and may not be filled from a later publication.

### 2.1 SETTLED — net-income mapping and normalized VAS input map

- F-Score net income = normalized `net_profit_loss_after_tax` (consolidated), because the criterion 1/3/4 denominator is consolidated `total_assets`; using a parent-only numerator against a consolidated denominator understates ROA for groups with material non-controlling interests.
- A diagnostic-only column `roa_parent_only`, computed from `attributable_to_parent_company` over the same denominator, must be written to the future output and must NEVER enter any criterion, percentile, or ranking.
- Sprint 5 E/P correctly uses `attributable_to_parent_company` because its denominator is market capitalisation, which reflects parent shareholders only. This difference is intentional and not an inconsistency.

The remaining rows in this table are SETTLED, approved by the owner on 2026-07-20:

| Economic input | Normalized field | Treatment and reason |
|---|---|---|
| CFO | `net_cash_inflows_outflows_from_operating_activities` | Use the explicit annual operating-cash-flow subtotal; do not reconstruct CFO from working-capital lines. |
| total assets | `total_assets` | Use the explicit year-end consolidated value for N, N-1, and N-2 as required. |
| long-term debt | `long_term_borrowings` | Use interest-bearing long-term borrowings; do not substitute total long-term liabilities. |
| current assets | `current_assets` | Use the explicit year-end subtotal. |
| current liabilities | `current_liabilities` | Use the explicit year-end subtotal. A zero or non-positive denominator blocks the criterion rather than producing a ratio. |
| revenue | `net_sales` | Use net sales consistently for gross margin and asset turnover; do not mix with gross `sales`. |
| gross profit | `gross_profit` | Prefer the explicit normalized gross-profit subtotal. If it is missing, a later approved build may use `net_sales + cost_of_sales` only when `cost_of_sales` is an explicit usable non-positive expense and the sign contract is logged; otherwise the criterion is UNSCORED. |
| cost of goods sold diagnostic/fallback | `cost_of_sales` | It is not silently substituted. Its presence and sign must be recorded whenever the proposed fallback is used. |
| share-issuance cash signal | `proceeds_from_issue_of_shares` | Use the explicit annual cash-flow line for year N. |
| common-share par-capital signal | `common_shares` | This is balance-sheet common-share par capital denominated in VND, not a share count. Compare the explicit end-N and end-(N-1) values to catch capital changes that the proceeds line alone may miss. The year-over-year comparison remains valid because par capital changes only when the share count changes, but `common_shares` must never be used as a share count anywhere. |

### 2.2 SETTLED — criterion 7 detection

- `common_shares_N > common_shares_N-1` AND `proceeds_from_issue_of_shares_N > 0` -> criterion 7 scores 0.
- `common_shares_N <= common_shares_N-1` AND `proceeds_from_issue_of_shares_N == 0` -> criterion 7 scores 1.
- `common_shares_N > common_shares_N-1` AND `proceeds_from_issue_of_shares_N == 0` -> criterion 7 is UNSCORED with flag `SHARE_INCREASE_NO_CASH_SUSPECTED`; it is never scored 0 and never scored 1.
- `common_shares_N <= common_shares_N-1` AND `proceeds_from_issue_of_shares_N > 0` -> criterion 7 scores 0, because cash was received from share issuance or owner capital contribution at group level even when parent par capital did not change. Recognised possible reasons include non-controlling contributions into subsidiaries and timing differences; none is asserted as fact for any specific ticker.
- Any missing, duplicate, non-numeric, or negative input -> UNSCORED with its own specific flag, distinct from the flag above.

The catch-all label `VALID_INPUT_COMBINATION_NOT_SETTLED` is removed. `MISSING_INPUT_UNSCORED` now means only genuinely missing, duplicate, non-numeric, or negative inputs.

The reason for the third branch is settled: an increase in common-share par capital with no cash proceeds is consistent with a stock dividend, bonus issue, or split, which raises no external capital and must not be penalised as an issuance; no corporate-action source is assumed or asserted. `common_shares` is balance-sheet common-share par capital denominated in VND, not a share count. Its year-over-year comparison remains valid because par capital changes only when the share count changes, and it must never be used as a share count anywhere.

For every ticker scored 0 by the fourth branch, write the diagnostic-only column `issue_proceeds_to_common_shares_ratio = proceeds_from_issue_of_shares_N / common_shares_N`. This column must NEVER gate, threshold, or alter any score.

The audit also records the N-1 signal using N-1 and N-2 so the two-year input history is explicit; criterion 7 itself is evaluated only for year N. Paid-in capital, charter capital, market-cap shares, and a fabricated zero are forbidden substitutes.

### 2.3 SETTLED — missing-data and score-display rule

- A missing input makes only the affected criterion `UNSCORED`, with the exact missing/duplicate/non-numeric/invalid-denominator flag.
- `UNSCORED` is never silently scored `0`; no value or zero may be fabricated.
- Report `F_SCORE_POINTS`, `F_SCORE_CRITERIA_SCORED`, and `F_SCORE_CRITERIA_UNSCORED` together, for example `6 points / 8 criteria scored / 1 UNSCORED`.
- The raw points remain the sum of scored binary criteria and are never rescaled to `0-9`.
- **SETTLED for ranking:** use `F_SCORE_POINTS / F_SCORE_CRITERIA_SCORED` only to form the F-Score component percentile, while preserving the raw points and denominator next to it. A zero scored denominator produces no percentile.
- A named constant `MIN_SCORED_CRITERIA = 7` is defined in exactly one place in the F-Score build script. A row whose `F_SCORE_CRITERIA_SCORED` is below that constant keeps its raw points and its ratio visible but is marked `LOW_CONFIDENCE_SCORED_DENOMINATOR` and is not eligible for the later quality ranking. It is a confidence flag, never an exclusion from the output.

## 3. SETTLED — Franchise Power definition

Franchise Power has two equal components: long-term average ROC and margin stability. It uses the maximum locally available point-in-time annual history per ticker and records `years_used` and the exact year labels.

Extended history is restated data usable for ranking today, not evidence of what was published at the time. See `docs/SPRINT_6_RESTATEMENT_DIFF.md`. It does not make Sprint 8 backtests point-in-time clean.

### 3.1 Settled ROC

For each usable year t:

```text
EBIT_PROXY_VAS_t =
    net_accounting_profit_loss_before_tax_t
    + abs(interest_expenses_t)

INVESTED_CAPITAL_t =
    owners_equity_t
    + short_term_borrowings_t
    + long_term_borrowings_t
    - cash_and_cash_equivalents_t

ROC_t =
    EBIT_PROXY_VAS_t
    / average(INVESTED_CAPITAL_t, INVESTED_CAPITAL_t-1)
```

All normalized inputs must be explicit and usable. A non-positive average invested-capital denominator makes that year unavailable. The long-term ROC component is the plain arithmetic mean of usable `ROC_t` observations; no winsorization or custom time weight is authorized in this spec.

### 3.2 Settled margin stability

For each usable year:

```text
gross_margin_t = gross_profit_t / net_sales_t
```

Margin instability is the population standard deviation of the usable annual gross margins; lower standard deviation ranks as higher stability. The explicit `gross_profit` field is preferred, with only the controlled proposed COGS fallback in section 2.1. No missing year is filled.

### 3.3 Settled minimum history, justified by the local audit

The approved minimum is defined in exactly one place: the named `PROPOSED_FRANCHISE_MIN_YEARS` constant in `scripts/audit_sprint6_readiness.py`. `docs/SPRINT_6_DATA_READINESS.md` records the measured extended-history distribution and the READY/INSUFFICIENT_HISTORY result produced from that constant. The measured result supports the new minimum while keeping short-history rows visible rather than excluding them.

Pandemic years 2020 and 2021 are retained and must not be excluded, because the franchise measure exists to test resilience through a shock and dropping stress years biases the measure upward.

A ticker below `PROPOSED_FRANCHISE_MIN_YEARS` remains in the all-survivor quality output with `INSUFFICIENT_HISTORY`. This is a low-confidence flag, not an exclusion; `years_used` and the available year labels remain visible.

## 4. SETTLED — composite quality and percentiles

The production composite, if approved, is the plain arithmetic mean of these component percentiles:

1. F-Score completion-ratio percentile from section 2.3;
2. long-term average ROC percentile, higher ROC better;
3. margin-stability percentile, lower population standard deviation better.

There are no custom weights. Each component has weight `1 / number_of_available_component_percentiles`. A missing component is not zero; it shrinks the reported denominator and raises a low-confidence flag. Every percentile is formed across all eligible Sprint 4 survivors. The resulting composite is then ranked separately within the EBIT/TEV candidate list and within the E/P candidate list. No value metric enters this mean.

## 5. Settled interest-anomaly gate

`docs/SPRINT_6_INTEREST_ANOMALY_INVESTIGATION.md` assigns exactly one local-evidence label to each of the `44` Sprint 5 anomaly rows across `36` tickers:

- `NET_PRESENTATION_SUSPECTED`: `40`;
- `PROVIDER_FIELD_SUSPECTED`: `0`;
- `UNEXPLAINED`: `4`.

The four `UNEXPLAINED` rows are `GMD 2025Q4`, `SAB 2025Q4`, `DTD 2025Q2`, and `LHC 2025Q2`. These statements are local-cache findings only, not external accounting assertions.

Any future formula consuming `financial_expenses` is blocked for a ticker-quarter still labelled `UNEXPLAINED`. The proposed Franchise Power ROC does not consume `financial_expenses`; it uses the settled Sprint 5 `abs(interest_expenses)` definition.

## 6. SETTLED — explicit dispositions

### 6.1 SETTLED — NTC

NTC may receive an F-Score because the local annual audit has all nine criterion input sets available, `complete_fscore_inputs_both_years=True`, and records its measured extended `franchise_years_used`. Its incomplete Sprint 5 TTM value window is unrelated to annual F-Score availability. Carry `SPRINT5_TTM_INCOMPLETE` as a visible cross-step flag; NTC cannot enter a Sprint 6 candidate-list rank unless it is already present in that unchanged Sprint 5 candidate list.

### 6.2 SETTLED — TRC

TRC may receive an F-Score because the local annual audit has all nine criterion input sets available, `complete_fscore_inputs_both_years=True`, and records its measured extended `franchise_years_used`. Carry `SPRINT5_TTM_INCOMPLETE` as a visible cross-step flag. Its annual quality evidence does not repair or replace the missing Sprint 5 TTM value evidence.

### 6.3 SETTLED — DBC

DBC may receive an F-Score because its annual balance-sheet, income-statement, and cash-flow datasets are locally present for the required years; the audit has all nine criterion input sets available, `complete_fscore_inputs_both_years=True`, and records its measured extended `franchise_years_used`. Carry `SPRINT5_QUARTERLY_BALANCE_MISSING_TEV_MISSING` as a visible cross-step flag. Annual quality availability must not fabricate the missing quarterly TEV or add DBC to the EBIT/TEV candidate list.

## 7. Readiness-audit contract

`scripts/audit_sprint6_readiness.py` must:

- read only the `156` merged Sprint 4 survivors and existing local annual normalized fundamentals;
- make no external API or network call and fetch no new data;
- enforce `available_from <= 2026-07-20`;
- reuse the stored Sprint 4 annual N/N-1 pair where valid and record any fallback;
- write exactly one row per survivor to `data/screener/sprint6_readiness_audit.csv`;
- expose file existence, row eligibility, and every individual input-availability flag for N and N-1, plus required N-2 denominators/signals;
- record annual history depth, Franchise Power `years_used`, exact year labels, and `INSUFFICIENT_HISTORY` without exclusion;
- write exact aggregate counts plus explicit NTC, TRC, and DBC rows to `docs/SPRINT_6_DATA_READINESS.md`;
- report an entirely absent input class as a build-phase prerequisite rather than fetching it;
- compute no F-Score criterion result, F-Score, ROC, margin stability, percentile, composite quality, or production rank.

The audit answers the cash-flow existence question first: a local annual normalized cash-flow dataset exists and contains eligible rows for `156/156` survivors. Proposed CFO_N and CFO_N-1 fields are each available for `156/156`. Complete proposed F-Score inputs for both years are available for `156/156`; this is readiness evidence, not authorization to calculate scores.

## 8. Build gate

The owner approved sections 2.1, 2.3, 3, 4, and 6 on 2026-07-20. Production F-Score is authorized from that date. Franchise Power, ROC, margin stability, component percentiles, composite quality, and candidate-list quality ranking are approved in principle but deliberately deferred to a separate later build task and must not be computed here.

This PR is restricted to specification text, the local readiness audit, the local anomaly investigation, their fixture tests, the Sprint 5 status closure, and one changelog entry. It authorizes no Sprint 7+ work, no momentum, no portfolio construction, no sector cap, no threshold/configuration change, no new dependency, no external fetch, and no modification of any Sprint 4 or Sprint 5 output.
