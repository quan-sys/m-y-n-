"""Summarize structured web driver research files."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_driver_research import CROSSCHECK_RESULT, validate_driver_research


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()


def _research_status(crosscheck: pd.DataFrame, source_log: pd.DataFrame) -> str:
    if crosscheck.empty or set(crosscheck["data_status"].astype(str)) == {"NEEDS_WEB_RESEARCH"}:
        return "PENDING"
    if not source_log.empty and (source_log["data_status"].astype(str) == "OK").any():
        return "PARTIAL"
    return "PENDING"


def summarize_driver_research(report_folder: str | Path) -> dict[str, object]:
    report_path = Path(report_folder)
    validation = validate_driver_research(report_path)
    if not validation.ok:
        raise ValueError("\n".join(validation.messages))

    source_log = pd.read_csv(report_path / "driver_source_log.csv")
    crosscheck = pd.read_csv(report_path / "sector_driver_crosscheck.csv")

    crosscheck_counts = {key: 0 for key in sorted(CROSSCHECK_RESULT)}
    if not crosscheck.empty:
        observed = crosscheck["crosscheck_result"].value_counts().to_dict()
        crosscheck_counts.update({str(key): int(value) for key, value in observed.items()})

    confidence_counts = source_log["confidence"].value_counts().to_dict() if not source_log.empty else {}
    unconfirmed_status = {"NEEDS_WEB_RESEARCH", "SOURCE_NOT_FOUND", "WEAK_SOURCE", "MANUAL_REVIEW_REQUIRED"}
    unconfirmed = 0
    if not crosscheck.empty:
        unconfirmed = int(crosscheck["data_status"].astype(str).isin(unconfirmed_status).sum())

    summary = {
        "report_folder": str(report_path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "research_status": _research_status(crosscheck, source_log),
        "sectors_researched": int(
            crosscheck.loc[~crosscheck["data_status"].astype(str).isin({"NEEDS_WEB_RESEARCH"}), "sector"].nunique()
        )
        if not crosscheck.empty
        else 0,
        "source_count_total": int(len(source_log)),
        "high_confidence_count": int(confidence_counts.get("HIGH", 0)),
        "medium_confidence_count": int(confidence_counts.get("MEDIUM", 0)),
        "low_confidence_count": int(confidence_counts.get("LOW", 0)),
        "unconfirmed_driver_count": unconfirmed,
        "crosscheck_counts": crosscheck_counts,
    }

    summary_path = report_path / "driver_research_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    notes_path = report_path / "driver_research_notes.md"
    summary_section = [
        "",
        "<!-- DRIVER_RESEARCH_SUMMARY_START -->",
        "## Driver Research Summary",
        "",
        f"- research_status: {summary['research_status']}",
        f"- sectors_researched: {summary['sectors_researched']}",
        f"- source_count_total: {summary['source_count_total']}",
        f"- unconfirmed_driver_count: {summary['unconfirmed_driver_count']}",
        "<!-- DRIVER_RESEARCH_SUMMARY_END -->",
        "",
    ]
    existing = notes_path.read_text(encoding="utf-8") if notes_path.exists() else ""
    if "<!-- DRIVER_RESEARCH_SUMMARY_START -->" not in existing:
        notes_path.write_text(existing.rstrip() + "\n" + "\n".join(summary_section), encoding="utf-8")

    return summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize driver research files.")
    parser.add_argument("report_folder", help="Path to reports/<YYYY-MM-DD> folder")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        summary = summarize_driver_research(args.report_folder)
    except Exception as exc:
        print("Driver research summary: FAIL")
        print(f"- {exc}")
        return 1

    print("Driver research summary: PASS")
    print(f"- report_folder: {summary['report_folder']}")
    print(f"- research_status: {summary['research_status']}")
    print(f"- sectors_researched: {summary['sectors_researched']}")
    print(f"- source_count_total: {summary['source_count_total']}")
    print(f"- unconfirmed_driver_count: {summary['unconfirmed_driver_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
