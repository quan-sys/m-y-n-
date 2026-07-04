from __future__ import annotations

from pathlib import Path
import sys


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.weekly import run_weekly_mvp  # noqa: E402


def main() -> int:
    result = run_weekly_mvp(
        universe_path=ROOT / "data" / "universe.csv",
        reports_root=ROOT / "reports",
    )
    print(f"Weekly MVP output: {result.output_dir.resolve()}")
    print(f"- {result.output_dir / 'WEEKLY_REPORT.md'}")
    print(f"- {result.output_dir / 'sector_summary.csv'}")
    print(f"- {result.output_dir / 'sector_indicators_tier1.csv'}")
    print(f"- {result.output_dir / 'data_quality.csv'}")
    print(f"- {result.output_dir / 'run_metadata.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
