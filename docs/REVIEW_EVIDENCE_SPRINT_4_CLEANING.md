# Review evidence — Sprint 4 Step 1 CLEANING

## 1. Starting and final HEAD

- Reviewer-approved starting HEAD for the PFD/future-date review fix: `70e161ff345f37b66a1717a9200187a9dd37646e`.
- Original cleaning implementation commits: `f5dd55e` and `70e161f`.
- Final HEAD is the commit containing this evidence file. Its exact SHA is reported by PR #4 and the required five-line owner handoff; a commit cannot contain its own SHA because changing this line changes that SHA.

## 2. Original cleaning implementation commit list

```text
<output/evidence commit containing this file> Write Sprint 4 Step 1 cleaning evidence
f5dd55e Implement Sprint 4 Step 1 cleaning pipeline
d58ae31 Prepare Sprint 4 cleaning data prerequisites
```

## 3. Original cleaning implementation changed-file list

```text
CHANGELOG.md
data/screener/step1_rejects.csv
data/screener/step1_survivors.csv
data/universe_rejects.csv
data_contract.md
docs/DIAG_SECTOR_A_REJECT_MIX_SPRINT_4.csv
docs/DIAG_SECTOR_B_WHATIF_SPRINT_4.csv
docs/REPORT_SPRINT_4_CLEANING.md
docs/REVIEW_EVIDENCE_SPRINT_4_CLEANING.md
docs/TEST_LOG_SPRINT_4_CLEANING.txt
scripts/run_sprint4_step1_cleaning.py
src/screener/step1_pipeline.py
tests/test_step1_pipeline.py
```

## 4. Original cleaning implementation diff stat

```text
 CHANGELOG.md                               |    1 +
 data/screener/step1_rejects.csv            |  223 +++
 data/screener/step1_survivors.csv          |  157 ++
 data/universe_rejects.csv                  | 2958 +++++++++++++++-------------
 data_contract.md                           |   18 +
 docs/DIAG_SECTOR_A_REJECT_MIX_SPRINT_4.csv |   16 +
 docs/DIAG_SECTOR_B_WHATIF_SPRINT_4.csv     |   16 +
 docs/REPORT_SPRINT_4_CLEANING.md           |   57 +
 docs/REVIEW_EVIDENCE_SPRINT_4_CLEANING.md  |  250 +++
 docs/TEST_LOG_SPRINT_4_CLEANING.txt        |  173 ++
 scripts/run_sprint4_step1_cleaning.py      |  157 ++
 src/screener/step1_pipeline.py             |  344 ++++
 tests/test_step1_pipeline.py               |  231 +++
 13 files changed, 3233 insertions(+), 1368 deletions(-)
```

## 5. Original cleaning implementation `origin/main..HEAD` diff stat

```text
 AGENTS.md                                  |   23 +
 CHANGELOG.md                               |    6 +
 config/screener.yaml                       |    3 +
 data/screener/step1_rejects.csv            |  223 +++
 data/screener/step1_survivors.csv          |  157 ++
 data/universe_rejects.csv                  | 2958 +++++++++++++++-------------
 data_contract.md                           |   18 +
 docs/COVERAGE_SPRINT_4_ANNUAL.md           |  346 ++++
 docs/DATA_INPUTS_SPRINT_4_CLEANING.md      |   45 +
 docs/DIAG_SECTOR_A_REJECT_MIX_SPRINT_4.csv |   16 +
 docs/DIAG_SECTOR_B_WHATIF_SPRINT_4.csv     |   16 +
 docs/REPORT_SPRINT_4_CLEANING.md           |   57 +
 docs/REVIEW_EVIDENCE_SPRINT_4_CLEANING.md  |  250 +++
 docs/SPEC_SPRINT_4.md                      |   40 +-
 docs/TEST_LOG_SPRINT_4_CLEANING.txt        |  173 ++
 docs/VNM_FORMULA_CALCULATIONS_SPRINT_4.md  |  135 ++
 docs/VNM_FORMULA_EVIDENCE_SPRINT_4.csv     |   34 +
 scripts/generate_sprint4_vnm_evidence.py   |   69 +
 scripts/run_sprint4_annual_coverage.py     |  526 +++++
 scripts/run_sprint4_step1_cleaning.py      |  157 ++
 src/screener/__init__.py                   |    1 +
 src/screener/step1_cleaning.py             |  522 +++++
 src/screener/step1_data.py                 |  755 +++++++
 src/screener/step1_pipeline.py             |  344 ++++
 tests/test_sprint4_annual_coverage.py      |   79 +
 tests/test_step1_cleaning.py               |  377 ++++
 tests/test_step1_data.py                   |  301 +++
 tests/test_step1_pipeline.py               |  231 +++
 28 files changed, 6487 insertions(+), 1375 deletions(-)
```

