# SPEC Sprint 3 - Financial Statement Data and Point-in-Time Discipline

This file is the local source of truth for Sprint 3. It is derived from `PLAN_quant_screener_myn.md` and follows the section structure of `docs/SPEC_MVP.md`. Sprint 3 establishes the financial-statement data layer and starts collecting forward-only point-in-time evidence. Correctness, provenance, and honest failure reporting take priority over coverage or speed.

## Scope

Sprint 3 is limited to the following work.

### Historical-period investigation

- Begin the sprint by investigating how to retrieve MORE than 4 historical periods for annual and quarterly financial statements.
- The pinned dependency remains `vnstock==4.0.3`.
- Inspect and smoke-test the public `vnstock.api` financial interface first.
- Test supported provider behavior without bypassing authentication, entitlement, rate limits, or provider terms.
- Record the tested provider, public method, period type, requested period count, returned period count, output shape, and exact error for every probe.
- vnstock returns LONG-format statements: columns item, item_en, item_id + one column per period; only 4 most recent periods by default.
- Source inspection of the pinned package shows internal limit or pagination machinery, but the public VCI statement methods do not expose a supported limit argument.
- Source inspection of the pinned package shows that `vnstock.api.Finance` accepts VCI and KBS; TCBS is not a supported Finance source in this version.
- Private methods and direct undocumented provider HTTP calls are not approved production interfaces.
- A longer-history path is accepted only after a real public-API smoke test proves the returned periods and preserves the required schema.
- If no supported longer-history path is confirmed, retain the 4-period baseline and accumulate new history through dated snapshots.
- Do not upgrade or replace `vnstock==4.0.3` during this sprint.
- Document the final finding in `data_contract.md` v2 before the remaining financial ingestion work is considered complete.
OPEN QUESTION: Confirm whether longer statement history requires a vnstock account entitlement and how that credential will be supplied locally without entering source control.

### Financial statement client

- Add `src/data/finance_client.py`.
- Build the new client on `vnstock.api`.
- The legacy Vnstock() class is deprecated since 31/08/2025 — the new client must be built on vnstock.api.
- Reuse the cache, retry, exponential-backoff, polite-sleep, stale-cache, and API-error patterns already present in `src/data/vnstock_client.py`.
- Support balance sheet, income statement, and cash flow retrieval.
- Support both quarterly and yearly periods.
- Provide the repository-facing operations `get_balance_sheet`, `get_income_statement`, and `get_cash_flow` for one ticker and one period type at a time.
- The ratio endpoint returns corrupted headers and MUST NOT be used.
- Ratios must eventually be computed from raw balance sheet, income statement, and cash flow data, but no ratio or screener formula is implemented here.
- Cache financial statements per ticker under `data/fundamentals/`.
- Preserve the raw provider response shape in cache before normalization.
- Normalize LONG-format statement data into tidy rows.
- The tidy identity is ticker, statement type, report period, and `item_id`.
- Use `item_id` as the join key because Vietnamese and English item names may change between versions.
- Preserve `item` and `item_en` as descriptive fields only.
- Never use an item name as a substitute key when `item_id` is missing.
- A missing `item_id` is a data-quality failure, not permission to invent one.
- Do not replace missing financial values with zero.

### Point-in-time fields

- Every normalized financial row must carry `report_period`, `period_end`, and `available_from`.
- there is NO publication-date field in the API.
- If a future supported source supplies a real publication date, preserve that date and identify its source explicitly.
- Otherwise calculate `available_from = period_end + LAG`.
- Use `LAG_QUARTER=30, LAG_SEMIANNUAL=60, LAG_ANNUAL=90 days`.
- Legal basis: Circular 96/2020/TT-BTC, Articles 10 & 14.
- These lags use the conservative extension limits from the master plan.
- No downstream consumer may use a row before its `available_from` date.
- Historical statements fetched today may be restated and therefore may differ from what an investor actually saw at the historical date.
- The lag rule cannot repair restatement look-ahead bias.
- `data_contract.md` v2 and `README.md` must disclose that limitation.
OPEN QUESTION: Define how non-calendar fiscal year-ends, if encountered, map provider period labels to `period_end`; do not silently assume a calendar year when the source proves otherwise.

### Universe snapshots

