from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from collections.abc import Iterable
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.vnstock_client import VnstockClient  # noqa: E402


EARLY_START_DATE = "1900-01-01"
PRICE_ADJUSTMENT_STATUS = "ADJUSTED_OBSERVED"
PRICE_UNIT = "THOUSAND_VND"
HASH_CONVENTION = "SHA256_OF_LF_ONLY_BYTES"
RAW_HASH_CONVENTION = "SHA256_OF_RAW_BYTES"
LAST_FULL_REPORT_YEAR = 2025
FETCH_STATUSES = ("OK", "EMPTY_RESPONSE", "FETCH_ERROR", "NOT_ATTEMPTED")
DAILY_COLUMNS = ("ticker", "date", "close_adjusted", "close_adjusted_unit", "volume")
COVERAGE_COLUMNS = (
    "ticker",
    "first_date",
    "last_date",
    "n_trading_days",
    "n_usable_years",
    "first_usable_year",
    "has_internal_gap",
    "largest_gap_days",
    "fetch_status",
    "fetch_error_class",
)
SUMMARY_COLUMNS = ("year", "n_tickers_usable", "n_tickers_present_but_short", "n_tickers_absent")


class LiveVciHistoryClient:
    """Call the same VCI Quote.history path and retry policy as VnstockClient."""

    def __init__(self) -> None:
        self._client = VnstockClient(use_cache=False)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    def fetch_history(self, ticker: str, end_date: date) -> pd.DataFrame:
        self._client._polite_sleep()
        vnstock = self._client._vnstock_module()
        quote_cls = getattr(vnstock, "Quote")
        quote = self._client._quiet_call(
            quote_cls,
            source=self._client.quote_source,
            symbol=ticker,
            random_agent=True,
            show_log=False,
        )
        return self._client._to_frame(
            self._client._quiet_call(
                quote.history,
                symbol=ticker,
                start=EARLY_START_DATE,
                end=end_date.isoformat(),
                interval="1D",
            )
        )


def read_universe(path: Path) -> list[str]:
    universe = pd.read_csv(path)
    if "ticker" not in universe.columns:
        raise ValueError(f"universe has no ticker column: {path}")
    tickers = [str(value).strip().upper() for value in universe["ticker"] if str(value).strip()]
    if len(tickers) != len(set(tickers)):
        raise ValueError("universe contains duplicate tickers")
    return tickers


def normalise_api_history(ticker: str, history: pd.DataFrame) -> pd.DataFrame:
    required = {"time", "close", "volume"}
    missing = sorted(required.difference(history.columns))
    if missing:
        raise ValueError(f"unexpected VCI Quote.history shape for {ticker}; missing columns: {', '.join(missing)}")
    frame = pd.DataFrame(
        {
            "ticker": ticker,
            "date": pd.to_datetime(history["time"], errors="coerce").dt.date,
            "close_adjusted": pd.to_numeric(history["close"], errors="coerce"),
            "close_adjusted_unit": PRICE_UNIT,
            "volume": pd.to_numeric(history["volume"], errors="coerce"),
        }
    )
    frame["date"] = frame["date"].map(lambda value: value.isoformat() if pd.notna(value) else "")
    return frame.reset_index(drop=True)


def usable_years(history: pd.DataFrame) -> list[int]:
    if history.empty:
        return []
    dates = pd.to_datetime(history["date"], errors="coerce")
    closes = pd.to_numeric(history["close_adjusted"], errors="coerce")
    valid = pd.DataFrame({"date": dates, "close": closes}).dropna()
    if valid.empty:
        return []
    counts = valid.assign(year=valid["date"].dt.year).groupby("year")["date"].nunique()
    return [int(year) for year, count in counts.items() if int(count) >= 200]


def internal_gap_metrics(ticker_dates: Iterable[object], market_dates: Iterable[object]) -> tuple[bool, int]:
    observed = pd.DatetimeIndex(pd.to_datetime(list(ticker_dates), errors="coerce")).dropna().normalize().unique().sort_values()
    if len(observed) < 2:
        return False, 0
    market = pd.DatetimeIndex(pd.to_datetime(list(market_dates), errors="coerce")).dropna().normalize().unique()
    internal_market = market[(market > observed[0]) & (market < observed[-1])]
    has_internal_gap = bool(len(internal_market.difference(observed)))
    largest_gap_days = int(pd.Series(observed).diff().dt.days.dropna().max())
    return has_internal_gap, largest_gap_days


