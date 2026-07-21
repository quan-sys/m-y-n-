from __future__ import annotations

import pandas as pd

from scripts.build_sprint7_portfolio import select_portfolio


def fixture_pool(rows: int = 30) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ticker": f"T{index:02d}",
                "icb2": f"SECTOR_{index % 10}",
                "composite_quality": 1 - index / 100,
                "quality_rank": index + 1,
                "franchise_history_status": "READY",
                "adtv_20d": 1_000_000,
            }
            for index in range(rows)
        ]
    )


def run_selection(pool: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    return select_portfolio(
        pool,
        holding_count=20,
        sector_cap=0.25,
        liquidity_adtv_days=5,
        portfolio_capital_vnd=1_000_000,
    )


def test_insufficient_history_is_blocked() -> None:
    pool = fixture_pool()
    pool.loc[0, "franchise_history_status"] = "INSUFFICIENT_HISTORY"
    holdings, skips = run_selection(pool)
    assert "T00" not in set(holdings["ticker"])
    assert skips.loc[skips["ticker"].eq("T00"), "reason"].item() == (
        "INSUFFICIENT_HISTORY_BLOCKED"
    )


def test_sector_cap_skips_sixth_same_sector_name() -> None:
    pool = fixture_pool()
    pool.loc[:5, "icb2"] = "CROWDED"
    holdings, skips = run_selection(pool)
    assert int(holdings["icb2"].eq("CROWDED").sum()) == 5
    assert skips.loc[skips["ticker"].eq("T05"), "reason"].item() == (
        "SECTOR_CAP_SKIPPED"
    )


def test_liquidity_cap_skips_tiny_adtv() -> None:
    pool = fixture_pool()
    pool.loc[0, "adtv_20d"] = 1
    holdings, skips = run_selection(pool)
    assert "T00" not in set(holdings["ticker"])
    assert skips.loc[skips["ticker"].eq("T00"), "reason"].item() == (
        "LIQUIDITY_CAP_SKIPPED"
    )


def test_exact_quality_tie_uses_ticker_ascending() -> None:
    pool = fixture_pool()
    pool.loc[0, ["ticker", "composite_quality"]] = ["ZZZ", 1.0]
    pool.loc[1, ["ticker", "composite_quality"]] = ["AAA", 1.0]
    holdings, _ = run_selection(pool)
    assert holdings["ticker"].head(2).tolist() == ["AAA", "ZZZ"]


def test_selection_stops_at_exactly_twenty() -> None:
    holdings, skips = run_selection(fixture_pool())
    assert len(holdings) == 20
    assert holdings["portfolio_rank"].tolist() == list(range(1, 21))
    assert set(holdings["ticker"]) == {f"T{index:02d}" for index in range(20)}
    assert skips.empty
