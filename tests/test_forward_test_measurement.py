from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from scripts.build_forward_test_measurement import (
    BENCHMARK_TICKER,
    FutureMeasurementDateError,
    MANIFEST_FILES,
    NO_SESSION_ON_OR_BEFORE,
    build_measurement,
    select_measurement_session,
)


class FixturePriceClient:
    def __init__(self, histories: dict[str, pd.DataFrame]) -> None:
        self.histories = histories
        self.calls: list[str] = []

    def fetch_price_history(self, ticker: str, months: int = 1) -> pd.DataFrame:
        self.calls.append(ticker)
        return self.histories[ticker].copy()


def _history(rows: list[tuple[str, float]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["time", "close"])


def _write_snapshot(repo_root: Path, rows: list[dict[str, object]]) -> None:
    snapshot = repo_root / "data" / "forward_test" / "snapshots" / "2026-07-21"
    snapshot.mkdir(parents=True)
    fills = pd.DataFrame(rows)
    benchmark = pd.DataFrame(
        [
            {
                "portfolio_id": "VN_INDEX",
                "ticker": BENCHMARK_TICKER,
                "fill_session_date": "2026-07-21",
                "close_adjusted": "1730.56",
                "fill_status": "FILLED",
                "target_weight": "",
            }
        ]
    )
    fills.to_csv(snapshot / "fills.csv", index=False, lineterminator="\n")
    benchmark.to_csv(snapshot / "benchmark.csv", index=False, lineterminator="\n")


def _fill_row(ticker: str, stored_close: str, weight: str = "1.0") -> dict[str, object]:
    return {
        "portfolio_id": "EBIT_TEV",
        "ticker": ticker,
        "fill_session_date": "2026-07-21",
        "close_adjusted": stored_close,
        "fill_status": "FILLED",
        "target_weight": weight,
    }


def _benchmark_history() -> pd.DataFrame:
    return _history([("2026-07-21", 1700.0), ("2026-07-22", 1717.0)])


def test_return_uses_refetched_entry_close_not_stored_close(tmp_path: Path) -> None:
    _write_snapshot(tmp_path, [_fill_row("AAA", "100")])
    client = FixturePriceClient(
        {
            "AAA": _history([("2026-07-21", 120.0), ("2026-07-22", 132.0)]),
            BENCHMARK_TICKER: _benchmark_history(),
        }
    )

    result = build_measurement(
        tmp_path,
        client,
        measurement_date=date(2026, 7, 22),
        mode="dry-run",
        run_date=date(2026, 7, 22),
        created_at_utc=datetime(2026, 7, 22, tzinfo=timezone.utc),
        main_sha="a" * 40,
    )

    position = result.positions.iloc[0]
    assert position["entry_close_adjusted_stored"] == 100.0
    assert position["entry_close_adjusted_refetched"] == 120.0
    assert position["ticker_return_pct"] == pytest.approx(10.0)
    assert position["ticker_return_pct"] != pytest.approx(32.0)
    assert result.portfolio_returns.loc[0, "portfolio_return_pct"] == pytest.approx(10.0)
    assert client.calls == ["AAA", BENCHMARK_TICKER]


def test_measurement_session_is_last_available_session_on_or_before_requested_date() -> None:
    history = _history(
        [
            ("2026-07-21", 10.0),
            ("2026-07-23", 12.0),
            ("2026-07-25", 14.0),
        ]
    )

    assert select_measurement_session(history, date(2026, 7, 24)) == ("2026-07-23", 12.0)


def test_future_measurement_date_stops_before_reading_or_fetching(tmp_path: Path) -> None:
    client = FixturePriceClient({})

    with pytest.raises(FutureMeasurementDateError, match="in the future"):
        build_measurement(
            tmp_path,
            client,
            measurement_date=date(2026, 7, 24),
            mode="quarterly",
            run_date=date(2026, 7, 23),
        )
    assert client.calls == []


def test_no_session_before_measurement_is_excluded_without_weight_redistribution(tmp_path: Path) -> None:
    _write_snapshot(
        tmp_path,
        [
            _fill_row("AAA", "100", "0.5"),
            _fill_row("BBB", "50", "0.5"),
        ],
    )
    client = FixturePriceClient(
        {
            "AAA": _history([("2026-07-21", 100.0), ("2026-07-22", 110.0)]),
            "BBB": _history([("2026-07-23", 55.0)]),
            BENCHMARK_TICKER: _benchmark_history(),
        }
    )

    result = build_measurement(
        tmp_path,
        client,
        measurement_date=date(2026, 7, 22),
        mode="dry-run",
        run_date=date(2026, 7, 22),
        created_at_utc=datetime(2026, 7, 22, tzinfo=timezone.utc),
        main_sha="b" * 40,
    )

    missing = result.positions.loc[result.positions["ticker"].eq("BBB")].iloc[0]
    assert missing["measurement_status"] == NO_SESSION_ON_OR_BEFORE
    assert missing["entry_close_adjusted_refetched"] == ""
    assert missing["measurement_close"] == ""
    assert missing["ticker_return_pct"] == ""
    assert missing["excluded_weight"] == pytest.approx(0.5)
    portfolio = result.portfolio_returns.iloc[0]
    assert portfolio["excluded_weight"] == pytest.approx(0.5)
    assert portfolio["portfolio_return_pct"] == pytest.approx(10.0)


def test_manifest_hashes_exactly_the_other_measurement_files(tmp_path: Path) -> None:
    _write_snapshot(tmp_path, [_fill_row("AAA", "100")])
    client = FixturePriceClient(
        {
            "AAA": _history([("2026-07-21", 100.0), ("2026-07-22", 110.0)]),
            BENCHMARK_TICKER: _benchmark_history(),
        }
    )

    result = build_measurement(
        tmp_path,
        client,
        measurement_date=date(2026, 7, 22),
        mode="dry-run",
        run_date=date(2026, 7, 22),
        created_at_utc=datetime(2026, 7, 22, tzinfo=timezone.utc),
        main_sha="c" * 40,
    )

    assert set(result.manifest["file"]) == set(MANIFEST_FILES)
    assert "MANIFEST.csv" not in set(result.manifest["file"])
    assert set(result.manifest["measurement_type"]) == {"DRY_RUN_NOT_A_QUARTERLY_MEASUREMENT"}
    assert all(b"\r\n" not in path.read_bytes() for path in result.output_directory.iterdir())