def build_coverage(
    tickers: list[str],
    daily: pd.DataFrame,
    statuses: dict[str, str],
    error_classes: dict[str, str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    error_classes = error_classes or {}
    unknown_statuses = sorted(set(statuses.values()).difference(FETCH_STATUSES))
    if unknown_statuses:
        raise ValueError("unknown fetch status: " + ", ".join(unknown_statuses))
    valid_dates = pd.to_datetime(daily.get("date", pd.Series(dtype=str)), errors="coerce").dropna()
    market_dates = valid_dates.unique()
    rows: list[dict[str, object]] = []
    for ticker in tickers:
        ticker_history = daily[daily["ticker"] == ticker].copy() if not daily.empty else daily.copy()
        non_null = ticker_history[pd.to_numeric(ticker_history.get("close_adjusted"), errors="coerce").notna()].copy()
        dates = pd.to_datetime(non_null.get("date", pd.Series(dtype=str)), errors="coerce").dropna()
        years = usable_years(non_null)
        has_gap, largest_gap = internal_gap_metrics(dates, market_dates)
        rows.append(
            {
                "ticker": ticker,
                "first_date": dates.min().date().isoformat() if not dates.empty else "",
                "last_date": dates.max().date().isoformat() if not dates.empty else "",
                "n_trading_days": int(dates.dt.normalize().nunique()) if not dates.empty else 0,
                "n_usable_years": len(years),
                "first_usable_year": min(years) if years else "",
                "has_internal_gap": has_gap,
                "largest_gap_days": largest_gap,
                "fetch_status": statuses.get(ticker, "NOT_ATTEMPTED"),
                "fetch_error_class": error_classes.get(ticker, ""),
            }
        )
    coverage = pd.DataFrame(rows, columns=COVERAGE_COLUMNS)
    summary_rows: list[dict[str, int]] = []
    if not daily.empty and valid_dates.notna().any():
        first_year = int(valid_dates.dt.year.min())
        for year in range(first_year, LAST_FULL_REPORT_YEAR + 1):
            year_rows = daily[pd.to_datetime(daily["date"], errors="coerce").dt.year == year].copy()
            counts = (
                year_rows.assign(_close=pd.to_numeric(year_rows["close_adjusted"], errors="coerce"))
                .dropna(subset=["_close"])
                .drop_duplicates(["ticker", "date"])
                .groupby("ticker")["date"]
                .nunique()
            )
            usable = int((counts >= 200).sum())
            present_short = int(((counts > 0) & (counts < 200)).sum())
            summary_rows.append(
                {
                    "year": year,
                    "n_tickers_usable": usable,
                    "n_tickers_present_but_short": present_short,
                    "n_tickers_absent": len(tickers) - usable - present_short,
                }
            )
    summary = pd.DataFrame(summary_rows, columns=SUMMARY_COLUMNS)
    return coverage, summary


def _normalise_lf(path: Path) -> None:
    content = path.read_bytes()
    normalised = content.replace(b"\r\n", b"\n")
    if normalised != content:
        path.write_bytes(normalised)


def _sha256(path: Path) -> str:
    content = path.read_bytes()
    if b"\r\n" in content:
        raise RuntimeError(f"refusing to hash non-LF-only file: {path}")
    return hashlib.sha256(content).hexdigest()


def _sha256_raw(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_daily_gzip(daily: pd.DataFrame, path: Path) -> str:
    ordered = daily[list(DAILY_COLUMNS)].sort_values(["ticker", "date"], kind="stable")
    ordered.to_csv(
        path,
        index=False,
        lineterminator="\n",
        compression={"method": "gzip", "compresslevel": 6, "mtime": 0},
    )
    return _sha256_raw(path)


def write_manifest(output_dir: Path, main_sha: str, fetch_date: str, created_at: datetime) -> pd.DataFrame:
    manifest_path = output_dir / "MANIFEST.csv"
    files = sorted(path for path in output_dir.iterdir() if path.is_file() and path.name != manifest_path.name)
    for path in files:
        if path.suffix != ".gz":
            _normalise_lf(path)
    created_text = created_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    manifest = pd.DataFrame(
        [
            {
                "file": path.name,
                "sha256": _sha256_raw(path) if path.suffix == ".gz" else _sha256(path),
                "hash_convention": RAW_HASH_CONVENTION if path.suffix == ".gz" else HASH_CONVENTION,
                "main_commit_sha": main_sha,
                "created_at_utc": created_text,
                "fetch_date": fetch_date,
                "price_adjustment_status": PRICE_ADJUSTMENT_STATUS,
            }
            for path in files
        ]
    )
    manifest.to_csv(manifest_path, index=False, lineterminator="\n")
    _normalise_lf(manifest_path)
    return manifest


def _read_existing(
    output_dir: Path, tickers: list[str]
) -> tuple[pd.DataFrame, dict[str, str], dict[str, str]]:
    daily_path = output_dir / "daily_close.csv"
    daily_gzip_path = output_dir / "daily_close.csv.gz"
    coverage_path = output_dir / "coverage_by_ticker.csv"
    if daily_gzip_path.exists():
        daily = pd.read_csv(daily_gzip_path, compression="gzip")
    elif daily_path.exists():
        daily = pd.read_csv(daily_path)
    else:
        daily = pd.DataFrame(columns=DAILY_COLUMNS)
    statuses = {ticker: "NOT_ATTEMPTED" for ticker in tickers}
    error_classes = {ticker: "" for ticker in tickers}
    if coverage_path.exists():
        existing = pd.read_csv(coverage_path, keep_default_na=False)
        legacy_map = {
            "PARTIAL_RUN": "NOT_ATTEMPTED",
            "NO_DATA": "EMPTY_RESPONSE",
            "API_ERROR": "FETCH_ERROR",
        }
        for row in existing.itertuples(index=False):
            ticker = str(row.ticker).strip().upper()
            if ticker not in statuses:
                continue
            statuses[ticker] = legacy_map.get(str(row.fetch_status), str(row.fetch_status))
            error_classes[ticker] = str(getattr(row, "fetch_error_class", ""))
    return daily, statuses, error_classes


def _write_artifacts(
    output_dir: Path,
    tickers: list[str],
    daily: pd.DataFrame,
    statuses: dict[str, str],
    error_classes: dict[str, str],
    main_sha: str,
    fetch_date: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    daily = daily[list(DAILY_COLUMNS)]
    coverage, summary = build_coverage(tickers, daily, statuses, error_classes)
    gzip_path = output_dir / "daily_close.csv.gz"
    write_daily_gzip(daily, gzip_path)
    uncompressed_path = output_dir / "daily_close.csv"
    if uncompressed_path.exists():
        uncompressed_path.unlink()
    coverage.to_csv(output_dir / "coverage_by_ticker.csv", index=False, lineterminator="\n")
    summary.to_csv(output_dir / "coverage_summary.csv", index=False, lineterminator="\n")
    write_manifest(output_dir, main_sha, fetch_date, datetime.now(timezone.utc))


def _main_sha(repo_root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "main"], cwd=repo_root, check=True, capture_output=True, text=True
    ).stdout.strip()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure reachable VCI daily price history without computing returns.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--fetch-date", default=date.today().isoformat())
    parser.add_argument(
        "--batch-size",
        type=int,
        default=0,
        help="Maximum untouched tickers to fetch this run; 0 means all remaining tickers.",
    )
    parser.add_argument(
        "--tickers",
        nargs="*",
        help="Optional universe tickers to fetch in this resumable run; all others remain PARTIAL_RUN.",
    )
    args = parser.parse_args(argv)
    if args.batch_size < 0:
        parser.error("--batch-size must be zero or positive")
    if args.tickers:
        args.tickers = list(
            dict.fromkeys(str(ticker).strip().upper() for ticker in args.tickers if str(ticker).strip())
        )
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    fetch_day = date.fromisoformat(args.fetch_date)
    tickers = read_universe(repo_root / "data" / "universe.csv")
    output_dir = repo_root / "data" / "price_history" / fetch_day.isoformat()
    daily, statuses, error_classes = _read_existing(output_dir, tickers)
    remaining = [ticker for ticker in tickers if statuses.get(ticker) == "NOT_ATTEMPTED"]
    if args.tickers:
        unknown = sorted(set(args.tickers).difference(tickers))
        if unknown:
            raise ValueError("requested tickers are not in data/universe.csv: " + ", ".join(unknown))
        wanted = set(args.tickers)
        selected = [ticker for ticker in remaining if ticker in wanted]
    else:
        selected = remaining
    selected = selected[: args.batch_size or None]
    client = LiveVciHistoryClient()
    main_sha = _main_sha(repo_root)

    try:
        for index, ticker in enumerate(selected, start=1):
            try:
                raw = client.fetch_history(ticker, fetch_day)
                if raw.empty:
                    normalised = pd.DataFrame(columns=DAILY_COLUMNS)
                    statuses[ticker] = "EMPTY_RESPONSE"
                else:
                    normalised = normalise_api_history(ticker, raw)
                    usable = pd.to_datetime(normalised["date"], errors="coerce").notna() & pd.to_numeric(
                        normalised["close_adjusted"], errors="coerce"
                    ).notna()
                    if not usable.any():
                        raise ValueError("provider returned rows but none had a usable date and close")
                    daily = normalised.copy() if daily.empty else pd.concat([daily, normalised], ignore_index=True)
                    statuses[ticker] = "OK"
                error_classes[ticker] = ""
                print(
                    f"FETCHED {index}/{len(selected)} {ticker} rows={len(normalised)} status={statuses[ticker]}",
                    flush=True,
                )
            except BaseException as exc:  # noqa: BLE001 - preserve provider failures as explicit status.
                if isinstance(exc, KeyboardInterrupt):
                    raise
                statuses[ticker] = "FETCH_ERROR"
                error_classes[ticker] = type(exc).__name__
                print(f"FETCH_ERROR {ticker}: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
    finally:
        _write_artifacts(
            output_dir,
            tickers,
            daily,
            statuses,
            error_classes,
            main_sha,
            fetch_day.isoformat(),
        )

    counts = pd.Series(statuses).value_counts().sort_index()
    for status, count in counts.items():
        print(f"FETCH_STATUS {status}={int(count)}")
    print(f"OUTPUT_DIR={output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