## 6. Exact input and filter evidence

- Evaluation date: `2026-07-18`.
- Sprint 3 ACCEPTED input rows: `378` from `data/universe.csv`.
- Formula-stage rows after upstream exclusions: `243`.
- Annual inputs: `data/fundamentals/run_state/sprint4_annual/2026-07-17/normalized`.

| Stage | Filter | Entering | Removed | Removal fraction | Removal % |
|---:|---|---:|---:|---:|---:|
| 1 | FINANCIAL_SECTOR_EXCLUDED | 378 | 63 | 0.16666666666666666 | 16.666666666667% |
| 2 | UPCOM_EXCLUDED_V1 | 315 | 72 | 0.22857142857142856 | 22.857142857143% |
| 3 | HIGH_ACCRUAL | 243 | 42 | 0.1728395061728395 | 17.283950617284% |
| 4 | M_SCORE_FLAG | 201 | 35 | 0.17412935323383086 | 17.412935323383% |
| 5 | PFD_HIGH_RISK | 166 | 10 | 0.060240963855421686 | 6.024096385542% |

- Survivor count: `156`.
- Every one of the `222` rejected tickers is unique and has exactly one primary reason.

## 7. Exact accrual cutoff evidence

- STA valid count: `243`; `k=25`; observed cutoff: `0.23389126844758945`.
- SNOA valid count: `243`; `k=25`; observed cutoff: `0.9859440018428138`.
- STA-only: `17`; SNOA-only: `17`; both: `8`; HIGH_ACCRUAL UNION: `42`.
- Both cutoffs use independent valid higher-tail populations and include every value equal to the observed boundary.

## 8. Exact M-Score and distress evidence

- M-Score rule: strictly `> -1.78`; valid `234`; formula-stage flagged `54`; primary M_SCORE_FLAG rejects after earlier filters `35`.
- Distress formula-stage `high_risk=True`: `13`; primary PFD_HIGH_RISK rejects after earlier filters: `10`.
- HoSE warning missing: `243`; no ticker is rejected solely because the warning is missing.
- Campbell and net-debt/EBITDA are not implemented.

## 9. Formula insufficiency counts

| Formula | Valid | Insufficient |
|---|---:|---:|
| STA | 243 | 0 |
| SNOA | 243 | 0 |
| DSRI | 242 | 1 |
| GMI | 242 | 1 |
| AQI | 241 | 2 |
| SGI | 243 | 0 |
| DEPI | 235 | 8 |
| SGAI | 242 | 1 |
| LVGI | 243 | 0 |
| TATA | 243 | 0 |
| M_SCORE | 234 | 9 |
| DISTRESS | 0 | 243 |

`DISTRESS` remains formula-insufficient because `hose_warning=None`, while independently known true accumulated-loss or negative-equity signals still produce `high_risk=True` as reviewed.

## 10. Guardrail and sector warnings

- Greater-than-30% guard status: `not triggered`.
- `SUSPECTED_FORMULA_OR_UNIT_BUG`: `False`.
- Sector A >approximately 2× review flag: `BÁN LẺ`.
- Sector diagnostics do not alter operative rejection reasons.

## 11. Outputs and row counts

```text
data/screener/step1_survivors.csv: 156
data/screener/step1_rejects.csv: 222
data/universe_rejects.csv: 1589
docs/DIAG_SECTOR_A_REJECT_MIX_SPRINT_4.csv: 15
docs/DIAG_SECTOR_B_WHATIF_SPRINT_4.csv: 15
docs/REPORT_SPRINT_4_CLEANING.md: 57 lines
docs/TEST_LOG_SPRINT_4_CLEANING.txt: 173 lines
```

## 12. Reject-history preservation proof

