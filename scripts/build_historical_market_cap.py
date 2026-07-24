from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRICE_PATH = (
    REPO_ROOT / "data" / "price_history" / "2026-07-24" / "deadjusted_close.csv.gz"
)
DEFAULT_SHARE_PATH = (
    REPO_ROOT
    / "data"
    / "share_count"
    / "2026-07-22"
    / "share_count_point_in_time.csv"
)
DEFAULT_OUTPUT_PATH = (
    REPO_ROOT
    / "data"
    / "market_cap"
    / "2026-07-24"
    / "market_cap_point_in_time.csv"
)

PRICE_COLUMNS = (
    "ticker",
    "date",
    "raw_close",
    "cumulative_factor",
    "adjustment_confidence",
)
SHARE_COLUMNS = (
    "ticker",
    "quarter",
    "measurement_date",
    "source_fiscal_year",
    "available_from",
    "shares_issued_derived",
    "staleness_days",
    "status",
)
OUTPUT_COLUMNS = (
    "ticker",
    "quarter",
    "measurement_date",
    "price_date_used",
    "raw_close",
    "shares_issued_derived",
    "market_cap_thousand_vnd",
    "price_confidence",
    "share_status",
    "market_cap_status",
)
SHARE_STATUS_MAP = {
    "PIT_ISSUED_OK": "OK",
    "PIT_TREASURY_PRESENT": "UPPER_BOUND",
    "NO_AVAILABLE_ANNUAL": "NO_SHARE_COUNT",
}


def _validate_columns(frame: pd.DataFrame, required: tuple[str, ...], label: str) -> None:
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"{label} missing required columns: {missing}")


def build_historical_market_cap(
    share_counts: pd.DataFrame,
    prices: pd.DataFrame,
) -> pd.DataFrame:
    _validate_columns(share_counts, SHARE_COLUMNS, "share-count input")
    _validate_columns(prices, PRICE_COLUMNS, "price input")

    unknown_share_statuses = sorted(
        set(share_counts["status"].dropna().astype(str)) - set(SHARE_STATUS_MAP)
    )
    if unknown_share_statuses:
        raise ValueError(f"unknown share statuses: {unknown_share_statuses}")

    price_work = prices.loc[:, PRICE_COLUMNS].copy()
    price_work["ticker"] = price_work["ticker"].astype(str)
    price_work["_date"] = pd.to_datetime(price_work["date"], errors="raise")
    price_work["raw_close"] = pd.to_numeric(price_work["raw_close"], errors="raise")
    invalid_confidence = sorted(
        set(price_work["adjustment_confidence"].dropna().astype(str)) - {"OK", "LOW"}
    )
    if invalid_confidence:
        raise ValueError(f"unknown adjustment confidence values: {invalid_confidence}")

    price_groups: dict[str, pd.DataFrame] = {}
    for ticker, group in price_work.groupby("ticker", sort=False):
        price_groups[str(ticker)] = group.sort_values("_date", kind="stable").reset_index(
            drop=True
        )

    rows: list[dict[str, object]] = []
    for share_row in share_counts.itertuples(index=False):
        ticker = str(share_row.ticker)
        measurement_date = pd.to_datetime(share_row.measurement_date, errors="raise")
        share_status = str(share_row.status)
        ticker_prices = price_groups.get(ticker)

        price_date_used: object = pd.NA
        raw_close: object = np.nan
        price_confidence: object = pd.NA
        has_price = False
        if ticker_prices is not None:
            dates = ticker_prices["_date"].to_numpy(dtype="datetime64[ns]")
            position = int(
                np.searchsorted(dates, measurement_date.to_datetime64(), side="right") - 1
            )
            if position >= 0:
                price_row = ticker_prices.iloc[position]
                price_date_used = price_row["_date"].strftime("%Y-%m-%d")
                raw_close = float(price_row["raw_close"])
                price_confidence = str(price_row["adjustment_confidence"])
                has_price = True

        shares_issued = pd.to_numeric(
            pd.Series([share_row.shares_issued_derived]), errors="coerce"
        ).iloc[0]
        if not has_price:
            market_cap_status = "NO_PRICE"
            market_cap = np.nan
        else:
            market_cap_status = SHARE_STATUS_MAP[share_status]
            if market_cap_status == "NO_SHARE_COUNT":
                market_cap = np.nan
            else:
                if pd.isna(shares_issued):
                    raise ValueError(
                        f"{ticker} {share_row.quarter} has {share_status} but no share count"
                    )
                market_cap = float(raw_close) * float(shares_issued)

        rows.append(
            {
                "ticker": ticker,
                "quarter": share_row.quarter,
                "measurement_date": pd.Timestamp(measurement_date).strftime("%Y-%m-%d"),
                "price_date_used": price_date_used,
                "raw_close": raw_close,
                "shares_issued_derived": shares_issued,
                "market_cap_thousand_vnd": market_cap,
                "price_confidence": price_confidence,
                "share_status": share_status,
                "market_cap_status": market_cap_status,
            }
        )

    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def write_output(frame: pd.DataFrame, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(
        path,
        index=False,
        columns=OUTPUT_COLUMNS,
        lineterminator="\n",
        float_format="%.12f",
    )
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_from_paths(price_path: Path, share_path: Path) -> pd.DataFrame:
    prices = pd.read_csv(price_path)
    share_counts = pd.read_csv(share_path)
    return build_historical_market_cap(share_counts, prices)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument("--prices", type=Path, default=DEFAULT_PRICE_PATH)
    parser.add_argument("--shares", type=Path, default=DEFAULT_SHARE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    result = build_from_paths(args.prices, args.shares)
    first_sha256 = write_output(result, args.output)
    with tempfile.TemporaryDirectory() as temp_directory:
        second_path = Path(temp_directory) / args.output.name
        second_sha256 = write_output(result, second_path)

    print(f"rows={len(result)}")
    print(f"first_sha256={first_sha256}")
    print(f"second_sha256={second_sha256}")
    print(f"byte_reproducible={first_sha256 == second_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
