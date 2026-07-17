"""Run the weekly analyst workflow without calling ChatGPT or web search."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_chatgpt_handoff import FILES_FOR_CHATGPT, build_handoff  # noqa: E402
from scripts.build_driver_research_template import build_driver_research_template  # noqa: E402
from scripts.validate_ai_package import format_result, validate_ai_package  # noqa: E402
from src.weekly import run_weekly_mvp  # noqa: E402


def _run_existing_report(report_folder: Path) -> int:
    validation = validate_ai_package(report_folder)
    if not validation.ok:
        print("Weekly analyst workflow: FAIL")
        print(format_result(validation))
        return 1

    handoff_path = build_handoff(report_folder)
    driver_paths = build_driver_research_template(report_folder)
    print("Weekly analyst workflow: PASS")
    print(f"- report folder: {report_folder}")
    print("- validation: PASS")
    print(f"- handoff: {handoff_path}")
    print(f"- driver research todo: {driver_paths['todo']}")
    print("- driver research: pending")
    print("")
    print("Files user should provide to ChatGPT:")
    for file_name in FILES_FOR_CHATGPT:
        print(f"- {report_folder / file_name}")
    print("")
    print("Next step:")
    print("Open HANDOFF_TO_CHATGPT.md and provide it to ChatGPT with the AI-ready files.")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run weekly analyst workflow.")
    parser.add_argument(
        "--existing-report",
        default=None,
        help="Use an existing reports/<YYYY-MM-DD> folder and avoid live API calls.",
    )
    parser.add_argument(
        "--limit-sectors",
        type=int,
        default=None,
        help="Optional quick-check limit when building a fresh weekly report.",
    )
    parser.add_argument(
        "--market-cap-limit",
        type=int,
        default=0,
        help="Maximum controlled live market-cap requests; default 0 disables them.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if args.existing_report:
        return _run_existing_report(Path(args.existing_report))

    result = run_weekly_mvp(
        universe_path=ROOT / "data" / "universe.csv",
        reports_root=ROOT / "reports",
        limit_sectors=args.limit_sectors,
        market_cap_limit=args.market_cap_limit,
    )
    return _run_existing_report(result.output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
