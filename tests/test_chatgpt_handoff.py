from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from scripts.build_chatgpt_handoff import build_handoff, render_handoff


def test_build_chatgpt_handoff_creates_markdown_from_valid_package(tmp_path):
    package = _write_valid_package(tmp_path)

    handoff = build_handoff(package)
    text = handoff.read_text(encoding="utf-8")

    assert handoff.name == "HANDOFF_TO_CHATGPT.md"
    assert "Sector Cycle Monitor" in text
    assert "universe_row_count" in text
    assert "378" in text
    for file_name in [
        "AI_INPUT_SUMMARY.md",
        "README_FOR_AI.md",
        "sector_cycle_signals.csv",
        "sector_driver_map.csv",
        "data_quality.csv",
        "run_metadata.json",
    ]:
        assert file_name in text


def test_handoff_contains_safety_rules_and_is_not_final_investment_report(tmp_path):
    package = _write_valid_package(tmp_path)
    handoff = build_handoff(package)
    text = handoff.read_text(encoding="utf-8").lower()

    for phrase in [
        "không khuyến nghị mua/bán",
        "không target price",
        "không ranking cổ phiếu",
        "không bịa dữ liệu",
        "không coi missing data là 0",
        "không thay cap-weight bằng equal-weight",
        "low_coverage",
        "data_weak",
    ]:
        assert phrase in text

    assert "đây không phải final investment report" in text
    assert "final investment report." not in text.replace("đây không phải final investment report.", "")


def test_build_handoff_fails_when_ai_package_validation_fails(tmp_path):
    package = _write_valid_package(tmp_path)
    (package / "sector_driver_map.csv").unlink()

    result = subprocess.run(
        [sys.executable, "scripts/build_chatgpt_handoff.py", str(package)],
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "Cannot build ChatGPT handoff" in result.stdout
    assert "Missing file: sector_driver_map.csv" in result.stdout
    assert not (package / "HANDOFF_TO_CHATGPT.md").exists()


def test_render_handoff_uses_metadata_summary():
    text = render_handoff(
        "reports/example",
        {
            "as_of": "2026-07-03",
            "generated_at": "2026-07-05T00:00:00+00:00",
            "universe_row_count": 378,
            "valid_price_total": 378,
            "api_error_total": 0,
            "index_source": "VNINDEX",
            "cap_weight_status": "OK;SKIPPED_MISSING_MARKET_CAP",
            "cycle_signal_sector_count": 19,
            "driver_map_sector_count": 19,
            "driver_map_row_count": 57,
        },
    )

    assert "reports/example" in text
    assert "2026-07-03" in text
    assert "VNINDEX" in text
    assert "57" in text


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

    pd.concat(
        [
            _driver_rows("BANKS", ["credit growth", "NIM"]),
            _driver_rows("RETAIL", ["retail sales", "consumer income"]),
        ],
        ignore_index=True,
    ).to_csv(package / "sector_driver_map.csv", index=False)

    metadata = {
        "as_of": "2026-07-03",
        "generated_at": "2026-07-05T00:00:00+00:00",
        "universe_row_count": 378,
        "valid_price_total": 378,
        "api_error_total": 0,
        "index_source": "VNINDEX",
        "cap_weight_status": "OK;SKIPPED_MISSING_MARKET_CAP",
        "ai_ready_package_created": True,
        "cycle_signals_created": True,
        "driver_map_created": True,
        "cycle_signal_sector_count": 2,
        "driver_map_sector_count": 2,
        "driver_map_row_count": 4,
    }
    (package / "run_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
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
