# SPEC Sprint 3 Audit Hardening — Evidence Reverification Addendum

This specification defines a narrow post-Sprint-3 hardening of the evidence-verification workflow. It does not reopen Sprint 3's financial-data rules, classifications, thresholds, or accepted results. The future implementation must verify evidence from the artifacts themselves instead of trusting stored success claims.

This is a specification-only change. Implementation is not authorized yet. No code, test, configuration, data, report, or workflow change may be made until the owner separately approves implementation of this specification.

## Scope

The future implementation is limited to hardening final verification and resume-completeness checks for `scripts/run_sprint3_full_coverage.py`:

- Recompute point-in-time row counts and violation counters directly from normalized artifact files.
- Compare recomputed artifact facts with the corresponding stored `progress.json` metadata.
- Reject any progress/artifact disagreement instead of trusting a stored completion flag.
- Classify missing, unreadable, empty, and schema-invalid artifacts explicitly.
- Prove that the dated snapshot belongs to the relevant run and exactly matches that run's universe outputs.
- Execute the fixture-only pytest suite directly and preserve its real exit status and captured output.
- Generate evidence wording that separates point-in-time results for successfully normalized rows from missing or ambiguous coverage/data cases.
- Remove hard-coded repository and pull-request state claims from generated evidence reports.
- Preserve all raw evidence and every existing honest failure classification.

This addendum does not authorize any implementation in this pull request.

## Verified Problems

1. `finalize()` currently totals `normalized_rows`, `missing_report_period`, `missing_available_from`, and `lag_mismatches` from stored progress records. It does not recompute those facts from the normalized artifacts during final verification.
2. `_record_is_complete()` currently checks only the stored `complete` flag plus raw and normalized file existence. It does not prove that stored metadata agrees with current file contents.
3. `_audit_point_in_time()` returns zero rows and zero violations for an empty normalized frame. A report can therefore say there were zero point-in-time violations without separately saying that a statement or ticker had no successfully normalized rows.
4. `snapshot_written` currently passes when the two expected snapshot files merely exist. Existence does not prove current-run provenance or equality with the corresponding universe outputs.
5. `pytest_green` currently trusts caller-supplied `--pytest-exit-code` and optional output. An arbitrary success value can therefore satisfy that Definition-of-Done check without a real fixture-suite execution.
6. Generated report text hard-codes `Full PR merge: NO` and `PR #1 remains unmerged`. PR #1 is merged, so these workflow-state claims are now false and must not be embedded as constants in evidence generation.

## Frozen Design

### 1. Canonical run evidence

- `data/fundamentals/run_state/<RUN_DATE>/progress.json` identifies the relevant run and its per-ticker, per-statement records.
- Normalized artifacts are the paths recorded by those records and must remain under `data/fundamentals/run_state/<RUN_DATE>/normalized/`.
- The expected statement set remains exactly balance sheet, income statement, and cash flow for every `ACCEPTED` ticker in the run's universe.
- Verification reads artifacts without rewriting them. Raw observations, normalized artifacts, and honest source errors are immutable evidence.
- Verification output must retain the ticker, statement type, artifact path, artifact status, recomputed counters, stored counters, and any mismatch reason.

### 2. Deterministic normalized-artifact verification

For every expected ticker and statement, final verification must apply this order:

1. Resolve the progress record and normalized path. A missing record or path is `MISSING_ARTIFACT` and fails evidence verification.
2. Require the normalized path to be inside the current run's normalized directory and to exist as a regular file. A missing or out-of-run path is `MISSING_ARTIFACT` and fails evidence verification.
3. Load the artifact according to its declared `.parquet` or `.csv` format. A load exception is `UNREADABLE_ARTIFACT`; preserve the redacted exception and fail evidence verification.
4. If the loaded frame has zero rows, classify it as `EMPTY_NORMALIZED`. Do not call it point-in-time clean and do not count it among audited rows. Compare its recomputed row count of zero with progress metadata. It remains visible through the existing missing/ambiguous data and coverage classification. An empty artifact paired with a stored successful non-empty claim is a verification failure.
5. For a non-empty frame, require `report_period`, `available_from`, `period_type`, and `period_end`. Missing required columns are `SCHEMA_INVALID_ARTIFACT` and fail evidence verification.
6. Recompute directly from the loaded rows:
   - `normalized_rows = len(frame)`;
   - `missing_report_period` from null `report_period` values;
   - `missing_available_from` from null `available_from` values;
   - `lag_mismatches` row by row using the locked lags `QUARTER=30`, `SEMIANNUAL=60`, and `ANNUAL=90`, with an unknown period type or missing date counted as a mismatch.
