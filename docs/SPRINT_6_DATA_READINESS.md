# Sprint 6 local data-readiness audit

- Evaluation date: `2026-07-20`.
- Survivor rows: `156`; unique tickers: `156`.
- Network/API calls: `0`; production F-Scores: `0`; production Franchise Power scores: `0`; production composite-quality scores: `0`.

## 1. Cash-flow dataset existence — answered first

**YES.** A local normalized annual cash-flow file exists for `156/156` survivors; `156/156` contain at least one annual row available by the evaluation date.
The proposed CFO field `net_cash_inflows_outflows_from_operating_activities` is available for year N in `156/156` rows and year N-1 in `156/156` rows.

## 2. Exact input availability counts

| availability flag | available | missing |
|---|---:|---:|
| `net_income_n_available` | 156 | 0 |
| `net_income_n_minus_1_available` | 156 | 0 |
| `cfo_n_available` | 156 | 0 |
| `cfo_n_minus_1_available` | 156 | 0 |
| `total_assets_n_available` | 156 | 0 |
| `total_assets_n_minus_1_available` | 156 | 0 |
| `total_assets_n_minus_2_available` | 156 | 0 |
| `long_term_debt_n_available` | 156 | 0 |
| `long_term_debt_n_minus_1_available` | 156 | 0 |
| `current_assets_n_available` | 156 | 0 |
| `current_assets_n_minus_1_available` | 156 | 0 |
| `current_liabilities_n_available` | 156 | 0 |
| `current_liabilities_n_minus_1_available` | 156 | 0 |
| `revenue_n_available` | 156 | 0 |
| `revenue_n_minus_1_available` | 156 | 0 |
| `gross_profit_n_available` | 156 | 0 |
| `gross_profit_n_minus_1_available` | 156 | 0 |
| `cogs_n_available` | 156 | 0 |
| `cogs_n_minus_1_available` | 156 | 0 |
| `issue_proceeds_n_available` | 156 | 0 |
| `issue_proceeds_n_minus_1_available` | 156 | 0 |
| `common_shares_n_available` | 156 | 0 |
| `common_shares_n_minus_1_available` | 156 | 0 |
| `common_shares_n_minus_2_available` | 156 | 0 |
| `gross_margin_inputs_n_available` | 156 | 0 |
| `gross_margin_inputs_n_minus_1_available` | 156 | 0 |
| `share_issuance_signal_n_available` | 156 | 0 |
| `share_issuance_signal_n_minus_1_available` | 156 | 0 |
| `criterion_1_inputs_available` | 156 | 0 |
| `criterion_2_inputs_available` | 156 | 0 |
| `criterion_3_inputs_available` | 156 | 0 |
| `criterion_4_inputs_available` | 156 | 0 |
| `criterion_5_inputs_available` | 156 | 0 |
| `criterion_6_inputs_available` | 156 | 0 |
| `criterion_7_inputs_available` | 156 | 0 |
| `criterion_8_inputs_available` | 156 | 0 |
| `criterion_9_inputs_available` | 156 | 0 |

## 3. F-Score build readiness

- Complete proposed F-Score inputs for both N and N-1, including required N-2 denominators/signals: `156/156`.
- All nine criteria have their required inputs available: `156/156`.
- Sprint 4 annual pair reused without fallback: `156/156`.
- This is availability evidence only. No criterion was evaluated and no F-Score was computed.

## 4. Franchise Power history depth

- Proposed minimum usable years: `3`.
- READY: `156/156`.
- INSUFFICIENT_HISTORY: `0/156`.

| franchise_years_used | ticker count |
|---:|---:|
| 3 | 156 |

The local cache exposes at most four annual report periods per ticker. ROC needs both a current and a prior invested-capital observation, so the observed maximum usable ROC/margin overlap is three years. The proposed minimum of three uses the full locally available comparable window; rows below it remain visible with `INSUFFICIENT_HISTORY` rather than being excluded.

## 5. NTC, TRC, and DBC explicit rows

| ticker | annual_n | annual_n_minus_1 | cash_flow annual file | nine criteria inputs available | complete F-Score inputs both years | franchise_years_used | franchise_history_status |
|---|---:|---:|---|---:|---|---:|---|
| NTC | 2025 | 2024 | True | 9 | True | 3 | READY |
| TRC | 2025 | 2024 | True | 9 | True | 3 | READY |
| DBC | 2025 | 2024 | True | 9 | True | 3 | READY |

## 6. Build-phase prerequisites

Entirely absent local input classes: `NONE`.
Partially missing audited availability flags: `NONE`.

Production quality computation remains **FORBIDDEN** until the owner approves `docs/SPEC_SPRINT_6.md`.
