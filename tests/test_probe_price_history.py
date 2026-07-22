from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from scripts.probe_price_history import (
    FETCH_STATUSES,
    HASH_CONVENTION,
    PRICE_UNIT,
    RAW_HASH_CONVENTION,
    build_coverage,
    internal_gap_metrics,
    normalise_api_history,
    usable_years,
    write_daily_gzip,
    write_manifest,
)


def test_normalises_real_vci_quote_history_shape() -> None:
    # Shape captured from a live VCI Quote.history VNM response on 2026-07-22.
    raw = pd.DataFrame(
        [
            {"time": "2006-01-19", "open": 2.08, "high": 2.08, "low": 2.08, "close": 2.08, "volume": 109350},
            {"time": "2026-07-22", "open": 58.7, "high": 60.1, "low": 58.4, "close": 59.1, "volume": 10506300},
        ]
    )

    result = normalise_api_history("VNM", raw)

    assert result.to_dict("records") == [
        {
            "ticker": "VNM",
            "date": "2006-01-19",
            "close_adjusted": 2.08,
            "close_adjusted_unit": PRICE_UNIT,
            "volume": 109350,
        },
        {
            "ticker": "VNM",
            "date": "2026-07-22",
            "close_adjusted": 59.1,
            "close_adjusted_unit": PRICE_UNIT,
            "volume": 10506300,
        },
    ]


def test_p5_requires_200_distinct_non_null_closes() -> None:
    dates_2020 = pd.bdate_range("2020-01-01", periods=200)
    dates_2021 = pd.bdate_range("2021-01-01", periods=200)
    history = pd.DataFrame(
        {
            "date": [*dates_2020.strftime("%Y-%m-%d"), *dates_2021.strftime("%Y-%m-%d")],
            "close_adjusted": [10.0] * 200 + [11.0] * 199 + [None],
        }
    )

    assert usable_years(history) == [2020]


def test_internal_gap_uses_observed_market_dates() -> None:
    market_dates = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06", "2020-01-07"])

    has_gap, largest_gap = internal_gap_metrics(
        pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-07"]), market_dates
    )

    assert has_gap is True
    assert largest_gap == 4


def test_coverage_keeps_every_universe_ticker() -> None:
    daily = pd.DataFrame(
        [
            {"ticker": "AAA", "date": "2020-01-02", "close_adjusted": 10.0, "close_adjusted_unit": PRICE_UNIT, "volume": 1},
        ]
    )

    coverage, _ = build_coverage(["AAA", "BBB"], daily, {"AAA": "OK", "BBB": "NOT_ATTEMPTED"})

    assert coverage["ticker"].tolist() == ["AAA", "BBB"]
    assert coverage.set_index("ticker").loc["BBB", "fetch_status"] == "NOT_ATTEMPTED"


def test_completed_run_uses_only_four_status_values_and_has_no_not_attempted() -> None:
    coverage, _ = build_coverage(
        ["AAA", "BBB", "CCC"],
        pd.DataFrame(columns=["ticker", "date", "close_adjusted", "close_adjusted_unit", "volume"]),
        {"AAA": "OK", "BBB": "EMPTY_RESPONSE", "CCC": "FETCH_ERROR"},
        {"CCC": "TimeoutError"},
    )

    assert set(coverage["fetch_status"]).issubset(FETCH_STATUSES)
    assert "NOT_ATTEMPTED" not in set(coverage["fetch_status"])
    assert coverage.set_index("ticker").loc["CCC", "fetch_error_class"] == "TimeoutError"


def test_gzip_round_trip_and_reproducibility_with_zero_mtime(tmp_path: Path) -> None:
    daily = pd.DataFrame(
        [
            {"ticker": "VNM", "date": "2026-07-22", "close_adjusted": 59.1, "close_adjusted_unit": PRICE_UNIT, "volume": 10506300},
        ]
    )
    path = tmp_path / "daily_close.csv.gz"

    first_hash = write_daily_gzip(daily, path)
    round_trip = pd.read_csv(path, compression="gzip")
    second_hash = write_daily_gzip(daily, path)

    pd.testing.assert_frame_equal(round_trip, daily)
    assert first_hash == second_hash


def test_manifest_excludes_itself_and_all_files_are_lf_only(tmp_path: Path) -> None:
    (tmp_path / "daily_close.csv").write_bytes(b"ticker,date\r\nVNM,2020-01-01\r\n")
    (tmp_path / "coverage_by_ticker.csv").write_bytes(b"ticker\r\nVNM\r\n")
    (tmp_path / "coverage_summary.csv").write_bytes(b"year\r\n2020\r\n")
    write_daily_gzip(
        pd.DataFrame(
            [{"ticker": "VNM", "date": "2020-01-01", "close_adjusted": 10.0, "close_adjusted_unit": PRICE_UNIT, "volume": 1}]
        ),
        tmp_path / "daily_close.csv.gz",
    )

    manifest = write_manifest(
        tmp_path,
        "a" * 40,
        "2026-07-22",
        datetime(2026, 7, 22, 8, 0, tzinfo=timezone.utc),
    )

    assert set(manifest["file"]) == {
        "daily_close.csv",
        "coverage_by_ticker.csv",
        "coverage_summary.csv",
        "daily_close.csv.gz",
    }
    assert "MANIFEST.csv" not in set(manifest["file"])
    conventions = manifest.set_index("file")["hash_convention"].to_dict()
    assert conventions["daily_close.csv.gz"] == RAW_HASH_CONVENTION
    assert set(value for key, value in conventions.items() if not key.endswith(".gz")) == {HASH_CONVENTION}
    assert all(
        b"\r\n" not in path.read_bytes()
        for path in tmp_path.iterdir()
        if path.is_file() and path.suffix != ".gz"
    )
