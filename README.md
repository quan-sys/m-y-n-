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

## Run Tests

```bash
pytest
```

Tests use local fixtures only and must not call the real `vnstock` API.

## Data Contract

See `data_contract.md` for output schemas, valid `reject_reason` values, valid `data_status` values, and no-fabrication rules.

## Current Limits

- The project currently covers M0 universe building only.
- ICB classification quality depends on public source coverage or explicit rows in `config/icb_overrides.csv`.
- Public data sources can be missing, stale, delayed, wrong, or temporarily unavailable.
- Missing data is rejected or marked; the pipeline must not invent financial values.
- M0 does not include indicators, scoring, weekly reports, BCTC, valuation, Tier 2 drivers, dashboards, or transaction recommendations.
- Live API calls run sequentially with random sleep, per-ticker cache/resume, and a soft stop after consecutive ticker-level API errors.
- `market_cap` can be blank in default M0 runs; blank means missing/not fetched data, not a fabricated value.
