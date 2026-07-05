from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.validate_ai_package import validate_ai_package


def test_validator_passes_valid_ai_package(tmp_path):
    package = _write_valid_package(tmp_path)

    result = validate_ai_package(package)

    assert result.ok is True
    assert result.required_files_ok is True
    assert result.sector_schema_ok is True
    assert result.driver_schema_ok is True
    assert result.metadata_ok is True
    assert result.sector_count == 2
    assert result.driver_map_sector_count == 2
    assert result.driver_map_row_count == 4


def test_validator_fails_when_required_file_is_missing(tmp_path):
    package = _write_valid_package(tmp_path)
    (package / "sector_driver_map.csv").unlink()

    result = validate_ai_package(package)

    assert result.ok is False
    assert "Missing file: sector_driver_map.csv" in result.messages


def test_validator_fails_when_sector_signals_column_is_missing(tmp_path):
    package = _write_valid_package(tmp_path)
    signals = pd.read_csv(package / "sector_cycle_signals.csv")
    signals = signals.drop(columns=["evidence_summary"])
    signals.to_csv(package / "sector_cycle_signals.csv", index=False)

    result = validate_ai_package(package)

    assert result.ok is False
    assert any("sector_cycle_signals.csv missing columns" in message for message in result.messages)
    assert any("evidence_summary" in message for message in result.messages)


def test_validator_fails_when_cycle_stage_is_invalid(tmp_path):
    package = _write_valid_package(tmp_path)
    signals = pd.read_csv(package / "sector_cycle_signals.csv")
    signals.loc[0, "candidate_cycle_stage"] = "BUY_NOW"
    signals.to_csv(package / "sector_cycle_signals.csv", index=False)

    result = validate_ai_package(package)

    assert result.ok is False
    assert any("Invalid candidate_cycle_stage values" in message for message in result.messages)


def test_validator_fails_when_metadata_counts_do_not_match(tmp_path):
    package = _write_valid_package(tmp_path)
    metadata_path = package / "run_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["driver_map_row_count"] = 99
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    result = validate_ai_package(package)

    assert result.ok is False
    assert any("driver_map_row_count mismatch" in message for message in result.messages)


def test_validator_fails_when_driver_map_has_too_few_drivers(tmp_path):
    package = _write_valid_package(tmp_path)
    drivers = pd.read_csv(package / "sector_driver_map.csv")
    drivers = drivers[drivers["sector"] != "BANKS"]
    drivers = pd.concat([drivers, _driver_rows("BANKS", ["credit growth"])], ignore_index=True)
    drivers.to_csv(package / "sector_driver_map.csv", index=False)
    _write_metadata(package, cycle_sector_count=2, driver_sector_count=2, driver_rows=len(drivers))

    result = validate_ai_package(package)

    assert result.ok is False
    assert any("Sectors with fewer than 2 drivers" in message for message in result.messages)
    assert any("BANKS" in message for message in result.messages)


def test_validator_fails_when_report_folder_is_missing(tmp_path):
    result = validate_ai_package(tmp_path / "missing-report")

    assert result.ok is False
    assert any("Report folder does not exist" in message for message in result.messages)


def _write_valid_package(base: Path) -> Path:
    package = base / "reports" / "2026-07-05"
    package.mkdir(parents=True)

    (package / "AI_INPUT_SUMMARY.md").write_text("AI summary fixture", encoding="utf-8")
    (package / "README_FOR_AI.md").write_text("README fixture", encoding="utf-8")
    (package / "data_quality.csv").write_text("sector,coverage_status\nBANKS,OK\nRETAIL,WATCH\n", encoding="utf-8")

    pd.DataFrame(
        [
            _signal_row("BANKS", "LEADERSHIP", "HIGH"),
            _signal_row("RETAIL", "UNCLEAR_DATA", "LOW"),
        ]
    ).to_csv(package / "sector_cycle_signals.csv", index=False)

    drivers = pd.concat(
        [
            _driver_rows("BANKS", ["credit growth", "NIM"]),
            _driver_rows("RETAIL", ["retail sales", "consumer income"]),
        ],
        ignore_index=True,
    )
    drivers.to_csv(package / "sector_driver_map.csv", index=False)
    _write_metadata(package, cycle_sector_count=2, driver_sector_count=2, driver_rows=4)
    return package


def _signal_row(sector: str, stage: str, confidence: str) -> dict[str, object]:
    return {
        "sector": sector,
        "ticker_count": 3,
        "valid_price_count": 3,
        "data_quality_status": "OK",
        "coverage_status": "OK",
        "relative_strength_1m_vs_vnindex": 0.01,
        "sector_return_1w_equal_weight": 0.02,
        "sector_return_1m_equal_weight": 0.03,
        "price_trend_signal": "POSITIVE",
        "relative_strength_signal": "POSITIVE",
        "momentum_signal": "POSITIVE",
        "breadth_signal": "HEALTHY",
        "liquidity_signal": "RISING",
        "data_confidence_signal": "OK",
        "candidate_cycle_stage": stage,
        "cycle_signal_confidence": confidence,
        "evidence_summary": "fixture evidence",
        "warning_flags": "",
    }


def _driver_rows(sector: str, names: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "sector": sector,
                "driver_name": name,
                "why_it_matters": "fixture reason",
                "driver_type": "PUBLIC_MACRO",
                "source_strategy": "CHATGPT_WEB_SEARCH_PUBLIC",
                "public_web_search_available": "yes",
                "codex_pipeline_required": "no",
                "priority": "HIGH",
                "interpretation_note": "verify with public source",
                "data_status": "NEEDS_WEB_RESEARCH",
            }
            for name in names
        ]
    )


def _write_metadata(
    package: Path,
    *,
    cycle_sector_count: int,
    driver_sector_count: int,
    driver_rows: int,
) -> None:
    metadata = {
        "ai_ready_package_created": True,
        "cycle_signals_created": True,
        "driver_map_created": True,
        "cycle_signal_sector_count": cycle_sector_count,
        "driver_map_sector_count": driver_sector_count,
        "driver_map_row_count": driver_rows,
    }
    (package / "run_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
