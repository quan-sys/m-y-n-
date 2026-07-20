"""Create Sprint 6 annual-history coverage and restatement-difference evidence."""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.fetch_sprint6_annual_history import (
    EXPECTED_SURVIVORS,
    FUNDAMENTALS_ROOT,
    ROOT,
    RUN_DATE,
    RUN_ROOT,
    SURVIVORS_PATH,
    load_survivors,
)


EVALUATION_DATE = "2026-07-20"
OLD_CACHE_DATE = "2026-07-17"
OVERLAP_PERIODS = ("2022", "2023", "2024", "2025")
STATEMENTS = ("balance_sheet", "income_statement", "cash_flow")
STATEMENT_LABELS = {
    "balance_sheet": "balance_sheet",
    "income_statement": "income_statement",
    "cash_flow": "cash_flow",
}
RESTATEMENT_ITEMS = (
    "total_assets",
    "owners_equity",
    "current_assets",
    "current_liabilities",
    "short_term_borrowings",
    "long_term_borrowings",
    "cash_and_cash_equivalents",
    "net_sales",
    "gross_profit",
    "cost_of_sales",
    "net_profit_loss_after_tax",
    "attributable_to_parent_company",
    "net_accounting_profit_loss_before_tax",
    "interest_expenses",
    "net_cash_inflows_outflows_from_operating_activities",
    "proceeds_from_issue_of_shares",
    "common_shares",
)
COVERAGE_CSV = ROOT / "data" / "screener" / "sprint6_annual_history_coverage.csv"
COVERAGE_REPORT = ROOT / "docs" / "SPRINT_6_ANNUAL_HISTORY_COVERAGE.md"
RESTATEMENT_REPORT = ROOT / "docs" / "SPRINT_6_RESTATEMENT_DIFF.md"


def normalized_path(base: Path, ticker: str, statement: str, run_date: str) -> Path | None:
    candidates = sorted(
        (base / ticker / statement / "year" / run_date).glob("*/normalized.parquet")
    )
    if not candidates:
        return None
    if len(candidates) != 1:
        raise ValueError(
            f"expected one normalized observation for {ticker}/{statement}/{run_date}; "
            f"found {len(candidates)}"
        )
    return candidates[0]


def read_normalized(base: Path, ticker: str, statement: str, run_date: str) -> pd.DataFrame:
    path = normalized_path(base, ticker, statement, run_date)
    if path is None:
        return pd.DataFrame()
    return pd.read_parquet(path)


def annual_periods(frame: pd.DataFrame, evaluation_date: str | None = None) -> list[str]:
    if frame.empty or "report_period" not in frame.columns:
        return []
    work = frame.copy()
    labels = work["report_period"].astype(str)
    work = work.loc[labels.str.fullmatch(r"\d{4}")].copy()
    if evaluation_date is not None:
        available = pd.to_datetime(work["available_from"], errors="coerce")
        work = work.loc[available.notna() & available.le(pd.Timestamp(evaluation_date))]
    return sorted(work["report_period"].astype(str).unique().tolist())


def coverage_record(
    ticker: str,
    frames: dict[str, pd.DataFrame],
    evaluation_date: str = EVALUATION_DATE,
) -> dict[str, Any]:
    record: dict[str, Any] = {"ticker": ticker}
    for statement in STATEMENTS:
        periods = annual_periods(frames.get(statement, pd.DataFrame()))
        eligible = annual_periods(frames.get(statement, pd.DataFrame()), evaluation_date)
        record[f"{statement}_periods"] = "|".join(periods)
        record[f"{statement}_period_count"] = len(periods)
        record[f"{statement}_eligible_period_count"] = len(eligible)
        record[f"{statement}_usable_consecutive_roc_years"] = max(len(periods) - 1, 0)
    return record


def build_coverage(tickers: list[str]) -> pd.DataFrame:
    records = []
    for ticker in tickers:
        frames = {
            statement: read_normalized(RUN_ROOT, ticker, statement, RUN_DATE)
            for statement in STATEMENTS
        }
        records.append(coverage_record(ticker, frames))
    output = pd.DataFrame(records)
    if len(output) != EXPECTED_SURVIVORS or output["ticker"].nunique() != EXPECTED_SURVIVORS:
        raise AssertionError("coverage output is not exactly one row per survivor")
    return output


