# SPEC Sprint 4 — Step 1: CLEANING (remove fraud & distress risk)

This file is the local source of truth for Sprint 4. It is derived verbatim from `PLAN_quant_screener_myn.md` (section "SPRINT 4 — Bước 1: LÀM SẠCH" and the verified-coefficients block) and follows the section structure of `docs/SPEC_SPRINT_3.md`. Sprint 4 turns the 378-ticker ACCEPTED universe from Sprint 3 into a *clean* universe where every removed ticker carries a labelled reason. Correctness, verbatim formulas, and honest failure reporting take priority over coverage or speed. No valuation, ranking, or portfolio construction happens here.


## Scope

Sprint 4 is limited to the following work:

- Add `src/screener/step1_cleaning.py` and `config/screener.yaml` cleaning thresholds (all cutoffs live in config, never hard-coded).
- Consume the Sprint 3 point-in-time normalized fundamentals and the 378-ticker ACCEPTED universe. Do NOT change the Sprint 3 data-layer, dedup, parser, normalization, or threshold code. EXCEPTION (see Step 0): Sprint 3 cached only QUARTERLY statements; the ANNUAL statements that STA/SNOA/M-Score require were never fetched, so Sprint 4 begins by fetching the annual period type through the UNCHANGED existing client. "No re-fetch" forbids re-pulling or altering the quarterly layer — it does NOT forbid fetching the annual period Sprint 4 needs.
- Apply five cleaning filters in a fixed order, each producing a labelled reject reason.
- Emit `data/screener/step1_survivors.csv` and extend `universe_rejects.csv` with the new labels.
- Every formula ships with a unit test whose expected numbers were computed by hand.

Sprint 4 does NOT: compute EBIT/TEV or E/P (Sprint 5), compute F-Score or Franchise Power (Sprint 6), rank or weight anything, or change any Sprint 3 config value.

## Step 0 — Annual fundamentals fetch (prerequisite, do this FIRST)

STA, SNOA, and all eight Beneish M-Score indices are ANNUAL constructs requiring two consecutive annual periods (N and N−1). The Sprint 3 coverage run cached quarterly statements only — annual was never fetched — so without this step every accrual and M-Score value would be INSUFFICIENT_DATA. Before any filter code:

- Fetch annual balance sheet, income statement, and cash flow for the non-financial ACCEPTED universe (~315 tickers) using the EXISTING `finance_client` with `period='year'`. Do NOT modify the client, parser, dedup, normalization, or any Sprint-3 threshold. A thin new run script that only CALLS the unchanged client is allowed; changing the client is not.
- The API returns the 4 most recent annual periods (~2022–2025). Cache them in the same layout Sprint 3 uses, with the same point-in-time stamp `available_from = period_end + LAG_ANNUAL (90 days)`.
- Point-in-time selection for the filters: use the two most-recent annual periods whose `available_from <= evaluation date` as N and N−1 (a mid-2026 run → N = 2025 annual, available_from 2026-03-31; N−1 = 2024).
- Going forward, every fundamentals fetch/snapshot must cover BOTH quarterly and annual period types so this gap does not recur.
- Restatement caveat: vnstock annual data is restated. Using the latest published annual pair for a live screen today is acceptable; it is NOT a clean basis for historical backtest (already recorded for Sprint 8).
- Output `docs/COVERAGE_SPRINT_4_ANNUAL.md`: per non-financial ACCEPTED ticker, how many consecutive annual periods are available and whether the specific items each formula needs (STA, SNOA, each M-Score index) are present for N and N−1. List every ticker that would fall to INSUFFICIENT_DATA_FOR_<FORMULA> and the missing item. Mirror the Sprint 3 quarterly coverage report structure.

Gate: STOP after Step 0 and report annual coverage. The five-filter code proceeds only after the owner reviews this coverage. If a large share of tickers lack two consecutive annual periods, flag it before writing any filter logic.

