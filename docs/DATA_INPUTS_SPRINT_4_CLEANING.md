# Sprint 4 cleaning data inputs

This note records the repository contract actually inspected on 2026-07-18. It does not define a new financial-data schema.

## Source paths

- Sprint 3 ACCEPTED universe: `data/universe.csv` (378 rows, all `status=ACCEPTED`). The identical dated source is `data/snapshots/2026-07-17/universe.csv`.
- Existing reject history: `data/universe_rejects.csv` (1,367 rows, all `status=REJECTED`). The identical dated source is `data/snapshots/2026-07-17/universe_rejects.csv`.
- Sprint 4 annual run metadata: `data/fundamentals/run_state/sprint4_annual/2026-07-17/progress.json` (315 non-financial ACCEPTED tickers).
- Annual balance sheet: `data/fundamentals/run_state/sprint4_annual/2026-07-17/normalized/<TICKER>/balance_sheet.parquet`.
- Annual income statement: `data/fundamentals/run_state/sprint4_annual/2026-07-17/normalized/<TICKER>/income_statement.parquet`.
- Annual cash flow: `data/fundamentals/run_state/sprint4_annual/2026-07-17/normalized/<TICKER>/cash_flow.parquet`.

The preparation layer reads these existing paths only. It does not call the live API.

## Input columns

The universe and reject files both contain:

`ticker`, `exchange`, `icb2`, `icb3`, `icb4`, `market_cap`, `adtv_20d`, `status`, `reject_reason`, `as_of`, `source`, `data_status`.

The three annual parquet statement types all contain:

`ticker`, `company_type`, `statement_type`, `period_type`, `report_period`, `period_end`, `available_from`, `item_id`, `item`, `item_en`, `value`, `currency`, `source`, `as_of`, `data_status`.

`exchange` and `icb2` come from the ACCEPTED universe. Financial values and their `source`, `as_of`, `available_from`, and `data_status` come from the annual parquet row that supplied the value.

## Annual-cache layout and join keys

The cache is partitioned first by ticker and then by statement filename. The inspected VNM files contain annual periods 2025, 2024, 2023, and 2022; their statement types are respectively `BALANCE_SHEET`, `INCOME_STATEMENT`, and `CASH_FLOW`.

The normalized financial-row key is `(ticker, statement_type, report_period, item_id)`. The ACCEPTED universe joins to the cache by normalized uppercase `ticker`. Inputs are then selected by the exact `(statement_type, report_period, item_id)` required by each formula; display names `item` and `item_en` are not join keys.

## Point-in-time and N/N−1 selection

Eligibility requires `period_type == ANNUAL` and a valid `available_from <= evaluation_date`. Rows with an invalid or future `available_from` are excluded before period selection. From the remaining years in descending order, the first year for which `year - 1` is also present becomes N/N−1. If no such pair exists, every formula receives its own explicit missing inputs rather than a fabricated period or value.

The repository creates `available_from` in `src/data/finance_client.py` as `period_end + LAG_ANNUAL`; the annual normalization key is also enforced there. The read-only pair selection and formula-input assembly used by cleaning prerequisites are in `src/screener/step1_data.py`.

## Known missing-data cases

- The existing `docs/COVERAGE_SPRINT_4_ANNUAL.md` reports valid required STA, SNOA, and full M-Score annual inputs for 315/315 non-financial ACCEPTED tickers as of 2026-07-17.
- A direct read-only audit found `undistributed_earnings` and `owners_equity` for N in 315/315 cached tickers.
- No HoSE warning/control-list membership field exists in `data/universe.csv`, `data/universe_rejects.csv`, or the annual statement cache. The warning signal therefore remains `None` unless an explicit value is supplied later.
- A missing statement row, non-numeric value, non-finite value, or zero required denominator remains formula-specific `INSUFFICIENT_DATA_FOR_<FORMULA>`; it is never replaced with zero and does not suppress independent formulas.
