# Changelog

## 2026-07-14

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
