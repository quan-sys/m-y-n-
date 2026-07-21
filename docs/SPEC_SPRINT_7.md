# Sprint 7 Step 4 — signal + portfolio construction specification

Status: **SPECIFICATION AND READ-ONLY READINESS AUDIT ONLY. PRODUCING AN ACTUAL PORTFOLIO IS FORBIDDEN PENDING SEPARATE OWNER APPROVAL.**

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

Sector cap = 25 percent of holdings, measured on `icb2`, applied to each of the two portfolios independently. When adding the next-ranked eligible ticker would push its `icb2` group above 25 percent of the target holding count, that ticker is SKIPPED and the next eligible ticker is considered; the skipped ticker is recorded with reason `SECTOR_CAP_SKIPPED` and is not silently dropped from the report. The spec must state explicitly that on current data the cap is NOT binding at 20-25 holdings (deepest sector is 4 names), and that its purpose is future periods where one sector becomes cheap simultaneously.

### S4. SETTLED — Momentum default

Momentum stays OFF by default. Implement momentum 12-2 as a config flag defaulting to disabled, per `PLAN.md`: Huang/Liu/Shu (2023) measured momentum 12-2 as statistically insignificant in Vietnam 2007-2022. Momentum may only ever act as a final veto filter, never as a score component, and only if walk-forward on Vietnamese data in Sprint 8 justifies enabling it. Long-only.

### S5. SETTLED — Equal weight

Equal weight. Each holding gets 1/N of capital. No optimiser, no Markowitz, no risk parity, no conviction weighting (DeMiguel 2009).

### S6. SETTLED — Sequential contract

Sequential contract, not a blended score. Value selects the candidate pool (Sprint 5), quality ranks inside that pool by `composite_quality` (Sprint 6), momentum if enabled vetoes last. There is no single value+quality composite number anywhere in Sprint 7.

### S7. SETTLED — Sector cycle reporting only

Sector cycle overlay from the existing weekly sector report is REPORTING ONLY. It is printed as a column next to each holding and must never veto, reweight, or reorder anything.

## 3. Owner approval pending

### P1. PROPOSED — Exact holding count

Recommendation: use a fixed target of 20 holdings in each independent portfolio, with all tickers tied at the twentieth boundary ordered by the P2 rule. Trade-off: 20 names keep the portfolio understandable and diversified while accepting more single-name concentration than a 25-name portfolio.

### P2. PROPOSED — Deterministic quality tie-break

Recommendation: when eligible tickers have identical `composite_quality` to full float precision, order them by ticker in ascending Unicode code-point order. Trade-off: this is fully reproducible but intentionally economically neutral and therefore gives no preference to liquidity or market capitalisation.

### P3. PROPOSED — Liquidity rule

Recommendation: make position value configurable and cap it at `0.10 × adtv_20d` by default, while a missing, non-numeric, or zero `adtv_20d` makes the ticker ineligible with reason `MISSING_OR_ZERO_ADTV_20D`. Trade-off: a 10-percent one-day-volume cap limits market impact but may block otherwise attractive small and illiquid companies.

### P4. PROPOSED — Rebalance cadence and as-of convention

Recommendation: rebalance quarterly on the final exchange trading day of March, June, September, and December, using only records available on or before that date; the first specification/readiness snapshot remains as of `2026-07-20`. Trade-off: quarterly rebalancing reduces turnover and data noise but reacts more slowly to new value or quality information.

### P5. PROPOSED — Cross-flagged tickers

Recommendation: add no new portfolio-stage block for NTC, TRC, or DBC beyond the unchanged candidate-list membership, so NTC/TRC retain visible `SPRINT5_TTM_INCOMPLETE` flags and DBC remains blocked from any list whose valuation evidence is missing but may remain eligible in an independent list where Sprint 5 already admitted it. Trade-off: this preserves the rule that quality never fills a valuation hole without unnecessarily blocking a ticker from a different valuation list whose evidence is complete.

### P6. PROPOSED — Future output schema

Recommendation: future `reports/<date>/PORTFOLIO.md` and `portfolio.csv` outputs should contain `portfolio_id`, `as_of`, `ticker`, `exchange`, `icb2`, candidate-list membership and value metric/rank, `composite_quality` and its three component percentiles, `franchise_history_status`, quality rank, target weight, sector count/share and cap status, `adtv_20d`, liquidity cap/status, momentum-enabled and veto-status fields without making momentum a score, sector-cycle reporting label, every carried cross-step flag, source snapshot paths, prior-period membership, and explicit `ENTER`, `HOLD`, or `EXIT` reason. Trade-off: the wide schema costs storage and reading effort but makes every future holding traceable through universe, value, quality, and portfolio construction.

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
