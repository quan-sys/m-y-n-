# SPEC MVP - M0 Hardening

This file is the local source of truth because `SPEC_CODEX_may_theo_doi_chu_ky_nganh.md` is not present in this repository.

## Scope

M0 is limited to:

- Repository skeleton.
- `vnstock` data wrapper.
- Universe builder.
- `data/universe.csv` and `data/universe_rejects.csv`.
- Fixture-based unit tests.
- Local run script.
- Data contract and changelog.

M0 must not include indicators, scoring, weekly reports, BCTC, Tier 2 drivers, deep-dive analysis, dashboards, databases, or GitHub Actions.

## Data Rules

- Never fabricate financial data.
- Every output row must include `source`, `as_of`, and `data_status`.
- Missing data must be marked as `MISSING_DATA`.
- API failures must be marked as `API_ERROR`.
- Stale cache data must be marked as `STALE_DATA`.
- Rejected symbols must always have a non-empty `reject_reason`.
- Tests must not call real APIs.

## Required Output Schema

Both `data/universe.csv` and `data/universe_rejects.csv` must use:

```text
ticker
exchange
icb2
icb3
icb4
market_cap
adtv_20d
status
reject_reason
as_of
source
data_status
```

`universe.csv` should contain only `ACCEPTED` rows. `universe_rejects.csv` should contain only `REJECTED` rows.

## Required Local Checks

```bash
python -m py_compile src/universe.py src/data/vnstock_client.py scripts/run_universe.py
pip install -r requirements.txt
pytest
python scripts/run_universe.py
```
