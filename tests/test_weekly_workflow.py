from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tests.test_chatgpt_handoff import _write_valid_package


def test_weekly_workflow_existing_report_passes_with_valid_fixture(tmp_path):
    package = _write_valid_package(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_weekly_workflow.py",
            "--existing-report",
            str(package),
        ],
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "Weekly analyst workflow: PASS" in result.stdout
    assert "validation: PASS" in result.stdout
    assert "HANDOFF_TO_CHATGPT.md" in result.stdout
    assert "driver research todo" in result.stdout
    assert (package / "HANDOFF_TO_CHATGPT.md").exists()
    assert (package / "driver_research_todo.md").exists()


def test_weekly_workflow_existing_report_fails_when_package_invalid(tmp_path):
    package = _write_valid_package(tmp_path)
    (package / "sector_cycle_signals.csv").unlink()

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_weekly_workflow.py",
            "--existing-report",
            str(package),
        ],
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "Weekly analyst workflow: FAIL" in result.stdout
    assert "Missing file: sector_cycle_signals.csv" in result.stdout
    assert not (package / "HANDOFF_TO_CHATGPT.md").exists()


def test_weekly_workflow_existing_report_does_not_require_live_pipeline(tmp_path):
    package = _write_valid_package(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_weekly_workflow.py",
            "--existing-report",
            str(package),
        ],
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "Files user should provide to ChatGPT" in result.stdout
    assert "AI_INPUT_SUMMARY.md" in result.stdout
    assert "run_metadata.json" in result.stdout
    assert "driver_research_todo.md" in result.stdout