7. Compare each recomputed integer with the stored progress value using exact equality. Any disagreement is `PROGRESS_ARTIFACT_MISMATCH`, records both values, and fails evidence verification.
8. Aggregate point-in-time counters only from successfully loaded, schema-valid, non-empty normalized rows. Separately aggregate counts of `MISSING_ARTIFACT`, `UNREADABLE_ARTIFACT`, `EMPTY_NORMALIZED`, `SCHEMA_INVALID_ARTIFACT`, and `PROGRESS_ARTIFACT_MISMATCH`.

`_record_is_complete()` must use the same artifact-verification result. A stored `complete=true` flag and file existence are necessary but never sufficient. A record is resumably complete only when its current artifacts load successfully, its recomputed metadata matches progress exactly, and its existing source/data status is internally consistent with whether normalized rows are present. The future implementation must not mark an incomplete or mismatched record complete merely to avoid reprocessing.

### 3. Honest empty and missing-data semantics

- Zero point-in-time violations means only zero violations among the explicitly reported number of successfully normalized rows.
- `EMPTY_NORMALIZED` is not a point-in-time pass. It is a separate data/coverage condition tied to the existing provider-missing or ambiguity reason.
- Missing or ambiguous statements and tickers remain in the same honest failure population. Audit hardening must not turn them into passes or remove their reasons.
- Evidence-integrity failures and financial-data coverage failures are separate dimensions and must be reported separately.
- The report must use wording equivalent to: `Among <N> successfully normalized rows, missing report_period=<x>, missing available_from=<y>, lag mismatches=<z>. Separately, <counts> statements were missing, unreadable, empty, schema-invalid, or metadata-mismatched and are not described as point-in-time clean.`

### 4. Snapshot provenance and equality

- A run must have one immutable `run_id` created when that run state is initialized and stored in `progress.json`.
- Snapshot creation must write a manifest for the same `run_id` and `RUN_DATE`. The manifest records creation time, source paths, destination paths, row counts, ordered column lists, and SHA-256 hashes of the source and snapshot bytes. SHA-256 must use the Python standard library; no dependency may be added.
- `snapshot_written` passes only when the manifest was produced by the relevant run, its `run_id` and `RUN_DATE` exactly match progress, and both snapshot files pass every comparison below.
- For `universe.csv` and `universe_rejects.csv`, verification must separately compare:
  1. readable CSV status;
  2. exact ordered schema;
  3. exact row count;
  4. deterministic content via byte-for-byte SHA-256 equality between the relevant run output and its snapshot copy.
- A pre-existing snapshot with a missing or different `run_id`, a stale manifest, or a creation record not produced by the relevant run cannot satisfy `snapshot_written`, even if files happen to exist.
- Any changed row, column order, column name, value, byte sequence, or row count fails snapshot verification and records the precise comparison that failed.

### 5. Pytest evidence

- Final verification must invoke the real fixture-only suite itself with `[sys.executable, "-m", "pytest", "-q"]`, repository root as the working directory, `shell=False`, and captured stdout/stderr.
- The actual subprocess return code is the sole source for `pytest_green`.
- The exact command, start/end timestamps, return code, stdout, and stderr must be saved under the current run state before the report is written.
- `pytest_green` passes only when that recorded invocation completed and its actual return code is zero.
- Remove or reject `--pytest-exit-code` and any other caller-supplied success override. A manually supplied zero can never satisfy the Definition of Done.
- Pytest must remain fixture-only. The verification command must not run a live API smoke script.

### 6. Generated report wording

