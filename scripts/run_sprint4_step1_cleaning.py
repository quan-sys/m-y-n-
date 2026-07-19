"""Run Sprint 4 Step-1 cleaning once from the reviewed local annual cache."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.screener.step1_data import UNIVERSE_COLUMNS, load_accepted_universe, load_reject_history
from src.screener.step1_pipeline import (
    FILTER_ORDER,
    FORMULA_NAMES,
    extend_reject_history,
    load_simple_config,
    run_cleaning_pipeline,
)


EVALUATION_DATE = "2026-07-18"
UNIVERSE_PATH = ROOT / "data" / "universe.csv"
REJECT_HISTORY_PATH = ROOT / "data" / "universe_rejects.csv"
CACHE_ROOT = ROOT / "data" / "fundamentals" / "run_state" / "sprint4_annual" / "2026-07-17" / "normalized"
SURVIVORS_PATH = ROOT / "data" / "screener" / "step1_survivors.csv"
REJECTS_PATH = ROOT / "data" / "screener" / "step1_rejects.csv"
SECTOR_A_PATH = ROOT / "docs" / "DIAG_SECTOR_A_REJECT_MIX_SPRINT_4.csv"
SECTOR_B_PATH = ROOT / "docs" / "DIAG_SECTOR_B_WHATIF_SPRINT_4.csv"
REPORT_PATH = ROOT / "docs" / "REPORT_SPRINT_4_CLEANING.md"


def cache_manifest(root: Path) -> dict[str, object]:
    records = [f"{path.relative_to(root).as_posix()}|{path.stat().st_size}|{path.stat().st_mtime_ns}" for path in sorted(root.rglob("*")) if path.is_file()]
    digest = sha256("\n".join(records).encode("utf-8")).hexdigest()
    return {"file_count": len(records), "manifest_sha256": digest}


def formula_counts(evaluated: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for name in FORMULA_NAMES:
        reason = evaluated[f"{name.lower()}_reason"]
        rows.append({"formula": name, "valid": int(reason.isna().sum()), "insufficient": int(reason.notna().sum())})
    distress_reason = evaluated["distress_reason"]
    rows.append({"formula": "DISTRESS", "valid": int(distress_reason.isna().sum()), "insufficient": int(distress_reason.notna().sum())})
    return rows


def render_report(result, universe_count: int, proof: dict[str, object], cache_before: dict[str, object], cache_after: dict[str, object]) -> str:
    stats = result.filter_stats
    counts = formula_counts(result.evaluated)
    sta_only = int((result.evaluated.sta_flag & ~result.evaluated.snoa_flag).sum())
    snoa_only = int((~result.evaluated.sta_flag & result.evaluated.snoa_flag).sum())
    both = int((result.evaluated.sta_flag & result.evaluated.snoa_flag).sum())
    union = int(result.evaluated.high_accrual_flag.sum())
    missing_warning = int(result.evaluated.distress_hose_warning.isna().sum())
    warnings = result.sector_a.loc[result.sector_a.review_flag, "icb2"].tolist()
    lines = [
        "# Sprint 4 — Step 1: CLEANING report", "",
        f"- Evaluation date: `{EVALUATION_DATE}`.",
        f"- Input: `{UNIVERSE_PATH.relative_to(ROOT).as_posix()}` with {universe_count} Sprint 3 ACCEPTED rows.",
        f"- Annual input: existing read-only cache `{CACHE_ROOT.relative_to(ROOT).as_posix()}`.", "",
        "## Fixed-order filter results", "",
        "| Filter | Entering | Removed | Removal % |", "|---|---:|---:|---:|",
    ]
    for row in stats.to_dict("records"):
        lines.append(f"| {row['filter']} | {row['entering']} | {row['removed']} | {row['removal_pct']:.12%} |")
    lines.extend(["", f"Survivors: **{len(result.survivors)}**.", "", "## Formula sufficiency", "", "| Formula | Valid | Insufficient |", "|---|---:|---:|"])
    for row in counts:
        lines.append(f"| {row['formula']} | {row['valid']} | {row['insufficient']} |")
    lines.extend([
        "", "## Threshold and signal evidence", "",
        f"- STA: valid={result.cutoffs['STA'].valid_count}; k={result.cutoffs['STA'].cut_count}; observed cutoff={result.cutoffs['STA'].cutoff!r}.",
        f"- SNOA: valid={result.cutoffs['SNOA'].valid_count}; k={result.cutoffs['SNOA'].cut_count}; observed cutoff={result.cutoffs['SNOA'].cutoff!r}.",
        f"- HIGH_ACCRUAL UNION: STA-only={sta_only}; SNOA-only={snoa_only}; both={both}; total={union}.",
        f"- M-Score: strict threshold `> -1.78`; valid={int(result.evaluated.m_score_reason.isna().sum())}; formula-stage flagged={int(result.evaluated.m_score_flag.sum())}.",
        f"- Distress: formula-stage high-risk={int(result.evaluated.pfd_high_risk_flag.sum())}; missing HoSE warning={missing_warning}. A missing warning alone is not a rejection.",
        "- Percentile method: ascending rank with `method=max`, divided by each valid population size; therefore the largest (worst) value is percentile 1. Within-ICB2 percentiles are diagnostic only.", "",
        "## Diagnostics and controls", "",
        f"- Sector A >2× review flags: {warnings if warnings else 'none'}.",
        f"- Greater-than-30% guard: {'SUSPECTED_FORMULA_OR_UNIT_BUG — REQUIRES_OWNER_REVIEW' if result.guard_triggered else 'not triggered'}.",
        f"- Reject history: {proof['historical_row_count']} historical + {proof['appended_sprint4_row_count']} appended = {proof['final_row_count']}; preservation={proof['historical_rows_preserved']}; hash={proof['historical_hash_after']}.",
        f"- Cache manifest unchanged: {cache_before == cache_after}; before={cache_before}; after={cache_after}.",
    ])
    if result.guard_triggered:
        lines.extend(["", "### Five-ticker guard evidence", "", result.guard_details.to_markdown(index=False)])
    lines.extend([
        "", "## Limitations", "",
        "- Point-in-time use is limited to cached rows whose `available_from` is on or before the evaluation date. The cache does not supply a HoSE warning list.",
        "- Annual statements may later be restated; this run uses the cached version available to this repository.",
        "- Fixture tests show behavior on fixtures but do not prove financial correctness for every real company.",
        "- This is a research risk-cleaning screen, not an investment recommendation.", "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluation-date", default=EVALUATION_DATE)
    args = parser.parse_args()
    if args.evaluation_date != EVALUATION_DATE:
        raise ValueError(f"evaluation date must remain {EVALUATION_DATE}")
    config = load_simple_config(ROOT / "config" / "screener.yaml")
    if config.get("SECTOR_MODE") != "whole_universe_log":
        raise ValueError("SECTOR_MODE must be whole_universe_log")
    universe = load_accepted_universe(UNIVERSE_PATH)
    history = load_reject_history(REJECT_HISTORY_PATH)
    if "filter_stage" in history.columns:
        historical_mask = history["filter_stage"].isna() | history["filter_stage"].astype(str).str.strip().eq("")
        history = history.loc[historical_mask, list(UNIVERSE_COLUMNS)].reset_index(drop=True)
    cache_before = cache_manifest(CACHE_ROOT)
    result = run_cleaning_pipeline(
        universe, CACHE_ROOT, EVALUATION_DATE,
        float(config["ACCRUAL_WORST_PCT"]), float(config["MSCORE_THRESHOLD"]),
    )
    extended, proof = extend_reject_history(history, result.rejects, universe)
    cache_after = cache_manifest(CACHE_ROOT)
    if cache_before != cache_after:
        raise RuntimeError("annual cache changed during read-only cleaning run")
    SURVIVORS_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.survivors.to_csv(SURVIVORS_PATH, index=False)
    result.rejects.to_csv(REJECTS_PATH, index=False)
    result.sector_a.to_csv(SECTOR_A_PATH, index=False)
    result.sector_b.to_csv(SECTOR_B_PATH, index=False)
    extended.to_csv(REJECT_HISTORY_PATH, index=False)
    REPORT_PATH.write_text(render_report(result, len(universe), proof, cache_before, cache_after), encoding="utf-8")
    summary = {
        "evaluation_date": EVALUATION_DATE,
        "input_paths": [str(UNIVERSE_PATH), str(REJECT_HISTORY_PATH), str(CACHE_ROOT)],
        "input_universe_rows": len(universe), "formula_stage_rows": len(result.evaluated),
        "filter_stats": result.filter_stats.to_dict("records"),
        "cutoffs": {name: {"valid_count": value.valid_count, "cut_count": value.cut_count, "cutoff": value.cutoff} for name, value in result.cutoffs.items()},
        "sta_only": int((result.evaluated.sta_flag & ~result.evaluated.snoa_flag).sum()),
        "snoa_only": int((~result.evaluated.sta_flag & result.evaluated.snoa_flag).sum()),
        "both": int((result.evaluated.sta_flag & result.evaluated.snoa_flag).sum()),
        "union": int(result.evaluated.high_accrual_flag.sum()),
        "m_score_valid": int(result.evaluated.m_score_reason.isna().sum()),
        "m_score_formula_stage_flagged": int(result.evaluated.m_score_flag.sum()),
        "distress_high_risk": int(result.evaluated.pfd_high_risk_flag.sum()),
        "missing_warning": int(result.evaluated.distress_hose_warning.isna().sum()),
        "formula_counts": formula_counts(result.evaluated),
        "guard_triggered": result.guard_triggered,
        "sector_warnings": result.sector_a.loc[result.sector_a.review_flag, "icb2"].tolist(),
        "output_rows": {str(SURVIVORS_PATH): len(result.survivors), str(REJECTS_PATH): len(result.rejects), str(SECTOR_A_PATH): len(result.sector_a), str(SECTOR_B_PATH): len(result.sector_b), str(REJECT_HISTORY_PATH): len(extended)},
        "reject_history_proof": proof, "cache_before": cache_before, "cache_after": cache_after,
    }
    print(json.dumps(summary, ensure_ascii=True, indent=2, default=str))
    return 2 if result.guard_triggered else 0


if __name__ == "__main__":
    raise SystemExit(main())