```text
historical_row_count: 1367
appended_sprint4_row_count: 222
final_row_count: 1589
historical_hash_before: 108ebb24f385b4134e4f6d7ba553399441ed5fc61fd80ca1a5469ea560102a49
historical_hash_after: 108ebb24f385b4134e4f6d7ba553399441ed5fc61fd80ca1a5469ea560102a49
historical_rows_preserved: true
```

The deterministic hash is computed from the original twelve columns after CSV normalization. A dataframe equality assertion also compared all 1,367 historical rows, in their original order, before writing.

## 13. Exact `data_contract.md` diff

```diff
diff --git a/data_contract.md b/data_contract.md
index 94ef444..e342ff9 100644
--- a/data_contract.md
+++ b/data_contract.md
@@ -44,9 +44,17 @@ reject_reason
 as_of
 source
 data_status
+filter_stage
+reason_label
+trigger_metric
+trigger_value
+threshold_or_cutoff
 ```

 Every row in this file must have `status = REJECTED` and a non-empty `reject_reason`.
+The five Sprint 4 audit columns are blank for historical rows and populated only
+for newly appended Sprint 4 cleaning rejects; historical row order and values
+in the original twelve columns remain unchanged.

 ## Column Meanings

@@ -62,6 +70,11 @@ Every row in this file must have `status = REJECTED` and a non-empty `reject_rea
 - `as_of`: Date of the latest source data used for the row, or the run date when no market data was available.
 - `source`: Source name and relevant calculation note, for example `vnstock` or `vnstock+adtv_close_x_volume_proxy`.
 - `data_status`: Data availability status.
+- `filter_stage`: One-based position of the first Sprint 4 cleaning filter that rejected the ticker.
+- `reason_label`: The ticker's single primary Sprint 4 rejection reason.
+- `trigger_metric`: Formula metric, signal, or upstream field that caused the rejection.
+- `trigger_value`: Cached value or known signal that triggered the rejection.
+- `threshold_or_cutoff`: Fixed threshold or observed whole-universe cutoff applied by that filter.

 ## Valid `reject_reason` Values

@@ -73,6 +86,11 @@ Every row in this file must have `status = REJECTED` and a non-empty `reject_rea
 - `API_ERROR`
 - `MISSING_ICB_CLASSIFICATION`
 - `UNSUPPORTED_EXCHANGE`
+- `FINANCIAL_SECTOR_EXCLUDED`
+- `UPCOM_EXCLUDED_V1`
+- `HIGH_ACCRUAL`
+- `M_SCORE_FLAG`
+- `PFD_HIGH_RISK`

 ## Valid `data_status` Values
```

## 14. Test evidence

- Required `py_compile` exit code: `0`.
- Full unfiltered `python -m pytest -q` exit code: `0`.
- Exact raw commands, stdout, stderr, and exit codes: `docs/TEST_LOG_SPRINT_4_CLEANING.txt`.
- Fixture tests demonstrate behavior on fixtures and do not independently prove financial correctness for every real company.

## 15. No forbidden changes or network/refetch

- The original cleaning implementation changed no Sprint 3 production file or pre-existing test file.
- `docs/SPEC_SPRINT_4.md`, `config/screener.yaml`, dependencies, Sprint 3 parser/client/normalization/cache generation, and existing tests are unchanged by this task.
- The new production call path imports only `step1_data` and `step1_cleaning`; neither the runner nor pipeline imports `vnstock`, an HTTP client, or a fetcher.
- Network access is blocked by the focused fixture test.
- Cache manifest before and after: `945` files, SHA-256 `5c3cef796abcc8d1fa54a49769720534724a60ab7ee4b1336450ed756027ac17`; unchanged `True`.
- No live API call and no refetch occurred.

## 16. Exact PR state

```text
url: https://github.com/quan-sys/m-y-n-/pull/4
base: main
head: agent/sprint4-step0-annual
state: OPEN
isDraft: true
mergedAt: null
autoMergeRequest: null
title: Sprint 4 — Step 1: CLEANING
```

## 17. PFD and future-`available_from` review correction

### Reviewer-approved starting HEAD and correction commit

```text
starting HEAD: 70e161ff345f37b66a1717a9200187a9dd37646e
final HEAD: <the correction commit containing this evidence; exact SHA is in PR #4 and the five-line handoff>
task-only commits:
<correction commit containing this evidence> Fix Sprint 4 PFD audit and future-date test
```

### Exact review-fix changed-file list

```text
data/screener/step1_rejects.csv
data/universe_rejects.csv
docs/REVIEW_EVIDENCE_SPRINT_4_CLEANING.md
docs/TEST_LOG_SPRINT_4_CLEANING.txt
src/screener/step1_pipeline.py
tests/test_step1_pipeline.py
```

### Exact review-fix diff stat

```text
 data/screener/step1_rejects.csv           |  20 ++---
 data/universe_rejects.csv                 |  20 ++---
 docs/REVIEW_EVIDENCE_SPRINT_4_CLEANING.md | 119 ++++++++++++++++++++++++++++--
 docs/TEST_LOG_SPRINT_4_CLEANING.txt       |   6 +-
 src/screener/step1_pipeline.py            |  12 ++-
 tests/test_step1_pipeline.py              |  92 ++++++++++++++++++++++--
 6 files changed, 232 insertions(+), 37 deletions(-)
