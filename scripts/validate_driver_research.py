"""Validate structured web driver research files."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_driver_research_template import CROSSCHECK_COLUMNS, SOURCE_LOG_COLUMNS


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()

SOURCE_TYPES = {
    "official_statistics",
    "regulator",
    "exchange",
    "company_disclosure",
    "reputable_news",
    "industry_report",
    "international_org",
    "data_provider",
    "other",
}

DATA_STATUS = {
    "OK",
    "PARTIAL",
    "WEAK_SOURCE",
    "SOURCE_NOT_FOUND",
    "STALE_SOURCE",
    "NEEDS_WEB_RESEARCH",
    "MANUAL_REVIEW_REQUIRED",
}

CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}

DRIVER_SIGNAL = {"POSITIVE", "NEGATIVE", "MIXED", "NEUTRAL", "UNCLEAR", "MISSING"}

CROSSCHECK_RESULT = {
    "DRIVER_CONFIRMS_STRENGTH",
    "DRIVER_CONFIRMS_WEAKNESS",
    "DRIVER_MIXED",
    "PRICE_STRONG_BUT_DRIVER_UNCONFIRMED",
    "PRICE_WEAK_BUT_DRIVER_UNCONFIRMED",
    "DRIVER_CONTRADICTS_PRICE_SIGNAL",
    "DATA_INSUFFICIENT",
}

EVIDENCE_STRENGTH = {"HIGH", "MEDIUM", "LOW"}

BANNED_PHRASES = [
    "nên mua",
    "nên bán",
    "mua vào",
    "bán ra",
    "target price",
    "upside",
    "downside",
    "khuyến nghị mua",
    "khuyến nghị bán",
    "top cổ phiếu",
    "cổ phiếu tốt nhất",
    "ranking cổ phiếu",
    "phím hàng",
]


@dataclass
class DriverResearchValidation:
    ok: bool = True
    messages: list[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.ok = False
        self.messages.append(message)


def _is_blank(value: object) -> bool:
    if value is None:
        return True
    if pd.isna(value):
        return True
    return str(value).strip() == ""


def _missing_columns(frame: pd.DataFrame, columns: list[str]) -> list[str]:
    existing = set(frame.columns)
    return [column for column in columns if column not in existing]


def _check_enum(
    result: DriverResearchValidation,
    frame: pd.DataFrame,
    column: str,
    allowed: set[str],
    file_name: str,
) -> None:
    if column not in frame:
        return
    values = frame[column].dropna().astype(str).str.strip()
    invalid = sorted({value for value in values if value and value not in allowed})
    if invalid:
        result.fail(f"{file_name}: invalid {column}: {', '.join(invalid)}")


def _scan_banned_text(result: DriverResearchValidation, path: Path, text: str) -> None:
    lowered = text.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            result.fail(f"{path.name}: banned phrase found: {phrase}")


def validate_driver_research(report_folder: str | Path) -> DriverResearchValidation:
    result = DriverResearchValidation()
    report_path = Path(report_folder)
    source_path = report_path / "driver_source_log.csv"
    crosscheck_path = report_path / "sector_driver_crosscheck.csv"
    notes_path = report_path / "driver_research_notes.md"

    if not report_path.exists():
        result.fail(f"Report folder does not exist: {report_path}")
        return result
    if not source_path.exists():
        result.fail("Missing file: driver_source_log.csv")
    if not crosscheck_path.exists():
        result.fail("Missing file: sector_driver_crosscheck.csv")
    if not result.ok:
        return result

    source_log = pd.read_csv(source_path)
    crosscheck = pd.read_csv(crosscheck_path)

    missing_source_columns = _missing_columns(source_log, SOURCE_LOG_COLUMNS)
    if missing_source_columns:
        result.fail("driver_source_log.csv missing columns: " + ", ".join(missing_source_columns))

    missing_crosscheck_columns = _missing_columns(crosscheck, CROSSCHECK_COLUMNS)
    if missing_crosscheck_columns:
        result.fail(
            "sector_driver_crosscheck.csv missing columns: "
            + ", ".join(missing_crosscheck_columns)
        )

    _check_enum(result, source_log, "source_type", SOURCE_TYPES, "driver_source_log.csv")
    _check_enum(result, source_log, "data_status", DATA_STATUS, "driver_source_log.csv")
    _check_enum(result, source_log, "confidence", CONFIDENCE, "driver_source_log.csv")
    _check_enum(result, crosscheck, "driver_signal", DRIVER_SIGNAL, "sector_driver_crosscheck.csv")
    _check_enum(
        result,
        crosscheck,
        "crosscheck_result",
        CROSSCHECK_RESULT,
        "sector_driver_crosscheck.csv",
    )
    _check_enum(
        result,
        crosscheck,
        "evidence_strength",
        EVIDENCE_STRENGTH,
        "sector_driver_crosscheck.csv",
    )
    _check_enum(result, crosscheck, "data_status", DATA_STATUS, "sector_driver_crosscheck.csv")

    if "sector" in source_log:
        for idx, value in source_log["sector"].items():
            if _is_blank(value):
                result.fail(f"driver_source_log.csv row {idx + 2}: empty sector")
    if "driver_name" in source_log:
        for idx, value in source_log["driver_name"].items():
            if _is_blank(value):
                result.fail(f"driver_source_log.csv row {idx + 2}: empty driver_name")

    if {"data_status", "source_url"}.issubset(source_log.columns):
        for idx, row in source_log.iterrows():
            if str(row["data_status"]).strip() == "OK" and _is_blank(row["source_url"]):
                result.fail(f"driver_source_log.csv row {idx + 2}: OK requires source_url")

    if {"confidence", "key_finding"}.issubset(source_log.columns):
        for idx, row in source_log.iterrows():
            if str(row["confidence"]).strip() == "HIGH" and _is_blank(row["key_finding"]):
                result.fail(f"driver_source_log.csv row {idx + 2}: HIGH confidence requires key_finding")

    if "sector" in crosscheck:
        for idx, value in crosscheck["sector"].items():
            if _is_blank(value):
                result.fail(f"sector_driver_crosscheck.csv row {idx + 2}: empty sector")

    if {"crosscheck_result", "summary"}.issubset(crosscheck.columns):
        for idx, row in crosscheck.iterrows():
            if str(row["crosscheck_result"]).strip() != "DATA_INSUFFICIENT" and _is_blank(row["summary"]):
                result.fail(
                    f"sector_driver_crosscheck.csv row {idx + 2}: crosscheck result requires summary"
                )

    if {"source_count", "evidence_strength", "data_status"}.issubset(crosscheck.columns):
        for idx, row in crosscheck.iterrows():
            source_count = pd.to_numeric(row["source_count"], errors="coerce")
            if pd.isna(source_count):
                result.fail(f"sector_driver_crosscheck.csv row {idx + 2}: source_count is not numeric")
                continue
            if int(source_count) == 0 and str(row["evidence_strength"]).strip() == "HIGH":
                result.fail(
                    f"sector_driver_crosscheck.csv row {idx + 2}: source_count 0 cannot be HIGH evidence"
                )
            if int(source_count) == 0 and str(row["data_status"]).strip() == "OK":
                result.fail(
                    f"sector_driver_crosscheck.csv row {idx + 2}: source_count 0 cannot have OK data_status"
                )

    if {"driver_signal", "crosscheck_result"}.issubset(crosscheck.columns):
        allowed_missing_results = {
            "DATA_INSUFFICIENT",
            "PRICE_STRONG_BUT_DRIVER_UNCONFIRMED",
            "PRICE_WEAK_BUT_DRIVER_UNCONFIRMED",
        }
        for idx, row in crosscheck.iterrows():
            if str(row["driver_signal"]).strip() == "MISSING" and str(row["crosscheck_result"]).strip() not in allowed_missing_results:
                result.fail(
                    f"sector_driver_crosscheck.csv row {idx + 2}: MISSING driver_signal has incompatible crosscheck_result"
                )

    _scan_banned_text(result, source_path, source_path.read_text(encoding="utf-8"))
    _scan_banned_text(result, crosscheck_path, crosscheck_path.read_text(encoding="utf-8"))
    if notes_path.exists():
        _scan_banned_text(result, notes_path, notes_path.read_text(encoding="utf-8"))

    return result


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate driver research files.")
    parser.add_argument("report_folder", help="Path to reports/<YYYY-MM-DD> folder")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = validate_driver_research(args.report_folder)
    if result.ok:
        print("Driver research validation: PASS")
        return 0
    print("Driver research validation: FAIL")
    for message in result.messages:
        print(f"- {message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
