"""Validate an AI-ready sector cycle report package."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import pandas as pd


REQUIRED_FILES = [
    "AI_INPUT_SUMMARY.md",
    "README_FOR_AI.md",
    "sector_cycle_signals.csv",
    "sector_driver_map.csv",
    "run_metadata.json",
    "data_quality.csv",
]

SECTOR_SIGNAL_COLUMNS = [
    "sector",
    "ticker_count",
    "valid_price_count",
    "data_quality_status",
    "coverage_status",
    "relative_strength_1m_vs_vnindex",
    "sector_return_1w_equal_weight",
    "sector_return_1m_equal_weight",
    "price_trend_signal",
    "relative_strength_signal",
    "momentum_signal",
    "breadth_signal",
    "liquidity_signal",
    "data_confidence_signal",
    "candidate_cycle_stage",
    "cycle_signal_confidence",
    "evidence_summary",
    "warning_flags",
]

DRIVER_MAP_COLUMNS = [
    "sector",
    "driver_name",
    "why_it_matters",
    "driver_type",
    "source_strategy",
    "public_web_search_available",
    "codex_pipeline_required",
    "priority",
    "interpretation_note",
    "data_status",
]

METADATA_KEYS = [
    "ai_ready_package_created",
    "cycle_signals_created",
    "driver_map_created",
    "cycle_signal_sector_count",
    "driver_map_sector_count",
    "driver_map_row_count",
]

ALLOWED_CYCLE_STAGES = {
    "LEADERSHIP",
    "IMPROVING",
    "NEUTRAL",
    "WEAKENING",
    "LAGGING",
    "UNCLEAR_DATA",
}

ALLOWED_CONFIDENCE = {"LOW", "MEDIUM", "HIGH"}

ALLOWED_SOURCE_STRATEGY = {
    "CHATGPT_WEB_SEARCH_PUBLIC",
    "OPTIONAL_CODEX_PUBLIC_DATA",
    "NOT_PUBLIC_OR_NOT_AVAILABLE",
    "FUTURE_MANUAL_INPUT",
}

YES_NO = {"yes", "no"}


@dataclass
class ValidationResult:
    ok: bool = True
    messages: list[str] = field(default_factory=list)
    sector_count: int | None = None
    driver_map_sector_count: int | None = None
    driver_map_row_count: int | None = None
    required_files_ok: bool = False
    sector_schema_ok: bool = False
    driver_schema_ok: bool = False
    metadata_ok: bool = False

    def fail(self, message: str) -> None:
        self.ok = False
        self.messages.append(message)


def _missing_columns(columns: Iterable[str], required: Iterable[str]) -> list[str]:
    existing = set(columns)
    return [column for column in required if column not in existing]


def _invalid_values(series: pd.Series, allowed: set[str]) -> list[str]:
    values = series.dropna().astype(str).str.strip()
    invalid = sorted({value for value in values if value not in allowed})
    return invalid


def _invalid_yes_no(series: pd.Series) -> list[str]:
    values = series.dropna().astype(str).str.strip().str.lower()
    invalid = sorted({value for value in values if value not in YES_NO})
    return invalid


def validate_ai_package(report_dir: str | Path) -> ValidationResult:
    result = ValidationResult()
    report_path = Path(report_dir)

    if not report_path.exists():
        result.fail(f"Report folder does not exist: {report_path}")
        return result
    if not report_path.is_dir():
        result.fail(f"Report path is not a folder: {report_path}")
        return result

    missing_files = [name for name in REQUIRED_FILES if not (report_path / name).exists()]
    if missing_files:
        for name in missing_files:
            result.fail(f"Missing file: {name}")
        return result
    result.required_files_ok = True

    try:
        signals = pd.read_csv(report_path / "sector_cycle_signals.csv")
    except Exception as exc:  # pragma: no cover - defensive message for CLI use
        result.fail(f"Cannot read sector_cycle_signals.csv: {exc}")
        return result

    missing_signal_columns = _missing_columns(signals.columns, SECTOR_SIGNAL_COLUMNS)
    if missing_signal_columns:
        result.fail(
            "sector_cycle_signals.csv missing columns: "
            + ", ".join(missing_signal_columns)
        )
    else:
        result.sector_schema_ok = True

    if "candidate_cycle_stage" in signals.columns:
        invalid_stages = _invalid_values(
            signals["candidate_cycle_stage"], ALLOWED_CYCLE_STAGES
        )
        if invalid_stages:
            result.fail("Invalid candidate_cycle_stage values: " + ", ".join(invalid_stages))

    if "cycle_signal_confidence" in signals.columns:
        invalid_confidence = _invalid_values(
            signals["cycle_signal_confidence"], ALLOWED_CONFIDENCE
        )
        if invalid_confidence:
            result.fail(
                "Invalid cycle_signal_confidence values: "
                + ", ".join(invalid_confidence)
            )

    try:
        drivers = pd.read_csv(report_path / "sector_driver_map.csv")
    except Exception as exc:  # pragma: no cover - defensive message for CLI use
        result.fail(f"Cannot read sector_driver_map.csv: {exc}")
        return result

    missing_driver_columns = _missing_columns(drivers.columns, DRIVER_MAP_COLUMNS)
    if missing_driver_columns:
        result.fail(
            "sector_driver_map.csv missing columns: "
            + ", ".join(missing_driver_columns)
        )
    else:
        result.driver_schema_ok = True

    if "source_strategy" in drivers.columns:
        invalid_strategy = _invalid_values(drivers["source_strategy"], ALLOWED_SOURCE_STRATEGY)
        if invalid_strategy:
            result.fail("Invalid source_strategy values: " + ", ".join(invalid_strategy))

    if "public_web_search_available" in drivers.columns:
        invalid_public = _invalid_yes_no(drivers["public_web_search_available"])
        if invalid_public:
            result.fail(
                "Invalid public_web_search_available values: " + ", ".join(invalid_public)
            )

    if "codex_pipeline_required" in drivers.columns:
        invalid_codex = _invalid_yes_no(drivers["codex_pipeline_required"])
        if invalid_codex:
            result.fail(
                "Invalid codex_pipeline_required values: " + ", ".join(invalid_codex)
            )

    try:
        metadata = json.loads((report_path / "run_metadata.json").read_text(encoding="utf-8"))
    except Exception as exc:
        result.fail(f"Cannot read run_metadata.json: {exc}")
        return result

    missing_metadata = [key for key in METADATA_KEYS if key not in metadata]
    if missing_metadata:
        result.fail("run_metadata.json missing keys: " + ", ".join(missing_metadata))

    result.sector_count = int(signals["sector"].nunique()) if "sector" in signals else None
    result.driver_map_sector_count = (
        int(drivers["sector"].nunique()) if "sector" in drivers else None
    )
    result.driver_map_row_count = len(drivers)

    if not missing_metadata:
        if metadata["cycle_signal_sector_count"] != result.sector_count:
            result.fail(
                "cycle_signal_sector_count mismatch: "
                f"metadata={metadata['cycle_signal_sector_count']} "
                f"actual={result.sector_count}"
            )
        if metadata["driver_map_sector_count"] != result.driver_map_sector_count:
            result.fail(
                "driver_map_sector_count mismatch: "
                f"metadata={metadata['driver_map_sector_count']} "
                f"actual={result.driver_map_sector_count}"
            )
        if metadata["driver_map_row_count"] != result.driver_map_row_count:
            result.fail(
                "driver_map_row_count mismatch: "
                f"metadata={metadata['driver_map_row_count']} "
                f"actual={result.driver_map_row_count}"
            )

        for flag in [
            "ai_ready_package_created",
            "cycle_signals_created",
            "driver_map_created",
        ]:
            if metadata.get(flag) is not True:
                result.fail(f"run_metadata.json flag is not true: {flag}")

    if "sector" in drivers.columns:
        driver_counts = drivers.groupby("sector", dropna=False).size()
        weak_sectors = sorted(
            str(sector) for sector, count in driver_counts.items() if count < 2
        )
        if weak_sectors:
            result.fail("Sectors with fewer than 2 drivers: " + ", ".join(weak_sectors))

    result.metadata_ok = (
        not missing_metadata
        and result.sector_count == metadata.get("cycle_signal_sector_count")
        and result.driver_map_sector_count == metadata.get("driver_map_sector_count")
        and result.driver_map_row_count == metadata.get("driver_map_row_count")
        and metadata.get("ai_ready_package_created") is True
        and metadata.get("cycle_signals_created") is True
        and metadata.get("driver_map_created") is True
    )

    return result


def format_result(result: ValidationResult) -> str:
    lines = [f"AI package validation: {'PASS' if result.ok else 'FAIL'}"]

    if result.ok:
        lines.extend(
            [
                "- required files: PASS",
                "- sector_cycle_signals schema: PASS",
                "- sector_driver_map schema: PASS",
                "- metadata consistency: PASS",
                f"- sector count: {result.sector_count}",
                f"- driver map sectors: {result.driver_map_sector_count}",
                f"- driver map rows: {result.driver_map_row_count}",
            ]
        )
    else:
        lines.extend(f"- {message}" for message in result.messages)
        lines.extend(
            [
                f"- required files: {'PASS' if result.required_files_ok else 'FAIL'}",
                f"- sector_cycle_signals schema: {'PASS' if result.sector_schema_ok else 'FAIL'}",
                f"- sector_driver_map schema: {'PASS' if result.driver_schema_ok else 'FAIL'}",
                f"- metadata consistency: {'PASS' if result.metadata_ok else 'FAIL'}",
            ]
        )
        if result.sector_count is not None:
            lines.append(f"- sector count: {result.sector_count}")
        if result.driver_map_sector_count is not None:
            lines.append(f"- driver map sectors: {result.driver_map_sector_count}")
        if result.driver_map_row_count is not None:
            lines.append(f"- driver map rows: {result.driver_map_row_count}")

    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an AI-ready report package.")
    parser.add_argument("report_folder", help="Path to reports/<YYYY-MM-DD> folder")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = validate_ai_package(args.report_folder)
    print(format_result(result))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
