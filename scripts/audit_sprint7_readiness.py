"""Read-only Sprint 7 signal and portfolio-construction readiness audit."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATHS = {
    "EBIT_TEV": ROOT / "data" / "screener" / "step2_candidates_ebit_tev.csv",
    "EP": ROOT / "data" / "screener" / "step2_candidates_ep.csv",
}
QUALITY_PATH = ROOT / "data" / "screener" / "sprint6_franchise_quality.csv"
SURVIVORS_PATH = ROOT / "data" / "screener" / "step1_survivors.csv"
OUTPUT_PATH = ROOT / "data" / "screener" / "sprint7_readiness_audit.csv"
CUTS = (15, 20, 25)


def prepare_pool(
    candidates: pd.DataFrame,
    quality: pd.DataFrame,
    survivors: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Join local evidence and apply only the settled non-READY hard block."""
    candidate_tickers = candidates[["ticker"]].copy()
    candidate_tickers["ticker"] = (
        candidate_tickers["ticker"].astype(str).str.strip().str.upper()
    )
    if candidate_tickers["ticker"].duplicated().any():
        raise ValueError("candidate list contains duplicate tickers")
    quality_fields = quality[
        ["ticker", "composite_quality", "franchise_history_status", "icb2"]
    ].copy()
    quality_fields["ticker"] = quality_fields["ticker"].astype(str).str.strip().str.upper()
    survivor_fields = survivors[["ticker", "adtv_20d"]].copy()
    survivor_fields["ticker"] = (
        survivor_fields["ticker"].astype(str).str.strip().str.upper()
    )
    joined = candidate_tickers.merge(
        quality_fields, on="ticker", how="left", validate="one_to_one"
    ).merge(survivor_fields, on="ticker", how="left", validate="one_to_one")
    status = joined["franchise_history_status"].fillna("MISSING").astype(str)
    blocked = joined.loc[status.ne("READY")].copy()
    blocked["franchise_history_status"] = status.loc[blocked.index]
    eligible = joined.loc[status.eq("READY")].copy()
    return eligible.reset_index(drop=True), blocked.reset_index(drop=True)


def ranked_usable(eligible: pd.DataFrame) -> pd.DataFrame:
    ranked = eligible.copy()
    ranked["composite_quality_numeric"] = pd.to_numeric(
        ranked["composite_quality"], errors="coerce"
    )
    return ranked.loc[ranked["composite_quality_numeric"].notna()].sort_values(
        ["composite_quality_numeric", "ticker"],
        ascending=[False, True],
        kind="mergesort",
    )


def exact_tie_count(ranked: pd.DataFrame, top_n: int = 30) -> int:
    """Return the number of exactly tied ticker pairs in the ranked top-N."""
    top = ranked.head(top_n)
    counts = top.groupby("composite_quality_numeric", dropna=False).size()
    return int(sum(count * (count - 1) // 2 for count in counts if count > 1))


def sector_snapshot(ranked: pd.DataFrame, cut: int) -> dict[str, Any]:
    top = ranked.head(cut).copy()
    sectors = top["icb2"].fillna("MISSING_ICB2").astype(str)
    sectors = sectors.mask(sectors.str.strip().eq(""), "MISSING_ICB2")
    counts = sectors.value_counts().sort_index()
    if counts.empty:
        deepest_sector = ""
        deepest_count = 0
        deepest_share = 0.0
    else:
        deepest_count = int(counts.max())
        deepest_sector = sorted(counts[counts.eq(deepest_count)].index)[0]
        deepest_share = deepest_count / len(top) * 100
    return {
        "cut": cut,
        "ranked_tickers_in_cut": int(len(top)),
        "icb2_distribution": "|".join(
            f"{sector}:{int(count)}" for sector, count in counts.items()
        ),
        "deepest_sector": deepest_sector,
        "deepest_sector_count": deepest_count,
        "deepest_sector_share_pct": deepest_share,
        "sector_cap_25_would_bind": bool(deepest_count > 0.25 * cut),
    }


def audit_list(
    list_name: str,
    candidates: pd.DataFrame,
    quality: pd.DataFrame,
    survivors: pd.DataFrame,
) -> list[dict[str, Any]]:
    eligible, blocked = prepare_pool(candidates, quality, survivors)
    ranked = ranked_usable(eligible)
    blocked_text = "|".join(
        f"{row.ticker}:{row.franchise_history_status}"
        for row in blocked.sort_values("ticker").itertuples()
    )
    quality_numeric = pd.to_numeric(eligible["composite_quality"], errors="coerce")
    adtv_numeric = pd.to_numeric(eligible["adtv_20d"], errors="coerce")
    common = {
        "candidate_list": list_name,
        "candidate_rows": int(len(candidates)),
        "non_ready_blocked_count": int(len(blocked)),
        "eligible_pool_size": int(len(eligible)),
        "eligible_pool_arithmetic": f"{len(candidates)} - {len(blocked)} = {len(eligible)}",
        "blocked_tickers_with_status": blocked_text,
        "eligible_missing_or_nonnumeric_composite_quality": int(quality_numeric.isna().sum()),
        "exact_tied_pairs_top30": exact_tie_count(ranked),
        "eligible_missing_or_zero_adtv_20d": int(
            (adtv_numeric.isna() | adtv_numeric.le(0)).sum()
        ),
    }
    return [{**common, **sector_snapshot(ranked, cut)} for cut in CUTS]


def build_audit() -> pd.DataFrame:
    quality = pd.read_csv(QUALITY_PATH)
    survivors = pd.read_csv(SURVIVORS_PATH)
    rows: list[dict[str, Any]] = []
    for list_name, path in CANDIDATE_PATHS.items():
        rows.extend(audit_list(list_name, pd.read_csv(path), quality, survivors))
    audit = pd.DataFrame(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(OUTPUT_PATH, index=False, lineterminator="\n")
    return audit


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    audit = build_audit()
    sys.stdout.write(audit.to_csv(index=False, lineterminator="\n"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