- Extend `scripts/run_universe.py` so every successful universe run writes a dated snapshot under `data/snapshots/YYYY-MM-DD/`.
- Each dated directory must contain an exact copy of the run's `universe.csv` and `universe_rejects.csv`.
- The latest files under `data/` remain the current M0 outputs.
- Snapshot creation must not relax universe acceptance or rejection rules.
- Snapshot creation must not alter the existing universe column order.
- A rerun for an existing date must be deterministic and must not silently mix rows from different runs.
- Snapshot provenance must identify the run date and source data status.
- These snapshots begin forward-only point-in-time collection now.
- After 6-12 months they provide real historical universe membership evidence; they do not reconstruct delisted symbols or past statements retroactively.

### Controlled market-cap fetching and price semantics

- Re-enable market-cap fetching only through a controlled, opt-in path.
- Use small batches, sequential or otherwise rate-limit-safe requests, polite sleep, retry, and a 7-day cache.
- Reuse the existing soft-stop behavior for consecutive API failures.
- Do not silently relax rate limits or retry forever to improve coverage.
- Prefer a source-reported market cap when available.
- If no direct market cap exists, a proxy may use current price multiplied by shares outstanding only when both source values are present.
- financial statements are in raw VND; the price API returns thousands of VND — any price×fundamentals combination must multiply price by 1000.
- The multiplication by 1000 requires a dedicated unit test.
- A proxy market cap must carry explicit proxy provenance in `source`.
- A failed or unavailable market-cap fetch remains missing; it is never zero.
- Investigate whether the price API returns adjusted or raw prices.
- Record the tested provider, endpoint, corporate-action example, observed behavior, and conclusion in `data_contract.md` v2.
- Do not treat one price series as suitable for both return calculations and market-cap calculations until the adjustment behavior is verified.
- Momentum in Sprint 7 and returns in Sprint 8 require adjusted prices.
- Market cap requires current raw price multiplied by current shares.
OPEN QUESTION: The plan does not define the small-batch size; expose it as a controlled runtime setting and do not invent a hard-coded production value.
OPEN QUESTION: Adjusted-versus-raw price behavior remains unverified until the required real smoke test and corporate-action comparison are completed.

### Company-type separation

- bank statements (e.g., VCB: 86 balance-sheet rows vs 122) have a different schema and must not be force-normalized.
- The verified smoke test also observed VCB income statement 26 rows vs 25 for a non-financial company, and cash flow 52 rows vs 41.
- Preserve company type or provider schema identity with every fetch result.
- Preserve bank and insurer raw data separately from non-financial data.
- Mechanical LONG-to-tidy reshaping is permitted when keyed on `item_id`.
- Semantic alignment of unlike bank, insurer, securities-company, and non-financial line items is forbidden.
- Sprint 3 does not exclude financial-sector companies from the universe.

### Documentation deliverables

- Update `data_contract.md` to version 2 with the financial schema, point-in-time rules, units, cache layout, provider findings, price-adjustment finding, error states, and known restatement limitation.
- Update `CHANGELOG.md` with the Sprint 3 specification and later implementation changes, including the reason for any behavior-affecting configuration.
- Update `README.md` only to disclose the point-in-time and restatement limitation required by the master plan.
- Add a fixture-based financial smoke-test contract and a separate real fetch script for controlled manual execution.
- The Sprint 3 Definition of Done is successful financial-statement retrieval for ≥ 90% of the universe, with every remaining ticker carrying an explicit `data_status` explanation.
- No financial statement row may have a missing `available_from`.

### Approved weekly point-in-time selection

- The financial-statement publication lags remain unchanged:
  `LAG_QUARTER=30`, `LAG_SEMIANNUAL=60`, and `LAG_ANNUAL=90` days.
- These lags define when a statement is allowed to be used. They do not define
  how often the pipeline or report runs.
- The pipeline may run weekly with a run-level `as_of` date.
- A weekly run may consume only statements where `available_from <= as_of`.
- If no newer statement is eligible, the run must use the most recent eligible
  statement and record `NO_NEW_FINANCIAL_REPORT` as the selection explanation.
- `NO_NEW_FINANCIAL_REPORT` is not a source-data failure. The selected statement
  keeps `data_status=OK` when its underlying data is valid.
- A weekly run must never reduce the 30/60/90-day lags to seven days.

### Approved whitelist-normalization gate — currently blocked

- Future normalization may accept only a versioned `REQUIRED_ITEMS` whitelist
  containing the `item_id` values required by the approved Sprint 4-6 formulas.
- Duplicate `item_id` values outside `REQUIRED_ITEMS` may remain only in the
  immutable raw observation and must be identified as
  `DUPLICATE_ITEM_ID_QUARANTINED`; they must not block an otherwise usable
  ticker.
- Normalization must fail only when the intersection between duplicated
  `item_id` values and `REQUIRED_ITEMS` is non-empty.
