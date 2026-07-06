from __future__ import annotations

import pandas as pd

from scripts.build_driver_research_template import build_driver_research_template
from scripts.validate_driver_research import validate_driver_research
from tests.test_chatgpt_handoff import _write_valid_package


def test_validate_driver_research_passes_placeholder_files(tmp_path):
    package = _write_valid_package(tmp_path)
    build_driver_research_template(package)

    result = validate_driver_research(package)

    assert result.ok is True


def test_validate_driver_research_fails_missing_required_column(tmp_path):
    package = _write_valid_package(tmp_path)
    paths = build_driver_research_template(package)
    crosscheck = pd.read_csv(paths["crosscheck"]).drop(columns=["warning"])
    crosscheck.to_csv(paths["crosscheck"], index=False)

    result = validate_driver_research(package)

    assert result.ok is False
    assert any("missing columns" in message for message in result.messages)
    assert any("warning" in message for message in result.messages)


def test_validate_driver_research_fails_high_confidence_without_key_finding(tmp_path):
    package = _write_valid_package(tmp_path)
    paths = build_driver_research_template(package)
    pd.DataFrame(
        [
            {
                "sector": "BANKS",
                "driver_name": "credit growth",
                "source_title": "Fixture source",
                "source_url": "https://example.com/source",
                "source_domain": "example.com",
                "source_type": "regulator",
                "source_date": "2026-07-01",
                "accessed_at": "2026-07-06",
                "key_finding": "",
                "data_status": "OK",
                "confidence": "HIGH",
                "notes": "",
            }
        ]
    ).to_csv(paths["source_log"], index=False)

    result = validate_driver_research(package)

    assert result.ok is False
    assert any("HIGH confidence requires key_finding" in message for message in result.messages)


def test_validate_driver_research_fails_source_count_zero_with_high_evidence(tmp_path):
    package = _write_valid_package(tmp_path)
    paths = build_driver_research_template(package)
    crosscheck = pd.read_csv(paths["crosscheck"])
    crosscheck.loc[0, "evidence_strength"] = "HIGH"
    crosscheck.to_csv(paths["crosscheck"], index=False)

    result = validate_driver_research(package)

    assert result.ok is False
    assert any("source_count 0 cannot be HIGH evidence" in message for message in result.messages)


def test_validate_driver_research_fails_banned_investment_phrase(tmp_path):
    package = _write_valid_package(tmp_path)
    paths = build_driver_research_template(package)
    crosscheck = pd.read_csv(paths["crosscheck"])
    crosscheck.loc[0, "summary"] = "nên mua ngành này"
    crosscheck.to_csv(paths["crosscheck"], index=False)

    result = validate_driver_research(package)

    assert result.ok is False
    assert any("banned phrase" in message for message in result.messages)


def test_validate_driver_research_fails_ok_without_source_url(tmp_path):
    package = _write_valid_package(tmp_path)
    paths = build_driver_research_template(package)
    pd.DataFrame(
        [
            {
                "sector": "BANKS",
                "driver_name": "credit growth",
                "source_title": "Fixture source",
                "source_url": "",
                "source_domain": "example.com",
                "source_type": "regulator",
                "source_date": "2026-07-01",
                "accessed_at": "2026-07-06",
                "key_finding": "Fixture finding",
                "data_status": "OK",
                "confidence": "MEDIUM",
                "notes": "",
            }
        ]
    ).to_csv(paths["source_log"], index=False)

    result = validate_driver_research(package)

    assert result.ok is False
    assert any("OK requires source_url" in message for message in result.messages)
