# sector-cycle-monitor

Python data pipeline for monitoring Vietnam equity sector cycles. M0 builds the stock universe and reject log. Sprint 2 adds an indicator-only weekly sector report; it does not compute formal scores, dashboards, valuation, BCTC, target prices, or transaction advice.

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

For a smaller runtime check:

```bash
python scripts/run_universe.py --limit 20
python scripts/run_universe.py --limit 100
```

Market cap fetching is disabled by default to reduce M0 API rate-limit pressure. Enable it only when needed:

```bash
python scripts/run_universe.py --fetch-market-cap
```

## Smoke Test Vnstock

```bash
python scripts/smoke_vnstock.py
```

The smoke test checks the real VCI symbol and ICB shapes without building the full universe.

## Run Sprint 2 Weekly MVP

```bash
python scripts/run_weekly_mvp.py
```

The script reads `data/universe.csv`, fetches/resumes OHLCV cache for accepted tickers, aggregates indicators by ICB2 sector, and writes:

- `reports/<YYYY-MM-DD>/WEEKLY_REPORT.md`
- `reports/<YYYY-MM-DD>/sector_summary.csv`
- `reports/<YYYY-MM-DD>/sector_indicators_tier1.csv`
- `reports/<YYYY-MM-DD>/data_quality.csv`
- `reports/<YYYY-MM-DD>/run_metadata.json`

For a quick local check only:

```bash
python scripts/run_weekly_mvp.py --limit-sectors 3
```

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
