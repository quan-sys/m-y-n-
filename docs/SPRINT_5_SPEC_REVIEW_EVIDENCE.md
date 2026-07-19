# Sprint 5 specification review evidence

Date: `2026-07-19`

## Main merge proof

- Freshly fetched `origin/main`: `db845e3d2e467523d12d8771c78f84ed17606bfa`.
- Branch created from that exact SHA: `agent/sprint5-step2-valuation-spec`.
- `docs/REPORT_SPRINT_4_CLEANING.md` exists on `origin/main`: PASS.
- `data/screener/step1_survivors.csv` exists on `origin/main`: PASS.
- `docs/SPEC_SPRINT_4.md` on `origin/main` contains `HIGH_ACCRUAL — UNION rule`: PASS.

These three checks independently prove the required Sprint 4 outputs and binding rule are present on merged main before Sprint 5 specification work begins.

## Sources opened before writing

- `AGENTS.md` (read fully)
- `05_ANTI_SLOPPY_RULES.md` (not present; verified by repository file search)
- `data_contract.md` (read fully)
- `config/screener.yaml` (read fully)
- `CHANGELOG.md` (read fully)
- `docs/SPEC_SPRINT_4.md` (read fully)
- `docs/REPORT_SPRINT_4_CLEANING.md` (read fully)
- `data/screener/step1_survivors.csv` (156 rows independently counted)
- `D:/download/học/PLAN_quant_screener_myn.md` (Sprint 5 binding section)
- `src/data/finance_client.py`
- `src/data/vnstock_client.py`
- `src/universe.py`
- Actual normalized quarterly cache files under `data/fundamentals/<ticker>/<statement>/quarter/`; schema and available item IDs were inspected from the stored parquet data.
- Existing market/price/share cache locations and repository references were searched; `src/data/cache/` contains only `.gitkeep` on this branch.

No formula or data definition was taken from a Codex summary or from memory.

## Open owner questions

1. **EBIT DEFINITION:** choose between the direct `operating_profit_loss` construction and the `net_accounting_profit_loss_before_tax + interest_expenses` construction. Both have joint four-quarter field coverage of 154/156, but they have different accounting scope.
2. **E/P EARNINGS DEFINITION:** choose between `net_profit_loss_after_tax` and `attributable_to_parent_company`. Both have four-quarter field coverage of 154/156; whole-company market capitalization must be paired with whole-company earnings.

Production for both candidates remains blocked pending owner approval. Independently, usable market-cap coverage is 0/156, so the cache-only readiness conclusion is `FAIL`.

## Exact changed-file list

```text
CHANGELOG.md
data/screener/sprint5_readiness_audit.csv
docs/SPEC_SPRINT_5.md
docs/SPRINT_5_DATA_READINESS.md
docs/SPRINT_5_SPEC_REVIEW_EVIDENCE.md
docs/SPRINT_5_SPEC_TEST_LOG.txt
scripts/audit_sprint5_readiness.py
tests/test_sprint5_readiness.py
```

## Exact diff stat

```text
 CHANGELOG.md                              |   4 +
 data/screener/sprint5_readiness_audit.csv | 157 ++++++++++++
 docs/SPEC_SPRINT_5.md                     | 132 ++++++++++
 docs/SPRINT_5_DATA_READINESS.md           |  97 ++++++++
 docs/SPRINT_5_SPEC_REVIEW_EVIDENCE.md     |  78 ++++++
 docs/SPRINT_5_SPEC_TEST_LOG.txt           |  13 +
 scripts/audit_sprint5_readiness.py        | 404 ++++++++++++++++++++++++++++++
 tests/test_sprint5_readiness.py           | 147 +++++++++++
 8 files changed, 1032 insertions(+)
```

## Scope confirmation

- No Sprint 3 or Sprint 4 code, test, specification, configuration, cache, or output changed.
- No dependency changed.
- No production EBIT, TEV, E/P, ranking, percentile, cheap set, or candidate list was computed.
- No live API call or refetch occurred.
- Only the eight paths explicitly allowed by the task changed.

## Test evidence

The full unfiltered suite command, exact stdout, stderr, and exit code are recorded in `docs/SPRINT_5_SPEC_TEST_LOG.txt`. Exit code: `0`.
