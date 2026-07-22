from __future__ import annotations

from collections.abc import Iterable
from datetime import date

import pandas as pd


INSUFFICIENT_TRADED_SESSIONS = "INSUFFICIENT_TRADED_SESSIONS"
PRE_GAP_SEGMENT_UNVERIFIED = "PRE_GAP_SEGMENT_UNVERIFIED"
ELIGIBILITY_COLUMNS = (
    "ticker",
    "eligible",
    "traded_sessions_12m",
    "reason",
    "segment_flag",
)


def compute_eligibility(
    price_rows: pd.DataFrame,
    rebalance_date: str | date | pd.Timestamp,
    *,
    min_traded_sessions_12m: int,
    ticker_identity_gap_days: int,
    universe_tickers: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Compute B1 eligibility from rows already restricted to dates before t."""
    if min_traded_sessions_12m < 1:
        raise ValueError("min_traded_sessions_12m must be positive")
    if ticker_identity_gap_days < 1:
        raise ValueError("ticker_identity_gap_days must be positive")
    required = {"ticker", "date", "volume"}
    missing = sorted(required.difference(price_rows.columns))
    if missing:
        raise ValueError("price rows missing columns: " + ", ".join(missing))

    t = pd.Timestamp(rebalance_date).normalize()
    frame = price_rows.copy()
    frame["_date"] = pd.to_datetime(frame["date"], errors="raise").dt.normalize()
    if bool((frame["_date"] >= t).any()):
        raise ValueError("eligibility input contains date >= rebalance date")
    frame["_volume"] = pd.to_numeric(frame["volume"], errors="coerce")
    frame["ticker"] = frame["ticker"].astype(str).str.strip().str.upper()

    if universe_tickers is None:
        tickers = sorted(frame["ticker"].unique())
    else:
        tickers = list(dict.fromkeys(str(ticker).strip().upper() for ticker in universe_tickers))

    window_start = t - pd.Timedelta(days=365)
    grouped = {ticker: group for ticker, group in frame.groupby("ticker", sort=False)}
    empty_rows = frame.iloc[0:0]
    results: list[dict[str, object]] = []
    for ticker in tickers:
        ticker_rows = grouped.get(ticker, empty_rows).sort_values("_date", kind="stable")
        traded = ticker_rows[
            ticker_rows["_date"].notna()
            & ticker_rows["_volume"].notna()
            & (ticker_rows["_volume"] > 0)
        ].copy()
        traded_dates = pd.DatetimeIndex(traded["_date"].drop_duplicates())
        segment_flag = ""
        segment_start: pd.Timestamp | None = None
        if len(traded_dates) >= 2:
            gaps = pd.Series(traded_dates).diff().dt.days
            long_gap_positions = gaps[gaps > ticker_identity_gap_days].index
            if len(long_gap_positions):
                segment_flag = PRE_GAP_SEGMENT_UNVERIFIED
                segment_start = pd.Timestamp(traded_dates[int(long_gap_positions[-1])])

        effective_start = max(window_start, segment_start) if segment_start is not None else window_start
        session_count = int(
            traded.loc[
                (traded["_date"] >= effective_start) & (traded["_date"] < t),
                "_date",
            ].nunique()
        )
        eligible = session_count >= min_traded_sessions_12m
        results.append(
            {
                "ticker": ticker,
                "eligible": eligible,
                "traded_sessions_12m": session_count,
                "reason": "" if eligible else INSUFFICIENT_TRADED_SESSIONS,
                "segment_flag": segment_flag,
            }
        )

    return pd.DataFrame(results, columns=ELIGIBILITY_COLUMNS)
