from datetime import date
from pathlib import Path

import pytest

from src.screener.artifact_archive import archive_artifact


ARCHIVE_AS_OF = "2025-03-14"


def _source(tmp_path: Path, content: bytes = b"ticker,value\nAAA,1\n") -> Path:
    source = tmp_path / "sprint6_fscore.csv"
    source.write_bytes(content)
    return source


def test_copies_artifact_byte_for_byte_to_dated_archive(tmp_path: Path) -> None:
    source = _source(tmp_path, b"\x00exact\xffbytes\n")

    destination = archive_artifact(source, ARCHIVE_AS_OF, repo_root=tmp_path)

    assert destination == tmp_path / "data" / "screener" / "archive" / ARCHIVE_AS_OF / source.name
    assert destination.read_bytes() == source.read_bytes()


def test_rearchiving_identical_bytes_is_a_no_op(tmp_path: Path) -> None:
    source = _source(tmp_path)
    destination = archive_artifact(source, ARCHIVE_AS_OF, repo_root=tmp_path)

    assert archive_artifact(source, ARCHIVE_AS_OF, repo_root=tmp_path) == destination


def test_different_existing_archive_bytes_raise_with_destination_path(tmp_path: Path) -> None:
    source = _source(tmp_path, b"first")
    destination = archive_artifact(source, ARCHIVE_AS_OF, repo_root=tmp_path)
    source.write_bytes(b"second")

    with pytest.raises(ValueError) as error:
        archive_artifact(source, ARCHIVE_AS_OF, repo_root=tmp_path)

    assert str(destination) in str(error.value)


def test_malformed_as_of_raises_with_bad_value(tmp_path: Path) -> None:
    source = _source(tmp_path)

    with pytest.raises(ValueError, match="2026-13-99"):
        archive_artifact(source, "2026-13-99", repo_root=tmp_path)


def test_missing_source_raises_with_source_path(tmp_path: Path) -> None:
    source = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="missing.csv"):
        archive_artifact(source, ARCHIVE_AS_OF, repo_root=tmp_path)


def test_archive_as_of_is_not_today() -> None:
    assert date.fromisoformat(ARCHIVE_AS_OF) < date.today()
