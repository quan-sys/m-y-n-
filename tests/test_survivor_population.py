from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.audit_sprint6_readiness import (
    assert_matches_survivors,
    load_survivors_checked,
)


ROOT = Path(__file__).resolve().parents[1]


def write_survivors(path: Path, tickers: list[str]) -> None:
    pd.DataFrame({"ticker": tickers}).to_csv(path, index=False)


@pytest.mark.parametrize("size", (3, 7, 200))
def test_load_survivors_checked_accepts_any_nonempty_population(
    tmp_path: Path, size: int
) -> None:
    path = tmp_path / "survivors.csv"
    tickers = [f"T{index:03d}" for index in range(size)]

    write_survivors(path, tickers)

    loaded = load_survivors_checked(path)

    assert loaded["ticker"].tolist() == tickers


def test_load_survivors_checked_rejects_duplicate_ticker(tmp_path: Path) -> None:
    path = tmp_path / "survivors.csv"
    write_survivors(path, ["VNM", "VNM"])

    with pytest.raises(ValueError, match="VNM"):
        load_survivors_checked(path)


def test_load_survivors_checked_rejects_blank_ticker(tmp_path: Path) -> None:
    path = tmp_path / "survivors.csv"

    for blank in ("", "   "):
        write_survivors(path, ["VNM", blank])
        with pytest.raises(ValueError, match="row index 1"):
            load_survivors_checked(path)


def test_load_survivors_checked_rejects_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "survivors.csv"
    pd.DataFrame({"ticker": []}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="empty"):
        load_survivors_checked(path)


def test_load_survivors_checked_rejects_missing_ticker_column(tmp_path: Path) -> None:
    path = tmp_path / "survivors.csv"
    pd.DataFrame({"symbol": ["VNM"]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="missing ticker"):
        load_survivors_checked(path)


def test_load_survivors_checked_normalizes_tickers(tmp_path: Path) -> None:
    path = tmp_path / "survivors.csv"
    write_survivors(path, [" vnm ", "FPT"])

    loaded = load_survivors_checked(path)

    assert loaded["ticker"].tolist() == ["VNM", "FPT"]


def test_load_survivors_checked_preserves_numeric_nan_dtype(tmp_path: Path) -> None:
    path = tmp_path / "survivors.csv"
    pd.DataFrame(
        {"ticker": ["VNM", "FPT", "VCB"], "numeric_value": [1.5, None, 4.5]}
    ).to_csv(path, index=False)

    loaded = load_survivors_checked(path)

    assert pd.api.types.is_float_dtype(loaded["numeric_value"])
    assert pd.isna(loaded.loc[1, "numeric_value"])
    assert loaded["numeric_value"].dropna().mean() == pytest.approx(3.0)


def test_assert_matches_survivors_accepts_different_row_order() -> None:
    survivors = pd.DataFrame({"ticker": ["AAA", "BBB", "CCC"]})
    output = pd.DataFrame({"ticker": ["CCC", "AAA", "BBB"]})

    assert_matches_survivors(output, survivors, "row order")


def test_assert_matches_survivors_names_missing_ticker() -> None:
    survivors = pd.DataFrame({"ticker": ["AAA", "BBB", "CCC"]})
    output = pd.DataFrame({"ticker": ["AAA", "BBB"]})

    with pytest.raises(AssertionError, match="CCC"):
        assert_matches_survivors(output, survivors, "missing ticker")


def test_assert_matches_survivors_names_extra_ticker() -> None:
    survivors = pd.DataFrame({"ticker": ["AAA", "BBB"]})
    output = pd.DataFrame({"ticker": ["AAA", "BBB", "CCC"]})

    with pytest.raises(AssertionError, match="CCC"):
        assert_matches_survivors(output, survivors, "extra ticker")


def test_assert_matches_survivors_rejects_duplicated_output_ticker() -> None:
    survivors = pd.DataFrame({"ticker": ["AAA", "BBB"]})
    output = pd.DataFrame({"ticker": ["AAA", "AAA", "BBB"]})

    with pytest.raises(AssertionError, match="duplicated"):
        assert_matches_survivors(output, survivors, "duplicated ticker")


def test_assert_matches_survivors_rejects_same_length_wrong_population() -> None:
    survivors = pd.DataFrame({"ticker": ["A", "B", "C"]})
    output = pd.DataFrame({"ticker": ["A", "B", "D"]})
    survivor_set = set(survivors["ticker"])
    output_set = set(output["ticker"])
    missing = survivor_set - output_set
    extra = output_set - survivor_set

    print(f"survivors={survivor_set}")
    print(f"output={output_set}")
    print(f"missing={missing}")
    print(f"extra={extra}")

    with pytest.raises(AssertionError, match="missing=\\['C'\\].*extra=\\['D'\\]"):
        assert_matches_survivors(output, survivors, "same length mismatch")


def test_scripts_do_not_reintroduce_expected_survivors_identifier() -> None:
    script_paths = sorted((ROOT / "scripts").rglob("*.py"))
    forbidden_identifier = "EXPECTED_" + "SURVIVORS"

    assert all(
        forbidden_identifier not in path.read_text(encoding="utf-8")
        for path in script_paths
    )
