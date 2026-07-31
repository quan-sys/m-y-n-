from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.screener.hose_warning import (
    COVERAGE_COLUMNS,
    WARNING_COLUMNS,
    assert_coverage,
    load_warning_table,
)
from src.screener.step1_pipeline import evaluate_formula_stage


def write_inputs(
    root: Path,
    warnings: list[dict[str, str]] | None = None,
    coverage: list[dict[str, str]] | None = None,
) -> None:
    input_root = root / "manual_inputs" / "hose_warning"
    input_root.mkdir(parents=True)
    pd.DataFrame(warnings or [], columns=WARNING_COLUMNS).to_csv(
        input_root / "warnings.csv", index=False
    )
    pd.DataFrame(coverage or [], columns=COVERAGE_COLUMNS).to_csv(
        input_root / "coverage.csv", index=False
    )


def warning_row(**overrides: str) -> dict[str, str]:
    row = {
        "ticker": "AAA",
        "status": "WARNING",
        "effective_date": "2025-04-01",
        "lifted_date": "",
        "source_url": "https://example.test/warning",
        "published_date": "2025-04-01",
        "recorded_at": "2025-04-02",
        "note": "fixture",
    }
    row.update(overrides)
    return row


def coverage_row(**overrides: str) -> dict[str, str]:
    row = {
        "exchange": "HOSE",
        "coverage_start": "2025-01-01",
        "coverage_end": "",
        "source_url": "https://example.test/coverage",
        "recorded_at": "2025-01-02",
        "note": "fixture",
    }
    row.update(overrides)
    return row


def test_missing_directory_raises_runtime_error(tmp_path: Path):
    with pytest.raises(RuntimeError):
        load_warning_table(tmp_path)


def test_wrong_column_order_raises_value_error(tmp_path: Path):
    input_root = tmp_path / "manual_inputs" / "hose_warning"
    input_root.mkdir(parents=True)
    pd.DataFrame(columns=tuple(reversed(WARNING_COLUMNS))).to_csv(
        input_root / "warnings.csv", index=False
    )
    pd.DataFrame(columns=COVERAGE_COLUMNS).to_csv(input_root / "coverage.csv", index=False)

    with pytest.raises(ValueError):
        load_warning_table(tmp_path)


def test_invalid_status_raises_value_error(tmp_path: Path):
    write_inputs(tmp_path, warnings=[warning_row(status="UNSUPPORTED")], coverage=[coverage_row()])

    with pytest.raises(ValueError):
        load_warning_table(tmp_path)


def test_warning_status_is_point_in_time(tmp_path: Path):
    write_inputs(
        tmp_path,
        warnings=[warning_row(lifted_date="2026-01-15")],
        coverage=[coverage_row()],
    )
    table = load_warning_table(tmp_path)

    assert table.status_for("AAA", "HOSE", "2025-03-31") is False
    assert table.status_for("AAA", "HOSE", "2025-04-01") is True
    assert table.status_for("AAA", "HOSE", "2026-01-14") is True
    assert table.status_for("AAA", "HOSE", "2026-01-15") is False


def test_absent_ticker_inside_coverage_is_false(tmp_path: Path):
    write_inputs(tmp_path, coverage=[coverage_row()])

    assert load_warning_table(tmp_path).status_for("MISSING", "HOSE", "2025-04-01") is False


def test_absent_ticker_outside_coverage_is_none(tmp_path: Path):
    write_inputs(tmp_path, coverage=[coverage_row()])

    assert load_warning_table(tmp_path).status_for("MISSING", "HNX", "2025-04-01") is None


def test_lowercase_warning_ticker_matches_uppercase_lookup(tmp_path: Path):
    write_inputs(tmp_path, warnings=[warning_row(ticker="aaa")], coverage=[coverage_row()])
    table = load_warning_table(tmp_path)

    assert table.status_for("AAA", "HOSE", "2025-04-01") is True
    assert table.status_for(" aaa ", "HOSE", "2025-04-01") is True


def test_space_padded_warning_ticker_matches_trimmed_lookup(tmp_path: Path):
    write_inputs(tmp_path, warnings=[warning_row(ticker="AAA ")], coverage=[coverage_row()])

    assert load_warning_table(tmp_path).status_for("AAA", "HOSE", "2025-04-01") is True


def test_lowercase_coverage_exchange_matches_uppercase_lookup(tmp_path: Path):
    write_inputs(tmp_path, warnings=[warning_row()], coverage=[coverage_row(exchange="hose")])

    assert load_warning_table(tmp_path).status_for("AAA", "HOSE", "2025-04-01") is True


def test_coverage_start_boundary_is_covered(tmp_path: Path):
    write_inputs(tmp_path, coverage=[coverage_row(coverage_start="2025-01-01")])

    assert load_warning_table(tmp_path).status_for("MISSING", "HOSE", "2025-01-01") is not None


def test_coverage_end_boundary_is_covered(tmp_path: Path):
    write_inputs(tmp_path, coverage=[coverage_row(coverage_end="2025-06-30")])
    table = load_warning_table(tmp_path)

    assert table.status_for("MISSING", "HOSE", "2025-06-30") is not None
    assert table.status_for("MISSING", "HOSE", "2025-07-01") is None


def test_assert_coverage_names_uncovered_exchange(tmp_path: Path):
    write_inputs(tmp_path, coverage=[coverage_row()])
    table = load_warning_table(tmp_path)

    with pytest.raises(RuntimeError, match="UPCOM"):
        assert_coverage(table, {"HOSE", "UPCOM"}, "2025-04-01")


def test_evaluate_formula_stage_without_warning_table_keeps_missing_warnings(monkeypatch):
    passed_warnings: list[bool | None] = []

    def fake_prepare(_row, _cache_root, _evaluation_date, *, hose_warning):
        passed_warnings.append(hose_warning)
        return object()

    def fake_prepared_row(_prepared, universe_row):
        return {
            "ticker": universe_row["ticker"],
            "distress_hose_warning": passed_warnings[-1],
        }

    monkeypatch.setattr("src.screener.step1_pipeline.prepare_ticker_from_cache", fake_prepare)
    monkeypatch.setattr("src.screener.step1_pipeline._prepared_row", fake_prepared_row)
    result = evaluate_formula_stage(
        pd.DataFrame({"ticker": ["AAA", "BBB"], "exchange": ["HOSE", "HNX"]}),
        "unused",
        "2025-04-01",
    )

    assert passed_warnings == [None, None]
    assert result["distress_hose_warning"].isna().all()


def test_lowercase_lookup_exchange_matches_uppercase_coverage(tmp_path: Path):
    write_inputs(tmp_path, warnings=[warning_row()], coverage=[coverage_row(exchange="HOSE")])

    assert load_warning_table(tmp_path).status_for("AAA", "hose", "2025-04-01") is True


def test_space_padded_lookup_exchange_matches_coverage(tmp_path: Path):
    write_inputs(tmp_path, warnings=[warning_row()], coverage=[coverage_row(exchange="HOSE")])

    assert load_warning_table(tmp_path).status_for("AAA", " HOSE ", "2025-04-01") is True


def test_assert_coverage_normalizes_lookup_exchange(tmp_path: Path):
    write_inputs(tmp_path, coverage=[coverage_row(exchange="HOSE")])

    assert_coverage(load_warning_table(tmp_path), [" hose "], "2025-04-01")
