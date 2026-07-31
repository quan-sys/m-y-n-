import sys
from pathlib import Path

import pytest

from scripts import build_sprint5_valuation as valuation
from scripts import run_sprint4_step1_cleaning as cleaning


class ReachedAfterCacheGuard(Exception):
    pass


def _configure_script(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, script: str):
    cache_root = tmp_path / f"{script}_cache"
    output_root = tmp_path / f"{script}_outputs"
    monkeypatch.setattr(sys, "argv", [f"{script}.py"])

    if script == "cleaning":
        monkeypatch.setattr(cleaning, "CACHE_ROOT", cache_root)
        monkeypatch.setattr(cleaning, "SURVIVORS_PATH", output_root / "step1_survivors.csv")
        monkeypatch.setattr(cleaning, "REJECTS_PATH", output_root / "step1_rejects.csv")
        monkeypatch.setattr(cleaning, "SECTOR_A_PATH", output_root / "sector_a.csv")
        monkeypatch.setattr(cleaning, "SECTOR_B_PATH", output_root / "sector_b.csv")
        monkeypatch.setattr(cleaning, "REPORT_PATH", output_root / "report.md")
        return cleaning, cache_root, output_root

    monkeypatch.setattr(valuation, "QUARTERLY_CACHE_ROOT", cache_root)
    monkeypatch.setattr(valuation, "ALL_OUTPUT_PATH", output_root / "step2_valuation_all.csv")
    monkeypatch.setattr(valuation, "EBIT_TEV_OUTPUT_PATH", output_root / "step2_candidates_ebit_tev.csv")
    monkeypatch.setattr(valuation, "EP_OUTPUT_PATH", output_root / "step2_candidates_ep.csv")
    return valuation, cache_root, output_root


@pytest.mark.parametrize("script", ("cleaning", "valuation"))
def test_missing_cache_directory_raises_with_cache_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, script: str
) -> None:
    module, cache_root, _ = _configure_script(monkeypatch, tmp_path, script)

    with pytest.raises(RuntimeError) as error:
        module.main()

    assert str(cache_root) in str(error.value)


@pytest.mark.parametrize("script", ("cleaning", "valuation"))
def test_empty_cache_directory_raises_with_zero_file_count(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, script: str
) -> None:
    module, cache_root, _ = _configure_script(monkeypatch, tmp_path, script)
    cache_root.mkdir()

    with pytest.raises(RuntimeError) as error:
        module.main()

    assert "file_count=0" in str(error.value)


@pytest.mark.parametrize("script", ("cleaning", "valuation"))
def test_missing_cache_guard_writes_no_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, script: str
) -> None:
    module, _, output_root = _configure_script(monkeypatch, tmp_path, script)

    with pytest.raises(RuntimeError):
        module.main()

    assert not output_root.exists()


@pytest.mark.parametrize("script", ("cleaning", "valuation"))
def test_nonempty_cache_passes_guard(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, script: str
) -> None:
    module, cache_root, _ = _configure_script(monkeypatch, tmp_path, script)
    cache_root.mkdir()
    (cache_root / "marker.txt").write_text("present", encoding="utf-8")

    if script == "cleaning":
        def stop_after_guard(*args: object, **kwargs: object) -> None:
            raise ReachedAfterCacheGuard

        monkeypatch.setattr(module, "run_cleaning_pipeline", stop_after_guard)
    else:
        def stop_after_guard() -> None:
            raise ReachedAfterCacheGuard

        monkeypatch.setattr(module, "build_valuation", stop_after_guard)

    with pytest.raises(ReachedAfterCacheGuard):
        module.main()
