# Sprint 7 Step 4 — signal + portfolio construction specification

Status: **THE OWNER APPROVED THE PRODUCTION BUILD ON 2026-07-21 FOR EXACTLY THE TWO SNAPSHOT PORTFOLIOS NAMED IN S13. ANY FURTHER AUTOMATION, WEEKLY WIRING, BACKTEST, OR WINNER SELECTION REMAINS FORBIDDEN.**

Readiness-audit evaluation date: `2026-07-20`.

## 1. Scope

- This task specifies the future signal and portfolio-construction contract and audits existing local inputs only.
- No portfolio, position, momentum value, backtest, walk-forward result, or winner selection is produced.
- The two Sprint 5 candidate lists remain unchanged and independent.

## 2. SETTLED — owner decisions of 2026-07-21

### S1. SETTLED — Two parallel portfolios

Two parallel portfolios. Sprint 7 builds one portfolio from `data/screener/step2_candidates_ebit_tev.csv` and a second, fully independent portfolio from `data/screener/step2_candidates_ep.csv`. There is no merge, no intersection, and no winner metric. Winner selection belongs to Sprint 8. Outputs are two separate files; neither list is privileged.

### S2. SETTLED — INSUFFICIENT_HISTORY hard block

INSUFFICIENT_HISTORY is a hard portfolio block. Any ticker whose `franchise_history_status` in `data/screener/sprint6_franchise_quality.csv` is not `READY` is INELIGIBLE for portfolio membership. The seven currently affected tickers are MZG, TSA, VVS, RYG, VPL, DVM, PPT. They remain visible in ranking tables and reports with their composite score and their status, but they can never be selected, never be a replacement, and never be a reserve. The reason is recorded in the spec: their composite quality rests on 3-4 years of history against a 5-year minimum, so their score is not comparable in confidence to the 149 READY tickers, and a 20-25 slot portfolio has no room for a lower-confidence score. VVS specifically ranked 14/45 on EBIT/TEV and 13/44 on E/P with composite 0.6849 on 3 years; this rank does not override the block.

### S3. SETTLED — Sector cap

Sector cap = 25 percent of holdings, measured on `icb2`, applied to each of the two portfolios independently. When adding the next-ranked eligible ticker would push its `icb2` group above 25 percent of the target holding count, that ticker is SKIPPED and the next eligible ticker is considered; the skipped ticker is recorded with reason `SECTOR_CAP_SKIPPED` and is not silently dropped from the report. On the 2026-07-20 data the 25 percent cap is not binding at 20 or 25 holdings because the deepest `icb2` group holds 4 names; the cap exists for future periods in which one sector becomes cheap simultaneously.

### S4. SETTLED — Momentum default

Momentum stays OFF by default. Implement momentum 12-2 as a config flag defaulting to disabled, per `PLAN.md`: Huang/Liu/Shu (2023) measured momentum 12-2 as statistically insignificant in Vietnam 2007-2022. Momentum may only ever act as a final veto filter, never as a score component, and only if walk-forward on Vietnamese data in Sprint 8 justifies enabling it. Long-only.

### S5. SETTLED — Equal weight

Equal weight. Each holding gets 1/N of capital. No optimiser, no Markowitz, no risk parity, no conviction weighting (DeMiguel 2009).

### S6. SETTLED — Sequential contract

Sequential contract, not a blended score. Value selects the candidate pool (Sprint 5), quality ranks inside that pool by `composite_quality` (Sprint 6), momentum if enabled vetoes last. There is no single value+quality composite number anywhere in Sprint 7.

### S7. SETTLED — Sector cycle reporting only

Sector cycle overlay from the existing weekly sector report is REPORTING ONLY. It is printed as a column next to each holding and must never veto, reweight, or reorder anything.

## 3. SETTLED — owner decisions of 2026-07-21 (round 2)

### S8. SETTLED — holding count

Each of the two portfolios holds exactly 20 names. The pool is 44 and 43 eligible tickers respectively, so 20 names keeps the selection meaningfully tighter than half the pool while remaining inside the 20-25 range in `PLAN.md`.

### S9. SETTLED — tie-break

When eligible tickers have identical `composite_quality` to full float precision, order them by ticker in ascending Unicode code-point order. This is reproducible and intentionally economically neutral.

### S10. SETTLED — liquidity rule, PLAN wins over the earlier proposal