## Filter order (fixed) and labels

Run filters in this exact order; a ticker exits at the first filter it fails and keeps that single reason label. Report the removal count and removal % of each filter separately.

1. `FINANCIAL_SECTOR_EXCLUDED` — ICB2 in banking, insurance, financial services / securities. EBIT/TEV, F-Score, and accruals are meaningless on bank/insurer statements. These are the 63 `FINANCIAL_RAW_FETCH_ONLY` tickers from Sprint 3 plus any other financial-ICB2 names. They stay in the sector monitor, out of the screener.
2. `UPCOM_EXCLUDED_V1` — exchange == UPCOM. Quarterly-disclosure obligations for UPCoM firms are looser than for listed firms (⚠️ re-check TT96 detail if later relaxing), missing quarters silently corrupt TTM EBIT, and all VN E/P evidence (Huang/Liu/Shu 2023) covers only HOSE+HNX. UPCoM names stay in the sector monitor.
3. `HIGH_ACCRUAL` — worst accruals percentile on STA and SNOA (default worst 10%, in config).
4. `M_SCORE_FLAG` — Beneish M-Score above threshold (default −1.78, in config).
5. `PFD_HIGH_RISK` — financial-distress screen (simple transparent filter is primary; full Campbell optional/parallel).

A ticker that survives all five is written to `step1_survivors.csv`.

## Accruals — verbatim formulas (Sloan 1996 STA, Hirshleifer 2004 SNOA)

Paste these directly; do NOT let the coder re-derive or "remember" a variant. Both are annual constructs — use annual point-in-time periods (N vs N−1), each row stamped with its Sprint-3 `available_from`.

**STA — Scaled Total Accruals (Sloan 1996), balance-sheet method:**

```
Accruals = (ΔCurrent Assets − ΔCash)
         − (ΔCurrent Liabilities − ΔShort-term Debt − ΔTaxes Payable)
         − Depreciation
STA      = Accruals / average Total Assets      (average of TA at N and N−1)
```
Δ means value at N minus value at N−1. Historical US low-minus-high decile spread ≈ 10.4%/yr in the first year. Higher STA = lower earnings quality = worse.

