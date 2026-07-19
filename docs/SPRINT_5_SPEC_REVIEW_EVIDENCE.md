# Sprint 5 specification review evidence

Date: `2026-07-19`

## Main merge proof

- Freshly fetched `origin/main` before this correction: `db845e3d2e467523d12d8771c78f84ed17606bfa`.
- Freshly fetched PR #5 HEAD before this correction: `12b3c49b42f3b8f49477844b94d7bcdc0cb2e7d3`.
- Neither ref had moved from the independently verified state in the owner prompt; there were no new commits to list.
- Branch: `agent/sprint5-step2-valuation-spec`; `origin/main` is its ancestor.
- `docs/REPORT_SPRINT_4_CLEANING.md` exists on `origin/main`: PASS.
- `data/screener/step1_survivors.csv` exists on `origin/main`: PASS.
- `docs/SPEC_SPRINT_4.md` on `origin/main` contains `HIGH_ACCRUAL — UNION rule`: PASS.

These three checks independently prove the required Sprint 4 outputs and binding rule are present on merged main before Sprint 5 specification work begins.

## Sources opened before writing

- `AGENTS.md` (read fully)
- `D:/download/học/05_ANTI_SLOPPY_RULES.md` (read fully)
- `data_contract.md` (read fully)
- `config/screener.yaml` (read fully)
- `CHANGELOG.md` (read fully)
- `docs/SPEC_SPRINT_4.md` (read fully)
- `docs/REPORT_SPRINT_4_CLEANING.md` (read fully)
- `data/screener/step1_survivors.csv` (156 rows independently counted)
- `D:/download/học/PLAN_quant_screener_myn.md` (Sprint 5 binding section)
- `D:/download/học/REQUIRED_ITEMS_v1_draft.md` (read fully)
- `src/data/finance_client.py`
- `src/data/vnstock_client.py`
- `src/universe.py`
- Actual normalized quarterly cache files under `data/fundamentals/<ticker>/<statement>/quarter/`; schema and available item IDs were inspected from the stored parquet data.
- Existing market/price/share cache locations and repository references were searched; `src/data/cache/` contains only `.gitkeep` on this branch.

All 156 actual normalized quarterly income-statement cache files selected by the audit were opened by the cache-only sign scan. No formula or data definition was taken from a PR body, Codex/Claude summary, or memory.

## Owner-approved definitions and sign result

1. **EBIT economic definition:** `EBIT_PROXY_VAS = TTM(net_accounting_profit_loss_before_tax) + TTM(interest_expense_magnitude)`; `operating_profit_loss` is not a production input.
2. **E/P production definition:** `TTM(attributable_to_parent_company) / current_parent_equity_market_cap`; `net_profit_loss_after_tax` remains diagnostic only.
3. **Interest sign evidence:** 3 positive, 568 negative, 51 zero, and 2 missing quarter values; HAG, IDI, and DTD have mixed non-zero signs; duplicate ticker count is 0.

The economic EBIT definition is approved but its production sign normalization is `OPEN QUESTION: INTEREST_EXPENSE_SIGN_AMBIGUOUS`; usable market-cap coverage remains 0/156, so readiness remains `FAIL`.

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
 CHANGELOG.md                              |   5 +
 data/screener/sprint5_readiness_audit.csv | 157 +++++++++
 docs/SPEC_SPRINT_5.md                     | 145 ++++++++
 docs/SPRINT_5_DATA_READINESS.md           | 133 ++++++++
 docs/SPRINT_5_SPEC_REVIEW_EVIDENCE.md     |  82 +++++
 docs/SPRINT_5_SPEC_TEST_LOG.txt           |  40 +++
 scripts/audit_sprint5_readiness.py        | 546 ++++++++++++++++++++++++++++++
 tests/test_sprint5_readiness.py           | 230 +++++++++++++
 8 files changed, 1338 insertions(+)
```

## Scope confirmation

- No Sprint 3 or Sprint 4 code, test, specification, configuration, cache, or output changed.
- No dependency changed.
- No production EBIT, TEV, E/P, ranking, percentile, cheap set, or candidate list was computed.
- No live API call or refetch occurred.
- Only the eight paths explicitly allowed by the task changed.

## Test evidence

All three required commands with exact stdout, stderr, and exit codes are recorded in `docs/SPRINT_5_SPEC_TEST_LOG.txt`; fixture tests show behavior on those fixtures but do not prove financial correctness for every real company. Both `py_compile` and full `pytest` exited `0`.
