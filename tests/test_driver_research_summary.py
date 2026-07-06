from __future__ import annotations

import json

import pandas as pd

from scripts.build_driver_research_template import build_driver_research_template
from scripts.summarize_driver_research import summarize_driver_research
from tests.test_chatgpt_handoff import _write_valid_package


def test_summarize_driver_research_creates_summary_json(tmp_path):
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
                "key_finding": "Public source confirms the driver is improving.",
                "data_status": "OK",
                "confidence": "HIGH",
                "notes": "",
            },
            {
                "sector": "RETAIL",
                "driver_name": "retail sales",
                "source_title": "Fixture source 2",
                "source_url": "https://example.com/source-2",
                "source_domain": "example.com",
                "source_type": "official_statistics",
                "source_date": "2026-07-01",
                "accessed_at": "2026-07-06",
                "key_finding": "Public source is partial.",
                "data_status": "PARTIAL",
                "confidence": "MEDIUM",
                "notes": "",
            },
        ]
    ).to_csv(paths["source_log"], index=False)

    crosscheck = pd.read_csv(paths["crosscheck"])
    crosscheck.loc[0, "driver_signal"] = "POSITIVE"
    crosscheck.loc[0, "crosscheck_result"] = "DRIVER_CONFIRMS_STRENGTH"
    crosscheck.loc[0, "evidence_strength"] = "HIGH"
    crosscheck.loc[0, "source_count"] = 1
    crosscheck.loc[0, "summary"] = "Public driver confirms the strong market signal."
    crosscheck.loc[0, "data_status"] = "OK"
    crosscheck.loc[1, "driver_signal"] = "MIXED"
    crosscheck.loc[1, "crosscheck_result"] = "DRIVER_MIXED"
    crosscheck.loc[1, "evidence_strength"] = "MEDIUM"
    crosscheck.loc[1, "source_count"] = 1
    crosscheck.loc[1, "summary"] = "Public driver is mixed."
    crosscheck.loc[1, "data_status"] = "PARTIAL"
    crosscheck.to_csv(paths["crosscheck"], index=False)

    summary = summarize_driver_research(package)
    saved = json.loads((package / "driver_research_summary.json").read_text(encoding="utf-8"))

    assert summary["source_count_total"] == 2
    assert summary["high_confidence_count"] == 1
    assert summary["medium_confidence_count"] == 1
    assert summary["crosscheck_counts"]["DRIVER_CONFIRMS_STRENGTH"] == 1
    assert summary["crosscheck_counts"]["DRIVER_MIXED"] == 1
    assert saved == summary
    assert "Driver Research Summary" in (package / "driver_research_notes.md").read_text(encoding="utf-8")
