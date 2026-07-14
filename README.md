# sector-cycle-monitor

Python data pipeline for monitoring Vietnam equity sector cycles. M0 builds the
stock universe and reject log. Sprint 2 adds an indicator-only weekly sector
report. Sprint 3 adds the financial-statement data foundation and forward-only
point-in-time snapshots; it still does not compute screener formulas,
portfolios, backtests, price targets, or transaction advice.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run M0

```bash
python scripts/run_universe.py
```

The script writes:

- `data/universe.csv`
- `data/universe_rejects.csv`
- `data/snapshots/<YYYY-MM-DD>/` for a complete, non-limited run

For a smaller runtime check:

```bash
python scripts/run_universe.py --limit 20
python scripts/run_universe.py --limit 100
```

Market cap fetching is disabled by default to reduce M0 API rate-limit pressure.
It requires an explicit controlled batch limit:

```bash
python scripts/run_universe.py --fetch-market-cap --market-cap-limit 20
```

Runs using `--limit` are diagnostic slices and do not create canonical
point-in-time snapshots.

## Smoke Test Vnstock

```bash
python scripts/smoke_vnstock.py
```

The smoke test checks the real VCI symbol and ICB shapes without building the full universe.

## Run Sprint 2 Weekly MVP

```bash
python scripts/run_weekly_mvp.py
```

Weekly live market-cap requests default to zero. To allow a controlled batch:

```bash
python scripts/run_weekly_mvp.py --market-cap-limit 20
```

The script reads `data/universe.csv`, fetches/resumes OHLCV cache for accepted tickers, aggregates indicators by ICB2 sector, and writes:

- `reports/<YYYY-MM-DD>/WEEKLY_REPORT.md`
- `reports/<YYYY-MM-DD>/sector_summary.csv`
- `reports/<YYYY-MM-DD>/sector_indicators_tier1.csv`
- `reports/<YYYY-MM-DD>/data_quality.csv`
- `reports/<YYYY-MM-DD>/run_metadata.json`

Sprint 2.3 adds an AI-ready sector package in the same report folder:

- `reports/<YYYY-MM-DD>/AI_INPUT_SUMMARY.md`
- `reports/<YYYY-MM-DD>/README_FOR_AI.md`
- `reports/<YYYY-MM-DD>/sector_cycle_signals.csv`
- `reports/<YYYY-MM-DD>/sector_driver_map.csv`

These files prepare structured sector-level inputs for later AI analysis. They do not add stock ranking, valuation, BCTC analysis, external driver values, or transaction advice.

## Sprint 2.4 — AI Analyst Template & Validation

Sprint 2.4 adds safe templates and validation for later ChatGPT sector-level reasoning:

- `docs/AI_ANALYST_REPORT_TEMPLATE.md`
- `docs/AI_ANALYST_PROMPT.md`
- `docs/SECTOR_DRIVER_WEB_RESEARCH_CHECKLIST.md`
- `docs/AI_REPORT_VALIDATION_CHECKLIST.md`
- `scripts/validate_ai_package.py`

Run validation:

```bash
python scripts/validate_ai_package.py reports/<YYYY-MM-DD>
```

Run tests:

```bash
pytest
```

This sprint does not create an end-to-end weekly workflow, a final AI market report, stock ranking, target prices, or buy/sell recommendations.

## Sprint 2.5 — End-to-End Weekly Analyst Workflow

Sprint 2.5 adds a weekly workflow for validating an AI-ready package and building a ChatGPT handoff:

- `docs/WEEKLY_ANALYST_WORKFLOW.md`
- `docs/HANDOFF_TO_CHATGPT_TEMPLATE.md`
- `scripts/build_chatgpt_handoff.py`
- `scripts/run_weekly_workflow.py`
- `docs/SAMPLE_FINAL_AI_SECTOR_REPORT_STRUCTURE.md`

Validate existing report and build ChatGPT handoff:

```bash
python scripts/run_weekly_workflow.py --existing-report reports/<YYYY-MM-DD>
```

Or build handoff directly:

```bash
python scripts/build_chatgpt_handoff.py reports/<YYYY-MM-DD>
```

This sprint does not run ChatGPT, does not web search, does not generate final market analysis automatically, and does not provide buy/sell recommendations.

## Sprint 2.7 — Web Driver Research Archive & Cross-check

Sprint 2.7 adds structured storage for driver web research after ChatGPT/user research is done:

- `docs/WEB_DRIVER_RESEARCH_WORKFLOW.md`
- `docs/DRIVER_RESEARCH_SCHEMA.md`
- `docs/CHATGPT_WEB_RESEARCH_PROMPT.md`
- `docs/DRIVER_CROSSCHECK_GUIDE.md`
- `scripts/build_driver_research_template.py`
- `scripts/validate_driver_research.py`
- `scripts/summarize_driver_research.py`

Build driver research placeholders:

```bash
python scripts/build_driver_research_template.py reports/<YYYY-MM-DD>
```

Validate saved research:

```bash
python scripts/validate_driver_research.py reports/<YYYY-MM-DD>
```

Summarize saved research:

```bash
python scripts/summarize_driver_research.py reports/<YYYY-MM-DD>
```

This sprint does not web search, does not call an AI API, does not invent driver data, and does not provide transaction advice.

