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

## Run Tests

```bash
pytest
```

Tests use local fixtures only and must not call the real `vnstock` API.

## Current Limits

- M0 only creates the repository skeleton, `vnstock` wrapper, universe builder, output CSV files, and tests.
- ICB classification quality depends on public source coverage or explicit rows in `config/icb_overrides.csv`.
- Public data sources can be missing, stale, delayed, wrong, or temporarily unavailable.
- Missing data is rejected or marked; the pipeline must not invent financial values.
