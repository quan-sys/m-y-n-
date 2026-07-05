"""Build a ChatGPT handoff file from a validated AI-ready report package."""

from __future__ import annotations

import argparse
import json
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

from scripts.validate_ai_package import format_result, validate_ai_package  # noqa: E402


FILES_FOR_CHATGPT = [
    "HANDOFF_TO_CHATGPT.md",
    "AI_INPUT_SUMMARY.md",
    "README_FOR_AI.md",
    "sector_cycle_signals.csv",
    "sector_driver_map.csv",
    "data_quality.csv",
    "run_metadata.json",
]


def _metadata_value(metadata: dict[str, object], key: str) -> object:
    value = metadata.get(key)
    if value in (None, ""):
        return "N/A"
    return value


def render_handoff(report_folder: str | Path, metadata: dict[str, object]) -> str:
    report_path = Path(report_folder)
    lines = [
        "# Sector Cycle Monitor — ChatGPT Handoff",
        "",
        "## 1. Project",
        "",
        "Sector Cycle Monitor theo dõi chu kỳ ngành ICB2 của thị trường chứng khoán Việt Nam.",
        "",
        "Đây không phải khuyến nghị đầu tư, không phải khuyến nghị mua/bán, không target price, và không ranking cổ phiếu.",
        "",
        "## 2. Report folder",
        "",
        f"`{report_path.as_posix()}`",
        "",
        "## 3. Analysis context",
        "",
        f"- Analysis date: `{_metadata_value(metadata, 'as_of')}`",
        f"- Generated at: `{_metadata_value(metadata, 'generated_at')}`",
        "",
        "## 4. File ChatGPT cần đọc",
        "",
    ]
    lines.extend(f"- `{name}`" for name in FILES_FOR_CHATGPT)
    lines.extend(
        [
            "",
            "## 5. Metadata summary",
            "",
            f"- universe_row_count: `{_metadata_value(metadata, 'universe_row_count')}`",
            f"- valid_price_total: `{_metadata_value(metadata, 'valid_price_total')}`",
            f"- api_error_total: `{_metadata_value(metadata, 'api_error_total')}`",
            f"- index_source: `{_metadata_value(metadata, 'index_source')}`",
            f"- cap_weight_status: `{_metadata_value(metadata, 'cap_weight_status')}`",
            f"- cycle_signal_sector_count: `{_metadata_value(metadata, 'cycle_signal_sector_count')}`",
            f"- driver_map_sector_count: `{_metadata_value(metadata, 'driver_map_sector_count')}`",
            f"- driver_map_row_count: `{_metadata_value(metadata, 'driver_map_row_count')}`",
            "",
            "## 6. Luật an toàn",
            "",
            "- Không khuyến nghị mua/bán.",
            "- Không target price.",
            "- Không ranking cổ phiếu.",
            "- Không deep-dive từng mã.",
            "- Không bịa dữ liệu hoặc driver live data.",
            "- Không coi missing data là 0.",
            "- Không thay cap-weight bằng equal-weight.",
            "- Nếu thiếu dữ liệu, ghi `N/A (MISSING_DATA)`.",
            "- Nếu API lỗi, ghi `API_ERROR`.",
            "- Nếu driver không có nguồn public đáng tin, ghi `N/A`.",
            "- Nếu dữ liệu `LOW_COVERAGE`, `WATCH`, hoặc `DATA_WEAK`, phải đọc thận trọng.",
            "",
            "## 7. Nhiệm vụ của ChatGPT",
            "",
            "1. Đọc toàn bộ package trong report folder.",
            "2. Web search driver public đáng tin.",
            "3. Phân biệt deterministic signal từ Codex và reasoning phân tích từ ChatGPT.",
            "4. Phân biệt driver public đã xác nhận và driver chưa xác nhận.",
            "5. Chọn ngành đáng theo dõi thêm nếu đủ điều kiện.",
            "6. Ghi rõ rủi ro dữ liệu và mức độ không chắc chắn.",
            "7. Không viết kết luận như một khuyến nghị giao dịch.",
            "",
            "## 8. Tài liệu hỗ trợ",
            "",
            "- `docs/AI_ANALYST_PROMPT.md`",
            "- `docs/AI_ANALYST_REPORT_TEMPLATE.md`",
            "- `docs/SECTOR_DRIVER_WEB_RESEARCH_CHECKLIST.md`",
            "- `docs/AI_REPORT_VALIDATION_CHECKLIST.md`",
            "- `docs/SAMPLE_FINAL_AI_SECTOR_REPORT_STRUCTURE.md`",
            "",
            "## 9. Nhắc lại",
            "",
            "Đây không phải final investment report. Đây là handoff để ChatGPT phân tích cấp ngành có kiểm soát.",
            "",
        ]
    )
    return "\n".join(lines)


def build_handoff(report_folder: str | Path) -> Path:
    report_path = Path(report_folder)
    validation = validate_ai_package(report_path)
    if not validation.ok:
        raise ValueError(format_result(validation))

    metadata = json.loads((report_path / "run_metadata.json").read_text(encoding="utf-8"))
    handoff_path = report_path / "HANDOFF_TO_CHATGPT.md"
    handoff_path.write_text(render_handoff(report_path, metadata), encoding="utf-8")
    return handoff_path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build ChatGPT handoff from an AI-ready report package.")
    parser.add_argument("report_folder", help="Path to reports/<YYYY-MM-DD> folder")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    report_path = Path(args.report_folder)
    validation = validate_ai_package(report_path)

    if not validation.ok:
        print("Cannot build ChatGPT handoff because AI package validation failed.")
        for message in validation.messages:
            print(f"- {message}")
        return 1

    metadata = json.loads((report_path / "run_metadata.json").read_text(encoding="utf-8"))
    handoff_path = report_path / "HANDOFF_TO_CHATGPT.md"
    handoff_path.write_text(render_handoff(report_path, metadata), encoding="utf-8")
    print(f"ChatGPT handoff created: {handoff_path}")
    print("AI package validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
