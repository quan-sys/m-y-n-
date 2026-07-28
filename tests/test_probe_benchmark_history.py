from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from scripts.probe_benchmark_history import (
    BENCHMARK_TICKER,
    INDEX_UNIT,
    KNOWN_CLOSES,
    OUTPUT_COLUMNS,
    PROBE_END,
    PROBE_START,
    normalise_api_history,
    run_probe,
    write_benchmark_daily_close,
)


def test_normalises_saved_vci_quote_history_shape() -> None:
    raw = pd.DataFrame(
        [
            {"time": "2026-07-21", "open": 1730.0, "high": 1735.0, "low": 1725.0, "close": 1730.56, "volume": 1},
            {"time": "2026-07-24", "open": 1680.0, "high": 1690.0, "low": 1675.0, "close": 1686.11, "volume": 2},
        ]
    )

    history = normalise_api_history(raw)

    assert history.to_dict("records") == [
        {"date": "2026-07-21", "close_adjusted": 1730.56, "volume": 1},
        {"date": "2026-07-24", "close_adjusted": 1686.11, "volume": 2},
    ]


class FixtureRangeClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, date, date]] = []

    def fetch_history(self, ticker: str, start: date, end: date) -> pd.DataFrame:
        self.calls.append((ticker, start, end))
        if start == date(2020, 1, 1):
            raise RuntimeError("fixture year failure")
        rows = [(start.isoformat(), 1000.0, 1), (end.isoformat(), 1100.0, 2)]
        for target_date, close in KNOWN_CLOSES.items():
            target = date.fromisoformat(target_date)
            if start <= target <= end:
                rows.append((target_date, float(close), 3))
        return pd.DataFrame(rows, columns=["time", "close", "volume"])


def test_probe_attempts_all_three_strategies_and_records_year_error() -> None:
    client = FixtureRangeClient()

    result = run_probe(client)

    assert len(client.calls) == 10
    assert client.calls[0] == (BENCHMARK_TICKER, PROBE_START, PROBE_END)
    assert client.calls[-1] == (BENCHMARK_TICKER, date(1900, 1, 1), PROBE_END)
    failed_year = next(record for record in result.yearly_records if record.strategy == "ii-2020")
    assert failed_year.error == "RuntimeError: fixture year failure"
    assert result.widest_range.error == ""


def test_writes_index_points_with_existing_daily_close_columns_plus_metadata(tmp_path: Path) -> None:
    history = pd.DataFrame(
        [
            {"date": "2026-07-21", "close_adjusted": 1730.56, "volume": 1},
            {"date": "2026-07-24", "close_adjusted": 1686.11, "volume": 2},
        ]
    )
    output_path = tmp_path / "benchmark_daily_close.csv.gz"

    write_benchmark_daily_close(history, output_path, date(2026, 7, 28))
    written = pd.read_csv(output_path, compression="gzip")

    assert tuple(written.columns) == OUTPUT_COLUMNS
    assert written["ticker"].tolist() == [BENCHMARK_TICKER, BENCHMARK_TICKER]
    assert written["close_adjusted_unit"].tolist() == [INDEX_UNIT, INDEX_UNIT]
    assert written["as_of"].tolist() == ["2026-07-28", "2026-07-28"]
    assert written["data_status"].tolist() == ["OK", "OK"]
