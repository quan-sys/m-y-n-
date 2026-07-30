from datetime import date as _date
from pathlib import Path
from shutil import copyfile as _copyfile


__all__ = ("archive_artifact",)


def archive_artifact(source_path: Path, as_of: str, *, repo_root: Path) -> Path:
    try:
        _date.fromisoformat(as_of)
    except ValueError as error:
        raise ValueError(f"invalid as_of value: {as_of}") from error

    destination = repo_root / "data" / "screener" / "archive" / as_of / source_path.name
    if not source_path.exists():
        raise FileNotFoundError(f"source artifact does not exist: {source_path}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if destination.read_bytes() != source_path.read_bytes():
            raise ValueError(f"archive destination differs from source: {destination}")
        return destination

    _copyfile(source_path, destination)
    return destination
