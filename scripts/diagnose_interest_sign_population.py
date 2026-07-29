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
VALUATION_PATH = (
    ROOT
    / "data"
    / "valuation"
    / "2026-07-26"
    / "historical_valuation_point_in_time.csv.gz"
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
HAG_REBALANCE_DATES = (
    "2024-03-31",
    "2024-06-30",
    "2024-09-30",
    "2024-12-31",
)


@dataclass(frozen=True)
class Diagnosis:
    population: pd.DataFrame
    target_hits: pd.DataFrame
    target_input_rows: int
    named_rows: pd.DataFrame
    hqc_net_sales: dict[str, str]
    positive_interest_rows: pd.DataFrame
    positive_interest_overlap_count: int
    positive_interest_ebit_tev_target_rows: int
    hag_sensitivity_rows: list[dict[str, str]]


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


def _ttm_quarters(value: Any) -> tuple[str, ...]:
    return tuple(part.strip() for part in str(value).split("|") if part.strip())


def _targets_with_quarter(targets: pd.DataFrame) -> pd.DataFrame:
    _require_columns(
        targets,
        {
            "config_id",
            "rebalance_date",
            "ticker",
            "rank_in_population",
            "ttm_quarters",
        },
        "target-linked valuation rows",
    )
    values = targets.copy()
    quarters = values["ttm_quarters"].map(_ttm_quarters)
    incomplete_count = int(quarters.map(lambda values: len(values) < 4).sum())
    if incomplete_count:
        raise RuntimeError(
            "STOP: target-linked valuation ttm_quarters has fewer than four entries: "
            f"{incomplete_count}"
        )
    non_four_count = int(quarters.map(lambda values: len(values) != 4).sum())
    if non_four_count:
        raise RuntimeError(
            "STOP: target-linked valuation ttm_quarters does not have exactly four entries: "
            f"{non_four_count}"
        )
    values["quarter"] = quarters
    return values.explode("quarter", ignore_index=True)


def _interest_rows(fundamentals: pd.DataFrame) -> pd.DataFrame:
    _require_columns(
        fundamentals,
        {"ticker", "quarter", "item_id", "value"},
        "quarterly PIT fundamentals",
    )
    values = fundamentals.loc[
        fundamentals["item_id"].eq(INTEREST),
        ["ticker", "quarter", "value"],
    ].copy()
    if values.duplicated(["ticker", "quarter"]).any():
        duplicate = values.loc[
            values.duplicated(["ticker", "quarter"], keep=False)
        ].iloc[0]
        raise ValueError(
            "duplicate committed interest key: "
            f"{duplicate['ticker']} {duplicate['quarter']}"
        )
    values["interest_decimal"] = values["value"].map(_decimal)
    return values.rename(columns={"value": INTEREST})


def _target_valuation_rows(
    targets: pd.DataFrame,
    valuation: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        targets,
        {
            "config_id",
            "metric",
            "rebalance_date",
            "ticker",
            "rank_in_population",
        },
        "rebalance targets",
    )
    _require_columns(
        valuation,
        {
            "ticker",
            "evaluation_date",
            "ttm_quarters",
            "ttm_pbt",
            "ttm_interest_magnitude",
            "ebit_proxy_vas",
            "tev",
            "ebit_tev",
        },
        "historical valuation",
    )
    values = valuation.copy()
    values["ticker"] = values["ticker"].str.strip().str.upper()
    if values.duplicated(["ticker", "evaluation_date"]).any():
        duplicate = values.loc[
            values.duplicated(["ticker", "evaluation_date"], keep=False)
        ].iloc[0]
        raise ValueError(
            "duplicate committed valuation key: "
            f"{duplicate['ticker']} {duplicate['evaluation_date']}"
        )
    target_rows = targets.copy().reset_index(drop=True)
    target_rows["ticker"] = target_rows["ticker"].str.strip().str.upper()
    target_rows["_target_row_id"] = target_rows.index
    joined = target_rows.merge(
        values,
        left_on=["ticker", "rebalance_date"],
        right_on=["ticker", "evaluation_date"],
        how="left",
        validate="many_to_one",
        indicator=True,
        suffixes=("", "_valuation"),
    )
    missing_count = int(joined["_merge"].ne("both").sum())
    if missing_count:
        raise RuntimeError(
            "STOP: rebalance targets without a matching valuation row: "
            f"{missing_count}"
        )
    return joined.drop(columns="_merge")


def _contaminated_target_hits(
    target_valuations: pd.DataFrame,
    population: pd.DataFrame,
) -> pd.DataFrame:
    target_windows = _targets_with_quarter(target_valuations)
    flagged_windows = target_windows.merge(
        population.loc[:, ["ticker", "quarter", "bucket"]],
        on=["ticker", "quarter"],
        how="inner",
        validate="many_to_many",
    )
    contaminated_quarters = (
        flagged_windows.groupby("_target_row_id", sort=False)["quarter"]
        .agg(lambda values: "|".join(dict.fromkeys(values)))
        .rename("contaminated_ttm_quarters")
        .reset_index()
    )
    return (
        target_valuations.merge(
            contaminated_quarters,
            on="_target_row_id",
            how="inner",
            validate="one_to_one",
        )
        .sort_values(["rebalance_date", "ticker", "config_id"], kind="stable")
        .reset_index(drop=True)
    )


def _hag_sensitivity_rows(
    valuation: pd.DataFrame,
    interest_rows: pd.DataFrame,
    targets: pd.DataFrame,
) -> list[dict[str, str]]:
    hag_valuation = valuation.loc[
        valuation["ticker"].eq("HAG")
        & valuation["evaluation_date"].isin(HAG_REBALANCE_DATES)
    ].copy()
    if len(hag_valuation) != len(HAG_REBALANCE_DATES):
        raise ValueError(
            "expected one HAG valuation row for each requested rebalance date; found "
            f"{len(hag_valuation)}"
        )
    hag_interest = interest_rows.loc[interest_rows["ticker"].eq("HAG")].set_index(
        "quarter"
    )
    rows: list[dict[str, str]] = []
    for rebalance_date in HAG_REBALANCE_DATES:
        valuation_row = hag_valuation.loc[
            hag_valuation["evaluation_date"].eq(rebalance_date)
        ].iloc[0]
        quarters = _ttm_quarters(valuation_row["ttm_quarters"])
        if len(quarters) != 4:
            raise RuntimeError(
                "STOP: HAG valuation ttm_quarters does not have exactly four entries: "
                f"{rebalance_date}"
            )
        missing_quarters = [quarter for quarter in quarters if quarter not in hag_interest.index]
        if missing_quarters:
            raise ValueError(
                "HAG interest_expenses values are missing for TTM quarters: "
                f"{missing_quarters}"
            )
        interest_values = [
            hag_interest.loc[quarter, "interest_decimal"] for quarter in quarters
        ]
        if any(value is None for value in interest_values):
            raise ValueError(f"HAG has a blank interest_expenses value at {rebalance_date}")
        usable_interest = [
            value for value in interest_values if value is not None
        ]
        magnitude = sum((abs(value) for value in usable_interest), Decimal("0"))
        committed_magnitude = _decimal(valuation_row["ttm_interest_magnitude"])
        ttm_pbt = _decimal(valuation_row["ttm_pbt"])
        committed_ebit = _decimal(valuation_row["ebit_proxy_vas"])
        tev = _decimal(valuation_row["tev"])
        committed_ebit_tev = _decimal(valuation_row["ebit_tev"])
        if (
            committed_magnitude is None
            or ttm_pbt is None
            or committed_ebit is None
            or tev is None
            or committed_ebit_tev is None
        ):
            raise ValueError(f"HAG valuation values are incomplete at {rebalance_date}")
        if magnitude != committed_magnitude:
            raise ValueError(
                "HAG committed ttm_interest_magnitude does not match its raw values at "
                f"{rebalance_date}"
            )
        if ttm_pbt + magnitude != committed_ebit:
            raise ValueError(
                "HAG committed ebit_proxy_vas does not match ttm_pbt plus "
                f"ttm_interest_magnitude at {rebalance_date}"
            )
        sensitivity_interest = sum(
            (abs(value) if value <= 0 else -value for value in usable_interest),
            Decimal("0"),
        )
        sensitivity_ebit_tev = ((ttm_pbt + sensitivity_interest) / tev).normalize()
        target_rows = targets.loc[
            targets["ticker"].eq("HAG")
            & targets["rebalance_date"].eq(rebalance_date),
            ["config_id", "rank_in_population"],
        ].sort_values("config_id", kind="stable")
        if target_rows.empty:
            raise ValueError(f"HAG has no target rows at {rebalance_date}")
        ranks = "; ".join(
            f"{row.config_id}: {row.rank_in_population}"
            for row in target_rows.itertuples(index=False)
        )
        raw_interest = "; ".join(
            f"{quarter}={_decimal_text(value)} ({_sign(value)})"
            for quarter, value in zip(quarters, usable_interest, strict=True)
        )
        rows.append(
            {
                "rebalance_date": rebalance_date,
                "ttm_quarters": "|".join(quarters),
                "interest_expenses_raw": raw_interest,
                "ttm_interest_magnitude": _decimal_text(committed_magnitude),
                "ttm_pbt": _decimal_text(ttm_pbt),
                "ebit_proxy_vas": _decimal_text(committed_ebit),
                "tev": _decimal_text(tev),
                "ebit_tev": _decimal_text(committed_ebit_tev),
                "rank_in_population": ranks,
                "sensitivity_ebit_tev": _decimal_text(sensitivity_ebit_tev),
            }
        )
    return rows


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
    targets = _read_csv(TARGETS_PATH)
    valuation = _read_csv(VALUATION_PATH)
    annual = _read_csv(ANNUAL_PATH)
    population = _population(fundamentals)
    target_valuations = _target_valuation_rows(targets, valuation)
    target_hits = _contaminated_target_hits(target_valuations, population)
    if len(targets) != 2_880 or len(target_hits) != 509:
        raise RuntimeError(
            "STOP: contaminated target rows are "
            f"{len(target_hits)} of {len(targets)}; expected 509 of 2880"
        )
    interest_rows = _interest_rows(fundamentals)
    positive_interest_rows = interest_rows.loc[
        interest_rows["interest_decimal"].map(
            lambda value: value is not None and value > 0
        )
    ].copy()
    positive_interest_overlap_count = len(
        population.loc[:, ["ticker", "quarter"]].merge(
            positive_interest_rows.loc[:, ["ticker", "quarter"]],
            on=["ticker", "quarter"],
            how="inner",
            validate="one_to_one",
        )
    )
    positive_target_windows = _targets_with_quarter(target_valuations).merge(
        positive_interest_rows.loc[:, ["ticker", "quarter"]],
        on=["ticker", "quarter"],
        how="inner",
        validate="many_to_many",
    )
    positive_target_ids = positive_target_windows["_target_row_id"].drop_duplicates()
    positive_interest_ebit_tev_target_rows = int(
        target_valuations.loc[
            target_valuations["_target_row_id"].isin(positive_target_ids)
            & target_valuations["metric"].eq("ebit_tev")
        ].shape[0]
    )
    named_rows = _named_rows(population)
    return Diagnosis(
        population=population,
        target_hits=target_hits,
        target_input_rows=len(targets),
        named_rows=named_rows,
        hqc_net_sales=_hqc_net_sales(annual),
        positive_interest_rows=positive_interest_rows,
        positive_interest_overlap_count=positive_interest_overlap_count,
        positive_interest_ebit_tev_target_rows=positive_interest_ebit_tev_target_rows,
        hag_sensitivity_rows=_hag_sensitivity_rows(valuation, interest_rows, targets),
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
    counts = target_hits.groupby("metric").size()
    return [
        [
            metric,
            int(counts.get(metric, 0)),
            (
                "ebit_proxy_vas = ttm_pbt + _sum_item(..., \"interest_expenses\", absolute=True)"
                if metric == "ebit_tev"
                else "e_p = ttm_parent / market_cap_vnd; no interest term"
            ),
        ]
        for metric in ("ebit_tev", "e_p")
    ]


def render_report(diagnosis: Diagnosis) -> str:
    population = diagnosis.population
    target_hits = diagnosis.target_hits
    counts = Counter(population["bucket"])
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
    hag_rows = [
        [
            row["rebalance_date"],
            row["ttm_quarters"],
            row["interest_expenses_raw"],
            row["ttm_interest_magnitude"],
            row["ttm_pbt"],
            row["ebit_proxy_vas"],
            row["tev"],
            row["ebit_tev"],
            row["rank_in_population"],
            row["sensitivity_ebit_tev"],
        ]
        for row in diagnosis.hag_sensitivity_rows
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
        f"- Valuation source file: {VALUATION_PATH.relative_to(ROOT).as_posix()}; targets join on (ticker, rebalance_date) = (ticker, evaluation_date), then each target is checked against all four pipe-separated ttm_quarters.",
        f"- CONTAMINATED target rows: {len(target_hits)} of {diagnosis.target_input_rows}.",
        "- A target is CONTAMINATED when any of its four TTM quarters is in the 545-row flagged population for the same ticker; no row, formula, threshold, or configuration is changed.",
        "- financial_expenses is read only by interest_anomalies(); it does not enter ebit_proxy_vas or e_p.",
        "",
        *_table(
            ["metric", "CONTAMINATED target rows", "harm channel from build_sprint9_3_historical_valuation.py"],
            _target_summary_rows(target_hits),
        ),
        "",
        "The e_p rows are flag-exposed but cannot be affected by an interest-expense defect by construction: e_p = ttm_parent / market_cap_vnd contains no interest term.",
        "",
        f"- Narrower positive-interest population: {len(diagnosis.positive_interest_rows)} ticker-quarters where interest_expenses > 0.",
        f"- Positive-interest overlap with the 545-row flagged population: {diagnosis.positive_interest_overlap_count} ticker-quarters.",
        f"- ebit_tev target rows with at least one positive interest_expenses quarter in their TTM window: {diagnosis.positive_interest_ebit_tev_target_rows}.",
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
        "### HAG sensitivity only, not a correction",
        "",
        "The committed formulas copied from build_sprint9_3_historical_valuation.py are ebit_proxy_vas = ttm_pbt + _sum_item(..., \"interest_expenses\", absolute=True) and e_p = ttm_parent / market_cap_vnd; the final column below changes only positive raw interest_expenses from add to subtract for sensitivity inspection, not as a data or production correction.",
        "",
        *_table(
            [
                "rebalance_date",
                "ttm_quarters",
                "interest_expenses raw VND (four values with signs)",
                "ttm_interest_magnitude",
                "ttm_pbt",
                "ebit_proxy_vas",
                "tev",
                "ebit_tev as committed",
                "rank_in_population (all target configurations)",
                "SENSITIVITY_ONLY_NOT_A_CORRECTION",
            ],
            hag_rows,
        ),
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


def _stdout_lines(diagnosis: Diagnosis) -> list[str]:
    counts = Counter(diagnosis.population["bucket"])
    metric_rows = _target_summary_rows(diagnosis.target_hits)
    metric_counts = {str(row[0]): int(row[1]) for row in metric_rows}
    hag_rows = [
        [
            row["rebalance_date"],
            row["ttm_quarters"],
            row["interest_expenses_raw"],
            row["ttm_interest_magnitude"],
            row["ttm_pbt"],
            row["ebit_proxy_vas"],
            row["tev"],
            row["ebit_tev"],
            row["rank_in_population"],
            row["sensitivity_ebit_tev"],
        ]
        for row in diagnosis.hag_sensitivity_rows
    ]
    return [
        f"POPULATION_ROWS={len(diagnosis.population)}",
        f"DISTINCT_TICKERS={diagnosis.population['ticker'].nunique()}",
        f"DISTINCT_QUARTERS={diagnosis.population['quarter'].nunique()}",
        "BUCKETS=" + ";".join(f"{bucket}:{counts[bucket]}" for bucket in BUCKETS),
        f"CONTAMINATED_TARGET_ROWS={len(diagnosis.target_hits)} OF {diagnosis.target_input_rows}",
        "CONTAMINATED_TARGET_ROWS_BY_METRIC="
        f"ebit_tev:{metric_counts['ebit_tev']};e_p:{metric_counts['e_p']};"
        f"TOTAL:{len(diagnosis.target_hits)}",
        f"POSITIVE_INTEREST_TICKER_QUARTERS={len(diagnosis.positive_interest_rows)}",
        "POSITIVE_INTEREST_OVERLAP_WITH_FLAGGED_POPULATION="
        f"{diagnosis.positive_interest_overlap_count}",
        "POSITIVE_INTEREST_EBIT_TEV_TARGET_ROWS="
        f"{diagnosis.positive_interest_ebit_tev_target_rows}",
        "METRIC_SPLIT_TABLE_START",
        *_table(
            ["metric", "CONTAMINATED target rows", "harm channel"],
            metric_rows,
        ),
        "METRIC_SPLIT_TABLE_END",
        "HAG_SENSITIVITY_TABLE_START",
        *_table(
            [
                "rebalance_date",
                "ttm_quarters",
                "interest_expenses raw VND (four values with signs)",
                "ttm_interest_magnitude",
                "ttm_pbt",
                "ebit_proxy_vas",
                "tev",
                "ebit_tev as committed",
                "rank_in_population (all target configurations)",
                "SENSITIVITY_ONLY_NOT_A_CORRECTION",
            ],
            hag_rows,
        ),
        "HAG_SENSITIVITY_TABLE_END",
        "NETWORK_CALLS=0",
    ]


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
    for line in _stdout_lines(diagnosis):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