The value of one position must not exceed `LIQUIDITY_ADTV_DAYS` days of that ticker's `adtv_20d`, with `LIQUIDITY_ADTV_DAYS = 5` per `PLAN.md`; the earlier proposal of `0.10 x adtv_20d` is REJECTED and must not appear anywhere in the repo. Position value is computed as `PORTFOLIO_CAPITAL_VND / 20` under equal weight, with `PORTFOLIO_CAPITAL_VND = 1000000000` as the default. Both constants live in `config/screener.yaml` and neither may be hard-coded in a script. A ticker whose position value would exceed `LIQUIDITY_ADTV_DAYS x adtv_20d` is skipped with reason `LIQUIDITY_CAP_SKIPPED` and the next eligible ticker is considered. A missing, non-numeric, or zero `adtv_20d` makes the ticker ineligible with reason `MISSING_OR_ZERO_ADTV_20D`. `adtv_20d` is a VND trading-value figure sourced from `universe.csv` (`adtv_close_x_volume_x1000_proxy`); do not rescale it and do not multiply it by 1000 again.

### S11. SETTLED — rebalance cadence and as-of convention

Rebalance quarterly on the final exchange trading day of March, June, September, and December, using only records available on or before that date. This first production snapshot uses the Sprint 6 evaluation date `2026-07-20` and is an off-cycle snapshot, not a rebalance.

### S12. SETTLED — cross-flagged tickers

No new portfolio-stage block is added for NTC, TRC, or DBC. Their candidate-list membership from Sprint 5 is unchanged and decides everything: NTC and TRC are in neither candidate list and therefore cannot appear; DBC is in the E/P list only and remains eligible there while remaining absent from the EBIT/TEV list. Quality never fills a valuation hole, and a ticker is never imported into a list it did not qualify for.

### S13. SETTLED — output schema and file names

Each portfolio row carries: `portfolio_id`, `as_of`, `ticker`, `exchange`, `icb2`, candidate-list membership with its value metric and value rank, `composite_quality` with its three component percentiles, `franchise_history_status`, quality rank, `target_weight`, sector count and sector share with cap status, `adtv_20d`, liquidity headroom and liquidity status, `momentum_enabled` and `momentum_veto_status`, sector-cycle reporting label, every carried cross-step flag, source snapshot paths, and an `ENTER` / `HOLD` / `EXIT` reason column. Because Sprint 7 keeps two parallel portfolios, the single `PORTFOLIO.md` / `portfolio.csv` naming in `PLAN.md` is extended to `reports/2026-07-20/PORTFOLIO_EBIT_TEV.md`, `reports/2026-07-20/PORTFOLIO_EP.md`, `reports/2026-07-20/portfolio_ebit_tev.csv`, and `reports/2026-07-20/portfolio_ep.csv`. No other new step or file name may be invented.

## 4. Carry-forward flags — OUT OF SCOPE for Sprint 7

These items remain open and are deferred to Sprint 8; this task does not attempt to fix them:

- HQC FY2024 non-positive `net_sales` inflating F-Score criterion 9 (diagnostic column `non_positive_revenue_n_minus_1`).
- 28 tickers with criterion 7 UNSCORED (`SHARE_INCREASE_NO_CASH_SUSPECTED`), corporate actions unverified.
- 20 tickers scored 0 by criterion 7 branch four, including VNM at ratio 0.000345; materiality threshold undecided.
- ROC arithmetic vs geometric mean; M-Score -1.78 and accrual 10 percent are US parameters lacking a Vietnamese percentile.
- 4 UNEXPLAINED interest-sign rows (GMD 2025Q4, SAB 2025Q4, DTD 2025Q2, LHC 2025Q2): any formula using `financial_expenses` remains locked for those ticker-quarters.
- `NET_DEBT_EBITDA_CAP` remains BLOCKED.
- Restatement: all 2018-2025 annual data is restated, not point-in-time clean; Sprint 8 backtest must not assume otherwise.

## 5. Read-only readiness-audit contract

- Read only the two existing Sprint 5 candidate lists, Sprint 6 Franchise Quality, and Sprint 4 survivors under `data/screener/`.
- Write only `data/screener/sprint7_readiness_audit.csv`.
- Keep all non-READY rows visible as blocked evidence and never create a portfolio or reserve list.
- Report the eligible-pool arithmetic, quality completeness, sector concentration at cuts 15/20/25, exact quality ties in the top 30, and missing or zero liquidity inputs.
- Make no network call, add no dependency, compute no momentum value, and modify no existing data file.

## 6. Build gate

An owner-approved later build task is required before any portfolio output, portfolio builder, signal computation, rebalance, weighting, or selection may be produced.
