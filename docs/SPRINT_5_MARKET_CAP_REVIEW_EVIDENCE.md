# Sprint 5 market-cap review evidence

- Current main SHA: `f75919882899f354074f4a15bd2196e92d7ca812`.
- Branch: `agent/sprint5-market-cap-foundation`.
- Survivor input: 156 rows / 156 unique tickers.
- Probe command: `python scripts/fetch_sprint5_market_cap.py --evaluation-date 2026-07-19 --probe-only`.
- Cache-only reassessment command: `python scripts/fetch_sprint5_market_cap.py --evaluation-date 2026-07-19 --probe-only --cache-only`.
- Interest investigation command: `python scripts/investigate_sprint5_interest_sign.py`.
- Actual public-method calls: 12 (four before the serialization failure, then eight in the completed probe).
- Full-universe cache hits: 0; 12 probe evidence records were reused locally for reassessment and are reported separately.
- Output market-cap rows: 0; unique market-cap tickers: 0. Stop condition 2 prohibited the 156-ticker fetch and snapshot.
- Direct/proxy/selected coverage: 0/156, 0/156, 0/156.
- No valuation, EBIT, TEV, EBIT/TEV, E/P, ranking, percentile, cheap set, or candidate list was run.
- No secret, credential, token, cookie, authentication material, or machine-specific path is committed.

## Files opened

`AGENTS.md`; owner-source files `05_ANTI_SLOPPY_RULES.md`, `PLAN_quant_screener_myn.md`, and `REQUIRED_ITEMS_v1_draft.md`; `data_contract.md`; `docs/SPEC_SPRINT_5.md`; `docs/SPRINT_5_DATA_READINESS.md`; `docs/SPRINT_5_SPEC_REVIEW_EVIDENCE.md`; `scripts/audit_sprint5_readiness.py`; `data/screener/sprint5_readiness_audit.csv`; `data/screener/step1_survivors.csv`; `src/data/vnstock_client.py`; `src/universe.py`; `src/weekly.py`; `tests/test_universe.py`; `tests/test_real_api_shapes.py`; `tests/test_weekly.py`; installed public `vnstock` Company/Trading adapters and VCI/KBS provider mappings; and the preserved raw/normalized quarterly income-statement cache plus metadata for HAG, IDI, and DTD.

## Changed files

```text
CHANGELOG.md
data/market_cap/2026-07-19/probe_public_methods.jsonl
data/market_cap/2026-07-19/probe_summary.json
data_contract.md
docs/SPEC_SPRINT_5.md
docs/SPRINT_5_INTEREST_SIGN_INVESTIGATION.md
docs/SPRINT_5_MARKET_CAP_REPORT.md
docs/SPRINT_5_MARKET_CAP_REVIEW_EVIDENCE.md
docs/SPRINT_5_MARKET_CAP_TEST_LOG.txt
scripts/fetch_sprint5_market_cap.py
scripts/investigate_sprint5_interest_sign.py
tests/test_sprint5_interest_sign.py
tests/test_sprint5_market_cap.py
```

## Diff stat

```text
 CHANGELOG.md                                       |   1 +
 .../2026-07-19/probe_public_methods.jsonl          |  12 +
 data/market_cap/2026-07-19/probe_summary.json      |  15 +
 data_contract.md                                   |   8 +
 docs/SPEC_SPRINT_5.md                              |  15 +
 docs/SPRINT_5_INTEREST_SIGN_INVESTIGATION.md       |  28 ++
 docs/SPRINT_5_MARKET_CAP_REPORT.md                 |  44 +++
 docs/SPRINT_5_MARKET_CAP_REVIEW_EVIDENCE.md        |  63 ++++
 docs/SPRINT_5_MARKET_CAP_TEST_LOG.txt              |  49 ++++
 scripts/fetch_sprint5_market_cap.py                | 318 +++++++++++++++++++++
 scripts/investigate_sprint5_interest_sign.py       | 174 +++++++++++
 tests/test_sprint5_interest_sign.py                |  22 ++
 tests/test_sprint5_market_cap.py                   |  39 +++
 13 files changed, 788 insertions(+)
```

## Commands and compact results

The first probe attempt stopped while serializing a list-valued DataFrame attribute after four VCI public-method calls. Exact error: `ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()`. The serialization helper was corrected without changing any financial acceptance rule. The completed eight-call probe wrote 12 evidence records and returned `contract_passed=false`. The cache-only reassessment reused all 12 records and returned the same result without a provider call.

The interest investigation read 12 cached ticker-quarter observations and returned HAG=`SOURCE_AMBIGUOUS`, IDI=`SOURCE_AMBIGUOUS`, DTD=`SOURCE_AMBIGUOUS`; EBIT sign gate=`INTEREST_EXPENSE_SIGN_AMBIGUOUS`.

Test commands and exact raw results are preserved in `docs/SPRINT_5_MARKET_CAP_TEST_LOG.txt`.
