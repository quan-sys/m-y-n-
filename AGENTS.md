# AGENTS.md — Rules for AI coding agents working on `quan-sys/m-y-n-`

This file is binding for every AI agent (Codex, ChatGPT, Claude, or other)
that reads, writes, or executes code in this repository. When these rules
conflict with your own defaults, these rules win.

## 1. What this project is

A Python data pipeline for Vietnamese equities. Today: universe builder (M0)
+ weekly sector-cycle indicator reports (Sprint 2.x), data from `vnstock`.
Target: a full Quantitative Value stock screener (clean → value → quality →
signals → portfolio) with point-in-time discipline, walk-forward backtesting,
and forward testing. The roadmap lives in `PLAN_quant_screener_myn.md`
(referred to below as THE PLAN). The plan is the source of truth for scope,
parameters, and verified facts. Do not contradict it silently.

A wrong number in this codebase can cost the owner real money. Correctness
and honesty beat speed and elegance. Every rule below exists for that reason.

## 2. Workflow — spec first, always

- Work happens in sprints (3 → 9). Each sprint has its own
  `docs/SPEC_SPRINT_N.md` written BEFORE any code, following the section
  structure of `docs/SPEC_MVP.md` (Scope / Data Rules / Required Output
  Schema / Required Local Checks / Must NOT Include).
- No spec, no code. If asked to code something without a spec, ask for the
  spec or propose one — do not start implementing.
- Implement ONLY what the current spec's Scope lists. The "Must NOT Include"
  section is a hard boundary, not a suggestion. Scope creep — adding
  dashboards, extra features, refactors, "improvements" — is a bug.
- One sprint at a time. Never reach into a later sprint's scope because it
  "seemed convenient".

## 3. Data rules — NEVER violate

1. NEVER fabricate financial data. Not in code, not in fixtures presented as
   real, not in reports, not in docs. If data is unavailable, say so.
2. Every output row carries `source`, `as_of`, `data_status`.
   Missing data = `MISSING_DATA`. API failure = `API_ERROR`.
   Stale cache = `STALE_DATA`. Rejected rows always have a non-empty
   `reject_reason`.
3. Tests NEVER call real APIs. Fixtures only. If a test needs realistic
   data, build a fixture from a saved real response and label its origin.
4. If an API call fails, report the failure verbatim. NEVER mock, stub, or
   invent data to make a script or test pass. A red test that tells the
   truth is worth more than a green test that lies.
5. Point-in-time discipline: any computation that consumes financial
   statements MUST respect `available_from` (publication date if provided,
   else `period_end + LAG`). Using a report before its `available_from` is
   look-ahead bias — the single worst class of bug in this project.

## 4. Verified constants — use as-is, do not re-derive

These were verified against primary sources on 2026-07-14 (details and
citations in THE PLAN, section "TRẠNG THÁI XÁC MINH"):

- Publication lags (Circular 96/2020/TT-BTC, Art. 10 & 14):
  `LAG_QUARTER=30`, `LAG_SEMIANNUAL=60`, `LAG_ANNUAL=90` days.
- vnstock financial statements come in LONG format: columns `item`,
  `item_en`, `item_id` plus one column per period; only the 4 most recent
  periods by default. Key all joins on `item_id` (names can change).
- There is NO publication-date field in the vnstock statements API.
- The vnstock `ratio` endpoint returns corrupted headers — BANNED. Compute
  every ratio from raw balance sheet / income statement / cash flow.
- UNITS TRAP: statements are in raw VND (~1e9–1e15 for large caps); the
  price API returns THOUSANDS of VND (the repo's own
  `adtv_close_x_volume_x1000_proxy` proves it). Any price × fundamentals
  combination (market cap, TEV, E/P) multiplies price by 1000. This
  requires its own dedicated unit test.
- Legacy `Vnstock()` entry class is deprecated (31/08/2025): new data
  clients are built on `vnstock.api`.
- Bank/insurer statements have a different schema (VCB: 86 balance-sheet
  rows vs 122 for non-financials). Never force-normalize them together.

## 5. Formulas — verbatim or not at all

- Every screener formula (Beneish M-Score, Piotroski F-Score, Sloan
  accruals, NOA/SNOA, Campbell PFD, EBIT/TEV, E/P) is written in THE PLAN
  and copied into the sprint spec. Implement EXACTLY that version.
- NEVER substitute a formula variant from your training memory, a blog, or
  "common knowledge" — published variants differ and the plan's versions
  were verified against the original papers.
- Every formula gets a unit test with hand-computed expected values.
- All thresholds and parameters (M-Score −1.78, value cut %, accrual
  percentile, LAGs, momentum on/off…) live in `config/screener.yaml`.
  Hard-coding a threshold in source code is a defect.
- US-calibrated absolute thresholds are hypotheses on VN data, not truths:
  log VN-universe percentiles alongside them so walk-forward can retune.

## 6. Bias guardrails

- Survivorship: historical backtests on vnstock data are permanently
  contaminated (delisted tickers vanish; statements are restated). Any
  backtest report MUST contain a non-empty "Known biases" section saying
  so. Clean data accumulates forward-only via `data/snapshots/YYYY-MM-DD/`.
- Never test the past using today's constituent list (the VN30 lesson).
- Momentum veto defaults to OFF (VN evidence: not significant,
  Huang/Liu/Shu 2023). Do not enable it without walk-forward evidence.
- Screener v1 excludes financial-sector tickers and UPCoM (Sprint 4 labels
  `FINANCIAL_SECTOR_EXCLUDED`, `UPCOM_EXCLUDED_V1`).
