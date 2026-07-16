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

### Approved whitelist normalization design

- Normalization may accept only the versioned `REQUIRED_ITEMS` whitelist below.
  These exact `item_id` values were mapped by the owner's mentor from the frozen
  Sprint 4-6 formulas using `docs/ITEM_INVENTORY_SPRINT_3.md`. Do not re-derive,
  rename, or extend them without a later owner-approved spec amendment.
- Duplicate `item_id` values outside `REQUIRED_ITEMS` remain only in the
  immutable raw observation with `DUPLICATE_ITEM_ID_QUARANTINED`; they do not
  block an otherwise usable ticker. The sole approved processing exception is
  the mandatory `other_current_assets` helper: its raw candidates may
  participate in Rule A only to resolve `short_term_investments`, after which
  the helper remains outside formula coverage and duplicate normalized output.
- Coverage of at least 90% is measured by the presence and uniqueness of every
  required item after the approved disambiguation rules run, not by accepting
  every provider row.
- The real-number evidence is preserved in
  `docs/VERIFY_DUP_ITEMS_SPRINT_3.md`. It supports the following two narrow,
  value-based rules in principle. This specification amendment does not
  authorize implementation until the owner reviews and explicitly approves the
  diff.

#### `REQUIRED_ITEMS` v1 — spec constant

```text
REQUIRED_ITEMS_VERSION=v1

BALANCE_SHEET_REQUIRED_ITEMS=
  current_assets
  cash_and_cash_equivalents
  short_term_investments
  accounts_receivable
  inventories_net
  fixed_assets
  tangible_fixed_assets
  total_assets
  current_liabilities
  short_term_borrowings
  taxes_and_other_payable_to_state_budget
  long_term_liabilities
  long_term_borrowings
  owners_equity
  undistributed_earnings
  minority_interests
  preferred_shares
  paid_in_capital

INCOME_STATEMENT_REQUIRED_ITEMS=
  net_sales
  cost_of_sales
  gross_profit
  selling_expenses
  general_and_admin_expenses
  operating_profit_loss
  interest_expenses
  net_accounting_profit_loss_before_tax
  net_profit_loss_after_tax
  attributable_to_parent_company

CASH_FLOW_REQUIRED_ITEMS=
  depreciation_and_amortization
  net_cash_inflows_outflows_from_operating_activities
  proceeds_from_issue_of_shares
```

- Version `v1` contains exactly 31 formula items: 18 balance-sheet items, 10
  income-statement items, and 3 cash-flow items.
- Presence means the exact `item_id` is returned for the correct statement.
  Uniqueness means exactly one normalized row per required `item_id` and report
  period after the approved duplicate rules run.
- A required item that is missing, remains duplicated, or is unresolved by the
  approved rules makes that ticker incomplete for formula coverage. Do not use
  `item` or `item_en` to replace it.

#### Fetch-required helper items — outside formula coverage

- `other_current_assets` is a mandatory Rule A helper. It is the closing term
  in the approved identity:

```text
current_assets = cash_and_cash_equivalents
    + short_term_investments
    + accounts_receivable
    + inventories_net
    + other_current_assets
```

- `other_current_assets` is not counted among the 31 formula coverage items,
  but Rule A cannot run without it. If it is missing for a ticker whose
  `short_term_investments` requires Rule A, do not guess; record
  `REQUIRED_ITEM_AMBIGUOUS` and quarantine that statement.
- `held_to_maturity_investment` is an optional fetch helper for auditing the
  observed short-term-investment split. Its absence does not block Rule A or
  formula coverage, and it must not be summed into or substituted for a required
  item.

#### Coverage scope and financial template boundary

- `REQUIRED_ITEMS` v1 applies only to the non-financial statement template.
- The Sprint 3 coverage denominator is the non-financial tickers whose universe
  status is `ACCEPTED`.
- Bank, insurer, securities, and other financial-sector tickers remain in the
  universe and still require successful immutable raw fetch evidence. They are
  not required to satisfy whitelist completeness and are neither the numerator
  nor denominator of the formula-coverage percentage.
- This coverage boundary is not the Sprint 4
  `FINANCIAL_SECTOR_EXCLUDED` screening decision and does not remove any ticker
  from the universe or sector monitor.

