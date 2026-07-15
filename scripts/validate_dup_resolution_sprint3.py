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
    parser.add_argument("--sample-size", type=int, default=20)
    parser.add_argument("--min-sleep", type=float, default=2.8)
    parser.add_argument("--max-sleep", type=float, default=3.6)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs" / "VALIDATE_DUP_RESOLUTION_SPRINT_3.md",
    )
    return parser.parse_args(argv)


def choose_sample(seed: int, sample_size: int) -> list[str]:
    universe = pd.read_csv(ROOT / "data" / "universe.csv")
    eligible = universe[
        universe["status"].eq("ACCEPTED")
        & ~universe["exchange"].eq("UPCOM")
        & ~universe["icb2"].isin(FINANCIAL_ICB2)
        & ~universe["ticker"].isin(CORE_TICKERS)
    ]
    tickers = sorted(eligible["ticker"].astype(str).unique())
    if len(tickers) < sample_size:
        raise ValueError(f"only {len(tickers)} eligible tickers for sample size {sample_size}")
    return random.Random(seed).sample(tickers, sample_size)


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
    sample = choose_sample(args.seed, args.sample_size)
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
        status = "AMBIGUOUS" if audit.get("ambiguous") else ("RESOLVED" if result.ok else "API_ERROR")
        record = {
            "ticker": ticker,
            "status": status,
            "data_status": result.status,
            "flags": audit.get("flags", []),
            "preferred_values": preferred_event.get("resolved_values"),
            "identity_candidates": identity_event.get("candidates", []),
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
            ]
        )

    clean = all(record["status"] == "RESOLVED" for record in records)
    resolved_count = sum(record["status"] == "RESOLVED" for record in records)
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
            f"Seeded random tickers: `{', '.join(sample)}`",
            f"All sample statements resolved cleanly: `{'YES' if clean else 'NO'}`",
            "",
            "This one-off probe used the supported public `vnstock.api.Finance` VCI",
            "quarterly balance-sheet interface. It did not run under pytest.",
            "",
            "## Tóm tắt đơn giản cho chủ project",
            "",
            f"- Đã chạy kiểm chứng thật cho {len(records)} mã; nguồn dữ liệu trả lời đủ cả {len(records)} mã.",
            f"- Có {resolved_count} mã phân biệt được rõ ràng và {len(ambiguous_tickers)} mã còn mơ hồ.",
            f"- Các mã mơ hồ: `{', '.join(ambiguous_tickers) or 'NONE'}`.",
            "- Mơ hồ nghĩa là các con số chưa tạo khoảng cách đủ lớn để hệ thống chọn an toàn; hệ thống đã dừng ở các mã đó thay vì đoán.",
            "- Vì mẫu chưa sạch, chưa được phép tính coverage toàn thị trường và không thay đổi ngưỡng 1% / 3 kỳ / 5 lần.",
            "- Việc còn lại: chủ project xem kết quả và quyết định hướng xử lý cho các mã mơ hồ. Sprint 3 chưa đạt điểm hoàn thành 90% trong lần chạy này.",
            "",
            "## Summary",
            "",
            *summary_rows,
            "",
            "## Coverage gate",
            "",
            (
                "The sample resolved cleanly; full whitelist coverage may now be recomputed."
                if clean
                else "STOP: the sample did not resolve cleanly, so full whitelist coverage was not recomputed and no threshold was changed."
            ),
            "",
            *sections,
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding="utf-8")
    (args.output.with_suffix(".json")).write_text(
        json.dumps(
            {"seed": args.seed, "sample": sample, "clean": clean, "records": records},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Report: {args.output.resolve()}")
    return 0 if clean else 2


if __name__ == "__main__":
    raise SystemExit(main())
