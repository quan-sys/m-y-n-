from __future__ import annotations

from pathlib import Path


DOCS = [
    Path("docs/AI_ANALYST_REPORT_TEMPLATE.md"),
    Path("docs/AI_ANALYST_PROMPT.md"),
    Path("docs/SECTOR_DRIVER_WEB_RESEARCH_CHECKLIST.md"),
    Path("docs/AI_REPORT_VALIDATION_CHECKLIST.md"),
]


def test_ai_report_docs_exist():
    for path in DOCS:
        assert path.exists(), f"Missing doc: {path}"


def test_ai_analyst_prompt_has_required_placeholders_and_files():
    text = Path("docs/AI_ANALYST_PROMPT.md").read_text(encoding="utf-8")

    for placeholder in ["[REPORT_FOLDER]", "[FILES_TO_READ]", "[ANALYSIS_DATE]"]:
        assert placeholder in text

    for file_name in [
        "AI_INPUT_SUMMARY.md",
        "README_FOR_AI.md",
        "sector_cycle_signals.csv",
        "sector_driver_map.csv",
        "data_quality.csv",
        "run_metadata.json",
    ]:
        assert file_name in text


def test_ai_report_docs_include_safety_rules():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in DOCS).lower()

    required_phrases = [
        "không khuyến nghị mua/bán",
        "không target price",
        "không ranking cổ phiếu",
        "không phân tích từng mã",
        "không coi missing data là 0",
        "không bịa",
        "web search",
        "n/a",
        "low_coverage",
        "data_weak",
        "cap-weight",
        "không thay cap-weight bằng equal-weight",
    ]

    for phrase in required_phrases:
        assert phrase in combined


def test_driver_research_checklist_covers_19_sector_groups():
    text = Path("docs/SECTOR_DRIVER_WEB_RESEARCH_CHECKLIST.md").read_text(encoding="utf-8")
    headings = [line for line in text.splitlines() if line.startswith("### ")]

    assert len(headings) >= 19
    assert "### NGÂN HÀNG" in text
    assert "### BẤT ĐỘNG SẢN" in text
    assert "### VIỄN THÔNG" in text


def test_validation_checklist_has_pass_fail_items():
    text = Path("docs/AI_REPORT_VALIDATION_CHECKLIST.md").read_text(encoding="utf-8")

    for section in ["Scope safety", "Data safety", "Reasoning quality", "Final decision"]:
        assert section in text
    assert "PASS/FAIL" in text
    assert "PASS WITH NOTES" in text
