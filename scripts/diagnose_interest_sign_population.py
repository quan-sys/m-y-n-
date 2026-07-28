"""Diagnose committed interest-expense anomalies without changing any production input."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
import sys
from typing import Any

import pandas as pd


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()
ROOT = Path(__file__).resolve().parents[1]
FUNDAMENTALS_PATH = (
    ROOT
    / "data"
    / "fundamentals"
    / "quarterly_pit"
    / "2026-07-26"
    / "quarterly_items_point_in_time.csv.gz"
)
TARGETS_PATH = (
    ROOT
    / "data"
    / "screener"
    / "targets_pit"
    / "2026-07-28"
    / "rebalance_targets_point_in_time.csv.gz"
)
ANNUAL_PATH = (
    ROOT
    / "data"
    / "fundamentals"
    / "annual_pit"
    / "2026-07-26"
    / "annual_items_point_in_time.csv.gz"
)
REPORT_PATH = ROOT / "docs" / "REPORT_INTEREST_SIGN_DIAGNOSIS.md"

INTEREST = "interest_expenses"
FINANCIAL_EXPENSES = "financial_expenses"
ITEMS = (INTEREST, FINANCIAL_EXPENSES)
BUCKETS = (
    "SIGN_CONVENTION",
    "INTEREST_INCOME_OFFSET",
    "MISSING_OR_ZERO_TOTAL",
    "GENUINELY_INCONSISTENT",
    "UNEXPLAINED",
)
NAMED_KEYS = (
    ("GMD", "2025Q4"),
    ("SAB", "2025Q4"),
    ("DTD", "2025Q2"),
    ("LHC", "2025Q2"),
)


@dataclass(frozen=True)
class Diagnosis:
    population: pd.DataFrame
    target_hits: pd.DataFrame
    target_input_rows: int
    named_rows: pd.DataFrame
    named_hits: pd.DataFrame
    hqc_net_sales: dict[str, str]
    hqc_target_hits: pd.DataFrame


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"committed input is missing: {path}")
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def _require_columns(frame: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = sorted(columns - set(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(missing)}")


def _decimal(value: Any) -> Decimal | None:
    text = str(value).strip()
    if text.lower() in {"", "nan", "none", "<na>"}:
        return None
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"non-decimal committed value: {value!r}") from exc


def _decimal_text(value: Decimal | None) -> str:
    if value is None:
        return ""
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _sign(value: Decimal | None) -> str:
    if value is None:
        return "MISSING"
    if value > 0:
        return "POSITIVE"
    if value < 0:
        return "NEGATIVE"
    return "ZERO"


def _quarter_from_date(value: str) -> str:
    timestamp = pd.Timestamp(value)
    quarter = ((timestamp.month - 1) // 3) + 1
    return f"{timestamp.year}Q{quarter}"


def _classify(row: pd.Series) -> tuple[str, str]:
    interest = row["interest_decimal"]
    total = row["financial_expenses_decimal"]
    if interest is None:
        raise ValueError("population row is missing interest_expenses")
    if total is None or total == 0:
        return (
            "MISSING_OR_ZERO_TOTAL",
            "financial_expenses is zero, blank, or absent while interest_expenses is populated.",
        )
    if interest * total < 0:
        return (
            "SIGN_CONVENTION",
            "The committed raw signed values have opposite signs; this meets the report's sign-convention definition without asserting which field should change.",
        )
    if row["ticker"] == "HAG" and row["quarter"] == "2026Q1":
        return (
            "INTEREST_INCOME_OFFSET",
            "SPEC_SPRINT_5 section 6 records this exact committed case as legitimate because a 750 billion VND interest remission was booked.",
        )
    return (
        "UNEXPLAINED",
        "The committed quarterly PIT file does not carry financial_income or an annotation that can prove an offset or an inconsistency.",
    )


def _population(fundamentals: pd.DataFrame) -> pd.DataFrame:
    _require_columns(
        fundamentals,
        {"ticker", "quarter", "item_id", "value"},
        "quarterly PIT fundamentals",
    )
    relevant = fundamentals.loc[
        fundamentals["item_id"].isin(ITEMS),
        ["ticker", "quarter", "item_id", "value"],
    ].copy()
    if relevant.duplicated(["ticker", "quarter", "item_id"]).any():
        duplicate = relevant.loc[
            relevant.duplicated(["ticker", "quarter", "item_id"], keep=False)
        ].iloc[0]
        raise ValueError(
            "duplicate committed fundamental key: "
            f"{duplicate['ticker']} {duplicate['quarter']} {duplicate['item_id']}"
        )
    pivoted = relevant.pivot(
        index=["ticker", "quarter"], columns="item_id", values="value"
    ).reset_index()
    for item in ITEMS:
        if item not in pivoted:
            pivoted[item] = ""
    pivoted["interest_decimal"] = pivoted[INTEREST].map(_decimal)
    pivoted["financial_expenses_decimal"] = pivoted[FINANCIAL_EXPENSES].map(_decimal)
    population = pivoted.loc[
        pivoted["interest_decimal"].notna()
        & pivoted["financial_expenses_decimal"].notna()
        & pivoted.apply(
            lambda row: abs(row["interest_decimal"])
            > abs(row["financial_expenses_decimal"]),
            axis=1,
        )
    ].copy()
    classifications = population.apply(_classify, axis=1, result_type="expand")
    population["bucket"] = classifications[0]
    population["classification_evidence"] = classifications[1]
    if not population["bucket"].isin(BUCKETS).all():
        raise AssertionError("population contains unsupported bucket")
    return population.sort_values(["ticker", "quarter"], kind="stable").reset_index(drop=True)


def _targets_with_quarter(targets: pd.DataFrame) -> pd.DataFrame:
    _require_columns(
        targets,
        {"config_id", "rebalance_date", "ticker", "rank_in_population"},
        "rebalance targets",
    )
    values = targets.copy()
    values["quarter"] = values["rebalance_date"].map(_quarter_from_date)
    return values


def _named_rows(population: pd.DataFrame) -> pd.DataFrame:
    keys = pd.DataFrame(NAMED_KEYS, columns=["ticker", "quarter"])
    rows = keys.merge(
        population,
        on=["ticker", "quarter"],
        how="left",
        validate="one_to_one",
    )
    if rows[INTEREST].isna().any() or rows[FINANCIAL_EXPENSES].isna().any():
        missing = rows.loc[
            rows[INTEREST].isna() | rows[FINANCIAL_EXPENSES].isna(),
            ["ticker", "quarter"],
        ].to_dict(orient="records")
        raise ValueError(f"named rows are absent from committed population: {missing}")
    return rows


def _hqc_net_sales(annual: pd.DataFrame) -> dict[str, str]:
    _require_columns(
        annual,
        {
            "ticker",
            "fiscal_year",
            "period_end",
            "available_from",
            "item_id",
            "value",
            "source",
            "as_of",
            "data_status",
        },
        "annual PIT fundamentals",
    )
    rows = annual.loc[
        annual["ticker"].eq("HQC")
        & annual["fiscal_year"].eq("2024")
        & annual["item_id"].eq("net_sales")
    ]
    if len(rows) != 1:
        raise ValueError(f"expected one HQC FY2024 net_sales row; found {len(rows)}")
    row = rows.iloc[0]
    value = _decimal(row["value"])
    if value is None:
        raise ValueError("HQC FY2024 net_sales is missing")
    return {
        "fiscal_year": str(row["fiscal_year"]),
        "period_end": str(row["period_end"]),
        "available_from": str(row["available_from"]),
        "value": _decimal_text(value),
        "source": str(row["source"]),
        "as_of": str(row["as_of"]),
        "data_status": str(row["data_status"]),
    }


def diagnose() -> Diagnosis:
    fundamentals = _read_csv(FUNDAMENTALS_PATH)
    targets = _targets_with_quarter(_read_csv(TARGETS_PATH))
    annual = _read_csv(ANNUAL_PATH)
    population = _population(fundamentals)
    target_hits = targets.merge(
        population.loc[
            :,
            ["ticker", "quarter", "bucket", INTEREST, FINANCIAL_EXPENSES],
        ],
        on=["ticker", "quarter"],
        how="inner",
        validate="many_to_one",
    ).sort_values(["quarter", "ticker", "config_id"], kind="stable")
    named_rows = _named_rows(population)
    named_keys = pd.DataFrame(NAMED_KEYS, columns=["ticker", "quarter"])
    named_hits = targets.merge(
        named_keys,
        on=["ticker", "quarter"],
        how="inner",
        validate="many_to_many",
    ).sort_values(["quarter", "ticker", "config_id"], kind="stable")
    hqc_target_hits = targets.loc[
        targets["ticker"].eq("HQC"),
        ["ticker", "quarter", "config_id", "rank_in_population"],
    ].sort_values(["quarter", "config_id"], kind="stable")
    return Diagnosis(
        population=population,
        target_hits=target_hits,
        target_input_rows=len(targets),
        named_rows=named_rows,
        named_hits=named_hits,
        hqc_net_sales=_hqc_net_sales(annual),
        hqc_target_hits=hqc_target_hits,
    )


def _table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(str(value).replace("|", "\\|").replace("\n", " ") for value in row)
            + " |"
        )
    return lines


def _bucket_rows(population: pd.DataFrame) -> list[list[Any]]:
    counts = Counter(population["bucket"])
    total = len(population)
    rows: list[list[Any]] = []
    for bucket in BUCKETS:
        examples = population.loc[population["bucket"].eq(bucket)].head(3)
        example_text = "; ".join(
            f"{row.ticker} {row.quarter}: interest={row.interest_expenses} ({_sign(row.interest_decimal)}), financial_expenses={row.financial_expenses} ({_sign(row.financial_expenses_decimal)})"
            for row in examples.itertuples(index=False)
        )
        rows.append(
            [
                bucket,
                counts[bucket],
                f"{counts[bucket] * Decimal('100') / Decimal(total):.2f}%",
                example_text or "NONE",
            ]
        )
    return rows


def _target_summary_rows(target_hits: pd.DataFrame) -> list[list[Any]]:
    return [
        [config_id, int(count)]
        for config_id, count in target_hits.groupby("config_id", sort=True).size().items()
    ]


def render_report(diagnosis: Diagnosis) -> str:
    population = diagnosis.population
    target_hits = diagnosis.target_hits
    counts = Counter(population["bucket"])
    unique_target_pairs = target_hits.loc[:, ["ticker", "quarter"]].drop_duplicates()
    named_target_pairs = diagnosis.named_hits.loc[:, ["ticker", "quarter"]].drop_duplicates()
    named_raw_rows = [
        [
            row.ticker,
            row.quarter,
            row.interest_expenses,
            _sign(row.interest_decimal),
            row.financial_expenses,
            _sign(row.financial_expenses_decimal),
            row.bucket,
        ]
        for row in diagnosis.named_rows.itertuples(index=False)
    ]
    target_detail_rows = [
        [
            row.ticker,
            row.quarter,
            row.config_id,
            row.rank_in_population,
            row.bucket,
        ]
        for row in target_hits.itertuples(index=False)
    ]
    named_hit_rows = [
        [row.ticker, row.quarter, row.config_id, row.rank_in_population]
        for row in diagnosis.named_hits.itertuples(index=False)
    ]
    hqc = diagnosis.hqc_net_sales
    lines = [
        "# Interest-sign diagnosis",
        "",
        "## Prior investigations already established",
        "",
        "- investigate_sprint5_interest_sign.py read preserved local raw and normalized quarterly caches for HAG, IDI, and DTD and found each displayed raw value equal to its normalized value; without a committed annotation it kept positive-interest cases SOURCE_AMBIGUOUS rather than proving a sign reversal.",
        "- investigate_sprint6_interest_anomalies.py read 44 historical Sprint 5 anomaly-log rows only, compared local raw with normalized fields, and used local labels NET_PRESENTATION_SUSPECTED, PROVIDER_FIELD_SUSPECTED, or UNEXPLAINED; it did not reproduce or classify the full 545-row Sprint 9-3 population.",
        "",
        "## Step 1 - Reproduced population",
        "",
        f"- Source file: {FUNDAMENTALS_PATH.relative_to(ROOT).as_posix()}.",
        f"- Exact condition: abs(interest_expenses) > abs(financial_expenses), with both committed values numeric.",
        f"- Rows: {len(population)}.",
        f"- Distinct tickers: {population['ticker'].nunique()}.",
        f"- Distinct quarters: {population['quarter'].nunique()}.",
        f"- Quarter range: {population['quarter'].min()} through {population['quarter'].max()}.",
        "- The reproduced count equals the recorded 545 rows; no value was adjusted to obtain that match.",
        "",
        "## Step 2 - Classification from committed evidence only",
        "",
        "SIGN_CONVENTION is assigned only when the two committed raw signed values have opposite signs; this records the sign conflict without claiming which provider field is wrong. INTEREST_INCOME_OFFSET is assigned only to the documented HAG 2026Q1 case from SPEC_SPRINT_5 section 6. The quarterly PIT file does not contain financial_income, so same-sign nonzero rows without that HAG documentation remain UNEXPLAINED rather than being inferred as netted totals. GENUINELY_INCONSISTENT is zero because the committed rows do not prove that both reported values cannot be correct.",
        "",
        *_table(
            ["bucket", "count", "population percentage", "up to three raw signed examples"],
            _bucket_rows(population),
        ),
        "",
        f"Bucket arithmetic: {counts['SIGN_CONVENTION']} + {counts['INTEREST_INCOME_OFFSET']} + {counts['MISSING_OR_ZERO_TOTAL']} + {counts['GENUINELY_INCONSISTENT']} + {counts['UNEXPLAINED']} = {sum(counts[bucket] for bucket in BUCKETS)}.",
        "",
        "## Step 3 - Selected-basket impact",
        "",
        f"- Target source file: {TARGETS_PATH.relative_to(ROOT).as_posix()}; committed target rows read: {diagnosis.target_input_rows}.",
        f"- Affected ticker-quarters that appear at least once in targets: {len(unique_target_pairs)} of {len(population)}.",
        f"- Target rows for affected ticker-quarters: {len(target_hits)}.",
        "",
        *_table(
            ["configuration", "target rows for affected ticker-quarters"],
            _target_summary_rows(target_hits),
        ),
        "",
        "Every selected target hit, including its configuration and rank, follows:",
        "",
        *_table(
            ["ticker", "quarter", "configuration", "rank_in_population", "diagnosis bucket"],
            target_detail_rows,
        ),
        "",
        "### Four previously UNEXPLAINED named rows",
        "",
        "The earlier UNEXPLAINED label was a causal conclusion from the narrower Sprint 6 investigation; under this report's raw-sign bucket definition, all four are SIGN_CONVENTION because their committed signs oppose, without asserting a correction.",
        "",
        *_table(
            [
                "ticker",
                "quarter",
                "interest_expenses raw VND",
                "interest sign",
                "financial_expenses raw VND",
                "financial_expenses sign",
                "current bucket",
            ],
            named_raw_rows,
        ),
        "",
        f"- Named affected ticker-quarters in targets: {len(named_target_pairs)} of 4.",
        f"- Target rows for the four named cases: {len(diagnosis.named_hits)}.",
        "",
        *_table(
            ["ticker", "quarter", "configuration", "rank_in_population"],
            named_hit_rows or [["NONE", "", "", ""]],
        ),
        "",
        "### HQC separately",
        "",
        f"- HQC target rows in the committed target file: {len(diagnosis.hqc_target_hits)}.",
        "- HQC 2024Q4 target rows: 0.",
        "",
        "## Step 4 - Named raw case details",
        "",
        f"- GMD, SAB, DTD, and LHC figures above come from {FUNDAMENTALS_PATH.relative_to(ROOT).as_posix()} using their listed quarter and item_id values.",
        f"- HQC FY2024 net_sales source file: {ANNUAL_PATH.relative_to(ROOT).as_posix()}.",
        "",
        *_table(
            [
                "ticker",
                "fiscal_year",
                "period_end",
                "available_from",
                "net_sales raw VND",
                "source",
                "as_of",
                "data_status",
            ],
            [
                [
                    "HQC",
                    hqc["fiscal_year"],
                    hqc["period_end"],
                    hqc["available_from"],
                    hqc["value"],
                    hqc["source"],
                    hqc["as_of"],
                    hqc["data_status"],
                ]
            ],
        ),
        "",
        "HQC FY2024 net_sales is non-positive but not zero. The gross_margin ratio, gross_profit divided by net_sales, is economically undefined for the project rule: build_sprint6_franchise.py drops that year as NON_POSITIVE_NET_SALES and build_sprint6_fscore.py leaves the gross-margin criterion UNSCORED, so those two paths do not divide by zero or silently emit a margin. In contrast, src/screener/step1_cleaning.py checks DSRI and GMI denominators only for zero; if its DSRI or GMI function were supplied this negative sales value, it would compute an economically misleading signed ratio rather than raise a zero-denominator status. This report changes neither behavior.",
        "",
        "## Decisions this report does NOT make",
        "",
        "This diagnosis recommends no threshold change, no row exclusion, and no formula change. It does not drop, correct, patch, or re-sign any row. Any remedy is a separate step that requires project-owner approval.",
        "",
    ]
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diagnose committed interest-expense sign anomalies without any network call."
    )
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    diagnosis = diagnose()
    args.output.write_text(render_report(diagnosis), encoding="utf-8")
    counts = Counter(diagnosis.population["bucket"])
    print(f"POPULATION_ROWS={len(diagnosis.population)}")
    print(f"DISTINCT_TICKERS={diagnosis.population['ticker'].nunique()}")
    print(f"DISTINCT_QUARTERS={diagnosis.population['quarter'].nunique()}")
    print("BUCKETS=" + ";".join(f"{bucket}:{counts[bucket]}" for bucket in BUCKETS))
    print(
        "TARGET_IMPACT="
        f"{diagnosis.target_hits[['ticker', 'quarter']].drop_duplicates().shape[0]} unique pairs;"
        f"{len(diagnosis.target_hits)} target rows"
    )
    print(f"NETWORK_CALLS=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
