"""Build placeholder files for weekly web driver research."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()

SOURCE_LOG_COLUMNS = [
    "sector",
    "driver_name",
    "source_title",
    "source_url",
    "source_domain",
    "source_type",
    "source_date",
    "accessed_at",
    "key_finding",
    "data_status",
    "confidence",
    "notes",
]

CROSSCHECK_COLUMNS = [
    "sector",
    "market_stage",
    "market_signal_summary",
    "driver_signal",
    "crosscheck_result",
    "evidence_strength",
    "source_count",
    "summary",
    "warning",
    "data_status",
]


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _split_focus(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _priority(row: pd.Series, focus: list[str]) -> int:
    sector = str(row["sector"])
    stage = str(row.get("candidate_cycle_stage", ""))
    confidence = str(row.get("cycle_signal_confidence", ""))
    warnings = str(row.get("warning_flags", ""))
    rs = pd.to_numeric(row.get("relative_strength_1m_vs_vnindex"), errors="coerce")
    coverage = str(row.get("coverage_status", ""))

    if sector in focus:
        return 1
    if stage == "LEADERSHIP" and confidence == "HIGH":
        return 1
    if stage == "IMPROVING" and confidence == "HIGH" and "LOW_BREADTH" in warnings:
        return 1
    if stage == "LAGGING" and pd.notna(rs) and rs < -0.02:
        return 1
    if coverage in {"WATCH", "LOW_COVERAGE"}:
        return 1
    return 2


def _market_signal(row: pd.Series) -> list[str]:
    return [
        f"- Stage: {row.get('candidate_cycle_stage', 'N/A (MISSING_DATA)')}",
        f"- RS 1M vs VNINDEX: {row.get('relative_strength_1m_vs_vnindex', 'N/A (MISSING_DATA)')}",
        f"- Return 1M: {row.get('sector_return_1m_equal_weight', 'N/A (MISSING_DATA)')}",
        f"- Breadth: {row.get('breadth_signal', 'N/A (MISSING_DATA)')}",
        f"- Liquidity: {row.get('liquidity_signal', 'N/A (MISSING_DATA)')}",
        f"- Warning: {row.get('warning_flags', 'N/A (MISSING_DATA)')}",
    ]


def _crosscheck_result_for_stage(stage: str) -> str:
    if stage in {"LEADERSHIP", "IMPROVING"}:
        return "PRICE_STRONG_BUT_DRIVER_UNCONFIRMED"
    if stage in {"LAGGING", "WEAKENING"}:
        return "PRICE_WEAK_BUT_DRIVER_UNCONFIRMED"
    return "DATA_INSUFFICIENT"


def build_driver_research_template(
    report_folder: str | Path,
    *,
    focus: str | None = None,
    overwrite: bool = False,
) -> dict[str, Path]:
    report_path = Path(report_folder)
    if not report_path.exists():
        raise FileNotFoundError(f"Report folder does not exist: {report_path}")

    signals_path = report_path / "sector_cycle_signals.csv"
    driver_map_path = report_path / "sector_driver_map.csv"
    if not signals_path.exists():
        raise FileNotFoundError(f"Missing file: {signals_path.name}")
    if not driver_map_path.exists():
        raise FileNotFoundError(f"Missing file: {driver_map_path.name}")

    signals = pd.read_csv(signals_path)
    drivers = pd.read_csv(driver_map_path)
    metadata = _read_json(report_path / "run_metadata.json")
    focus_sectors = _split_focus(focus)

    signals = signals.copy()
    signals["_priority"] = signals.apply(lambda row: _priority(row, focus_sectors), axis=1)
    signals = signals.sort_values(["_priority", "sector"], kind="stable")

    todo_path = report_path / "driver_research_todo.md"
    source_log_path = report_path / "driver_source_log.csv"
    crosscheck_path = report_path / "sector_driver_crosscheck.csv"
    notes_path = report_path / "driver_research_notes.md"

    generated_at = datetime.now(timezone.utc).isoformat()
    title_date = metadata.get("as_of") or report_path.name
    lines = [
        f"# Driver Research Todo — {title_date}",
        "",
        "Mục tiêu: biến checklist driver thành research có nguồn public, nhưng không tự kết luận giao dịch.",
        "",
        "Quy tắc:",
        "- Không bịa dữ liệu.",
        "- Không coi missing data là 0.",
        "- Nếu chưa có nguồn public đáng tin, ghi `SOURCE_NOT_FOUND` hoặc `NEEDS_WEB_RESEARCH`.",
        "- File này chỉ là việc cần kiểm tra, không phải lời khuyên giao dịch.",
        "",
        f"Generated at: {generated_at}",
        "",
    ]

    for priority in [1, 2]:
        subset = signals[signals["_priority"] == priority]
        if subset.empty:
            continue
        lines.extend([f"## Priority {priority}", ""])
        for _, row in subset.iterrows():
            sector = row["sector"]
            sector_drivers = drivers[drivers["sector"] == sector]
            lines.extend([f"### {sector}", "", "Market signal:"])
            lines.extend(_market_signal(row))
            lines.extend(["", "Drivers to research:"])
            if sector_drivers.empty:
                lines.append("- N/A (MISSING_DATA)")
            else:
                for _, driver in sector_drivers.iterrows():
                    lines.append(
                        f"- {driver['driver_name']} — why it matters: {driver['why_it_matters']}"
                    )
            lines.extend(
                [
                    "",
                    "Questions for ChatGPT:",
                    "1. Có nguồn public đáng tin nào xác nhận driver này không?",
                    "2. Driver hiện đang ủng hộ, phủ định hay chưa rõ so với market signal?",
                    "3. Nguồn có mới và đáng tin không?",
                    "4. Cross-check result nên là gì?",
                    "",
                ]
            )

    todo_path.write_text("\n".join(lines), encoding="utf-8")

    if overwrite or not source_log_path.exists():
        pd.DataFrame(columns=SOURCE_LOG_COLUMNS).to_csv(source_log_path, index=False)

    if overwrite or not crosscheck_path.exists():
        rows = []
        for _, row in signals.drop(columns=["_priority"]).iterrows():
            stage = str(row.get("candidate_cycle_stage", "UNCLEAR_DATA"))
            rows.append(
                {
                    "sector": row["sector"],
                    "market_stage": stage,
                    "market_signal_summary": row.get("evidence_summary", "N/A (MISSING_DATA)"),
                    "driver_signal": "MISSING",
                    "crosscheck_result": _crosscheck_result_for_stage(stage),
                    "evidence_strength": "LOW",
                    "source_count": 0,
                    "summary": "N/A (MISSING_DATA)",
                    "warning": "Driver research pending.",
                    "data_status": "NEEDS_WEB_RESEARCH",
                }
            )
        pd.DataFrame(rows, columns=CROSSCHECK_COLUMNS).to_csv(crosscheck_path, index=False)

    if overwrite or not notes_path.exists():
        notes = [
            f"# Driver Research Notes — {title_date}",
            "",
            "Status: NEEDS_WEB_RESEARCH",
            "",
            "Dán kết quả web research đã tóm tắt vào đây sau khi ChatGPT kiểm tra nguồn public.",
            "",
            "Không bịa dữ liệu. Nếu không có nguồn đáng tin, ghi `SOURCE_NOT_FOUND`.",
            "",
        ]
        notes_path.write_text("\n".join(notes), encoding="utf-8")

    return {
        "todo": todo_path,
        "source_log": source_log_path,
        "crosscheck": crosscheck_path,
        "notes": notes_path,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build driver research placeholder files.")
    parser.add_argument("report_folder", help="Path to reports/<YYYY-MM-DD> folder")
    parser.add_argument("--focus", default=None, help="Comma-separated sector names to prioritize.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing research files.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        paths = build_driver_research_template(
            args.report_folder,
            focus=args.focus,
            overwrite=args.overwrite,
        )
    except Exception as exc:
        print("Driver research template: FAIL")
        print(f"- {exc}")
        return 1

    print("Driver research template: PASS")
    for label, path in paths.items():
        print(f"- {label}: {path}")
    print("- note: Driver research pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
