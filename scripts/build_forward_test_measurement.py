from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
import hashlib
import math
from pathlib import Path
import subprocess
import sys
from typing import Protocol

import pandas as pd


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.build_forward_test_snapshot import (  # noqa: E402
    HASH_CONVENTION,
    LiveVciPriceClient,
    PRICE_PROVIDER,
    PRICE_SOURCE,
)


SNAPSHOT_DATE = date(2026, 7, 21)
SNAPSHOT_DIRECTORY = Path("data") / "forward_test" / "snapshots" / SNAPSHOT_DATE.isoformat()
MEASUREMENTS_DIRECTORY = Path("data") / "forward_test" / "measurements"
BENCHMARK_TICKER = "VNINDEX"
MEASUREMENT_TYPES = {
    "quarterly": "QUARTERLY",
    "dry-run": "DRY_RUN_NOT_A_QUARTERLY_MEASUREMENT",
}
FILLED = "FILLED"
NO_SESSION_ON_OR_BEFORE = "NO_SESSION_ON_OR_BEFORE"
NO_FILLED_POSITIONS = "NO_FILLED_POSITIONS"
MANIFEST_FILES = ("positions.csv", "portfolio_returns.csv", "benchmark.csv")
POSITION_COLUMNS = (
    "measurement_type",
    "portfolio_id",
    "ticker",
    "fill_session_date",
    "target_weight",
    "entry_close_adjusted_stored",
    "entry_close_adjusted_refetched",
    "refetch_drift_pct",
    "measurement_session_date",
    "measurement_close",
    "ticker_return_pct",
    "weighted_contribution_pct",
    "excluded_weight",
    "measurement_status",
    "price_source",
    "price_provider",
    "price_as_of",
    "source",
    "as_of",
    "data_status",
)
PORTFOLIO_RETURN_COLUMNS = (
    "measurement_type",
    "portfolio_id",
    "portfolio_return_pct",
    "included_weight",
    "excluded_weight",
    "position_count",
    "filled_position_count",
    "excluded_position_count",
    "measurement_status",
    "source",
    "as_of",
    "data_status",
)
BENCHMARK_COLUMNS = (
    "measurement_type",
    "ticker",
    "fill_session_date",
    "entry_close_adjusted_stored",
    "entry_close_adjusted_refetched",
    "refetch_drift_pct",
    "measurement_session_date",
    "measurement_close",
    "benchmark_return_pct",
    "measurement_status",
    "price_source",
    "price_provider",
    "price_as_of",
    "source",
    "as_of",
    "data_status",
)
MANIFEST_COLUMNS = (
    "measurement_type",
    "file",
    "sha256",
    "hash_convention",
    "main_commit_sha",
    "created_at_utc",
)


class PriceClient(Protocol):
    def fetch_price_history(self, ticker: str, months: int = 1) -> pd.DataFrame: ...


class FutureMeasurementDateError(ValueError):
    pass


class MeasurementExistsError(RuntimeError):
    pass


class MeasurementFetchError(RuntimeError):
    pass


@dataclass(frozen=True)
class PriceObservation:
    entry_close_adjusted_refetched: float
    measurement_session_date: str
    measurement_close: float
    price_as_of: str


@dataclass(frozen=True)
class MeasurementResult:
    positions: pd.DataFrame
    portfolio_returns: pd.DataFrame
    benchmark: pd.DataFrame
    manifest: pd.DataFrame
    provider_fetch_count: int
    output_directory: Path


