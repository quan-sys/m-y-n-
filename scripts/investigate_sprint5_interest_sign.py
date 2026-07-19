from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd


TICKERS = ("HAG", "IDI", "DTD")
ITEM_IDS = (
    "interest_expenses",
    "financial_expenses",
    "financial_income",
    "net_accounting_profit_loss_before_tax",
)


def classify_positive_interest(
    *, raw_value: float, normalized_value: float, confirmation_evidence: str = ""
) -> str:
    if raw_value <= 0:
        raise ValueError("classification applies only to positive interest_expenses")
    if raw_value != normalized_value:
        raise ValueError("raw/normalized mismatch requires separate exact evidence")
    if confirmation_evidence:
        if confirmation_evidence == "PROVIDER_SIGN_REVERSAL_CONFIRMED":
            return confirmation_evidence
        if confirmation_evidence == "ACCOUNTING_REVERSAL_OR_CREDIT_CONFIRMED":
            return confirmation_evidence
        raise ValueError("unsupported confirmation evidence")
    return "SOURCE_AMBIGUOUS"


def _latest_cache(ticker: str, cache_root: Path) -> tuple[Path, Path]:
    candidates = sorted(
        (cache_root / ticker / "income_statement" / "quarter").glob("*/*/normalized.parquet")
    )
    if not candidates:
        raise FileNotFoundError(f"no cached quarterly income statement for {ticker}")
    normalized_path = candidates[-1]
    raw_path = normalized_path.with_name("raw.parquet")
    if not raw_path.exists():
        raise FileNotFoundError(f"raw cache missing for {ticker}: {raw_path}")
    return normalized_path, raw_path


def _raw_period_column(report_period: str) -> str:
    return report_period[:4] + "-Q" + report_period[-1]


def investigate(cache_root: Path) -> tuple[list[dict[str, Any]], dict[str, str]]:
    evidence: list[dict[str, Any]] = []
    ticker_classifications: dict[str, str] = {}
    for ticker in TICKERS:
        normalized_path, raw_path = _latest_cache(ticker, cache_root)
        normalized = pd.read_parquet(normalized_path)
        raw = pd.read_parquet(raw_path)
        periods = sorted(normalized["report_period"].dropna().unique(), reverse=True)[:4]
        positive_classes: list[str] = []
        for report_period in periods:
            period_rows = normalized[normalized["report_period"].eq(report_period)]
            normalized_by_item = period_rows.set_index("item_id")
            raw_column = _raw_period_column(report_period)
            values: dict[str, float] = {}
            raw_rows: dict[str, pd.Series] = {}
            for item_id in ITEM_IDS:
                normalized_row = normalized_by_item.loc[item_id]
                raw_row = raw.loc[raw["item_id"].eq(item_id)].iloc[0]
                values[item_id] = float(raw_row[raw_column])
                raw_rows[item_id] = raw_row
                normalized_value = float(normalized_row["value"])
                if values[item_id] != normalized_value:
                    raise ValueError(
                        f"raw/normalized mismatch: {ticker} {report_period} {item_id}"
                    )
            interest = values["interest_expenses"]
            financial_expenses = values["financial_expenses"]
            sign_relationship = (
                f"interest={'POSITIVE' if interest > 0 else 'NEGATIVE' if interest < 0 else 'ZERO'}; "
                f"financial_expenses={'POSITIVE' if financial_expenses > 0 else 'NEGATIVE' if financial_expenses < 0 else 'ZERO'}; "
                "raw_equals_normalized=YES"
            )
            classification = "NOT_APPLICABLE"
            if interest > 0:
                classification = classify_positive_interest(
                    raw_value=interest,
                    normalized_value=float(normalized_by_item.loc["interest_expenses", "value"]),
                )
                positive_classes.append(classification)
            interest_raw = raw_rows["interest_expenses"]
            evidence.append(
                {
                    "ticker": ticker,
                    "report_period": report_period,
                    "available_from": str(
                        normalized_by_item.loc["interest_expenses", "available_from"]
                    )[:10],
                    "interest_expenses_raw_value": int(interest),
                    "interest_expenses_item_name": str(interest_raw["item"]),
                    "financial_expenses_raw_value": int(values["financial_expenses"]),
                    "financial_income_raw_value": int(values["financial_income"]),
                    "net_accounting_profit_loss_before_tax_raw_value": int(
                        values["net_accounting_profit_loss_before_tax"]
                    ),
                    "source_cache_path": raw_path.as_posix(),
                    "raw_source_label": (
                        f"{interest_raw['item']} / {interest_raw['item_en']} / "
                        f"item_id={interest_raw['item_id']}"
                    ),
                    "sign_relationship": sign_relationship,
                    "positive_observation_classification": classification,
                }
            )
        ticker_classifications[ticker] = (
            "SOURCE_AMBIGUOUS"
            if "SOURCE_AMBIGUOUS" in positive_classes
            else positive_classes[0]
            if positive_classes
            else "NO_POSITIVE_OBSERVATION"
        )
    return evidence, ticker_classifications


def render_report(evidence: list[dict[str, Any]], classifications: dict[str, str]) -> str:
    lines = [
        "# Sprint 5 interest-expense sign investigation",
        "",
        "This investigation reads the preserved raw and normalized quarterly cache only; it makes no API call and changes no financial formula.",
        "",
        "| ticker | report_period | available_from | interest_expenses raw value | interest_expenses item_name | financial_expenses raw value | financial_income raw value | net_accounting_profit_loss_before_tax raw value | source cache path | raw source label | sign relationship | classification |",
        "|---|---|---|---:|---|---:|---:|---:|---|---|---|---|",
    ]
    for row in evidence:
        lines.append(
            "| {ticker} | {report_period} | {available_from} | {interest_expenses_raw_value} | "
            "{interest_expenses_item_name} | {financial_expenses_raw_value} | "
            "{financial_income_raw_value} | {net_accounting_profit_loss_before_tax_raw_value} | "
            "`{source_cache_path}` | {raw_source_label} | {sign_relationship} | "
            "{positive_observation_classification} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Classification",
            "",
            *[f"- {ticker}: `{classifications[ticker]}`" for ticker in TICKERS],
            "",
            "The raw provider rows and normalized rows are identical for every displayed value. The stored evidence contains no annotation proving a provider sign reversal or an accounting reversal/credit. Therefore every positive observation is `SOURCE_AMBIGUOUS`; no `CONFIRMED` label is justified.",
            "",
            "EBIT sign gate: `INTEREST_EXPENSE_SIGN_AMBIGUOUS`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-root", type=Path, default=Path("data/fundamentals"))
    parser.add_argument(
        "--output", type=Path, default=Path("docs/SPRINT_5_INTEREST_SIGN_INVESTIGATION.md")
    )
    args = parser.parse_args()
    evidence, classifications = investigate(args.cache_root)
    args.output.write_text(render_report(evidence, classifications), encoding="utf-8")
    print(f"rows={len(evidence)}")
    print("classifications=" + ",".join(f"{key}:{value}" for key, value in classifications.items()))
    print("ebit_sign_gate=INTEREST_EXPENSE_SIGN_AMBIGUOUS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
