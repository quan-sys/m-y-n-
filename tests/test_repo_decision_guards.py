from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_screener_archive_is_gitignored():
    lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert "data/screener/archive/" in {line.strip() for line in lines}


def test_net_debt_ebitda_cap_stays_absent():
    loaded = yaml.safe_load((ROOT / "config" / "screener.yaml").read_text(encoding="utf-8"))

    assert isinstance(loaded, dict) and loaded
    assert loaded["MSCORE_THRESHOLD"] == -1.78
    assert "NET_DEBT_EBITDA_CAP" not in loaded, (
        "NET_DEBT_EBITDA_CAP is blocked by owner decision; see DEF-4"
    )


def test_deferred_defect_registry_is_complete():
    lines = (ROOT / "docs" / "KNOWN_LIMITS_AND_DEFERRED_DEFECTS.md").read_text(
        encoding="utf-8"
    ).splitlines()

    for identifier in ("LIM-1", "DEF-1", "DEF-2", "DEF-3", "DEF-4", "DEF-5", "DEF-6"):
        assert any(line.startswith(f"## {identifier}") for line in lines)
    assert sum(line.startswith("Status:") for line in lines) >= 6
