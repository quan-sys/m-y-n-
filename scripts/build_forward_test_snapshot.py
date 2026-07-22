from __future__ import annotations

import argparse
import hashlib
import importlib
import math
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Protocol

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.vnstock_client import VnstockClient


SNAPSHOT_DATE = date(2026, 7, 21)
WINDOW_END = date(2026, 7, 28)
PORTFOLIO_FILES = ("portfolio_ebit_tev.csv", "portfolio_ep.csv")
PORTFOLIO_LABELS = {
    "portfolio_ebit_tev.csv": "EBIT_TEV",
    "portfolio_ep.csv": "EP",
}
BENCHMARK_SYMBOLS = ("VNINDEX",)
SANITY_SYMBOLS = ("FPT", "VNM", "VIC")
RAW_STATUS = "NOT_AVAILABLE_SINGLE_ADJUSTED_SERIES"
INDEX_RAW_STATUS = "NOT_APPLICABLE_INDEX"
PRICE_UNIT = "THOUSAND_VND"
INDEX_UNIT = "INDEX_POINTS"
PRICE_SOURCE = "vnstock.Quote.history"
PRICE_PROVIDER = "VCI"
HASH_CONVENTION = "SHA256_OF_LF_ONLY_BYTES"
OUTPUT_COLUMNS = (
    "portfolio_id",
    "ticker",
    "fill_session_date",
    "close_raw",
    "close_raw_status",
    "close_adjusted",
    "close_adjusted_unit",
    "price_source",
    "price_provider",
    "price_as_of",
    "fill_status",
    "target_weight",
)


class PriceClient(Protocol):
    def fetch_price_history(self, ticker: str, months: int = 1) -> pd.DataFrame: ...


@dataclass(frozen=True)
class FillObservation:
    fill_session_date: str
    close_adjusted: float
    price_as_of: str
    fill_status: str = "FILLED"


class SnapshotExistsError(RuntimeError):
    pass


class MissingCloseError(RuntimeError):
    pass


class LiveVciPriceClient:
    """Use the repository's existing VnstockClient -> VCI Quote.history path."""

    def __init__(self) -> None:
        self._client = object.__new__(VnstockClient)
        settings = {
            "source": "vnstock",
            "listing_source": "VCI",
            "quote_source": "VCI",
            "company_source": "VCI",
            "min_sleep_seconds": 2.8,
            "max_sleep_seconds": 3.6,
            "use_cache": False,
            "_terminal_api_error": None,
        }
        for name, value in settings.items():
            setattr(self._client, name, value)

    def fetch_price_history(self, ticker: str, months: int = 1) -> pd.DataFrame:
        _import_vnstock_without_upgrade_check()
        return self._client._fetch_price_history(ticker=ticker, months=months)


def _import_vnstock_without_upgrade_check() -> None:
    """Avoid a non-price package-update request; quote requests remain untouched."""
    try:
        import requests
    except ImportError:
        importlib.import_module("vnstock")
        return

    original_get = requests.get

    def skip_package_update(url: str, *args: object, **kwargs: object) -> object:
        if "pypi.org" in str(url):
            raise requests.exceptions.RequestException("package update check disabled")
        return original_get(url, *args, **kwargs)

    requests.get = skip_package_update
    try:
        importlib.import_module("vnstock")
    finally:
        requests.get = original_get


def select_fill(history: pd.DataFrame) -> FillObservation | None:
    if history.empty:
        return None
    date_column = next(
        (column for column in ("time", "date", "trading_date", "tradingDate", "datetime") if column in history),
        None,
    )
    if date_column is None or "close" not in history:
        return None
    candidates = history.copy()
    candidates["_session_date"] = pd.to_datetime(candidates[date_column], errors="coerce")
    candidates["_close"] = pd.to_numeric(candidates["close"], errors="coerce")
    candidates = candidates[
        candidates["_session_date"].notna()
        & candidates["_close"].notna()
        & candidates["_session_date"].dt.date.between(SNAPSHOT_DATE, WINDOW_END)
    ].sort_values("_session_date")
    if candidates.empty:
        return None
    first = candidates.iloc[0]
    close = float(first["_close"])
    if not math.isfinite(close):
        return None
    session_date = first["_session_date"].date().isoformat()
    price_as_of = candidates["_session_date"].max().date().isoformat()
    return FillObservation(session_date, close, price_as_of)


def no_session_in_window() -> dict[str, object]:
    return {
        "fill_session_date": "",
        "close_adjusted": "",
        "price_as_of": "",
        "fill_status": "NO_SESSION_IN_WINDOW",
    }


def _filled_row(portfolio_id: str, ticker: str, target_weight: object, fill: FillObservation) -> dict[str, object]:
    return {
        "portfolio_id": portfolio_id,
        "ticker": ticker,
        "fill_session_date": fill.fill_session_date,
        "close_raw": "",
        "close_raw_status": RAW_STATUS,
        "close_adjusted": fill.close_adjusted,
        "close_adjusted_unit": PRICE_UNIT,
        "price_source": PRICE_SOURCE,
        "price_provider": PRICE_PROVIDER,
        "price_as_of": fill.price_as_of,
        "fill_status": fill.fill_status,
        "target_weight": target_weight,
    }


def _benchmark_row(ticker: str, fill: FillObservation) -> dict[str, object]:
    row = _filled_row("VN_INDEX", ticker, "", fill)
    row["close_raw_status"] = INDEX_RAW_STATUS
    row["close_adjusted_unit"] = INDEX_UNIT
    return row


def _normalise_lf(path: Path) -> bool:
    original = path.read_bytes()
    normalised = original.replace(b"\r\n", b"\n")
    if normalised == original:
        return False
    path.write_bytes(normalised)
    return True


