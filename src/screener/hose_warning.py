"""Point-in-time HoSE warning data loaded from reviewed manual inputs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re
from typing import Iterable

import pandas as pd


WARNING_COLUMNS = (
    "ticker", "status", "effective_date", "lifted_date", "source_url",
    "published_date", "recorded_at", "note",
)
COVERAGE_COLUMNS = (
    "exchange", "coverage_start", "coverage_end", "source_url",
    "recorded_at", "note",
)
ALLOWED_STATUSES = ("WARNING", "CONTROL", "SPECIAL_CONTROL")


@dataclass(frozen=True)
class _Warning:
    ticker: str
    effective_date: date
    lifted_date: date | None


@dataclass(frozen=True)
class _Coverage:
    exchange: str
    coverage_start: date
    coverage_end: date | None


@dataclass(frozen=True)
class WarningTable:
    """Reviewed warning rows and the exchanges/dates they cover."""

    warnings: tuple[_Warning, ...]
    coverage: tuple[_Coverage, ...]

    def status_for(self, ticker: str, exchange: str, evaluation_date: str) -> bool | None:
        """Return the point-in-time warning status, or None outside coverage."""

        as_of = _parse_date(evaluation_date, "evaluation_date")
        covered = any(
            row.exchange == exchange
            and row.coverage_start <= as_of
            and (row.coverage_end is None or as_of <= row.coverage_end)
            for row in self.coverage
        )
        if not covered:
            return None
        return any(
            row.ticker == ticker
            and row.effective_date <= as_of
            and (row.lifted_date is None or as_of < row.lifted_date)
            for row in self.warnings
        )


def _parse_date(value: str, field: str) -> date:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"{field} must be YYYY-MM-DD: {value!r}")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be YYYY-MM-DD: {value!r}") from exc


def _parse_optional_date(value: str, field: str) -> date | None:
    return None if value == "" else _parse_date(value, field)


def _read_manual_csv(path: Path, expected_columns: tuple[str, ...]) -> pd.DataFrame:
    if not path.is_file():
        raise RuntimeError(f"missing HoSE warning manual input: {path}")
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    if tuple(frame.columns) != expected_columns:
        raise ValueError(
            "HoSE warning manual input must use exactly these columns: "
            + ", ".join(expected_columns)
        )
    return frame


def load_warning_table(root: Path) -> WarningTable:
    """Load manual warning facts and coverage, validating their exact contract."""

    input_root = root / "manual_inputs" / "hose_warning"
    warnings_frame = _read_manual_csv(input_root / "warnings.csv", WARNING_COLUMNS)
    coverage_frame = _read_manual_csv(input_root / "coverage.csv", COVERAGE_COLUMNS)

    warnings: list[_Warning] = []
    for row in warnings_frame.to_dict("records"):
        if row["status"] not in ALLOWED_STATUSES:
            raise ValueError(f"invalid HoSE warning status: {row['status']!r}")
        effective_date = _parse_date(row["effective_date"], "effective_date")
        lifted_date = _parse_optional_date(row["lifted_date"], "lifted_date")
        _parse_optional_date(row["published_date"], "published_date")
        _parse_optional_date(row["recorded_at"], "recorded_at")
        warnings.append(_Warning(row["ticker"], effective_date, lifted_date))

    coverage: list[_Coverage] = []
    for row in coverage_frame.to_dict("records"):
        coverage_start = _parse_date(row["coverage_start"], "coverage_start")
        coverage_end = _parse_optional_date(row["coverage_end"], "coverage_end")
        _parse_optional_date(row["recorded_at"], "recorded_at")
        coverage.append(_Coverage(row["exchange"], coverage_start, coverage_end))
    return WarningTable(tuple(warnings), tuple(coverage))


def assert_coverage(table: WarningTable, exchanges: Iterable[str], evaluation_date: str) -> None:
    """Require every formula-universe exchange to have coverage at the given date."""

    uncovered = sorted(
        exchange for exchange in set(exchanges)
        if table.status_for("", exchange, evaluation_date) is None
    )
    if uncovered:
        raise RuntimeError(
            f"HoSE warning coverage is missing for {evaluation_date}: {', '.join(uncovered)}"
        )