#### Approved formula-input caveats — documentation only

1. `taxes_and_other_payable_to_state_budget` is broader than the Sloan
   formulation's taxes-payable input. The owner accepts it as an approximation;
   every later consumer and report must disclose that limitation.
2. Use `minority_interests` for the current reporting regime. If
   `minority_interests_before_2015` is non-zero, log a warning; do not silently
   combine or substitute the legacy field.
3. Shares outstanding for TEV must come from the price API, never from the
   balance sheet.
4. Later EBIT is computed as
   `net_accounting_profit_loss_before_tax + interest_expenses`, not from
   `operating_profit_loss`. VAS line 30 already nets financial income and
   expense, so it is not clean EBIT. Keep `operating_profit_loss` only for the
   later EBITDA distress proxy.
5. The later M-Score DEPI input uses `tangible_fixed_assets` (net book value)
   plus `depreciation_and_amortization` as an accepted approximation of the
   original gross-PP&E plus accumulated-depreciation formulation. Reports must
   disclose this approximation.

#### Named configuration values

The implementation must read these values from configuration; none may be
hard-coded in source:

```text
IDENTITY_TOL=0.01
IDENTITY_MIN_PERIODS=3
IDENTITY_MARGIN=5.0
DUP_MATERIALITY_EPS=0.01
```

- `IDENTITY_TOL` is a relative-error fraction, so `0.01` means 1%.
- `IDENTITY_MIN_PERIODS` is the minimum number of available periods that must
  individually pass the tolerance.
- `IDENTITY_MARGIN` is the minimum separation between the winning combination's
  mean error and the best rival combination for each duplicated item.
- `DUP_MATERIALITY_EPS` is the maximum difference between duplicate candidate
  rows as a fraction of reported `current_assets`; `0.01` means 1%.
- The implementation-stage change must place these settings in the approved
  project configuration and record the reason in `CHANGELOG.md`.

#### Rule A — identity-based selection for duplicated current-asset items

- Apply this rule only when `short_term_investments` and/or
  `other_current_assets` has duplicate candidate rows.
- Build every candidate combination from one reported
  `short_term_investments` row and one reported `other_current_assets` row. A
  non-duplicated side contributes its single reported row.
- Do not sum duplicate candidates. Do not use row position, source order,
  `item`, or `item_en` to select a candidate.
- For each available period and candidate combination, calculate:

```text
rhs = cash_and_cash_equivalents
    + short_term_investments_candidate
    + accounts_receivable
    + inventories_net
    + other_current_assets_candidate

identity_error = abs(current_assets - rhs) / abs(current_assets)
```

- A period is available for this rule only when `current_assets` is non-zero and
  every aggregate input and both candidate values are numeric source values.
  Missing values remain missing; the rule must not convert `NaN` to zero.
- Before evaluating candidate combinations, inspect the identity inputs
  `cash_and_cash_equivalents`, `accounts_receivable`, `inventories_net`, and
  `current_assets` and the candidate items. Before Rule A scoring, if all
  duplicate rows of one identity-related item are numerically identical in
  every returned period, collapse them to their common reported values and log
  `DUPLICATE_VERIFIED_IDENTICAL` with all source row indices and values. For
  this comparison, `NaN` equals `NaN`; `NaN` does not equal a number.
- If duplicated `cash_and_cash_equivalents`, `accounts_receivable`,
  `inventories_net`, or `current_assets` rows are not identical, do not extend the
  combination search and do not apply the immaterial-difference rule to those
  inputs. Record `REQUIRED_ITEM_AMBIGUOUS` for the statement.
- Score each candidate combination by its mean `identity_error` across all
  periods available for that combination. The candidate with the smallest mean
  error is the provisional winner.
- Apply the tolerance condition to that winner: its per-period
  `identity_error` must be `<= IDENTITY_TOL` in at least
  `IDENTITY_MIN_PERIODS` available periods. A winner that misses this condition
  cannot be selected by either the margin or immaterial-difference path.
