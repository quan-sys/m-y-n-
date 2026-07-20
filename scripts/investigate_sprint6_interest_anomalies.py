"""Classify all Sprint 5 interest anomalies using preserved local rows only."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sys
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPORT = ROOT / "docs" / "REPORT_SPRINT_5_VALUATION.md"
FUNDAMENTALS_ROOT = ROOT / "data" / "fundamentals"
OUTPUT_PATH = ROOT / "docs" / "SPRINT_6_INTEREST_ANOMALY_INVESTIGATION.md"
EXPECTED_ROWS = 44
ITEM_IDS = ("interest_expenses", "financial_expenses", "financial_income")
LABELS = (
    "NET_PRESENTATION_SUSPECTED",
    "PROVIDER_FIELD_SUSPECTED",
    "UNEXPLAINED",
)


def parse_anomaly_rows(report_text: str) -> list[dict[str, Any]]:
    try:
        section = report_text.split("## Interest-expense anomaly log", 1)[1].split(
            "## Tests and limitations", 1
        )[0]
    except IndexError as exc:
        raise ValueError("Sprint 5 anomaly table section is missing") from exc
    rows: list[dict[str, Any]] = []
    for line in section.splitlines():
        if not line.startswith("| ") or line.startswith("| ticker") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 7 or not re.fullmatch(r"[A-Z0-9]+", cells[0]):
            continue
        rows.append(
            {
                "ticker": cells[0],
                "report_period": cells[1],
                "reported_interest_raw": int(cells[2]),
                "reported_financial_expenses_raw": int(cells[4]),
            }
        )
    if len(rows) != EXPECTED_ROWS:
        raise ValueError(f"expected {EXPECTED_ROWS} anomaly rows; found {len(rows)}")
    if len({(row['ticker'], row['report_period']) for row in rows}) != EXPECTED_ROWS:
        raise ValueError("anomaly table contains duplicate ticker-period rows")
    return rows


def _latest_quarter_cache(ticker: str) -> tuple[Path, Path]:
    normalized = sorted(
        (FUNDAMENTALS_ROOT / ticker / "income_statement" / "quarter").glob(
            "*/*/normalized.parquet"
        )
    )
    if not normalized:
        raise FileNotFoundError(f"no local quarterly income cache for {ticker}")
    normalized_path = normalized[-1]
    raw_path = normalized_path.with_name("raw.parquet")
    if not raw_path.exists():
        raise FileNotFoundError(f"raw local cache missing for {ticker}: {raw_path}")
    return normalized_path, raw_path


def _integer(value: Any) -> int:
    numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric):
        raise ValueError(f"non-numeric local evidence: {value!r}")
    return int(round(float(numeric)))


def investigate_row(anomaly: dict[str, Any]) -> dict[str, Any]:
    ticker = anomaly["ticker"]
    period = anomaly["report_period"]
    normalized_path, raw_path = _latest_quarter_cache(ticker)
    normalized = pd.read_parquet(normalized_path)
    raw = pd.read_parquet(raw_path)
    normalized_period = normalized.loc[
        normalized["report_period"].astype(str).eq(period)
        & normalized["item_id"].astype(str).isin(ITEM_IDS)
    ]
    raw_period_column = period[:4] + "-Q" + period[-1]
    if raw_period_column not in raw.columns:
        raise ValueError(f"raw period {raw_period_column} missing for {ticker}")

    raw_values: dict[str, int] = {}
    normalized_values: dict[str, int] = {}
    verbatim_labels: list[str] = []
    for item_id in ITEM_IDS:
        raw_matches = raw.loc[raw["item_id"].astype(str).eq(item_id)]
        normalized_matches = normalized_period.loc[
            normalized_period["item_id"].astype(str).eq(item_id)
        ]
        if len(raw_matches) != 1 or len(normalized_matches) != 1:
            raise ValueError(f"expected one {item_id} row for {ticker} {period}")
        raw_row = raw_matches.iloc[0]
        normalized_row = normalized_matches.iloc[0]
        raw_values[item_id] = _integer(raw_row[raw_period_column])
        normalized_values[item_id] = _integer(normalized_row["value"])
        verbatim_labels.append(
            f'"{raw_row["item"]}" / "{raw_row["item_en"]}" / item_id={item_id}'
        )

    if raw_values["interest_expenses"] != anomaly["reported_interest_raw"]:
        raise ValueError(f"Sprint 5 interest value mismatch for {ticker} {period}")
    if (
        raw_values["financial_expenses"]
        != anomaly["reported_financial_expenses_raw"]
    ):
        raise ValueError(f"Sprint 5 financial-expense value mismatch for {ticker} {period}")

    provider_mismatch = any(
        raw_values[item_id] != normalized_values[item_id]
        for item_id in ("interest_expenses", "financial_expenses")
    )
    interest = raw_values["interest_expenses"]
    financial_expenses = raw_values["financial_expenses"]
    if provider_mismatch:
        label = "PROVIDER_FIELD_SUSPECTED"
        rationale = (
            "Raw and normalized values differ for at least one tested field; the local "
            "provider-to-normalized mapping is therefore suspected."
        )
    elif interest * financial_expenses > 0:
        label = "NET_PRESENTATION_SUSPECTED"
        rationale = (
            "Raw equals normalized; interest_expenses and financial_expenses have the "
            "same non-zero sign while abs(interest_expenses) exceeds "
            "abs(financial_expenses). This is consistent with, but does not prove, a "
            "net presentation."
        )
    else:
        label = "UNEXPLAINED"
        rationale = (
            "Raw equals normalized, but interest_expenses and financial_expenses have "
            "opposite signs; no local annotation explains the relationship."
        )
    if label not in LABELS:
        raise AssertionError(f"unsupported label: {label}")
    return {
        "ticker": ticker,
        "report_period": period,
        "interest_expenses_raw": interest,
        "financial_expenses_raw": financial_expenses,
        "financial_income_raw": raw_values["financial_income"],
        "interest_expenses_normalized": normalized_values["interest_expenses"],
        "financial_expenses_normalized": normalized_values["financial_expenses"],
        "raw_labels_verbatim": "; ".join(verbatim_labels),
        "raw_source_path": raw_path.relative_to(ROOT).as_posix(),
        "normalized_source_path": normalized_path.relative_to(ROOT).as_posix(),
        "label": label,
        "local_rationale": rationale,
    }


def investigate() -> list[dict[str, Any]]:
    anomalies = parse_anomaly_rows(SOURCE_REPORT.read_text(encoding="utf-8"))
    investigated = [investigate_row(row) for row in anomalies]
    if len(investigated) != EXPECTED_ROWS:
        raise AssertionError("investigation did not preserve all anomaly rows")
    if any(row["label"] not in LABELS for row in investigated):
        raise AssertionError("every anomaly must have exactly one approved label")
    return investigated


def render_report(rows: list[dict[str, Any]]) -> str:
    counts = Counter(row["label"] for row in rows)
    lines = [
        "# Sprint 6 local interest-expense anomaly investigation",
        "",
        "This investigation reads only preserved local raw and normalized quarterly fundamentals. It makes no API call and asserts no external fact.",
        "",
        f"- Total anomaly rows: `{len(rows)}`.",
        f"- Affected tickers: `{len({row['ticker'] for row in rows})}`.",
        f"- `NET_PRESENTATION_SUSPECTED`: `{counts['NET_PRESENTATION_SUSPECTED']}`.",
        f"- `PROVIDER_FIELD_SUSPECTED`: `{counts['PROVIDER_FIELD_SUSPECTED']}`.",
        f"- `UNEXPLAINED`: `{counts['UNEXPLAINED']}`.",
        "",
        "`NET_PRESENTATION_SUSPECTED` means the same-sign raw fields are locally consistent with a net presentation; it is not a claim about the issuer or provider. `PROVIDER_FIELD_SUSPECTED` requires a raw-versus-normalized mismatch. `UNEXPLAINED` means the local cache has no adequate explanation.",
        "",
        "| ticker | period | interest raw | financial expenses raw | financial income raw | interest normalized | financial expenses normalized | raw labels quoted verbatim | local source | label | local evidence conclusion |",
        "|---|---|---:|---:|---:|---:|---:|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {ticker} | {report_period} | {interest_expenses_raw} | "
            "{financial_expenses_raw} | {financial_income_raw} | "
            "{interest_expenses_normalized} | {financial_expenses_normalized} | "
            "{raw_labels_verbatim} | `{raw_source_path}`; `{normalized_source_path}` | "
            "{label} | {local_rationale} |".format(**row)
        )
    unexplained = [row for row in rows if row["label"] == "UNEXPLAINED"]
    lines.extend(
        [
            "",
            "## Rows requiring owner-led external verification",
            "",
        ]
    )
    if unexplained:
        lines.extend(
            f"- `{row['ticker']} {row['report_period']}`: local raw and normalized fields match, but the interest-expense and financial-expense signs conflict; verify against the issuer's filed statement/notes or another owner-approved external source."
            for row in unexplained
        )
    else:
        lines.append("- `NONE`.")
    lines.extend(
        [
            "",
            "Any future formula consuming `financial_expenses` is blocked for a ticker-quarter that remains `UNEXPLAINED`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rows = investigate()
    OUTPUT_PATH.write_text(render_report(rows), encoding="utf-8")
    counts = Counter(row["label"] for row in rows)
    print(f"rows={len(rows)}; tickers={len({row['ticker'] for row in rows})}")
    print(
        "labels="
        + ";".join(f"{label}:{counts[label]}" for label in LABELS)
    )
    print(
        "external_verification="
        + "|".join(
            f"{row['ticker']}:{row['report_period']}"
            for row in rows
            if row["label"] == "UNEXPLAINED"
        )
    )
    print("network_calls=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