def _sha256(path: Path) -> str:
    content = path.read_bytes()
    if b"\r\n" in content:
        raise RuntimeError(f"refusing to hash non-LF-only file: {path}")
    digest = hashlib.sha256()
    digest.update(content)
    return digest.hexdigest()


def copy_portfolios(source_dir: Path, target_dir: Path) -> None:
    for filename in PORTFOLIO_FILES:
        shutil.copyfile(source_dir / filename, target_dir / filename)


def _main_sha(repo_root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "main"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _write_manifest(target_dir: Path, commit_sha: str, created: datetime) -> pd.DataFrame:
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    created_text = created.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    payload_files = (*PORTFOLIO_FILES, "fills.csv", "benchmark.csv")
    for filename in payload_files:
        _normalise_lf(target_dir / filename)
    manifest = pd.DataFrame(
        [
            {
                "file": filename,
                "sha256": _sha256(target_dir / filename),
                "hash_convention": HASH_CONVENTION,
                "main_commit_sha": commit_sha,
                "created_at_utc": created_text,
            }
            for filename in payload_files
        ]
    )
    manifest_path = target_dir / "MANIFEST.csv"
    manifest.to_csv(manifest_path, index=False, lineterminator="\n")
    if b"\r\n" in manifest_path.read_bytes():
        raise RuntimeError(f"manifest is not LF-only: {manifest_path}")
    return manifest


def build_snapshot(
    repo_root: Path,
    client: PriceClient,
    *,
    created_at_utc: datetime | None = None,
    main_sha: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, FillObservation]]:
    source_dir = repo_root / "reports" / "2026-07-20"
    target_dir = repo_root / "data" / "forward_test" / "snapshots" / SNAPSHOT_DATE.isoformat()
    if target_dir.exists():
        raise SnapshotExistsError(f"refusing to overwrite existing snapshot directory: {target_dir}")

    portfolios = {filename: pd.read_csv(source_dir / filename) for filename in PORTFOLIO_FILES}
    portfolio_tickers = sorted(
        {str(ticker).strip().upper() for frame in portfolios.values() for ticker in frame["ticker"]}
    )
    requested_symbols = portfolio_tickers + [symbol for symbol in SANITY_SYMBOLS if symbol not in portfolio_tickers]

    observations: dict[str, FillObservation] = {}
    missing: list[str] = []
    for ticker in requested_symbols:
        observation = select_fill(client.fetch_price_history(ticker, months=1))
        if observation is None:
            missing.append(ticker)
        else:
            observations[ticker] = observation

    benchmark_symbol = ""
    for attempted_symbol in BENCHMARK_SYMBOLS:
        observation = select_fill(client.fetch_price_history(attempted_symbol, months=1))
        if observation is not None:
            benchmark_symbol = attempted_symbol
            observations[attempted_symbol] = observation
            break
    if not benchmark_symbol:
        missing.append("benchmark attempted symbols: " + ", ".join(BENCHMARK_SYMBOLS))

    missing_portfolio_rows = [
        f"{PORTFOLIO_LABELS[filename]}:{str(row.ticker).strip().upper()}"
        for filename, frame in portfolios.items()
        for row in frame.itertuples(index=False)
        if str(row.ticker).strip().upper() not in observations
    ]
    if missing or missing_portfolio_rows:
        details = sorted(set(missing + missing_portfolio_rows))
        raise MissingCloseError("missing usable close; snapshot not created: " + ", ".join(details))

    fill_rows: list[dict[str, object]] = []
    for filename, frame in portfolios.items():
        for row in frame.itertuples(index=False):
            ticker = str(row.ticker).strip().upper()
            fill_rows.append(_filled_row(PORTFOLIO_LABELS[filename], ticker, row.target_weight, observations[ticker]))
    fills = pd.DataFrame(fill_rows, columns=OUTPUT_COLUMNS)
    benchmark = pd.DataFrame(
        [_benchmark_row(benchmark_symbol, observations[benchmark_symbol])],
        columns=OUTPUT_COLUMNS,
    )

    if len(fills) != 40 or len(benchmark) != 1:
        raise RuntimeError(f"unexpected output row counts: fills={len(fills)}, benchmark={len(benchmark)}")
    combined = pd.concat([fills, benchmark], ignore_index=True)
    if combined["close_adjusted"].isna().any() or (combined["fill_session_date"] < SNAPSHOT_DATE.isoformat()).any():
        raise RuntimeError("invalid fill date or adjusted close; snapshot not created")

    target_dir.mkdir(parents=True)
    copy_portfolios(source_dir, target_dir)
    fills.to_csv(target_dir / "fills.csv", index=False, lineterminator="\n")
    benchmark.to_csv(target_dir / "benchmark.csv", index=False, lineterminator="\n")

    created = created_at_utc or datetime.now(timezone.utc)
    _write_manifest(target_dir, main_sha or _main_sha(repo_root), created)
    return fills, benchmark, observations


def main() -> int:
    parser = argparse.ArgumentParser(description="Open the immutable 2026-07-21 forward-test snapshot.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    fills, benchmark, observations = build_snapshot(args.repo_root.resolve(), LiveVciPriceClient())
    print(pd.concat([fills, benchmark], ignore_index=True).to_csv(index=False), end="")
    print("MAGNITUDE_SANITY")
    for ticker in SANITY_SYMBOLS:
        print(f"{ticker},{observations[ticker].close_adjusted},{PRICE_UNIT}")
    raw_count = int((pd.concat([fills, benchmark])["close_raw_status"] == RAW_STATUS).sum())
    print(f"RAW_STATUS_COUNT={raw_count}")
    print("MANIFEST_EXCLUDES_ITSELF=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