- Long-only. No shorting logic anywhere.

## 7. Engineering conventions

- Python, pinned deps in `requirements.txt`. Do NOT add a dependency
  without asking first.
- Every new fetcher must have tests that mimic the real API shape and a smoke
  test against the real API before a milestone is considered complete. Do not
  rely only on tidy fixtures invented for tests.
- Mọi fetcher mới phải có test mô phỏng đúng shape API thật và phải có smoke
  test trên API thật trước khi coi milestone là xong. Không được chỉ test bằng
  fixture "đẹp" do mình tự nghĩ ra.
- Reuse existing patterns: cache/retry/polite-sleep from
  `src/data/vnstock_client.py`; report layout from `src/weekly.py`;
  test style from `tests/`.
- Windows environment: consoles may default to cp1252. Every script that
  prints must reconfigure stdout/stderr to UTF-8 (see
  `scripts/smoke_vnstock_finance.py` for the pattern).
- Every PR/change set: `python -m py_compile` on touched files, `pytest`
  green, `CHANGELOG.md` updated, `data_contract.md` updated if any schema
  changed. A schema change without a data-contract update is incomplete.
- Config changes that alter screener behavior get a CHANGELOG entry with a
  REASON. Silent parameter tuning is how you data-mine yourself.

## 8. Stop and ask — do not proceed without human approval

- Deleting or renaming any existing file.
- Adding, removing, or upgrading any dependency.
- Changing the schema of `universe.csv`, `universe_rejects.csv`, or
  anything in `data_contract.md`.
- Modifying `src/universe.py` or `src/weekly.py` beyond what the current
  spec explicitly requires.
- Anything touching real money, live trading, or order placement — this
  repo is research/education only and must stay that way.
- Any situation where required information is missing: write
  `OPEN QUESTION: …` and stop, instead of inventing an answer.

## 9. Communication style

- Report what actually happened: exact commands, exact output, exact
  errors. No summaries that hide failures.
- Never treat Codex summaries, recommendations, claimed test results, or conclusions as evidence. Before reporting to the owner, independently inspect the actual repository state, PR, commits, diff, changed files, and available test evidence. Anything that cannot be independently verified must be labelled UNVERIFIED. Green tests alone do not prove sprint completion.
- After each completed step, state: what was done, what was verified, what
  remains, and any OPEN QUESTIONs.
- The owner is not a programmer. After every run and before every report,
  explain the result in simple Vietnamese: what ran, whether it succeeded or
  failed, what the result means, what remains, and whether the owner must decide
  anything.
- Minimize code jargon. Explain any necessary technical term immediately in
  ordinary language and include one short concrete example when the behavior is
  difficult to understand.
- Never assume the owner understands commands, APIs, schemas, tests, branches,
  commits, pull requests, or other software-development terms.
- After writing a sprint spec, explain it in plain Vietnamese for an owner who
  does not know how to code: goal, inputs, workflow, outputs, exclusions,
  financial risks, open decisions, and a simple example. Do not implement the
  sprint until the owner explicitly approves the spec.
- Uncertainty labels in docs and reports: ✅ verified / ⚠️ estimate or
  secondary source / ❓ unverified. Never present ⚠️ or ❓ material as fact.

### Owner-review reporting rules

- Before every owner report, reread the reporting rules in this `AGENTS.md`.
- Every review report uses exactly nine numbered sections.
- Each section normally contains exactly one complete summary sentence.
- Section 1 states what Codex actually accomplished, including freshly fetched
  HEAD and the complete diff scope.
- Section 2 states the practical impact in ordinary Vietnamese.
- Every number identifies the file, command, or calculation from which it was
  independently obtained.
- Codex summaries, recommendations, claimed test results, and conclusions are
  not evidence.
- Use only ✅ confirmed, ⚠️ estimate, and ❓ unclear.
- Every pytest statement says that fixture tests show behavior on those
  fixtures but do not prove real-world financial correctness.
- Use only step names already present in the current SPEC or PLAN.
- Section 8 contains PASS, PARTIAL, or FAIL.
- Section 9 states the next task and explains the purpose of the next prompt in
  one sentence.
- Do not list low-value file, commit, diff, or command details unless they
  affect the conclusion.

## 10. GitHub publishing and secret safety

- This local project and `https://github.com/quan-sys/m-y-n-` are one
  project. That repository is the canonical remote. Never push this work to
  a different repository or account without explicit owner approval.
- After an approved change is complete and its required checks have run,
  publish only the intended files to the canonical repository. Use a focused
  branch and pull request unless the owner explicitly requests a direct push
  to the default branch.
- Before every commit and push, inspect the exact diff and staged file list
  for secrets. NEVER commit or print API keys, access tokens, passwords,
  cookies, credentials, private keys, `.env` files, or local authentication
  configuration.
- Ensure secret-bearing and machine-local files are covered by `.gitignore`.
  Do not assume a filename is safe: scan file contents for credential patterns
  as well. Redact any secret when reporting a finding.
- If a possible secret is found, unstage or exclude the affected file, report
  only its location and secret type, and stop for owner guidance. If a secret
  may already have reached Git history or GitHub, advise immediate revocation
  and rotation; deleting the file alone is not sufficient.
- Never use broad staging such as `git add -A` without first confirming that
  every changed and untracked file belongs to the intended change set.
- Before publishing, verify that the Git remote resolves to
  `quan-sys/m-y-n-`, GitHub authentication is active, and the destination
  branch is correct. If the local folder is not a Git checkout or publishing
  tools/authentication are unavailable, report the blocker and do not invent
  a successful push.