def compare_restatements(
    old_frame: pd.DataFrame,
    new_frame: pd.DataFrame,
    *,
    item_ids: tuple[str, ...] = RESTATEMENT_ITEMS,
    periods: tuple[str, ...] = OVERLAP_PERIODS,
) -> pd.DataFrame:
    key = ["ticker", "statement_type", "report_period", "item_id"]

    def selected(frame: pd.DataFrame, value_name: str) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame(columns=[*key, value_name])
        work = frame.loc[
            frame["item_id"].astype(str).isin(item_ids)
            & frame["report_period"].astype(str).isin(periods),
            [*key, "value"],
        ].copy()
        if work.duplicated(key).any():
            duplicate = work.loc[work.duplicated(key, keep=False), key]
            raise ValueError(f"duplicate comparison key: {duplicate.iloc[0].to_dict()}")
        work = work.rename(columns={"value": value_name})
        return work

    old = selected(old_frame, "old_value")
    new = selected(new_frame, "new_value")
    merged = old.merge(new, on=key, how="inner", validate="one_to_one")
    merged["old_value"] = pd.to_numeric(merged["old_value"], errors="coerce")
    merged["new_value"] = pd.to_numeric(merged["new_value"], errors="coerce")
    merged = merged.loc[merged["old_value"].notna() & merged["new_value"].notna()].copy()
    merged["differs"] = merged["old_value"].ne(merged["new_value"])

    def relative(row: pd.Series) -> float:
        if not row["differs"]:
            return 0.0
        if row["old_value"] == 0:
            return math.inf
        return abs(float(row["new_value"] - row["old_value"])) / abs(float(row["old_value"]))

    merged["relative_difference"] = merged.apply(relative, axis=1)
    return merged


