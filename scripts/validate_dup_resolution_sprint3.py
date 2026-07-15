from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import random
import sys

import pandas as pd


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.finance_client import FinanceClient  # noqa: E402


SEED = 20260715
CORE_TICKERS = ("VNM", "HPG", "FPT", "VCB")
ORIGINAL_SEEDED_TICKERS = (
    "CSM", "DVP", "C32", "VOS", "PHR", "DP3", "DHC", "DRC", "VCS", "TLH",
    "HID", "DXP", "LBE", "ASM", "PVP", "CTF", "HDG", "PVC", "NCT", "VC7",
)
FINANCIAL_ICB2 = {"NGÂN HÀNG", "BẢO HIỂM", "DỊCH VỤ TÀI CHÍNH"}
REPORT_ITEMS = {
    "current_assets",
    "cash_and_cash_equivalents",
    "short_term_investments",
    "accounts_receivable",
    "inventories",
    "other_current_assets",
    "preferred_shares",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Live Sprint 3 duplicate-resolution validation")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--additional-size", type=int, default=16)
    parser.add_argument("--min-sleep", type=float, default=2.8)
    parser.add_argument("--max-sleep", type=float, default=3.6)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs" / "VALIDATE_DUP_RESOLUTION_SPRINT_3.md",
    )
    return parser.parse_args(argv)


def choose_sample(seed: int, additional_size: int) -> tuple[list[str], list[str]]:
    universe = pd.read_csv(ROOT / "data" / "universe.csv")
    eligible = universe[
        universe["status"].eq("ACCEPTED")
        & ~universe["exchange"].eq("UPCOM")
        & ~universe["icb2"].isin(FINANCIAL_ICB2)
        & ~universe["ticker"].isin(CORE_TICKERS)
    ]
    tickers = sorted(eligible["ticker"].astype(str).unique())
    missing_original = sorted(set(ORIGINAL_SEEDED_TICKERS) - set(tickers))
    if missing_original:
        raise ValueError(f"original seeded tickers are no longer eligible: {missing_original}")
    remaining = [ticker for ticker in tickers if ticker not in ORIGINAL_SEEDED_TICKERS]
    if len(remaining) < additional_size:
        raise ValueError(f"only {len(remaining)} additional eligible tickers")
    additional = random.Random(seed).sample(remaining, additional_size)
    return list(ORIGINAL_SEEDED_TICKERS), additional


def _number(value: object) -> str:
    return "NaN" if pd.isna(value) else str(float(value))