- Financial coverage of at least 90% must be measured by the presence and
  uniqueness of every `REQUIRED_ITEMS` value, not by accepting every provider
  row.
- Do not implement this behavior until the complete whitelist is copied from
  the approved Sprint 4-6 formula specifications and verified against real API
  responses.
- The first minimum plan-derived whitelist check already found two required
  balance-sheet identifiers used by NOA/SNOA:
  `short_term_investments` and `preferred_shares`.
- The 2026-07-15 public VCI check found both identifiers duplicated twice for
  VNM, HPG, and FPT. Neither identifier was duplicated in VCB, although VCB had
  other duplicate identifiers outside this minimum confirmed set.
- Because required identifiers intersect the duplicate set, the owner-approved
  stop condition is active. Do not complete the whitelist, change normalization,
  choose a duplicate row, aggregate duplicates, or begin Sprint 4 without a new
  owner decision.
- The complete evidence and root-cause analysis are recorded in
  `docs/SPRINT_3_DUPLICATE_ITEM_ID_INVESTIGATION.md`.

### Proposed provider identifier — not part of the schema

- The preferred resolution is for vnstock/VCI to expose the original stable
  provider field identifier through a supported public API.
- A future data-contract proposal may add `provider_item_id` only after a real
  public-API smoke test proves that it is present, unique, and stable across
  periods and company types.
- `provider_item_id` is not approved in the current schema and must not be
  synthesized from item names, row positions, private methods, or undocumented
  HTTP endpoints.

## Data Rules

- Never fabricate financial data.
- Every output row must include `source`, `as_of`, and `data_status`.
- Missing data must be marked as `MISSING_DATA`.
- API failures must be marked as `API_ERROR`.
- Stale cache data must be marked as `STALE_DATA`.
- Tests must not call real APIs; tests use fixtures only.
- A live smoke test must be a separate, explicitly invoked command.
- Report source errors verbatim, except secrets must always be redacted.
- Do not convert an API failure into a successful result through mock data.
- `as_of` records the retrieval or source-observation date.
- `report_period` identifies the financial period represented by the value.
- `period_end` is the end date of that financial period.
- `available_from` is the earliest date the row may be consumed.
- A real publication date, when genuinely supplied, takes precedence over the conservative lag-derived date and must retain provenance.
- In the current verified API shape, use `period_end + LAG` because there is no publication-date field.
- Financial values from statements remain in raw VND.
- Valid large-company statement magnitudes are expected in the approximate range 1e9-1e15 VND.
- Values around 1e3-1e6 for large-company statement totals indicate a likely unit conversion or API problem and must stop that fetch from being accepted.
- The verified VNM current-assets example is 38,757,016,956,726 VND for 2026-Q1; it is a sanity reference, not a hard-coded production value.
- Null values remain null and carry the correct status.
- Negative values remain negative when supplied by the source.
- Duplicate tidy keys are a validation failure and must not be silently summed.
- Raw cached responses are immutable evidence for the fetch date.
- Re-fetching may create a new dated cache observation; it must not rewrite an earlier observation as though the new restated value were historically known.
- API credentials, tokens, cookies, and local authentication files must never be written to logs, fixtures, snapshots, docs, commits, or GitHub.

## Required Output Schema

### Normalized financial statement rows

`data/fundamentals/` normalized outputs must contain these fields:

- `ticker`
- `company_type`
- `statement_type`
- `period_type`
- `report_period`
- `period_end`
- `available_from`
- `item_id`
- `item`
- `item_en`
- `value`
- `currency`
- `source`
- `as_of`
- `data_status`

Allowed `statement_type` values are `BALANCE_SHEET`, `INCOME_STATEMENT`, and
`CASH_FLOW`.

Allowed `period_type` values in Sprint 3 are `QUARTER`, `SEMIANNUAL`, and
`ANNUAL` only when the source period can be identified honestly.

`currency` must be `VND` for accepted statement values covered by the verified
unit rule.

The unique tidy key is:

- `ticker`
- `statement_type`
- `report_period`
- `item_id`

### Financial fetch-status rows

A per-ticker fetch-status output must contain:

- `ticker`
- `company_type`
- `statement_type`
- `period_type`
- `requested_at`
- `returned_period_count`
- `source`
- `as_of`
- `data_status`
- `error`

The status output records missing statements and API failures without creating
fake financial line items.

`error` must contain the exact source failure with all secrets redacted.

### Universe snapshot outputs

Each `data/snapshots/YYYY-MM-DD/universe.csv` and
`data/snapshots/YYYY-MM-DD/universe_rejects.csv` must retain the existing M0
schema exactly:

- `ticker`
- `exchange`
- `icb2`
- `icb3`
- `icb4`
- `market_cap`
- `adtv_20d`
- `status`
- `reject_reason`
- `as_of`
- `source`
- `data_status`

`universe.csv` contains only `ACCEPTED` rows.

`universe_rejects.csv` contains only `REJECTED` rows, and every row has a
non-empty `reject_reason`.

The existing universe schema is not expanded in Sprint 3.

Market-cap provenance must remain explicit in the existing `source` field and
in cache or run metadata documented by `data_contract.md` v2.

## Required Local Checks

- Run `python -m py_compile src/data/finance_client.py scripts/run_universe.py scripts/smoke_vnstock_finance.py`.
- Run `pytest` and require the full fixture-based suite to pass.
- Verify tests do not import or call a real vnstock API.
- Add fixture coverage for all three statement types and both quarterly and yearly period modes.
- Verify LONG-to-tidy normalization preserves `item_id` and does not use names as keys.
- Verify missing `item_id` fails honestly.
- Verify duplicate tidy keys fail rather than aggregate silently.
- Verify `LAG_QUARTER=30`, `LAG_SEMIANNUAL=60`, and `LAG_ANNUAL=90` produce the expected `available_from` dates from hand-computed fixture dates.
- Verify no normalized row has a missing `available_from`.
- Verify missing values remain missing with `MISSING_DATA`.
- Verify API failures remain failures with `API_ERROR`.
- Verify stale-cache fallbacks carry `STALE_DATA`.
- Verify the `ratio` endpoint is never called.
- Verify raw VND values are not divided into thousands, millions, or billions.
- Verify the large-company 1e9-1e15 VND magnitude guard.
- Verify suspicious 1e3-1e6 large-company totals stop acceptance.
- Verify price multiplied by shares or fundamentals multiplies the price by 1000 exactly once.
- Verify bank and non-financial schemas are not force-normalized.
- Verify market-cap cache freshness is 7 days.
- Verify snapshot paths use `data/snapshots/YYYY-MM-DD/`.
- Verify snapshot files preserve the current universe schemas and row status rules.
- Run the real fetch script once on ≥3 tickers.
- The real set must include VNM, at least one other non-financial ticker, and at least one bank ticker to expose schema differences.
- The real run must exercise balance sheet, income statement, and cash flow in quarterly and yearly modes.
- Record returned period counts and determine whether a supported path returns more than 4 periods.
- Record whether the tested price endpoint is adjusted or raw using a documented corporate-action comparison.
- Manually verify VNM net revenue against cafef.vn or vietstock.vn.
- The VNM unit check must remain raw VND at ~1e13 scale.
- Do not copy the comparison site's displayed unit without converting it back to raw VND for an apples-to-apples comparison.
- Inspect the first dated universe snapshot and compare it with the latest `data/universe.csv` and `data/universe_rejects.csv` from the same run.
- Inspect the coverage summary and require successful retrieval for ≥ 90% of the universe before declaring the Sprint 3 implementation complete.
- If Python or dependencies are unavailable, report the exact failure; do not claim that `py_compile`, `pytest`, or the real run passed.

## Must NOT Include

- No accruals, Sloan accruals, NOA, or SNOA formulas.
- No Beneish M-Score formula or threshold.
- No Piotroski F-Score formula or threshold.
- No EBIT/TEV, E/P, valuation rank, or value cut.
- No Franchise Power or quality score.
- No momentum signal.
- No composite score.
- No portfolio construction, weighting, sector cap, or rebalance logic.
- No live trading, order placement, broker integration, or real-money action.
- No backtesting, walk-forward testing, or performance metrics.
- No UPCoM exclusion.
- No financial-sector exclusion.
- `FINANCIAL_SECTOR_EXCLUDED` and `UPCOM_EXCLUDED_V1` belong to Sprint 4.
- No changes to the acceptance logic of the current universe builder.
- No semantic force-normalization of banks, insurers, securities companies, and non-financial companies.
- No use of the corrupted `ratio` endpoint.
- No undocumented direct provider HTTP calls.
- No use of private vnstock methods as production interfaces.
- No fabricated publication dates.
- No fabricated financial values or synthetic coverage.
- No use of restated data as though it were historically point-in-time.
- No dashboards.
- No machine learning.
- No GitHub Actions.
- No database.
- No new dependencies beyond `requirements.txt`.
- No dependency additions, removals, or upgrades.
- No change to `vnstock==4.0.3`.
- No API key, token, password, cookie, credential, or private configuration in source control, logs, test fixtures, documentation, or reports.
