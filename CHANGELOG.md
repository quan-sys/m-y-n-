# Changelog

## 2026-07-17

- Added a consolidated 2026-07-17 project handoff that supersedes the older
  2026-07-15 handoff, preserves every owner-approved Sprint 3 decision and
  result, identifies the authoritative files for a new chat, and records the
  exact hard stop before PR merge or Sprint 4.
- Completed the owner-approved full `ACCEPTED` universe Sprint 3 run with
  controlled public-API batching and cache reuse: 378 tickers, including 315
  non-financial coverage candidates and 63 financial-sector raw-fetch-only
  tickers. No threshold or screener configuration value changed.
- Measured `REQUIRED_ITEMS` v1 coverage at 308/315 non-financial tickers, or
  97.777777777778%, above the 90% Definition of Done gate. The seven honest
  failures are AGX, BAF, DBC, DSH, GTD, ODE, and TAB; the detailed report keeps
  each provider-missing or `REQUIRED_ITEM_AMBIGUOUS` reason instead of guessing.
- Audited 271,862 normalized fundamentals rows: zero missing `report_period`,
  zero missing `available_from`, and zero 30/60/90-day lag mismatches. All 63
  financial-sector tickers completed their three raw fetches.
- Wrote point-in-time universe and reject snapshots for the run spanning
  2026-07-16 and 2026-07-17, and recorded the first snapshot as 2026-07-16.
  The full fixture-only pytest suite is green at 100% with exit code 0.
- Kept PR #1 unmerged and stopped before Sprint 4 for owner and mentor review.
- Sprint 3 CLOSED — full ACCEPTED universe REQUIRED_ITEMS v1 coverage 97.78%, PR #1 merged.
- Specify Sprint 4 step-1 cleaning (accruals STA/SNOA, Beneish M-Score, distress PFD); spec only, no implementation.
- Revise Sprint 4 step-1 cleaning spec to freeze AQI/TATA inputs and block the net-debt-to-EBITDA sub-signal pending an owner-approved cap; spec only, no implementation.

## 2026-07-16

- Ran the owner-approved controlled live validation on 12 existing `ACCEPTED`
  non-financial sample tickers: FPT, CSM, DVP, C32, VOS, PHR, DP3, DHC, DRC,
  VCS, TLH, and HID. All 36 quarterly statement requests were fresh public VCI
  fetches with 2.8-3.6 second polite sleeps and were cached by content hash.
- Verified all 156 ticker-item checks for the 10 income-statement and 3
  cash-flow `REQUIRED_ITEMS` v1 fields are present and unique in the live raw
  responses. Across all three statements, all 372 ticker-item checks are
  `PRESENT_UNIQUE`; there are no missing or newly duplicated required items.
  The full-universe coverage job, thresholds, Sprint 4, and PR merge remain
  untouched pending owner review.
- Corrected Rule A's production identity input from gross `inventories` to the
  spec-approved `inventories_net`. This is an accounting bug fix: current
  assets contain inventory after its loss provision, and the cached rows prove
  `inventories + provision_for_decline_in_inventories = inventories_net`.
  `IDENTITY_TOL=0.01`, `IDENTITY_MIN_PERIODS=3`, `IDENTITY_MARGIN=5.0`, and
  `DUP_MATERIALITY_EPS=0.01` are unchanged.
- Recomputed rather than forced the affected fixture expectations. Mean
  absolute inventory provision as a share of current assets is C32 2.8249%,
  VCS 1.2388%, PVC 2.3986%, DRC 0.3106%, TLH 1.3393%, CTF 0.1550%, VHC
  1.7733%, and HT1 0.5329%. With net inventory, each cached identity winner is
  exact across all four periods and its different-STI rival remains positive,
  so these cases now exercise the unchanged per-item margin path. The cached
  report records the before/after errors and provision values verbatim.
