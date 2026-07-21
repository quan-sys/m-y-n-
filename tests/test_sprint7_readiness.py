from __future__ import annotations

import math

import pandas as pd

from scripts.audit_sprint7_readiness import (
    exact_tie_count,
    prepare_pool,
    ranked_usable,
    sector_snapshot,
)


def test_non_ready_row_is_blocked_from_eligible_pool() -> None:
    candidates = pd.DataFrame({"ticker": ["AAA", "BBB"]})
    quality = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB"],
            "composite_quality": [0.8, 0.9],
            "franchise_history_status": ["READY", "INSUFFICIENT_HISTORY"],
            "icb2": ["SECTOR A", "SECTOR B"],
        }
    )
    survivors = pd.DataFrame(
        {"ticker": ["AAA", "BBB"], "adtv_20d": [1000, 2000]}
    )
    eligible, blocked = prepare_pool(candidates, quality, survivors)
    assert eligible["ticker"].tolist() == ["AAA"]
    assert blocked[["ticker", "franchise_history_status"]].to_dict("records") == [
        {"ticker": "BBB", "franchise_history_status": "INSUFFICIENT_HISTORY"}
    ]


def test_sector_snapshot_reports_deepest_share_and_binding() -> None:
    eligible = pd.DataFrame(
        {
            "ticker": ["A", "B", "C", "D", "E", "F"],
            "composite_quality": [0.9, 0.8, 0.7, 0.6, 0.5, 0.4],
            "icb2": ["X", "X", "X", "X", "Y", "Y"],
        }
    )
    snapshot = sector_snapshot(ranked_usable(eligible), 6)
    assert snapshot["deepest_sector"] == "X"
    assert snapshot["deepest_sector_count"] == 4
    assert math.isclose(snapshot["deepest_sector_share_pct"], 4 / 6 * 100)
    assert snapshot["sector_cap_25_would_bind"] is True


def test_exact_tie_detection_counts_tied_pairs() -> None:
    eligible = pd.DataFrame(
        {
            "ticker": ["A", "B", "C", "D", "E"],
            "composite_quality": [0.9, 0.9, 0.8, 0.8, 0.8],
            "icb2": ["X"] * 5,
        }
    )
    assert exact_tie_count(ranked_usable(eligible), top_n=30) == 4