- The report must have separate sections for `Point-in-time audit of successfully normalized rows`, `Data and coverage gaps`, and `Evidence-integrity failures`.
- The point-in-time section must print the recomputed row denominator next to every zero-violation claim.
- The data/coverage section must preserve missing provider data, `REQUIRED_ITEM_AMBIGUOUS`, and every existing reject reason.
- The evidence-integrity section must list artifact, progress, snapshot, and pytest verification failures without relabelling them as financial-data failures.
- Generated reports must not hard-code PR numbers, merge state, branch state, review state, Sprint state, or other mutable repository workflow claims.
- The strings `Full PR merge: NO` and `PR #1 remains unmerged` must be removed from report generation. No replacement PR-state assertion is required for evidence verification.

### 7. Preservation and compatibility

- Preserve every raw response, normalized artifact, progress record, and generated evidence input; never rewrite historical source evidence to make verification pass.
- Preserve `REQUIRED_ITEMS` v1, all duplicate-resolution decisions, all seven current non-financial failure classifications, and the accepted 308/315 result.
- The hardened verifier may expose an evidence-integrity failure, but it must not silently alter a financial classification, threshold, mapping, whitelist, or raw value.
- The unchanged valid Sprint 3 fixture package must still reproduce the same universe and coverage totals. Reproduction does not authorize suppressing a newly detected evidence-integrity mismatch.

## Required Future Implementation Tests

Implementation is not authorized in this task. After separate owner approval, fixture-only tests must prove all of the following:

1. Tampering with a normalized artifact causes verification to fail even when `progress.json` still says complete.
2. Tampering with a stored row count or lag count causes verification to fail.
3. A stale pre-existing snapshot cannot satisfy `snapshot_written`.
4. A snapshot with one changed row, column, or value fails verification.
5. Passing a fake pytest exit code cannot produce a green Definition of Done.
6. Missing or empty normalized statements remain visible as coverage/data failures and are not described as point-in-time clean data.
7. A valid unchanged Sprint 3 evidence package still reproduces exactly:
   - 378 `ACCEPTED` tickers;
   - 315 non-financial coverage tickers;
   - 63 financial raw-fetch-only tickers;
   - 308 non-financial passes;
   - 7 non-financial failures;
   - coverage `308/315` exactly;
   without changing any threshold or classification.

Additional guard tests must prove that missing, unreadable, schema-invalid, metadata-mismatched, and empty-success artifacts cannot satisfy the evidence-integrity gate; that real nonzero pytest output remains captured; and that no generated report contains hard-coded PR merge-state claims.

## Definition of Done

This specification-only task is complete only when:

- Exactly one new file exists: `docs/SPEC_SPRINT_3_AUDIT_HARDENING.md`.
- No production code, test code, config, data, report, README, `AGENTS.md`, `CHANGELOG.md`, or other existing file is changed.
- This specification contains Scope, Verified Problems, Frozen Design, Required Future Implementation Tests, Definition of Done, and Must Not Include sections.
- The specification explicitly states that implementation is not authorized yet.
- The commit contains no secrets.
- A pull request is opened and remains unmerged.
- Work stops for owner and reviewer approval.

The later hardening implementation is not complete until every required future test passes, all recomputed artifact facts agree with stored metadata, snapshot provenance and exact equality pass, the actual fixture-suite invocation is green, report wording is honest, and the existing 378/315/63/308/7/308-of-315 classifications reproduce without threshold or classification changes. That later implementation requires a separate owner approval.

## Must Not Include

- No code change in this task.
- No Sprint 4 implementation.
- No screener, valuation, quality, distress, momentum, portfolio, or backtest logic.
- No change to `REQUIRED_ITEMS` v1.
- No change to duplicate-resolution mappings.
- No change to `IDENTITY_TOL=0.01`.
- No change to `IDENTITY_MIN_PERIODS=3`.
- No change to `IDENTITY_MARGIN=5.0`.
- No change to `DUP_MATERIALITY_EPS=0.01`.
- No attempt to convert AGX, BAF, DBC, DSH, GTD, ODE, or TAB into passes.
- No fabricated financial data, ticker, classification, or market value.
- No new dependency.
- No vnstock version change.
- No GitHub Actions implementation in this task.
- No modification of existing Sprint 3 evidence, reports, results, code, tests, configuration, or data.
- No pull-request merge in this task.