- Added the cache-only 40-ticker `REQUIRED_ITEMS` v1 verification report and
  CSV evidence. The run performs no network calls, records uncached statements
  as absence of cached evidence rather than provider absence, and stops before
  the full-universe >=90% gate.
- Added the owner-mentor-delivered, versioned `REQUIRED_ITEMS` v1 spec constant
  exactly as supplied: 18 balance-sheet, 10 income-statement, and 3 cash-flow
  `item_id` values. No mapping was re-derived from display names.
- Documented mandatory `other_current_assets` and optional
  `held_to_maturity_investment` as fetch helpers outside formula coverage;
  missing the mandatory helper makes Rule A ambiguous rather than guessable.
- Limited whitelist completeness coverage to `ACCEPTED` non-financial tickers
  while retaining raw-fetch obligations and universe membership for financial
  templates.
- Recorded the five owner-approved input caveats for the broader tax-payable
  approximation, current-versus-legacy minority interests, price-API share
  counts, EBIT construction, and the M-Score DEPI approximation.
- Changed the next validation gate to a cached-first 40-ticker per-item report
  followed by a hard stop before any full-universe run. Thresholds, code,
  schema, normalization, and Sprint 4 remain unchanged in this spec-only step.

## 2026-07-15

- Implemented the approved R1 per-item margin so a candidate is compared only
  with combinations that change that same source row; this removes false
  ambiguity such as VNM without changing the 1% identity tolerance or 5x margin.
- Implemented R2 with `DUPLICATE_VERIFIED_IDENTICAL` and complete source-value
  logging because numerically identical duplicate rows contain no disagreement.
- Added `DUP_MATERIALITY_EPS=0.01` to configuration and implemented R3 only
  after the unchanged identity tolerance passes; this permits auditable small
  candidate differences while leaving material or poor-fitting cases ambiguous.
- Approved a spec-only refinement from combination-level to per-item identity
  margins. Reason: VNM's correct short-term-investment row beat every rival
  short-term-investment row by about 208x, but the former comparison incorrectly
  rejected it because another combination changed only `other_current_assets`.
- Approved identical-duplicate verification before identity scoring. Reason:
  rows with the same reported values in every period contain no numerical
  disagreement, so collapsing them is auditable without guessing.
- Added the proposed named `DUP_MATERIALITY_EPS=0.01` rule for Rule A candidates.
  Reason: immaterial row differences up to 1% of current assets may use the best
  identity row, while a failed 1% identity fit still remains ambiguous; the
  existing `IDENTITY_TOL` and `IDENTITY_MARGIN` values are unchanged.
- Implemented the owner-approved value-based duplicate resolution for required
  balance-sheet items. Identity winners require at least three periods within
  1% and a 5x mean-error margin; these named values live in
  `config/screener.yaml` so later changes cannot be hidden in source code.
- Added the safety rule that duplicated identity inputs may be collapsed only
  when their reported values are identical in every period; conflicting inputs
  produce `REQUIRED_ITEM_AMBIGUOUS` rather than extending the search or guessing.
- Recorded the real VCI duplicate-`item_id` investigation for VNM, HPG, FPT,
  and VCB in `docs/SPRINT_3_DUPLICATE_ITEM_ID_INVESTIGATION.md`.
- Documented the root cause in pinned `vnstock==4.0.3`: distinct provider fields
  can collapse to the same normalized English display-name identifier while the
  supported public output drops the original provider field and parent context.
- Added the approved weekly point-in-time selection rule: keep the 30/60/90-day
  lags, select only `available_from <= as_of`, and use
  `NO_NEW_FINANCIAL_REPORT` as an explanation without changing valid data from
  `data_status=OK`.
- Added the approved whitelist-normalization policy and coverage definition, but
  did not implement them because the minimum confirmed NOA/SNOA required items
  `short_term_investments` and `preferred_shares` were duplicated for VNM, HPG,
  and FPT.
- Recorded that `provider_item_id` remains a proposal only; the schema is
  unchanged pending a supported public identifier and real smoke verification.