def _markdown_table(frame: pd.DataFrame, periods: list[str]) -> list[str]:
    lines = [
        "| raw_index | item | item_en | item_id | " + " | ".join(periods) + " |",
        "| ---: | --- | --- | --- | " + " | ".join("---:" for _ in periods) + " |",
    ]
    for index, row in frame.iterrows():
        values = " | ".join(_number(row[period]) for period in periods)
        lines.append(
            f"| {index} | {row.get('item', '')} | {row.get('item_en', '')} | "
            f"{row.get('item_id', '')} | {values} |"
        )
    return lines


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    original_sample, additional_sample = choose_sample(args.seed, args.additional_size)
    sample = [*original_sample, *additional_sample]
    tickers = [*CORE_TICKERS, *sample]
    client = FinanceClient(
        cache_dir=ROOT / "data" / "fundamentals",
        min_sleep_seconds=args.min_sleep,
        max_sleep_seconds=args.max_sleep,
        use_cache=False,
    )
    records: list[dict[str, object]] = []
    sections: list[str] = []
    for ticker in tickers:
        result = client.get_balance_sheet(
            ticker,
            "quarter",
            company_type="BANK" if ticker == "VCB" else "NON_FINANCIAL",
            expect_large_company_scale=True,
        )
        metadata = result.metadata or {}
        audit = dict(metadata.get("duplicate_resolution") or {})
        observation = Path(str(metadata.get("observation_path", "")))
        raw_path = observation / "raw.parquet"
        raw = pd.read_parquet(raw_path) if raw_path.exists() else pd.DataFrame()
        periods = [
            str(column)
            for column in raw.columns
            if str(column) not in {"item", "item_en", "item_id"}
        ]
        evidence = raw[raw.get("item_id", pd.Series(dtype=str)).astype(str).isin(REPORT_ITEMS)]
        preferred_event = next(
            (
                event for event in audit.get("events", [])
                if event.get("flag") == "DUPLICATE_RESOLVED_NON_NAN"
            ),
            {},
        )
        identity_event = next(
            (
                event for event in audit.get("events", [])
                if event.get("flag") == "IDENTITY_CANDIDATE_ERRORS"
            ),
            {},
        )
        margin_events = [
            event for event in audit.get("events", [])
            if event.get("flag") == "IDENTITY_PER_ITEM_MARGIN"
        ]
        materiality_events = [
            event for event in audit.get("events", [])
            if event.get("flag") in {"DUPLICATE_MATERIALITY_CHECK", "DUPLICATE_RESOLVED_IMMATERIAL"}
        ]
        identical_events = [
            event for event in audit.get("events", [])
            if event.get("flag") == "DUPLICATE_VERIFIED_IDENTICAL"
        ]
        status = "AMBIGUOUS" if audit.get("ambiguous") else ("RESOLVED" if result.ok else "API_ERROR")
        record = {
            "ticker": ticker,
            "status": status,
            "data_status": result.status,
            "flags": audit.get("flags", []),
            "preferred_values": preferred_event.get("resolved_values"),
            "identity_candidates": identity_event.get("candidates", []),
            "per_item_margins": margin_events,
            "materiality_comparisons": materiality_events,
            "identical_duplicates": identical_events,
            "error": result.error or "",
        }
        records.append(record)
        print(
            f"{ticker}: {status}; data_status={result.status}; "
            f"flags={','.join(record['flags']) or 'NONE'}; error={result.error or ''}",
            flush=True,
        )
        sections.extend(
            [
                f"## {ticker}",
                "",
                f"- Result: `{status}`",
                f"- data_status: `{result.status}`",
                f"- Flags: `{json.dumps(record['flags'], ensure_ascii=False)}`",
                f"- Resolved preferred values: `{json.dumps(record['preferred_values'], ensure_ascii=False)}`",
                f"- Error: `{result.error or ''}`",
                "",
                "### Verbatim relevant raw rows",
                "",
                *_markdown_table(evidence, periods),
                "",
                "### Identity candidate errors",
                "",
                "```json",
                json.dumps(record["identity_candidates"], ensure_ascii=False, indent=2),
                "```",
                "",
                "### Per-item margins",
                "",
                "```json",
                json.dumps(record["per_item_margins"], ensure_ascii=False, indent=2),
                "```",
                "",
                "### Materiality comparisons and identical duplicates",
                "",
                "```json",
                json.dumps(
                    {
                        "materiality": record["materiality_comparisons"],
                        "identical": record["identical_duplicates"],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                "```",
                "",
            ]
        )

    clean = all(record["status"] == "RESOLVED" for record in records)
    resolved_count = sum(record["status"] == "RESOLVED" for record in records)
    validation_resolution_coverage = resolved_count / len(records) if records else 0.0
    ambiguous_tickers = [
        str(record["ticker"]) for record in records if record["status"] == "AMBIGUOUS"
    ]
    summary_rows = [
        "| ticker | result | data_status | preferred values | flags |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in records:
        summary_rows.append(
            f"| {record['ticker']} | {record['status']} | {record['data_status']} | "
            f"`{json.dumps(record['preferred_values'], ensure_ascii=False)}` | "
            f"`{json.dumps(record['flags'], ensure_ascii=False)}` |"
        )
    document = "\n".join(
        [
            "# Sprint 3 live duplicate-resolution validation",
            "",
            f"Date: {date.today().isoformat()}",
            f"Fixed seed: `{args.seed}`",
            f"Original seeded tickers: `{', '.join(original_sample)}`",
            f"Additional seeded tickers: `{', '.join(additional_sample)}`",
            f"All 40 validation tickers: `{', '.join(tickers)}`",
            f"All sample statements resolved cleanly: `{'YES' if clean else 'NO'}`",
            "",
            "This one-off probe used the supported public `vnstock.api.Finance` VCI",
            "quarterly balance-sheet interface. It did not run under pytest.",
            "",
            "## Tóm tắt đơn giản cho chủ project",
            "",
            f"- Đã chạy kiểm chứng thật cho {len(records)} mã; nguồn dữ liệu trả lời đủ cả {len(records)} mã.",
            f"- Có {resolved_count} mã phân biệt được rõ ràng và {len(ambiguous_tickers)} mã còn mơ hồ.",
            f"- Coverage xử lý trùng trong nhóm kiểm chứng: {resolved_count}/{len(records)} = {validation_resolution_coverage:.2%}; thấp hơn mốc 90%.",
            f"- Các mã mơ hồ: `{', '.join(ambiguous_tickers) or 'NONE'}`.",
            "- Mơ hồ nghĩa là các con số chưa tạo khoảng cách đủ lớn để hệ thống chọn an toàn; hệ thống đã dừng ở các mã đó thay vì đoán.",
            "- Ngưỡng 1% / 3 kỳ / 5 lần được giữ nguyên; không có điều chỉnh để làm đẹp kết quả.",
            "- Sau bước này, coverage toàn thị trường được tính riêng theo danh sách REQUIRED_ITEMS đầy đủ.",
            "",
            "## Summary",
            "",
            *summary_rows,
            "",
            "## Coverage gate",
            "",
            f"Duplicate-resolution validation coverage: {resolved_count}/{len(records)} = {validation_resolution_coverage:.2%} (below 90%).",
            "The complete Sprint 4-6 REQUIRED_ITEMS list is not yet present in the repository, so a full-universe complete-whitelist percentage cannot be computed without inventing an unapproved mapping. See `docs/COVERAGE_SPRINT_3.md`.",
            "",
            *sections,
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding="utf-8")
    (args.output.with_suffix(".json")).write_text(
        json.dumps(
            {
                "seed": args.seed,
                "original_sample": original_sample,
                "additional_sample": additional_sample,
                "sample": sample,
                "tickers": tickers,
                "clean": clean,
                "validation_resolution_coverage": validation_resolution_coverage,
                "records": records,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Report: {args.output.resolve()}")
    return 0 if clean else 2


if __name__ == "__main__":
    raise SystemExit(main())
