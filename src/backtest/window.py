from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from math import ceil

import pandas as pd


WINDOW_COLUMNS = (
    "rebalance_date",
    "candidate_pool_size",
    "threshold",
    "meets_threshold",
    "THIN_CANDIDATE_POOL",
)


def compute_backtest_window(
    periods: Sequence[tuple[str | date | pd.Timestamp, int]],
    portfolio_size: int,
    multiple: float,
) -> tuple[pd.Timestamp | None, pd.DataFrame]:
    """Resolve C2 in chronological order and retain later thin periods per C3."""
    if portfolio_size < 1:
        raise ValueError("portfolio_size must be positive")
    if multiple <= 0:
        raise ValueError("multiple must be positive")

    threshold = ceil(multiple * portfolio_size)
    start_date: pd.Timestamp | None = None
    prior_date: pd.Timestamp | None = None
    rows: list[dict[str, object]] = []
    for raw_date, raw_pool_size in periods:
        rebalance_date = pd.Timestamp(raw_date).normalize()
        if prior_date is not None and rebalance_date <= prior_date:
            raise ValueError("rebalance dates must be strictly chronological")
        prior_date = rebalance_date
        candidate_pool_size = int(raw_pool_size)
        if candidate_pool_size < 0:
            raise ValueError("candidate_pool_size cannot be negative")

        meets_threshold = candidate_pool_size >= threshold
        if start_date is None and meets_threshold:
            start_date = rebalance_date
        rows.append(
            {
                "rebalance_date": rebalance_date,
                "candidate_pool_size": candidate_pool_size,
                "threshold": threshold,
                "meets_threshold": meets_threshold,
                "THIN_CANDIDATE_POOL": start_date is not None and not meets_threshold,
            }
        )

    return start_date, pd.DataFrame(rows, columns=WINDOW_COLUMNS)