- Kept Sprint 3 incomplete, the draft PR unmerged, and Sprint 4 not started.

## 2026-07-14

- Added `src/data/finance_client.py` on the public `vnstock.api.Finance`
  interface with fixture-tested quarterly/yearly balance sheet, income
  statement, and cash-flow retrieval.
- Added LONG-to-tidy normalization keyed on `item_id`, conservative
  `available_from` lags, raw-VND magnitude checks, explicit error statuses,
  secret redaction, and content-addressed immutable observations.
- Added full-universe point-in-time snapshots under
  `data/snapshots/YYYY-MM-DD/`; limited diagnostic runs are excluded and
  conflicting same-date observations fail explicitly.
- Corrected market-cap proxy units to shares × price × 1000 and renamed the
  source marker to `SHARES_X_LAST_CLOSE_X1000_PROXY`.
- Added explicit market-cap request limits to M0 and weekly runtime paths;
  weekly live market-cap requests now default to zero.
- Added `scripts/smoke_vnstock_finance.py` for the separate ≥3 ticker live API
  check, including raw response shape and returned-period evidence.
- Preserved raw financial responses before normalization and added redacted
  `failure.json` evidence when validation rejects a response.
- Ran the public VCI smoke path for VNM, FPT, and VCB: 12/18 requests normalized;
  six balance-sheet responses failed honestly because provider `item_id` values
  were duplicated. All raw responses returned exactly 4 periods.
- Probed the public KBS finance source for VNM quarterly balance sheet; it
  returned an empty `[0, 0]` response with 0 periods and `MISSING_DATA`.
- Verified VNM Q1 2026 net sales against CafeF at `16,148,657,871,623` raw VND.
- Documented a VNM 2020 corporate-action comparison showing that historical VCI
  OHLC is retroactively adjusted rather than raw.
- Added fixture-only finance tests covering all statement types, 30/60/90-day
  lags, missing values, duplicate keys, unit traps, cache immutability,
  `API_ERROR`, `STALE_DATA`, secret redaction, and public API routing.
- Upgraded `data_contract.md` to v2 for fundamentals, snapshots, price units,
  provider findings, restatement bias, and unresolved price-adjustment status.
- Added `docs/SPEC_SPRINT_3.md` for the financial-statement data layer,
  point-in-time availability rules, universe snapshots, controlled market-cap
  retrieval, price-unit verification, and explicit Sprint 3 exclusions.
- Expanded `AGENTS.md` with the master-plan constraints, non-coder spec review
  requirement, and GitHub secret-safety publishing rules.
- Hardened `.gitignore` against local Python environments, `.env` secrets, and
  private key files while allowing a non-secret `.env.example` template.

## 2026-07-05

