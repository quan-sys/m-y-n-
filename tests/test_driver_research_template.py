from __future__ import annotations

from pathlib import Path

from scripts.build_driver_research_template import build_driver_research_template
from tests.test_chatgpt_handoff import _write_valid_package


def test_build_driver_research_template_creates_todo_and_placeholders(tmp_path):
    package = _write_valid_package(tmp_path)

    paths = build_driver_research_template(package)

    todo = paths["todo"].read_text(encoding="utf-8")
    assert "Driver Research Todo" in todo
    assert "BANKS" in todo
    assert "credit growth" in todo
    assert "không phải lời khuyên giao dịch" in todo.lower()
    assert paths["source_log"].exists()
    assert paths["crosscheck"].exists()
    assert paths["notes"].exists()


def test_build_driver_research_template_prioritizes_focus_sector(tmp_path):
    package = _write_valid_package(tmp_path)

    paths = build_driver_research_template(package, focus="RETAIL")

    text = paths["todo"].read_text(encoding="utf-8")
    priority_one = text.split("## Priority 1", 1)[1].split("## Priority 2", 1)[0]
    assert "RETAIL" in priority_one


def test_build_driver_research_template_does_not_overwrite_existing_source_log(tmp_path):
    package = _write_valid_package(tmp_path)
    paths = build_driver_research_template(package)
    paths["source_log"].write_text("custom research\n", encoding="utf-8")

    build_driver_research_template(package)

    assert paths["source_log"].read_text(encoding="utf-8") == "custom research\n"


def test_build_driver_research_template_output_has_no_banned_investment_phrases(tmp_path):
    package = _write_valid_package(tmp_path)
    paths = build_driver_research_template(package)
    combined = "\n".join(Path(path).read_text(encoding="utf-8").lower() for path in paths.values())

    for phrase in ["nên mua", "nên bán", "target price", "upside", "downside", "phím hàng"]:
        assert phrase not in combined
