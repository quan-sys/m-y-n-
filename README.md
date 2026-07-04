# sector-cycle-monitor

Python data pipeline skeleton for monitoring Vietnam equity sector cycles. M0 only builds the stock universe and reject log; it does not compute indicators, scores, reports, dashboards, or investment recommendations.

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

## Run Sprint 2 Weekly MVP

```bash
python scripts/run_weekly_mvp.py
```

The script reads `data/universe.csv` and writes `reports/<YYYY-MM-DD>/WEEKLY_REPORT.md`, `sector_summary.csv`, `sector_indicators_tier1.csv`, `data_quality.csv`, and `run_metadata.json`.

## Run Tests

```bash
pytest
```

Tests use local fixtures only and must not call the real `vnstock` API.

## Data Contract

See `data_contract.md` for output schemas, valid `reject_reason` values, valid `data_status` values, and no-fabrication rules.

## Current Limits

- The project currently covers M0 universe building and Sprint 2 Tier 1 market-only weekly reporting.
- ICB classification quality depends on public source coverage or explicit rows in `config/icb_overrides.csv`.
- Public data sources can be missing, stale, delayed, wrong, or temporarily unavailable.
- Missing data is rejected or marked; the pipeline must not invent financial values.
- The weekly MVP does not include BCTC, valuation, Tier 2 drivers, formal scoring, dashboards, or transaction recommendations.