- Added Sprint 2.7 web driver research archive and cross-check workflow.
- Added driver research schema, ChatGPT web research prompt, and cross-check guide.
- Added scripts to build driver research placeholders, validate saved research, and summarize research status.
- Updated weekly workflow to create `driver_research_todo.md` and pending driver research placeholders.
- Added tests for driver research template generation, validation, summary, and workflow integration.
- Added Sprint 2.5 weekly analyst workflow documentation.
- Added ChatGPT handoff template and handoff builder.
- Added weekly workflow script for existing-report validation and handoff generation.
- Added sample final AI sector report structure without market conclusions.
- Added tests for handoff and weekly workflow safety.
- Added Sprint 2.4 AI analyst report template, prompt, web research checklist, and validation checklist.
- Added AI package validator for required files, schemas, sector counts, driver map counts, and metadata consistency.
- Added tests for AI package validation and AI report documentation safety.
- Added Sprint 2.3 AI-ready weekly package outputs: `AI_INPUT_SUMMARY.md`, `README_FOR_AI.md`, `sector_cycle_signals.csv`, and `sector_driver_map.csv`.
- Added deterministic candidate sector-cycle labels with confidence and warning flags.
- Added sector-level driver map for later public web research without fetching or inventing live driver values.
- Updated weekly metadata and report text to expose AI-package status while keeping cap-weight skipped when market-cap coverage is incomplete.
- Added Sprint 2.2 market-cap investigation support in weekly reporting.
- Added weekly market-cap enrichment from company overview with `SOURCE_REPORTED_MARKET_CAP` and `SHARES_X_LAST_CLOSE_PROXY` markers.
- Added controlled cap-weight skip fields: market-cap coverage, `cap_weight_status`, and `cap_weight_reason`.
- Updated market-cap source markers and tests to avoid unflagged proxy data.
- Hardened Sprint 2.1 weekly OHLCV fetch accounting with fetched/cached/stale/API_ERROR counts.
- Added quote-source fallback for ticker and index history fetches.
- Added `UNIVERSE_EQUAL_WEIGHT_PROXY` relative-strength fallback when VNINDEX/VN30 are unavailable.
- Extended `data_quality.csv` with cache/stale/error tickers, `index_source`, and `cap_weight_available`.
- Clarified in the weekly report that cap-weight returns remain `N/A (MISSING_DATA)` when M0 `market_cap` is blank.
- Added Sprint 2.1 unit tests for index proxy fallback, data-quality cache/error fields, and report context.

## 2026-07-04

- Added M0 hardening documentation in `docs/SPEC_MVP.md`.
- Added `data_contract.md` for universe and reject output schemas.
- Confirmed dependency and project metadata files are line-formatted and valid.
- Kept scope limited to M0 universe building and fixture-based tests.
- Switched the vnstock wrapper defaults to VCI for listing, quote, and company data.
- Added VCI long-format ICB pivoting into `icb2/icb3/icb4`.
- Added `UNSUPPORTED_EXCHANGE` rejection for stock rows outside HOSE/HNX/UPCOM.
- Added market cap proxy support with `mktcap_shares_x_close_proxy` source marker.
- Added mock tests for real VCI API shapes and a real API smoke script.
- Verified `scripts/smoke_vnstock.py` against real VCI API: 3,467 raw symbol rows, 1,745 stock rows, 7,748 raw ICB rows, and 1,745 tickers mapped to ICB2.
- Added `--limit` runtime option, slower sequential request pacing, per-run raw/stock/ICB2 summary counts, and soft-stop handling for consecutive API errors.
- Fixed VCI price-history unit handling for ADTV proxy by using `close * volume * 1000` when prices are quoted in thousand VND.
- Made market cap fetching optional via `--fetch-market-cap` to reduce M0 API pressure; default outputs leave `market_cap` blank instead of fabricating it.
- Verified full `scripts/run_universe.py` run: 3,467 raw symbols, 1,745 stock symbols, 1,729 tickers with ICB2, 378 accepted rows, 1,367 rejected rows, and all 19 ICB2 sectors covered. Top rejects were `LOW_LIQUIDITY`, `UNSUPPORTED_EXCHANGE`, `MISSING_PRICE_6M`, and 1 `API_ERROR`.
- Added Sprint 2 MVP `scripts/run_weekly_mvp.py` and `src/weekly.py` for indicator-only weekly ICB2 sector reporting.
- Added Sprint 2 outputs under `reports/<YYYY-MM-DD>/`: `WEEKLY_REPORT.md`, `sector_summary.csv`, `sector_indicators_tier1.csv`, `data_quality.csv`, and `run_metadata.json`.
- Added sector-level tier 1 indicators: equal-weight returns, optional cap-weight returns, VN-Index relative strength, MA breadth, 52w drawdown/low distance, liquidity trend, and non-annualized 20d volatility.
- Added data quality coverage gates and `confidence_lite` as a data-confidence measure, not an investment score.
- Added Sprint 2 unit tests for indicators, missing-data handling, report safety, quality coverage, and run metadata.