```

### Exact full unfiltered test result

```text
........................................................................ [ 35%]
........................................................................ [ 70%]
............................................................             [100%]
exit code: 0
```

The exact commands, stdout, stderr, and exit codes for `py_compile`, full unfiltered pytest, and the cache-only pipeline are stored in `docs/TEST_LOG_SPRINT_4_CLEANING.txt`.

### All PFD primary rejects and corrected triggering signals

| ticker | trigger_value |
|---|---|
| APH | accumulated_loss |
| ASP | accumulated_loss |
| HVN | accumulated_loss |
| LDG | accumulated_loss |
| TLH | accumulated_loss |
| TSC | accumulated_loss |
| TTF | accumulated_loss |
| VPG | accumulated_loss |
| GKM | accumulated_loss |
| OCH | accumulated_loss |

PFD primary rejects: `10`; empty `trigger_value`: `0`. The serialization accepts Python `True` and NumPy/pandas boolean true scalars, while `False`, `None`, `NaN`, and `pd.NA` do not become printed financial signals. The rejection decision remains based on the reviewed `distress_high_risk` result.

### Corrected future-date regression proof

- Only `tests/test_step1_pipeline.py::test_future_available_from_exclusion` changed; `tests/test_step1_data.py::test_future_available_from_rows_are_excluded` remains byte-for-byte unchanged from starting HEAD `70e161f`.
- The corrected test builds keyed records and explicitly passes `columns=ANNUAL_COLUMNS`.
- It asserts the resulting column tuple equals `ANNUAL_COLUMNS` and every `period_type` equals `ANNUAL`, excluding malformed-row explanations.
- With the valid 2026 row at `available_from='2026-08-01'` and evaluation date `2026-07-18`, eligible periods are exactly 2025 and 2024 and the selected pair is `(2025, 2024)`.
- For the same 2026 row changed only to `available_from='2026-07-01'`, 2026 becomes eligible and the selected pair is `(2026, 2025)`. This positive control proves the date gate does not reject everything.

### Regenerated-output and preservation proof

```text
survivors: 156
detailed rejects: 222
PFD_HIGH_RISK primary rejects: 10
PFD_HIGH_RISK rows with non-empty trigger_value: 10
historical rejects: 1367
appended Sprint 4 rejects: 222
final reject history: 1589
duplicate Sprint 4 reject tickers: 0
historical_hash_before: 108ebb24f385b4134e4f6d7ba553399441ed5fc61fd80ca1a5469ea560102a49
historical_hash_after: 108ebb24f385b4134e4f6d7ba553399441ed5fc61fd80ca1a5469ea560102a49
historical_rows_preserved: true
cache_file_count_before: 945
cache_file_count_after: 945
cache_manifest_before: 5c3cef796abcc8d1fa54a49769720534724a60ab7ee4b1336450ed756027ac17
cache_manifest_after: 5c3cef796abcc8d1fa54a49769720534724a60ab7ee4b1336450ed756027ac17
```

No rejection decision, formula, threshold, cutoff, filter order, spec, config, Sprint 3 production/test file, dependency, or cache source changed. No live API call or refetch occurred.

### PR state after correction packaging

```text
url: https://github.com/quan-sys/m-y-n-/pull/4
base: main
head: agent/sprint4-step0-annual
state: OPEN
isDraft: true
mergedAt: null
autoMergeRequest: null
title: Sprint 4 — Step 1: CLEANING
```

Sprint 4 — Step 1: CLEANING implementation is ready for owner review; it is not merged and is not approved as final.
