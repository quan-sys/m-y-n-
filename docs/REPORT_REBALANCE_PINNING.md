# Rebalance pinning inventory

| file path | line number | constant or path expression | what it controls | rerun result |
|---|---:|---|---|---|
| `scripts/build_sprint7_portfolio.py` | 21 | `AS_OF = "2026-07-20"` | Default date for the report root, portfolio IDs, `as_of` output values, and report prose. | The fixed value reuses `reports/2026-07-20`; a different date writes a new dated folder. |
| `scripts/build_sprint7_portfolio.py` | 25 | `ROOT / "data" / "screener" / "sprint6_franchise_quality.csv"` | Undated latest Franchise Power input. | Its producer overwrites the existing artifact. |
| `scripts/build_sprint7_portfolio.py` | 26 | `ROOT / "data" / "screener" / "step1_survivors.csv"` | Undated latest Step 1 input. | Its producer overwrites the existing artifact. |
| `scripts/build_sprint7_portfolio.py` | 27 | `ROOT / "data" / "screener" / "sprint6_fscore.csv"` | Undated latest F-Score input. | Its producer overwrites the existing artifact. |
| `scripts/build_sprint7_portfolio.py` | 28 | `ROOT / "reports" / AS_OF` | Portfolio CSV and Markdown report directory. | The fixed value reuses the existing dated folder; a different date writes a new dated folder. |
| `scripts/build_sprint7_portfolio.py` | 31 | `ROOT / "data" / "screener" / "step2_candidates_ebit_tev.csv"` | Undated latest EBIT/TEV candidate input. | Its producer overwrites the existing artifact. |
| `scripts/build_sprint7_portfolio.py` | 39 | `ROOT / "data" / "screener" / "step2_candidates_ep.csv"` | Undated latest E/P candidate input. | Its producer overwrites the existing artifact. |
| `scripts/build_sprint5_valuation.py` | 23 | `EVALUATION_DATE = "2026-07-20"` | Eligibility and TTM date for the candidate artifacts consumed by Sprint 7. | Re-running writes over the undated candidate artifacts below. |
| `scripts/build_sprint5_valuation.py` | 25 | `ROOT / "data" / "screener" / "step1_survivors.csv"` | Undated latest Step 1 input to candidate construction. | Its producer overwrites the existing artifact. |
| `scripts/build_sprint5_valuation.py` | 26 | `ROOT / "data" / "market_cap" / "2026-07-19" / "universe_market_cap.csv"` | Fixed dated market-cap input for candidate construction. | Reads one existing dated artifact; no new folder is selected. |
| `scripts/build_sprint5_valuation.py` | 27 | `ROOT / "data" / "fundamentals" / "run_state" / "2026-07-17" / "normalized"` | Fixed dated quarterly-fundamentals input for candidate construction. | Reads one existing dated artifact; no new folder is selected. |
| `scripts/build_sprint5_valuation.py` | 29 | `ROOT / "data" / "screener" / "step2_valuation_all.csv"` | Undated latest full valuation output. | Overwrites the existing artifact. |
| `scripts/build_sprint5_valuation.py` | 30 | `ROOT / "data" / "screener" / "step2_candidates_ebit_tev.csv"` | Undated latest EBIT/TEV candidate output. | Overwrites the existing artifact. |
| `scripts/build_sprint5_valuation.py` | 31 | `ROOT / "data" / "screener" / "step2_candidates_ep.csv"` | Undated latest E/P candidate output. | Overwrites the existing artifact. |
| `scripts/run_sprint4_step1_cleaning.py` | 27 | `EVALUATION_DATE = "2026-07-18"` | Fixed evaluation date used to produce Step 1 survivors. | Re-running writes over the undated Step 1 outputs below. |
| `scripts/run_sprint4_step1_cleaning.py` | 30 | `ROOT / "data" / "fundamentals" / "run_state" / "sprint4_annual" / "2026-07-17" / "normalized"` | Fixed dated annual-fundamentals input to Step 1 cleaning. | Reads one existing dated artifact; no new folder is selected. |
| `scripts/run_sprint4_step1_cleaning.py` | 31 | `ROOT / "data" / "screener" / "step1_survivors.csv"` | Step 1 output consumed by Sprint 6 and Sprint 7. | Overwrites the existing artifact. |
| `scripts/run_sprint4_step1_cleaning.py` | 32 | `ROOT / "data" / "screener" / "step1_rejects.csv"` | Undated Step 1 reject output produced with survivors. | Overwrites the existing artifact. |
| `scripts/run_sprint4_step1_cleaning.py` | 35 | `ROOT / "docs" / "REPORT_SPRINT_4_CLEANING.md"` | Undated Step 1 report. | Overwrites the existing artifact. |
| `scripts/audit_sprint6_readiness.py` | 14 | `ROOT / "data" / "screener" / "step1_survivors.csv"` | Undated latest Step 1 input imported by the F-Score and Franchise scripts. | Its producer overwrites the existing artifact. |
| `scripts/audit_sprint6_readiness.py` | 15-17 | `ROOT / "data" / "fundamentals" / "sprint6_annual_history" / "2026-07-20"` | Fixed dated annual-fundamentals root imported by the F-Score and Franchise scripts. | Reads one existing dated folder; no new folder is selected. |
| `scripts/audit_sprint6_readiness.py` | 18 | `ROOT / "data" / "screener" / "sprint6_readiness_audit.csv"` | Undated readiness-audit output. | Overwrites the existing artifact. |
| `scripts/audit_sprint6_readiness.py` | 19 | `ROOT / "docs" / "SPRINT_6_DATA_READINESS.md"` | Undated readiness-audit report. | Overwrites the existing artifact. |
| `scripts/audit_sprint6_readiness.py` | 20 | `EVALUATION_DATE = "2026-07-20"` | Eligibility date imported by the F-Score and Franchise scripts. | Re-running their producers writes over the undated outputs below. |
| `scripts/build_sprint6_fscore.py` | 50 | `ROOT / "data" / "screener" / "sprint6_fscore.csv"` | F-Score output consumed by Sprint 7 and Franchise Power. | Overwrites the existing artifact. |
| `scripts/build_sprint6_fscore.py` | 51 | `ROOT / "docs" / "REPORT_SPRINT_6_FSCORE.md"` | Undated F-Score report. | Overwrites the existing artifact. |
| `scripts/build_sprint6_franchise.py` | 60 | `ROOT / "data" / "screener" / "sprint6_fscore.csv"` | Undated latest F-Score input. | Its producer overwrites the existing artifact. |
| `scripts/build_sprint6_franchise.py` | 61 | `ROOT / "data" / "screener" / "step2_candidates_ebit_tev.csv"` | Undated latest EBIT/TEV candidate input. | Its producer overwrites the existing artifact. |
| `scripts/build_sprint6_franchise.py` | 62 | `ROOT / "data" / "screener" / "step2_candidates_ep.csv"` | Undated latest E/P candidate input. | Its producer overwrites the existing artifact. |
| `scripts/build_sprint6_franchise.py` | 63 | `ROOT / "data" / "screener" / "sprint6_franchise_quality.csv"` | Franchise Power output consumed by Sprint 7. | Overwrites the existing artifact. |
| `scripts/build_sprint6_franchise.py` | 64 | `ROOT / "docs" / "REPORT_SPRINT_6_FRANCHISE_QUALITY.md"` | Undated Franchise Power report. | Overwrites the existing artifact. |
