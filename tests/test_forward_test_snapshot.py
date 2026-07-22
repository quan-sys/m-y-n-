from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from scripts.build_forward_test_snapshot import (
    HASH_CONVENTION,
    INDEX_RAW_STATUS,
    INDEX_UNIT,
    PORTFOLIO_FILES,
    MissingCloseError,
    SnapshotExistsError,
    build_snapshot,
    no_session_in_window,
    select_fill,
)


class FixturePriceClient:
    def __init__(self, histories: dict[str, pd.DataFrame] | None = None) -> None:
        self.histories = histories or {}

    def fetch_price_history(self, ticker: str, months: int = 1) -> pd.DataFrame:
        return self.histories.get(
            ticker,
            pd.DataFrame([{"time": "2026-07-21", "close": 42.5}]),
        ).copy()


def _write_portfolios(repo_root: Path) -> dict[str, bytes]:
    source_dir = repo_root / "reports" / "2026-07-20"
    source_dir.mkdir(parents=True)
    originals: dict[str, bytes] = {}
    for filename, prefix in zip(PORTFOLIO_FILES, ("A", "B"), strict=True):
        frame = pd.DataFrame(
            {
                "portfolio_id": [prefix] * 20,
                "ticker": [f"{prefix}{index:02d}" for index in range(20)],
                "target_weight": [0.05] * 20,
            }
        )
        path = source_dir / filename
        frame.to_csv(path, index=False, lineterminator="\n")
        originals[filename] = path.read_bytes()
    return originals


def test_refuses_to_overwrite_existing_snapshot(tmp_path: Path) -> None:
    target = tmp_path / "data" / "forward_test" / "snapshots" / "2026-07-21"
    target.mkdir(parents=True)

    with pytest.raises(SnapshotExistsError, match="refusing to overwrite"):
        build_snapshot(tmp_path, FixturePriceClient())


def test_fill_session_cannot_precede_decision_date() -> None:
    history = pd.DataFrame(
        [
            {"time": "2026-07-20", "close": 10.0},
            {"time": "2026-07-21", "close": 11.0},
        ]
    )

    fill = select_fill(history)

    assert fill is not None
    assert fill.fill_session_date == "2026-07-21"
    assert fill.close_adjusted == 11.0


def test_no_session_in_window_path_and_build_writes_nothing(tmp_path: Path) -> None:
    _write_portfolios(tmp_path)
    no_session = no_session_in_window()
    histories = {"A00": pd.DataFrame([{"time": "2026-07-20", "close": 10.0}])}

    assert no_session == {
        "fill_session_date": "",
        "close_adjusted": "",
        "price_as_of": "",
        "fill_status": "NO_SESSION_IN_WINDOW",
    }
    with pytest.raises(MissingCloseError, match="A00"):
        build_snapshot(tmp_path, FixturePriceClient(histories))
    assert not (tmp_path / "data" / "forward_test" / "snapshots" / "2026-07-21").exists()


def test_portfolio_copies_are_byte_identical(tmp_path: Path) -> None:
    originals = _write_portfolios(tmp_path)

    build_snapshot(
        tmp_path,
        FixturePriceClient(),
        created_at_utc=datetime(2026, 7, 21, 8, 0, tzinfo=timezone.utc),
        main_sha="a" * 40,
    )

    target = tmp_path / "data" / "forward_test" / "snapshots" / "2026-07-21"
    for filename, expected_bytes in originals.items():
        assert (target / filename).read_bytes() == expected_bytes


def test_snapshot_files_are_lf_only_and_manifest_declares_convention(tmp_path: Path) -> None:
    _write_portfolios(tmp_path)

    build_snapshot(
        tmp_path,
        FixturePriceClient(),
        created_at_utc=datetime(2026, 7, 21, 8, 0, tzinfo=timezone.utc),
        main_sha="a" * 40,
    )

    target = tmp_path / "data" / "forward_test" / "snapshots" / "2026-07-21"
    assert all(b"\r\n" not in path.read_bytes() for path in target.iterdir() if path.is_file())
    manifest = pd.read_csv(target / "MANIFEST.csv")
    assert set(manifest["hash_convention"]) == {HASH_CONVENTION}
    assert "MANIFEST.csv" not in set(manifest["file"])


def test_index_row_uses_points_not_currency(tmp_path: Path) -> None:
    _write_portfolios(tmp_path)

    _, benchmark, _ = build_snapshot(
        tmp_path,
        FixturePriceClient(),
        created_at_utc=datetime(2026, 7, 21, 8, 0, tzinfo=timezone.utc),
        main_sha="a" * 40,
    )

    assert benchmark.loc[0, "close_adjusted_unit"] == INDEX_UNIT
    assert benchmark.loc[0, "close_raw_status"] == INDEX_RAW_STATUS
    assert "VND" not in benchmark.loc[0, "close_adjusted_unit"]


def test_repository_snapshot_files_are_lf_only() -> None:
    snapshot_root = Path(__file__).resolve().parents[1] / "data" / "forward_test" / "snapshots"
    snapshot_files = [path for path in snapshot_root.rglob("*") if path.is_file()]

    assert snapshot_files
    assert all(b"\r\n" not in path.read_bytes() for path in snapshot_files)