- Evaluate the margin separately for each still-duplicated candidate item `X`:
  1. `winner_X` is the best-scoring combination.
  2. `rival_X` is the best-scoring combination whose source row for `X`
     differs from `winner_X`; combinations that change only another item are
     not rivals for `X`.
  3. Accept `X` by margin only when the winner passes the tolerance condition
     and `rival_X.mean_error >= IDENTITY_MARGIN * winner_X.mean_error`.
- If `winner_X.mean_error` is zero, the per-item margin passes only when
  `rival_X.mean_error` is strictly positive. A zero-error rival for `X` is a
  tie and does not pass the margin path.
- If a candidate item `X` differs across rows and does not pass the per-item
  margin, calculate the maximum pairwise materiality over periods with numeric,
  non-zero `current_assets`:

```text
duplicate_difference_X = max(|X_row_i - X_row_j| / abs(current_assets))
```

- Accept `X` through the immaterial-difference path only when the best
  combination passes the same tolerance condition and
  `duplicate_difference_X <= DUP_MATERIALITY_EPS`. Select the `X` row used by
  the best identity combination, record `DUPLICATE_RESOLVED_IMMATERIAL`, and
  log every compared source value and per-period difference. This rule applies
  only to Rule A candidate items; it never resolves conflicting aggregate
  identity inputs.
- If a duplicated Rule A candidate item passes neither its per-item margin nor
  the immaterial-difference path, the statement is ambiguous. Every duplicated
  candidate item must resolve; resolving one item does not authorize guessing
  another.
- Success retains only the resolved required candidates for normalized use,
  records the applicable `DUPLICATE_RESOLVED_BY_IDENTITY`,
  `DUPLICATE_VERIFIED_IDENTICAL`, and/or
  `DUPLICATE_RESOLVED_IMMATERIAL` flags, and logs every candidate's per-period
  and mean errors.
- Failure must not select any candidate. Record `REQUIRED_ITEM_AMBIGUOUS`, retain
  the raw observation, quarantine that statement for required-item coverage,
  and exclude the ticker from the coverage numerator without removing it from
  the universe files.

#### Rule B — duplicated `preferred_shares`

- Among duplicated `preferred_shares` candidates, discard only candidates that
  are `NaN` in every returned period. This removes an uninformative field; it is
  not permission to convert `NaN` to zero.
- If exactly one candidate remains, use it and record
  `DUPLICATE_RESOLVED_NON_NAN`.
- If zero or more than one candidate remains, do not select a value. Record
  `REQUIRED_ITEM_AMBIGUOUS`, retain the raw observation, quarantine that
  statement for required-item coverage, and exclude the ticker from the
  coverage numerator without removing it from the universe files.
- If the resolved candidate is greater than zero in any period, also record
  `PREFERRED_POSITIVE_REVIEW`. Every such ticker requires owner inspection.

#### Resolution evidence and schema boundary

- `DUPLICATE_RESOLVED_BY_IDENTITY`, `DUPLICATE_VERIFIED_IDENTICAL`,
  `DUPLICATE_RESOLVED_IMMATERIAL`, `DUPLICATE_RESOLVED_NON_NAN`,
  `REQUIRED_ITEM_AMBIGUOUS`, `PREFERRED_POSITIVE_REVIEW`, candidate values,
  materiality comparisons, and identity errors must be retained in observation
  metadata and fetch-status explanations for audit.
- These flags do not add `provider_item_id` or authorize another new normalized
  financial-row column in this spec-review step.
- `provider_item_id` remains outside the approved schema. It must not be
  synthesized from names, row positions, private methods, or undocumented HTTP
  endpoints.
- The implementation must preserve the original raw observation before either
  rule runs.

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
- Duplicate tidy keys must never be silently summed. Outside `REQUIRED_ITEMS`
  they are quarantined in raw evidence. Duplicated required items may proceed
  only through Rule A or Rule B; an unresolved case is
  `REQUIRED_ITEM_AMBIGUOUS` and produces no normalized required-item selection.
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
- After separate owner approval of this spec, add fixture tests using the
  verbatim VNM, HPG, and FPT values in
  `docs/VERIFY_DUP_ITEMS_SPRINT_3.md`; pytest must not call the real API.
- Verify Rule A evaluates every value-based candidate combination, logs all
  per-period and mean identity errors, and never uses row position or labels.
