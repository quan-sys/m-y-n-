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

### 2.1 PROPOSED — normalized VAS input map (owner approval required)

| Economic input | Proposed normalized field | Proposed treatment and reason |
|---|---|---|
| net income | `net_profit_loss_after_tax` | Use consolidated after-tax profit because the denominator is consolidated `total_assets`. `attributable_to_parent_company` excludes non-controlling profit while the proposed asset denominator does not exclude the related assets, so it is not the proposed F-Score numerator. This differs intentionally from Sprint 5 E/P, whose numerator matches parent equity market capitalization. |
| CFO | `net_cash_inflows_outflows_from_operating_activities` | Use the explicit annual operating-cash-flow subtotal; do not reconstruct CFO from working-capital lines. |
| total assets | `total_assets` | Use the explicit year-end consolidated value for N, N-1, and N-2 as required. |
| long-term debt | `long_term_borrowings` | Use interest-bearing long-term borrowings; do not substitute total long-term liabilities. |
| current assets | `current_assets` | Use the explicit year-end subtotal. |
| current liabilities | `current_liabilities` | Use the explicit year-end subtotal. A zero or non-positive denominator blocks the criterion rather than producing a ratio. |
| revenue | `net_sales` | Use net sales consistently for gross margin and asset turnover; do not mix with gross `sales`. |
| gross profit | `gross_profit` | Prefer the explicit normalized gross-profit subtotal. If it is missing, a later approved build may use `net_sales + cost_of_sales` only when `cost_of_sales` is an explicit usable non-positive expense and the sign contract is logged; otherwise the criterion is UNSCORED. |
| cost of goods sold diagnostic/fallback | `cost_of_sales` | It is not silently substituted. Its presence and sign must be recorded whenever the proposed fallback is used. |
| share-issuance cash signal | `proceeds_from_issue_of_shares` | Use the explicit annual cash-flow line for year N. |
| common-share balance signal | `common_shares` | Compare the explicit end-N and end-(N-1) values to catch non-cash/common-share increases that the proceeds line alone may miss. |

### 2.2 PROPOSED — criterion 7 detection (owner approval required)

Criterion 7 receives one point only when both local signals are explicit and usable, `proceeds_from_issue_of_shares_N == 0`, and `common_shares_N <= common_shares_N-1`.

- If issue proceeds are positive or common shares increased, the criterion receives `0`.
- A negative issue-proceeds value, duplicate row, missing value, non-numeric value, or missing comparison-year common-shares value makes the criterion `UNSCORED` and raises a specific flag.
- The audit also records the N-1 signal using N-1 and N-2 so the two-year input history is explicit; the settled F-Score criterion itself is evaluated only for year N.
- Paid-in capital, charter capital, market-cap shares, and a fabricated zero are forbidden substitutes.

### 2.3 PROPOSED — missing-data and score-display rule (owner approval required)

- A missing input makes only the affected criterion `UNSCORED`, with the exact missing/duplicate/non-numeric/invalid-denominator flag.
- `UNSCORED` is never silently scored `0`; no value or zero may be fabricated.
- Report `F_SCORE_POINTS`, `F_SCORE_CRITERIA_SCORED`, and `F_SCORE_CRITERIA_UNSCORED` together, for example `6 points / 8 criteria scored / 1 UNSCORED`.
- The raw points remain the sum of scored binary criteria and are never rescaled to `0-9`.
- **PROPOSED for ranking:** use `F_SCORE_POINTS / F_SCORE_CRITERIA_SCORED` only to form the F-Score component percentile, while preserving the raw points and denominator next to it. A zero scored denominator produces no percentile.

## 3. PROPOSED — Franchise Power definition (owner approval required)

Franchise Power has two equal components: long-term average ROC and margin stability. It uses the maximum locally available point-in-time annual history per ticker and records `years_used` and the exact year labels.

### 3.1 Proposed ROC

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

### 3.2 Proposed margin stability

For each usable year:

```text
gross_margin_t = gross_profit_t / net_sales_t
```

Margin instability is the population standard deviation of the usable annual gross margins; lower standard deviation ranks as higher stability. The explicit `gross_profit` field is preferred, with only the controlled proposed COGS fallback in section 2.1. No missing year is filled.

### 3.3 Proposed minimum history, justified by the local audit

The proposed minimum is `3` usable common ROC/margin years. `docs/SPRINT_6_DATA_READINESS.md` finds four annual report periods in the local comparable cache and, because ROC needs a prior invested-capital observation, an observed maximum of three usable common years. The audit result is exactly `156/156` tickers with `years_used=3`.

A ticker below `3` years remains in the all-survivor quality output with `INSUFFICIENT_HISTORY`. This is a low-confidence flag, not an exclusion; `years_used` and the available year labels remain visible.

## 4. PROPOSED — composite quality and percentiles (owner approval required)

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

## 6. PROPOSED — explicit dispositions (owner approval required)

### 6.1 PROPOSED — NTC

NTC may receive an F-Score because the local annual audit has all nine criterion input sets available, `complete_fscore_inputs_both_years=True`, and `franchise_years_used=3`. Its incomplete Sprint 5 TTM value window is unrelated to annual F-Score availability. Carry `SPRINT5_TTM_INCOMPLETE` as a visible cross-step flag; NTC cannot enter a Sprint 6 candidate-list rank unless it is already present in that unchanged Sprint 5 candidate list.

### 6.2 PROPOSED — TRC

TRC may receive an F-Score because the local annual audit has all nine criterion input sets available, `complete_fscore_inputs_both_years=True`, and `franchise_years_used=3`. Carry `SPRINT5_TTM_INCOMPLETE` as a visible cross-step flag. Its annual quality evidence does not repair or replace the missing Sprint 5 TTM value evidence.

### 6.3 PROPOSED — DBC

DBC may receive an F-Score because its annual balance-sheet, income-statement, and cash-flow datasets are locally present for the required years; the audit has all nine criterion input sets available, `complete_fscore_inputs_both_years=True`, and `franchise_years_used=3`. Carry `SPRINT5_QUARTERLY_BALANCE_MISSING_TEV_MISSING` as a visible cross-step flag. Annual quality availability must not fabricate the missing quarterly TEV or add DBC to the EBIT/TEV candidate list.

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

Production F-Score, Franchise Power, component percentile, composite quality, and candidate-list quality ranking are **FORBIDDEN** until the owner explicitly approves this specification, including every subsection marked `PROPOSED`.

This PR is restricted to specification text, the local readiness audit, the local anomaly investigation, their fixture tests, the Sprint 5 status closure, and one changelog entry. It authorizes no Sprint 7+ work, no momentum, no portfolio construction, no sector cap, no threshold/configuration change, no new dependency, no external fetch, and no modification of any Sprint 4 or Sprint 5 output.