Sprint 2.1 hardens this run by:

- skipping fresh per-ticker OHLCV cache hits and logging fetched/cached/stale/API_ERROR counts;
- using stale OHLCV cache with `STALE_DATA` when a new fetch fails;
- trying a quote-source fallback for ticker and index history fetches;
- using `UNIVERSE_EQUAL_WEIGHT_PROXY` for relative strength when VNINDEX/VN30 are unavailable;
- adding `cached_price_count`, `stale_price_count`, `api_error_tickers`, `index_source`, and `cap_weight_available` to `data_quality.csv`.

Sprint 2.2 checks market-cap availability in the weekly run:

- direct company overview market cap is marked `SOURCE_REPORTED_MARKET_CAP`;
- share-count times close times `1000` fallback is marked `SHARES_X_LAST_CLOSE_X1000_PROXY`;
- cap-weight returns stay `N/A (MISSING_DATA)` unless market-cap coverage is complete for the sector return window;
- controlled skips are marked with `cap_weight_status=SKIPPED_MISSING_MARKET_CAP` and a reason in `data_quality.csv`.

For a quick local check only:

```bash
python scripts/run_weekly_mvp.py --limit-sectors 3
```

## Sprint 3 — Financial Statements and Point-in-Time Data

Sprint 3 adds:

- `src/data/finance_client.py`, built on the public `vnstock.api.Finance`
  interface;
- balance sheet, income statement, and cash-flow retrieval for quarterly and
  yearly periods;
- LONG-to-tidy normalization keyed on `item_id`;
- content-addressed raw and normalized caches under `data/fundamentals/`;
- `report_period`, `period_end`, and conservative `available_from` dates;
- full-universe snapshots under `data/snapshots/YYYY-MM-DD/`;
- controlled market-cap request limits and the required price `×1000` unit
  conversion;
- fixture-only unit tests and a separate live finance smoke command.

Run the explicit live finance smoke test on at least three tickers:

```bash
python scripts/smoke_vnstock_finance.py --tickers VNM FPT VCB
```

Tests never execute this live command. The smoke output is local and ignored by
Git.

The current pinned public API returns only the 4 most recent statement periods
by default. A supported public longer-history path has not yet been confirmed.
The `ratio` endpoint is forbidden because its verified headers are corrupted.

Financial statements are raw VND, while VCI prices are thousands of VND. Any
price-times-shares or price-times-fundamentals calculation multiplies price by
`1000` exactly once.

The API has no publication-date field, so availability uses conservative legal
lags: quarter 30 days, semiannual 60 days, and annual 90 days. Historical
statements may be restated; downloading them today does not recreate what an
investor knew at the original date.

The documented VNM 2020 corporate-action comparison shows that historical VCI
OHLC is retroactively adjusted, not a raw historical price series. It must not
be combined with historical share counts to create raw historical market cap.

The 2026-07-14 live finance run completed all 18 requests for VNM, FPT, and VCB.
Twelve income-statement and cash-flow requests normalized successfully. Six
balance-sheet responses were preserved but rejected because the provider
reused `item_id` values, which violates the approved unique-key contract. The
pipeline does not sum those rows or substitute names as keys.

The VNM Q1 2026 `net_sales` value matched CafeF exactly at
`16,148,657,871,623` raw VND. Full-universe ≥90% coverage remains open, so
Sprint 3 is not yet declared complete.

## Run Tests

```bash
pytest
```

Tests use local fixtures only and must not call the real `vnstock` API.

## Data Contract

See `data_contract.md` for output schemas, valid `reject_reason` values, valid `data_status` values, and no-fabrication rules.

## Current Limits

- The project currently covers M0 universe building and Sprint 2 indicator-only weekly reporting.
- ICB classification quality depends on public source coverage or explicit rows in `config/icb_overrides.csv`.
- Public data sources can be missing, stale, delayed, wrong, or temporarily unavailable.
- Missing data is rejected or marked; the pipeline must not invent financial values.
- Sprint 2 does not include formal scoring, BCTC, valuation, Tier 2 drivers, deep-dive analysis, dashboards, or transaction advice.
- Live API calls run sequentially with random sleep, per-ticker cache/resume, and a soft stop after consecutive ticker-level API errors.
- `market_cap` can be blank in default M0 runs; blank means missing/not fetched data, not a fabricated value.
- If `market_cap` is blank, Sprint 2 cap-weight indicators are reported as `N/A (MISSING_DATA)` rather than silently falling back to equal-weight.
- If VNINDEX/VN30 history is unavailable, Sprint 2.1 reports relative strength versus the `UNIVERSE_EQUAL_WEIGHT_PROXY` and flags that source explicitly.
- Sprint 2.2 does not fabricate share counts or use zero-filled market caps; cap-weight is skipped when reliable coverage is incomplete.
- Sprint 2.3 adds deterministic candidate cycle labels and a sector driver checklist for later public web research; these are inputs, not final analytical conclusions.
- Historical financial statements from vnstock may be restated and are not
  clean historical point-in-time evidence.
- Financial-sector statement schemas remain separate; Sprint 3 does not
  force-normalize or exclude them.
- Sprint 3 does not implement accruals, M-Score, F-Score, valuation, portfolio
  construction, backtesting, dashboards, machine learning, or GitHub Actions.