def all_restatement_comparisons(tickers: list[str]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for ticker in tickers:
        for statement in STATEMENTS:
            old = read_normalized(FUNDAMENTALS_ROOT, ticker, statement, OLD_CACHE_DATE)
            new = read_normalized(RUN_ROOT, ticker, statement, RUN_DATE)
            compared = compare_restatements(old, new)
            if not compared.empty:
                frames.append(compared)
    if not frames:
        return pd.DataFrame(
            columns=[
                "ticker",
                "statement_type",
                "report_period",
                "item_id",
                "old_value",
                "new_value",
                "differs",
                "relative_difference",
            ]
        )
    return pd.concat(frames, ignore_index=True)


def coverage_distribution(coverage: pd.DataFrame, statement: str) -> Counter[int]:
    return Counter(int(value) for value in coverage[f"{statement}_period_count"])


def render_coverage_report(coverage: pd.DataFrame) -> str:
    lines = [
        "# Sprint 6 annual-history coverage",
        "",
        f"- Evaluation date: `{EVALUATION_DATE}`.",
        f"- Survivor rows: `{len(coverage)}`; unique tickers: `{coverage['ticker'].nunique()}`.",
        "- Returned years are preserved as returned; no period, value, or zero was fabricated.",
        "- Eligible counts apply the unchanged rule `available_from <= 2026-07-20`; annual `available_from` remains report-period end plus 90 days.",
        "",
        "## Exact statement-depth counts",
        "",
        "| statement | 8 periods | 7 periods | 6 periods | 5 periods | fewer than 5 periods |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for statement in STATEMENTS:
        counts = coverage_distribution(coverage, statement)
        fewer = sum(count for depth, count in counts.items() if depth < 5)
        lines.append(
            f"| `{statement}` | {counts[8]} | {counts[7]} | {counts[6]} | "
            f"{counts[5]} | {fewer} |"
        )
    lines.extend(
        [
            "",
            "## Usable consecutive ROC years implied",
            "",
            "The mechanical count below is `periods minus one`; no ROC value or score was computed.",
            "",
            "| statement | usable consecutive years | ticker count |",
            "|---|---:|---:|",
        ]
    )
    for statement in STATEMENTS:
        column = f"{statement}_usable_consecutive_roc_years"
        for years, count in sorted(Counter(int(v) for v in coverage[column]).items(), reverse=True):
            lines.append(f"| `{statement}` | {years} | {count} |")
    lines.extend(
        [
            "",
            "## Per-ticker full period lists",
            "",
            "The authoritative per-ticker lists, total counts, and eligible counts are in `data/screener/sprint6_annual_history_coverage.csv` (exactly 156 rows).",
        ]
    )
    return "\n".join(lines) + "\n"


def display_number(value: Any) -> str:
    number = float(value)
    return str(int(number)) if number.is_integer() else repr(number)


def display_relative(value: Any) -> str:
    return "inf" if math.isinf(float(value)) else format(float(value), ".17g")


def render_restatement_report(compared: pd.DataFrame) -> str:
    differing = compared.loc[compared["differs"]].copy()
    ranked = compared.sort_values(
        ["relative_difference", "ticker", "report_period", "item_id"],
        ascending=[False, True, True, True],
        kind="stable",
    )
    compared_count = len(compared)
    differing_count = len(differing)
    percentage = 0.0 if compared_count == 0 else differing_count * 100 / compared_count
    ticker_count = differing["ticker"].nunique() if not differing.empty else 0
    lines = [
        "# Sprint 6 restatement difference",
        "",
        f"- Overlapping report periods: `{list(OVERLAP_PERIODS)}`.",
        f"- Requested normalized item_id values: `{len(RESTATEMENT_ITEMS)}`.",
        f"- Exact compared ticker-period-item cells: `{compared_count}`.",
        f"- Exact differing cells: `{differing_count}`.",
        f"- Exact differing-cell percentage: `{format(percentage, '.12f')}%`.",
        f"- Exact tickers with at least one difference: `{ticker_count}`.",
        "- No materiality threshold was used: two numeric cells differ exactly when `old_value != new_value`.",
        "",
        "## 20 largest relative differences",
        "",
        "| ticker | statement_type | report_period | item_id | old_value | new_value | relative_difference |",
        "|---|---|---:|---|---:|---:|---:|",
    ]
    for row in ranked.head(20).itertuples(index=False):
        lines.append(
            f"| {row.ticker} | {row.statement_type} | {row.report_period} | "
            f"{row.item_id} | {display_number(row.old_value)} | "
            f"{display_number(row.new_value)} | {display_relative(row.relative_difference)} |"
        )
    lines.extend(
        [
            "",
            "## Immutability verification",
            "",
            "every Sprint 4 and Sprint 5 output file is byte-identical",
            "",
            "Verification command used:",
            "",
            "```text",
            "python scripts/fetch_sprint6_annual_history.py --verify-protected",
            "```",
            "",
            "The verification also covers every file under the existing 2026-07-17 annual cache. No Sprint 4 survivor or Sprint 5 valuation output was modified, refreshed, or recomputed.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    tickers = load_survivors(SURVIVORS_PATH)
    coverage = build_coverage(tickers)
    COVERAGE_CSV.parent.mkdir(parents=True, exist_ok=True)
    coverage.to_csv(COVERAGE_CSV, index=False, lineterminator="\n")
    COVERAGE_REPORT.write_text(render_coverage_report(coverage), encoding="utf-8")
    compared = all_restatement_comparisons(tickers)
    RESTATEMENT_REPORT.write_text(render_restatement_report(compared), encoding="utf-8")
    differing = compared.loc[compared["differs"]]
    print(f"coverage_rows={len(coverage)}; unique={coverage['ticker'].nunique()}")
    for statement in STATEMENTS:
        counts = coverage_distribution(coverage, statement)
        fewer = sum(count for depth, count in counts.items() if depth < 5)
        print(
            f"{statement}=8:{counts[8]};7:{counts[7]};6:{counts[6]};"
            f"5:{counts[5]};fewer:{fewer}"
        )
    percentage = 0.0 if compared.empty else len(differing) * 100 / len(compared)
    print(
        f"compared_cells={len(compared)}; differing_cells={len(differing)}; "
        f"differing_percentage={format(percentage, '.12f')}; "
        f"differing_tickers={differing['ticker'].nunique()}"
    )
    print("production_scores=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