Item map (Sprint-3 whitelist): ΔCurrent Assets=`current_assets`, ΔCash=`cash_and_cash_equivalents`, ΔCurrent Liabilities=`current_liabilities`, ΔShort-term Debt=`short_term_borrowings`, ΔTaxes Payable=`taxes_and_other_payable_to_state_budget` (⚠️ broader than Sloan's US "taxes payable" — accepted approximation, already caveated in Sprint 3), Depreciation=`depreciation_and_amortization` (cash-flow), Total Assets=`total_assets`.

**SNOA — Scaled Net Operating Assets (Hirshleifer et al. 2004), VAS-adjusted:**

```
Operating Assets      = Total Assets − Cash & short-term investments
Operating Liabilities = Total Assets − Short-term Debt − Long-term Debt − Owners' Equity
NOA                   = Operating Assets − Operating Liabilities
= Short-term Debt + Long-term Debt + Owners' Equity − Cash & short-term investments
SNOA                  = NOA / beginning Total Assets      (Total Assets at N−1)
```

Item map: Cash & short-term investments = `cash_and_cash_equivalents` + `short_term_investments`; Short-term Debt = `short_term_borrowings`; Long-term Debt = `long_term_borrowings`; Owners' Equity = `owners_equity` (VAS balance-sheet code 400). Higher SNOA = balance-sheet bloat = worse.

> ⚠️ **VAS ADJUSTMENT — do NOT re-introduce a separate Minority Interest / Preferred Stock subtraction.** Under Vietnamese VAS (Circular 200), `owners_equity` (code 400) ALREADY INCLUDES minority interest (`minority_interests`, code 429) and preferred capital, and the sheet balances as `Total Assets = Short-term Liabilities + Long-term Liabilities + owners_equity` (hand-checked VNM 2024: 18,459.55 + 415.11 + 36,174.40 = 55,049.06 = Total Assets). The original US Hirshleifer formula subtracts Minority Interest and Preferred Stock as SEPARATE financing claims because US GAAP presents common equity WITHOUT them. Subtracting them here would remove minority/preferred TWICE (double-count), inflating SNOA by ≈ (minority + preferred) / beginning Total Assets — for VNM ≈ +0.07, enough to mis-flag `HIGH_ACCRUAL`; worst for holding/conglomerate structures. `minority_interests` and `preferred_shares` MUST NOT appear anywhere in the SNOA computation.

## Beneish M-Score — verbatim (original 1999 unweighted probit)

```
M = −4.840 + 0.920·DSRI + 0.528·GMI + 0.404·AQI + 0.892·SGI
    + 0.115·DEPI − 0.172·SGAI + 4.679·TATA − 0.327·LVGI
```

Eight indices, each a ratio of year N to year N−1 unless noted:

- **DSRI** (Days Sales in Receivables) = (Receivables_N / Sales_N) / (Receivables_{N−1} / Sales_{N−1}). Receivables = `accounts_receivable` — confirmed to be the AGGREGATE short-term receivables line (VAS 130), which already rolls up trade receivables and construction-progress receivables, so DSRI does NOT undercount for construction/contractor firms. Sales = `net_sales`.
- **GMI** (Gross Margin Index) = GrossMargin_{N−1} / GrossMargin_N, where GrossMargin = `gross_profit` / `net_sales`.
- **AQI** (Asset Quality Index) = AQ_N / AQ_{N−1}, where AQ = 1 − (Current Assets + Net PP&E) / Total Assets. Net PP&E = `tangible_fixed_assets` — FROZEN. This is the same line the project already uses for DEPI (decision #8), so both M-Score PP&E inputs stay consistent. Do NOT substitute `fixed_assets`; the coder has no choice here.
- **SGI** (Sales Growth Index) = Sales_N / Sales_{N−1}.
- **DEPI** (Depreciation Index) = DepRate_{N−1} / DepRate_N, where DepRate = Depreciation / (Depreciation + Net PP&E). Depreciation = `depreciation_and_amortization`.
- **SGAI** (SG&A Index) = (SGA_N / Sales_N) / (SGA_{N−1} / Sales_{N−1}), SGA = `selling_expenses` + `general_and_admin_expenses`.
- **LVGI** (Leverage Index) = Leverage_N / Leverage_{N−1}, Leverage = (Current Liabilities + Long-term Liabilities) / Total Assets. Use `current_liabilities` + `long_term_liabilities`.
- **TATA** (Total Accruals to Total Assets) = (Income from continuing operations − Cash from operations) / Total Assets. FROZEN inputs: Income from continuing operations = `net_profit_loss_after_tax` (total after-tax profit of the whole company, BEFORE the minority-interest split — the standard Beneish "income from continuing operations"); Cash from operations = `net_cash_inflows_outflows_from_operating_activities`; Total Assets = `total_assets`. Do NOT substitute a pre-tax line or `attributable_to_parent_company`. Mandatory VNM hand-check against cafef/vietstock before this index is accepted.

Threshold: **M > −1.78 ⇒ flag** (probability 3.76%, tuned for a 20:1–30:1 error-cost ratio). Keep −1.78 as the default but ALSO log each ticker's M-Score percentile within the VN universe so a later walk-forward (Sprint 8) can retune. When documenting results, describe the model honestly: holdout catches ≈50% of manipulators before public detection at 7.2% false positives — a coarse screen, not a precise fraud detector. (The "76%" in the old handoff is NOT the holdout figure; use 50% / 7.2%.)

## Financial distress — PFD

Primary (ship this): a simple, transparent filter → `PFD_HIGH_RISK` if ANY of: accumulated losses (`undistributed_earnings` < 0) OR negative owners' equity (`owners_equity` < 0) OR (if obtainable) HOSE warning/control-list membership. These three signals need NO threshold.

The net-debt-to-EBITDA sub-signal is BLOCKED for v1: `PLAN_quant_screener_myn.md` has no owner-approved cap, so per the no-invention rule it is deferred until the owner sets `NET_DEBT_EBITDA_CAP` explicitly. Do NOT invent a cap and do NOT flag on net-debt/EBITDA until that value exists. The distress filter ships and works on the three threshold-free signals alone.

Optional / parallel experimental only: the full Campbell (2006) logit. Coefficients are already verified — paste, do NOT let the coder invent them:

```
const −9.164; NIMTAAVG −20.264; TLMTA 1.416; EXRETAVG −7.129;
SIGMA 1.411; RSIZE −0.045; CASHMTA −2.132; MB 0.075; PRICE −0.058
```
The three variables PRICE (capped at $15), RSIZE and EXRETAVG (both benchmarked to a US index) are US-market-specific — replace with a VN-universe percentile or drop the variable, and document clearly that this is a re-calibrated model, NOT original Campbell. If Campbell cannot be transferred cleanly, the simple filter alone is sufficient for Sprint 4.

## Sector handling (DECIDED)

Per project decision #12: value+quality ranking stays whole-universe (Sprint 5–6); portfolio-level sector caps come later (Sprint 7). For the Sprint-4 accruals + M-Score flags, #12 allowed either full sector-neutralization or at-minimum logging sector. This is now decided using the real ICB2 distribution of the 315 non-financial ACCEPTED tickers (16 groups, not 19):

- 4 large groups hold 59% of names (Xây dựng 59, BĐS 57, Thực phẩm 37, Công nghiệp 33) and could support a per-sector 10% cut.
- 7 of 16 groups have < 10 names. Viễn thông has only 2 (worst-10% = 0.2 → rounding to 1 cuts 50% of the group); CNTT / Truyền thông / Du lịch have 6 each (cut 1 = 16.7%). A per-sector cut therefore applies an effective rate ranging 10.2%–50% across groups — not a real 10% filter. Full sector-neutralization is rejected as the operative filter for this reason.

Operative rule: compute HIGH_ACCRUAL and M_SCORE_FLAG percentile cutoffs on the WHOLE non-financial universe. Config `SECTOR_MODE: whole_universe_log`.

Diagnostics REQUIRED in the same run (this is how the bias question is answered empirically, not assumed):

1. `docs/DIAG_SECTOR_A_REJECT_MIX_SPRINT_4.csv` — for the whole-universe rejects, the ICB2 composition of the reject set vs each ICB2's weight in the universe. If any ICB2's share of rejects exceeds ~2× its universe weight, flag it as possible sector-baseline bias for owner review (do NOT auto-correct).
2. `docs/DIAG_SECTOR_B_WHATIF_SPRINT_4.csv` — what a per-sector (option B) cut WOULD flag instead, plus each group's size and effective cut rate, so the thin-bucket instability is visible in numbers.

Additionally log each survivor/reject row with its ICB2 and its within-sector accrual/M-Score percentile. Full sector-neutralization stays a candidate for walk-forward (Sprint 8), decided later on this diagnostic evidence.

## Per-line data sufficiency (the ODE case)

Motivated by ODE (Sprint 3: balance sheet + income statement present, cash flow missing). Do NOT blanket-fail a ticker that is missing one statement. Instead, each formula declares the items/statements it needs; if a ticker lacks an input for formula X, label that formula `INSUFFICIENT_DATA_FOR_<FORMULA>` for that ticker only and still evaluate the other filters. A ticker excluded upstream (e.g. ODE is UPCoM → `UPCOM_EXCLUDED_V1`) never reaches the formula stage, but the per-line rule must be in place for non-excluded tickers that are missing cash-flow-derived inputs (Depreciation for STA/DEPI, CFO for TATA).

## Point-in-time discipline (reuse Sprint 3, do not re-open)

Every value used in a Δ or ratio must come from a row whose `available_from` (= period_end + LAG 30/60/90) is on/before the evaluation date. N and N−1 are consecutive annual point-in-time periods. Reuse Sprint 3's parser and audit; add no new lag logic.

## Config keys (new, in config/screener.yaml — additive only)

`ACCRUAL_WORST_PCT: 0.10`, `MSCORE_THRESHOLD: -1.78`, `SECTOR_MODE: whole_universe_log`. `NET_DEBT_EBITDA_CAP` is intentionally ABSENT (blocked — the owner will set it later); the net-debt/EBITDA distress sub-signal stays disabled until it is added. Every threshold here is either a concrete value or explicitly blocked — none are left as empty fill-in placeholders. Do NOT touch the four existing Sprint-3 thresholds.

## Required output schema

`data/screener/step1_survivors.csv`: ticker, exchange, icb2, plus each raw metric (STA, SNOA, M_score, and its 8 sub-indices, distress inputs) and its within-sector percentile. `universe_rejects.csv` extended: ticker, filter_stage, reason_label, the metric value that triggered it, and ICB2.

## Required local checks

- One unit test per formula (STA, SNOA, each of the 8 M-Score indices, M-Score total, distress) with hand-computed expected values, using one large liquid name (e.g. VNM) cross-checked by hand against vietstock/cafef BCTC.
- SNOA double-count guard: the SNOA unit test MUST prove the result is INDEPENDENT of `minority_interests` and `preferred_shares`. Compute SNOA for the VNM fixture, then set BOTH fields to arbitrary large garbage values, recompute, and assert SNOA is byte-for-byte unchanged. This regression fails the moment any future edit re-subtracts minority/preferred (the VAS double-count bug). Also assert the algebraic identity NOA == short_term_borrowings + long_term_borrowings + owners_equity − (cash_and_cash_equivalents + short_term_investments).
- A unit-consistency test (đồng vs nghìn vs tỷ): wrong units make accruals/M-Score silently meaningless.
- A guard test: if any single filter removes > 30% of the universe, the run flags "suspected formula/unit bug — stop and hand-check 5 tickers."
- pytest green; no Sprint-3 test modified or skipped.

## Definition of Done

Each filter's removal count and % printed to a report; every formula has a passing hand-computed unit test; survivors + labelled rejects written; both sector-diagnostic CSVs (`DIAG_SECTOR_A_REJECT_MIX`, `DIAG_SECTOR_B_WHATIF`) written; no Sprint-3 config/threshold/code touched; PR opened, NOT merged; stop for owner + mentor review.

## Must NOT include

No valuation/ranking/weighting; no coefficient invention (M-Score and Campbell numbers are fixed constants from PLAN); no threshold tuning "for nicer numbers"; no changes to Sprint-3 dedup, cache, or thresholds; no re-fetch of the data layer.

## Carry-forward caveats (⚠️/❓)

- ⚠️ `taxes_and_other_payable_to_state_budget` broader than Sloan's US taxes-payable — accepted approximation.
- ⚠️ EBIT = pre-tax profit + interest; DEPI/AQI PP&E line and TATA earnings line must be pinned by the coder and unit-tested (repo item naming: `fixed_assets` vs `tangible_fixed_assets`).
- ⚠️ M-Score −1.78 and accrual 10% cut are US-calibrated hypotheses → log VN percentiles for later walk-forward, do not treat as sacred.
- ⚠️ Campbell PRICE/RSIZE/EXRET are US-specific → re-calibrate or drop; simple distress filter is the shippable primary.
- ✅ Resolved: `accounts_receivable` is the aggregate VAS-130 line, so DSRI does not undercount construction-progress receivables.