def _number(value: object, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be numeric") from error
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def _history_dates_and_closes(history: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if history.empty:
        raise MeasurementFetchError(f"{ticker}: empty series")
    date_column = next(
        (column for column in ("time", "date", "trading_date", "tradingDate", "datetime") if column in history),
        None,
    )
    if date_column is None or "close" not in history:
        raise MeasurementFetchError(f"{ticker}: series missing date or close column")
    rows = pd.DataFrame(
        {
            "session_date": pd.to_datetime(history[date_column], errors="coerce").dt.normalize(),
            "close": pd.to_numeric(history["close"], errors="coerce"),
        }
    )
    rows = rows.loc[rows["session_date"].notna() & rows["close"].gt(0)].copy()
    if rows.empty:
        raise MeasurementFetchError(f"{ticker}: series has no positive traded close")
    return rows.sort_values("session_date", kind="mergesort").drop_duplicates(
        "session_date",
        keep="last",
    )


def _required_lookback_months(run_date: date, snapshot_fill_session_dates: list[str]) -> int:
    if not snapshot_fill_session_dates:
        raise ValueError("snapshot has no fill session date")
    oldest_fill_session = min(date.fromisoformat(value) for value in snapshot_fill_session_dates)
    span_days = max(0, (run_date - oldest_fill_session).days)
    return max(3, math.ceil(span_days / 30) + 2)


def select_measurement_session(
    history: pd.DataFrame,
    measurement_date: date,
) -> tuple[str, float] | None:
    date_column = next(
        (column for column in ("time", "date", "trading_date", "tradingDate", "datetime") if column in history),
        None,
    )
    if history.empty or date_column is None or "close" not in history:
        return None
    rows = pd.DataFrame(
        {
            "session_date": pd.to_datetime(history[date_column], errors="coerce").dt.normalize(),
            "close": pd.to_numeric(history["close"], errors="coerce"),
        }
    )
    rows = rows.loc[
        rows["session_date"].notna()
        & rows["close"].gt(0)
        & rows["session_date"].le(pd.Timestamp(measurement_date))
    ].sort_values("session_date", kind="mergesort")
    if rows.empty:
        return None
    selected = rows.iloc[-1]
    return selected["session_date"].date().isoformat(), float(selected["close"])


def _price_observation(
    ticker: str,
    history: pd.DataFrame,
    fill_session_date: str,
    measurement_date: date,
    requested_months: int,
) -> PriceObservation | None:
    rows = _history_dates_and_closes(history, ticker)
    fill_day = pd.Timestamp(fill_session_date).normalize()
    latest = pd.Timestamp(rows["session_date"].max()).normalize()
    earliest = pd.Timestamp(rows["session_date"].min()).normalize()
    session_count = len(rows)
    if latest < fill_day:
        raise MeasurementFetchError(
            f"{ticker}: latest session {latest.date().isoformat()} is earlier than snapshot fill session "
            f"{fill_session_date}; requested_months={requested_months}; "
            f"earliest_session={earliest.date().isoformat()}; latest_session={latest.date().isoformat()}; "
            f"session_count={session_count}"
        )
    resolved = select_measurement_session(history, measurement_date)
    if resolved is None:
        return None
    entry_rows = rows.loc[rows["session_date"].eq(fill_day)]
    if entry_rows.empty:
        raise MeasurementFetchError(
            f"{ticker}: fetched series has no close for snapshot fill session {fill_session_date}; "
            f"requested_months={requested_months}; earliest_session={earliest.date().isoformat()}; "
            f"latest_session={latest.date().isoformat()}; session_count={session_count}"
        )
    entry_close = float(entry_rows.iloc[-1]["close"])
    measurement_session_date, measurement_close = resolved
    return PriceObservation(
        entry_close_adjusted_refetched=entry_close,
        measurement_session_date=measurement_session_date,
        measurement_close=measurement_close,
        price_as_of=latest.date().isoformat(),
    )


def _measurement_type(mode: str) -> str:
    try:
        return MEASUREMENT_TYPES[mode]
    except KeyError as error:
        raise ValueError(f"unknown measurement mode: {mode}") from error


def _read_snapshot(snapshot_directory: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    fills = pd.read_csv(snapshot_directory / "fills.csv", dtype=str, keep_default_na=False)
    benchmark = pd.read_csv(snapshot_directory / "benchmark.csv", dtype=str, keep_default_na=False)
    fill_columns = {"portfolio_id", "ticker", "fill_session_date", "close_adjusted", "fill_status", "target_weight"}
    benchmark_columns = {"ticker", "fill_session_date", "close_adjusted", "fill_status"}
    missing_fills = sorted(fill_columns.difference(fills.columns))
    missing_benchmark = sorted(benchmark_columns.difference(benchmark.columns))
    if missing_fills:
        raise ValueError("snapshot fills missing columns: " + ", ".join(missing_fills))
    if missing_benchmark:
        raise ValueError("snapshot benchmark missing columns: " + ", ".join(missing_benchmark))
    if not fills["fill_status"].eq(FILLED).all() or not benchmark["fill_status"].eq(FILLED).all():
        raise MeasurementFetchError("snapshot contains a row without a FILLED entry close")
    return fills.copy(), benchmark.copy()


def _fetch_once_per_symbol(
    client: PriceClient,
    symbols: list[str],
    months: int,
) -> tuple[dict[str, pd.DataFrame], int]:
    histories: dict[str, pd.DataFrame] = {}
    for ticker in symbols:
        try:
            # The provider window is 31 * months + 10 days back from TODAY (the
            # run date), not from the measurement date, so the span uses run_date.
            history = client.fetch_price_history(ticker, months=months)
        except BaseException as error:  # noqa: BLE001
            raise MeasurementFetchError(f"{ticker}: {error}") from error
        if history.empty:
            raise MeasurementFetchError(f"{ticker}: empty series")
        histories[ticker] = history.copy()
    return histories, len(symbols)


def _position_row(
    snapshot_row: pd.Series,
    observation: PriceObservation | None,
    measurement_type: str,
) -> dict[str, object]:
    ticker = str(snapshot_row["ticker"]).strip().upper()
    stored = _number(snapshot_row["close_adjusted"], f"{ticker} stored close")
    weight = _number(snapshot_row["target_weight"], f"{ticker} target weight")
    common = {
        "measurement_type": measurement_type,
        "portfolio_id": str(snapshot_row["portfolio_id"]),
        "ticker": ticker,
        "fill_session_date": str(snapshot_row["fill_session_date"]),
        "target_weight": weight,
        "entry_close_adjusted_stored": stored,
        "price_source": PRICE_SOURCE,
        "price_provider": PRICE_PROVIDER,
        "source": "data/forward_test/snapshots/2026-07-21/fills.csv",
        "as_of": str(snapshot_row["fill_session_date"]),
    }
    if observation is None:
        return {
            **common,
            "entry_close_adjusted_refetched": "",
            "refetch_drift_pct": "",
            "measurement_session_date": "",
            "measurement_close": "",
            "ticker_return_pct": "",
            "weighted_contribution_pct": "",
            "excluded_weight": weight,
            "measurement_status": NO_SESSION_ON_OR_BEFORE,
            "price_as_of": "",
            "data_status": "MISSING_DATA",
        }
    entry_refetched = observation.entry_close_adjusted_refetched
    ticker_return_pct = (observation.measurement_close / entry_refetched - 1.0) * 100.0
    return {
        **common,
        "entry_close_adjusted_refetched": entry_refetched,
        "refetch_drift_pct": (entry_refetched - stored) / stored * 100.0,
        "measurement_session_date": observation.measurement_session_date,
        "measurement_close": observation.measurement_close,
        "ticker_return_pct": ticker_return_pct,
        "weighted_contribution_pct": weight * ticker_return_pct,
        "excluded_weight": 0.0,
        "measurement_status": FILLED,
        "price_as_of": observation.price_as_of,
        "data_status": "OK",
    }


def _portfolio_return_rows(
    positions: pd.DataFrame,
    measurement_type: str,
    snapshot_as_of: str,
    positions_source: str,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for portfolio_id, frame in positions.groupby("portfolio_id", sort=True):
        weights = pd.to_numeric(frame["target_weight"], errors="raise")
        filled = frame["measurement_status"].eq(FILLED)
        included_weight = float(weights.loc[filled].sum())
        excluded_weight = float(weights.loc[~filled].sum())
        if included_weight == 0:
            portfolio_return: float | str = ""
            status = NO_FILLED_POSITIONS
            data_status = "MISSING_DATA"
        else:
            returns = pd.to_numeric(frame.loc[filled, "ticker_return_pct"], errors="raise")
            portfolio_return = float((weights.loc[filled] * returns).sum() / included_weight)
            status = FILLED
            data_status = "OK"
        rows.append(
            {
                "measurement_type": measurement_type,
                "portfolio_id": portfolio_id,
                "portfolio_return_pct": portfolio_return,
                "included_weight": included_weight,
                "excluded_weight": excluded_weight,
                "position_count": len(frame),
                "filled_position_count": int(filled.sum()),
                "excluded_position_count": int((~filled).sum()),
                "measurement_status": status,
                "source": positions_source,
                "as_of": snapshot_as_of,
                "data_status": data_status,
            }
        )
    return pd.DataFrame(rows, columns=PORTFOLIO_RETURN_COLUMNS)


def _benchmark_row(
    snapshot_row: pd.Series,
    observation: PriceObservation | None,
    measurement_type: str,
) -> dict[str, object]:
    ticker = str(snapshot_row["ticker"]).strip().upper()
    stored = _number(snapshot_row["close_adjusted"], "VNINDEX stored close")
    common = {
        "measurement_type": measurement_type,
        "ticker": ticker,
        "fill_session_date": str(snapshot_row["fill_session_date"]),
        "entry_close_adjusted_stored": stored,
        "price_source": PRICE_SOURCE,
        "price_provider": PRICE_PROVIDER,
        "source": "data/forward_test/snapshots/2026-07-21/benchmark.csv",
        "as_of": str(snapshot_row["fill_session_date"]),
    }
    if observation is None:
        return {
            **common,
            "entry_close_adjusted_refetched": "",
            "refetch_drift_pct": "",
            "measurement_session_date": "",
            "measurement_close": "",
            "benchmark_return_pct": "",
            "measurement_status": NO_SESSION_ON_OR_BEFORE,
            "price_as_of": "",
            "data_status": "MISSING_DATA",
        }
    entry_refetched = observation.entry_close_adjusted_refetched
    return {
        **common,
        "entry_close_adjusted_refetched": entry_refetched,
        "refetch_drift_pct": (entry_refetched - stored) / stored * 100.0,
        "measurement_session_date": observation.measurement_session_date,
        "measurement_close": observation.measurement_close,
        "benchmark_return_pct": (observation.measurement_close / entry_refetched - 1.0) * 100.0,
        "measurement_status": FILLED,
        "price_as_of": observation.price_as_of,
        "data_status": "OK",
    }


def _normalise_lf(path: Path) -> None:
    path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


def _sha256_lf(path: Path) -> str:
    content = path.read_bytes()
    if b"\r\n" in content:
        raise RuntimeError(f"refusing to hash non-LF-only file: {path}")
    return hashlib.sha256(content).hexdigest()


def _main_sha(repo_root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "origin/main"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _write_manifest(
    output_directory: Path,
    measurement_type: str,
    main_sha: str,
    created_at_utc: datetime,
) -> pd.DataFrame:
    created = created_at_utc if created_at_utc.tzinfo else created_at_utc.replace(tzinfo=timezone.utc)
    created_text = created.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    for filename in MANIFEST_FILES:
        _normalise_lf(output_directory / filename)
    manifest = pd.DataFrame(
        [
            {
                "measurement_type": measurement_type,
                "file": filename,
                "sha256": _sha256_lf(output_directory / filename),
                "hash_convention": HASH_CONVENTION,
                "main_commit_sha": main_sha,
                "created_at_utc": created_text,
            }
            for filename in MANIFEST_FILES
        ],
        columns=MANIFEST_COLUMNS,
    )
    manifest_path = output_directory / "MANIFEST.csv"
    manifest.to_csv(manifest_path, index=False, lineterminator="\n")
    _normalise_lf(manifest_path)
    return manifest


def build_measurement(
    repo_root: Path,
    client: PriceClient,
    *,
    measurement_date: date,
    mode: str,
    run_date: date | None = None,
    created_at_utc: datetime | None = None,
    main_sha: str | None = None,
    overwrite: bool = False,
) -> MeasurementResult:
    current_date = run_date or date.today()
    if measurement_date > current_date:
        raise FutureMeasurementDateError(
            f"measurement date {measurement_date.isoformat()} is in the future relative to run date "
            f"{current_date.isoformat()}"
        )
    measurement_type = _measurement_type(mode)
    snapshot_directory = repo_root / SNAPSHOT_DIRECTORY
    fills, snapshot_benchmark = _read_snapshot(snapshot_directory)
    output_directory = repo_root / MEASUREMENTS_DIRECTORY / measurement_date.isoformat()
    expected_output_files = {*MANIFEST_FILES, "MANIFEST.csv"}
    if output_directory.exists() and not overwrite:
        raise MeasurementExistsError(f"refusing to overwrite existing measurement directory: {output_directory}")
    if output_directory.exists():
        actual_output_files = {path.name for path in output_directory.iterdir()}
        if actual_output_files != expected_output_files:
            raise MeasurementExistsError(
                f"refusing to overwrite unexpected measurement directory contents: {output_directory}"
            )

    fills["ticker"] = fills["ticker"].astype(str).str.strip().str.upper()
    benchmark_row = snapshot_benchmark.iloc[0]
    benchmark_ticker = str(benchmark_row["ticker"]).strip().upper()
    if benchmark_ticker != BENCHMARK_TICKER:
        raise ValueError(f"snapshot benchmark ticker must be {BENCHMARK_TICKER}")
    symbols = sorted(set(fills["ticker"])) + [benchmark_ticker]
    snapshot_fill_session_dates = [
        *fills["fill_session_date"].astype(str).tolist(),
        *snapshot_benchmark["fill_session_date"].astype(str).tolist(),
    ]
    requested_months = _required_lookback_months(current_date, snapshot_fill_session_dates)
    histories, fetch_count = _fetch_once_per_symbol(client, symbols, requested_months)

    observations: dict[str, PriceObservation | None] = {}
    for ticker, ticker_rows in fills.groupby("ticker", sort=True):
        fill_dates = tuple(sorted(ticker_rows["fill_session_date"].unique()))
        if len(fill_dates) != 1:
            raise ValueError(f"{ticker}: snapshot has inconsistent fill session dates")
        observations[ticker] = _price_observation(
            ticker,
            histories[ticker],
            str(fill_dates[0]),
            measurement_date,
            requested_months,
        )
    benchmark_observation = _price_observation(
        benchmark_ticker,
        histories[benchmark_ticker],
        str(benchmark_row["fill_session_date"]),
        measurement_date,
        requested_months,
    )

    position_rows = [
        _position_row(snapshot_row, observations[str(snapshot_row["ticker"])], measurement_type)
        for _, snapshot_row in fills.iterrows()
    ]
    positions = pd.DataFrame(position_rows, columns=POSITION_COLUMNS)
    portfolio_returns = _portfolio_return_rows(
        positions,
        measurement_type,
        str(benchmark_row["fill_session_date"]),
        (MEASUREMENTS_DIRECTORY / measurement_date.isoformat() / "positions.csv").as_posix(),
    )
    benchmark = pd.DataFrame(
        [_benchmark_row(benchmark_row, benchmark_observation, measurement_type)],
        columns=BENCHMARK_COLUMNS,
    )

    output_directory.mkdir(parents=True, exist_ok=overwrite)
    positions.to_csv(output_directory / "positions.csv", index=False, lineterminator="\n")
    portfolio_returns.to_csv(output_directory / "portfolio_returns.csv", index=False, lineterminator="\n")
    benchmark.to_csv(output_directory / "benchmark.csv", index=False, lineterminator="\n")
    manifest = _write_manifest(
        output_directory,
        measurement_type,
        main_sha or _main_sha(repo_root),
        created_at_utc or datetime.now(timezone.utc),
    )
    return MeasurementResult(
        positions=positions,
        portfolio_returns=portfolio_returns,
        benchmark=benchmark,
        manifest=manifest,
        provider_fetch_count=fetch_count,
        output_directory=output_directory,
    )


def _print_intermediates(result: MeasurementResult) -> None:
    sjd = result.positions.loc[
        result.positions["portfolio_id"].eq("EBIT_TEV") & result.positions["ticker"].eq("SJD")
    ].iloc[0]
    benchmark = result.benchmark.iloc[0]
    print("SJD_EBIT_TEV_INTERMEDIATES")
    for column in (
        "entry_close_adjusted_stored",
        "entry_close_adjusted_refetched",
        "refetch_drift_pct",
        "measurement_session_date",
        "measurement_close",
        "ticker_return_pct",
        "target_weight",
        "weighted_contribution_pct",
    ):
        print(f"{column}={sjd[column]}")
    print("VNINDEX_INTERMEDIATES")
    for column in (
        "entry_close_adjusted_stored",
        "entry_close_adjusted_refetched",
        "refetch_drift_pct",
        "measurement_session_date",
        "measurement_close",
        "benchmark_return_pct",
    ):
        print(f"{column}={benchmark[column]}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Measure the immutable 2026-07-21 forward-test snapshot.")
    parser.add_argument("--measurement-date", type=date.fromisoformat, required=True)
    parser.add_argument("--mode", choices=tuple(MEASUREMENT_TYPES), required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    result = build_measurement(
        REPO_ROOT,
        LiveVciPriceClient(),
        measurement_date=args.measurement_date,
        mode=args.mode,
        overwrite=args.overwrite,
    )
    positions = result.positions
    ticker_counts = positions.groupby("ticker")["portfolio_id"].nunique()
    measurement_type = _measurement_type(args.mode)
    print(f"MEASUREMENT_DATE={args.measurement_date.isoformat()}")
    print(f"MEASUREMENT_TYPE={measurement_type}")
    print(f"POSITION_ROWS={len(positions)}")
    print("PORTFOLIO_ROW_COUNTS=" + ";".join(
        f"{portfolio_id}={count}"
        for portfolio_id, count in positions.groupby("portfolio_id", sort=True).size().items()
    ))
    print(f"DISTINCT_TICKERS={positions['ticker'].nunique()}")
    print(f"TICKERS_IN_BOTH_PORTFOLIOS={(ticker_counts == 2).sum()}")
    print(f"PROVIDER_FETCH_COUNT={result.provider_fetch_count}")
    stored_matches = positions["entry_close_adjusted_stored"].astype(str).eq(
        pd.read_csv(REPO_ROOT / SNAPSHOT_DIRECTORY / "fills.csv", dtype=str, keep_default_na=False)["close_adjusted"]
    )
    print(f"STORED_CLOSE_MATCHED_ROWS={int(stored_matches.sum())}")
    for ticker in ("SJD", "NCT", "PTB"):
        stored = positions.loc[positions["ticker"].eq(ticker), "entry_close_adjusted_stored"].iloc[0]
        print(f"STORED_CLOSE_{ticker}={stored}")
    nct = positions.loc[positions["ticker"].eq("NCT")].iloc[0]
    print(f"NCT_REFETCH_DRIFT_PCT={nct['refetch_drift_pct']}")
    print(f"NCT_TICKER_RETURN_PCT={nct['ticker_return_pct']}")
    for portfolio_id in ("EBIT_TEV", "EP"):
        portfolio_return = result.portfolio_returns.loc[
            result.portfolio_returns["portfolio_id"].eq(portfolio_id), "portfolio_return_pct"
        ].iloc[0]
        print(f"{portfolio_id}_PORTFOLIO_RETURN_PCT={portfolio_return}")
    print(f"BENCHMARK_ENTRY_CLOSE_ADJUSTED_STORED={result.benchmark.loc[0, 'entry_close_adjusted_stored']}")
    print(f"BENCHMARK_RETURN_PCT={result.benchmark.loc[0, 'benchmark_return_pct']}")
    print("ALL_OUTPUT_ROWS_MEASUREMENT_TYPE=" + measurement_type)
    print(f"MANIFEST_EXCLUDES_ITSELF={'MANIFEST.csv' not in set(result.manifest['file'])}")
    _print_intermediates(result)
    print(f"OUTPUT_DIRECTORY={result.output_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