- Verify Rule A resolves the approved VNM/HPG/FPT fixtures under
  `IDENTITY_TOL=0.01`, `IDENTITY_MIN_PERIODS=3`, and
  `IDENTITY_MARGIN=5.0`.
- Add fixture cases copied from the cached validation evidence: VNM and HDG
  resolve through the per-item margin; HID resolves through identical-row
  verification. The earlier gross-inventory fixture expectations are replaced
  by a mechanical rerun with the accounting-correct `inventories_net` input.
  DRC, TLH, CTF, C32, VCS, PVC, VHC, and HT1 may resolve only when their cached
  values pass the unchanged tolerance and per-item 5x margin, or Rule R3. Tests
  must assert the recomputed path and must not preserve or force a historical
  status.
- Verify a same-`X` combination with a different other-current-asset row is not
  treated as `rival_X`.
- Verify identical duplicate comparisons treat `NaN` as equal only to `NaN`,
  never to a reported number, and log `DUPLICATE_VERIFIED_IDENTICAL`.
- Verify the immaterial-difference path logs all values, never applies to
  conflicting aggregate identity inputs, and cannot override a failed identity
  tolerance.
- Verify an ambiguous candidate set produces `REQUIRED_ITEM_AMBIGUOUS` and no
  selection.
- Verify failure of the identity-margin condition produces
  `REQUIRED_ITEM_AMBIGUOUS` and no selection.
- Verify Rule B discards only all-period-`NaN` candidates without converting
  missing values to zero.
- Verify Rule B records `DUPLICATE_RESOLVED_NON_NAN` only when exactly one
  candidate remains and records `PREFERRED_POSITIVE_REVIEW` when any resolved
  period is positive.
- Verify duplicate tidy keys outside `REQUIRED_ITEMS` are quarantined rather
  than aggregated and do not block the ticker.
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
- Inspect the coverage summary and require complete, unique `REQUIRED_ITEMS` v1
  for at least 90% of the `ACCEPTED` non-financial denominator before declaring
  Sprint 3 complete. Financial-sector tickers require raw fetch success but do
  not enter this formula-coverage percentage.
- After fixture tests pass, re-run the separate one-off live validation script
  on VNM, HPG, FPT, VCB, the same 20 sampled `ACCEPTED` non-financial,
  non-UPCoM tickers, and 16 additional eligible tickers, for 40 total.
- The live validation sample must use a fixed seed and print the exact sampled
  ticker list. Keep seed `20260715` so the original 20 remain unchanged, then
  draw the additional 16 deterministically. It must not run under pytest.
- For every validation ticker, report resolved versus ambiguous status, all
  identity errors, and the resolved preferred-share value or honest absence.
- Preserve verbatim real numbers and add the simple Vietnamese summary required
  by `AGENTS.md`.
- After separate owner approval of this amendment, verify the existing
  40-ticker sample using cached raw observations where available. For every
  non-financial ticker, report every `REQUIRED_ITEMS` v1 item as present and
  unique, missing, duplicated, or ambiguous after Rules A/B/R1-R3. Report the
  mandatory `other_current_assets` helper separately.
- The sample report must preserve verbatim evidence and include the simple
  Vietnamese summary required by `AGENTS.md`. Stop after that sample report; do
  not run the full-universe coverage job until a later owner decision.
- Any later tolerance change requires owner approval and a `CHANGELOG.md` entry
  stating the reason.
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
- No removal of financial-sector tickers from the universe or sector monitor;
  the approved non-financial whitelist-coverage denominator is only a data
  template boundary, not a Sprint 4 screening exclusion.
- `FINANCIAL_SECTOR_EXCLUDED` and `UPCOM_EXCLUDED_V1` belong to Sprint 4.
- No changes to the acceptance logic of the current universe builder.
- No semantic force-normalization of banks, insurers, securities companies, and non-financial companies.
- No summing duplicate candidates.
- No first-row, last-row, ordinal, or source-position selection.
- No use of `item` or `item_en` as a key or tie-breaker.
- No threshold tuning without owner approval and a documented reason.
- No `provider_item_id` in the normalized schema.
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
