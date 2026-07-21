"""Build Sprint 6 Franchise Power and composite quality from local annual data.

Formulas copied verbatim from docs/SPEC_SPRINT_6.md section 3.1:

EBIT_PROXY_VAS_t =
    net_accounting_profit_loss_before_tax_t
    + abs(interest_expenses_t)

INVESTED_CAPITAL_t =
    owners_equity_t
    + short_term_borrowings_t
    + long_term_borrowings_t
    - cash_and_cash_equivalents_t

ROC_t =
    EBIT_PROXY_VAS_t
    / average(INVESTED_CAPITAL_t, INVESTED_CAPITAL_t-1)

Formula copied verbatim from docs/SPEC_SPRINT_6.md section 3.2:

gross_margin_t = gross_profit_t / net_sales_t
"""

from __future__ import annotations

from collections import Counter
import csv
from dataclasses import dataclass
import io
import math
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Any, Iterable

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_sprint6_readiness import (  # noqa: E402
    CRITERION7_NO_SHARE_INCREASE_CASH,
    CRITERION7_SCORE_0,
    EVALUATION_DATE,
    EXPECTED_SURVIVORS,
    FUNDAMENTALS_ROOT,
    PROPOSED_FRANCHISE_MIN_YEARS,
    SURVIVORS_PATH,
    _franchise_years,
    classify_criterion7_branch,
    eligible_annual_rows,
    item_value_status,
    latest_annual_frame,
)


FSCORE_PATH = ROOT / "data" / "screener" / "sprint6_fscore.csv"
EBIT_TEV_CANDIDATES_PATH = ROOT / "data" / "screener" / "step2_candidates_ebit_tev.csv"
EP_CANDIDATES_PATH = ROOT / "data" / "screener" / "step2_candidates_ep.csv"
OUTPUT_PATH = ROOT / "data" / "screener" / "sprint6_franchise_quality.csv"
REPORT_PATH = ROOT / "docs" / "REPORT_SPRINT_6_FRANCHISE_QUALITY.md"

PBT = "net_accounting_profit_loss_before_tax"
INTEREST = "interest_expenses"
EQUITY = "owners_equity"
SHORT_DEBT = "short_term_borrowings"
LONG_DEBT = "long_term_borrowings"
CASH = "cash_and_cash_equivalents"
NET_SALES = "net_sales"
GROSS_PROFIT = "gross_profit"
COGS = "cost_of_sales"

READINESS_DISTRIBUTION = {7: 146, 6: 1, 5: 2, 4: 4, 3: 3}
READINESS_STATUS = {"READY": 149, "INSUFFICIENT_HISTORY": 7}


@dataclass(frozen=True)
class RocYear:
    year: int
    pbt: float
    interest: float
    ebit: float
    equity: float
    short_debt: float
    long_debt: float
    cash: float
    invested_capital: float
    prior_equity: float
    prior_short_debt: float
    prior_long_debt: float
    prior_cash: float
    prior_invested_capital: float
    average_invested_capital: float
    roc: float


@dataclass(frozen=True)
class MarginYear:
    year: int
    gross_profit: float
    net_sales: float
    gross_margin: float
    fallback_used: bool


def _value(
    frame: pd.DataFrame, item_id: str, year: int
) -> tuple[float | None, str]:
    value, status = item_value_status(frame, item_id, year)
    if status != "OK" or value is None:
        return None, f"{item_id.upper()}_{status if status != 'OK' else 'MISSING'}"
    return float(value), ""


def compute_roc_year(
    income: pd.DataFrame, balance: pd.DataFrame, year: int
) -> tuple[RocYear | None, str]:
    values: dict[str, float] = {}
    flags: list[str] = []
    for name, frame, item, item_year in (
        ("pbt", income, PBT, year),
        ("interest", income, INTEREST, year),
        ("equity", balance, EQUITY, year),
        ("short_debt", balance, SHORT_DEBT, year),
        ("long_debt", balance, LONG_DEBT, year),
        ("cash", balance, CASH, year),
        ("prior_equity", balance, EQUITY, year - 1),
        ("prior_short_debt", balance, SHORT_DEBT, year - 1),
        ("prior_long_debt", balance, LONG_DEBT, year - 1),
        ("prior_cash", balance, CASH, year - 1),
    ):
        value, flag = _value(frame, item, item_year)
        if flag:
            flags.append(f"{item_year}:{flag}")
        elif value is not None:
            values[name] = value
    if flags:
        return None, ";".join(flags)
    ebit = values["pbt"] + abs(values["interest"])
    invested = (
        values["equity"]
        + values["short_debt"]
        + values["long_debt"]
        - values["cash"]
    )
    prior_invested = (
        values["prior_equity"]
        + values["prior_short_debt"]
        + values["prior_long_debt"]
        - values["prior_cash"]
    )
    average_invested = (invested + prior_invested) / 2
    if average_invested <= 0:
        return None, "NON_POSITIVE_AVERAGE_INVESTED_CAPITAL"
    return (
        RocYear(
            year=year,
            pbt=values["pbt"],
            interest=values["interest"],
            ebit=ebit,
            equity=values["equity"],
            short_debt=values["short_debt"],
            long_debt=values["long_debt"],
            cash=values["cash"],
            invested_capital=invested,
            prior_equity=values["prior_equity"],
            prior_short_debt=values["prior_short_debt"],
            prior_long_debt=values["prior_long_debt"],
            prior_cash=values["prior_cash"],
            prior_invested_capital=prior_invested,
            average_invested_capital=average_invested,
            roc=ebit / average_invested,
        ),
        "",
    )


def compute_roc_series(
    income: pd.DataFrame, balance: pd.DataFrame, years: Iterable[int]
) -> tuple[list[RocYear], list[tuple[int, str]]]:
    usable: list[RocYear] = []
    dropped: list[tuple[int, str]] = []
    for year in sorted(years):
        observation, reason = compute_roc_year(income, balance, int(year))
        if observation is None:
            dropped.append((int(year), reason))
        else:
            usable.append(observation)
    return usable, dropped


def summarize_roc(
    observations: list[RocYear] | list[float],
) -> tuple[float | None, float | None, str]:
    values = [float(item.roc if isinstance(item, RocYear) else item) for item in observations]
    if not values:
        return None, None, "NO_USABLE_ROC_YEARS"
    arithmetic = statistics.fmean(values)
    if any(value <= 0 for value in values):
        return arithmetic, None, "NON_POSITIVE_ROC_YEAR_PRESENT"
    geometric = math.exp(statistics.fmean(math.log(value) for value in values))
    return arithmetic, geometric, ""


def compute_margin_year(
    income: pd.DataFrame, year: int
) -> tuple[MarginYear | None, str]:
    sales, sales_flag = _value(income, NET_SALES, year)
    if sales_flag:
        return None, sales_flag
    if sales is None or sales <= 0:
        return None, "NON_POSITIVE_NET_SALES"
    gross, gross_status = item_value_status(income, GROSS_PROFIT, year)
    fallback = False
    if gross_status != "OK" or gross is None:
        cogs, cogs_status = item_value_status(income, COGS, year)
        if cogs_status != "OK" or cogs is None:
            return None, f"GROSS_PROFIT_{gross_status}|COGS_{cogs_status}"
        if float(cogs) > 0:
            return None, "POSITIVE_COGS_FALLBACK_FORBIDDEN"
        gross = sales + float(cogs)
        fallback = True
    gross_value = float(gross)
    return (
        MarginYear(
            year=year,
            gross_profit=gross_value,
            net_sales=sales,
            gross_margin=gross_value / sales,
            fallback_used=fallback,
        ),
        "",
    )


def compute_margin_series(
    income: pd.DataFrame, years: Iterable[int]
) -> tuple[list[MarginYear], list[tuple[int, str]]]:
    usable: list[MarginYear] = []
    dropped: list[tuple[int, str]] = []
    for year in sorted(years):
        observation, reason = compute_margin_year(income, int(year))
        if observation is None:
            dropped.append((int(year), reason))
        else:
            usable.append(observation)
    return usable, dropped


def summarize_margin(
    observations: list[MarginYear] | list[float],
) -> tuple[float | None, float | None, float | None, str]:
    values = [
        float(item.gross_margin if isinstance(item, MarginYear) else item)
        for item in observations
    ]
    if not values:
        return None, None, None, "NO_USABLE_MARGIN_YEARS"
    mean = statistics.fmean(values)
    if len(values) < 2:
        return mean, None, None, "FEWER_THAN_TWO_USABLE_MARGIN_YEARS"
    population_std = statistics.pstdev(values)
    if mean <= 0:
        return mean, population_std, None, "NON_POSITIVE_MEAN_GROSS_MARGIN"
    if population_std == 0:
        return mean, population_std, None, "ZERO_MARGIN_VARIANCE"
    return mean, population_std, mean / population_std, ""


def rank_percentile(
    values: pd.Series, *, maximum_mask: pd.Series | None = None
) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    result = pd.Series(float("nan"), index=values.index, dtype=float)
    valid = numeric.notna()
    count = int(valid.sum())
    if count == 1:
        result.loc[valid] = 1.0
    elif count > 1:
        ranks = numeric.loc[valid].rank(method="average", ascending=True)
        result.loc[valid] = (ranks - 1) / (count - 1)
    if maximum_mask is not None:
        result.loc[maximum_mask.fillna(False)] = 1.0
    return result


def composite_value(values: Iterable[float | None]) -> tuple[float | None, int]:
    usable = [float(value) for value in values if value is not None and not pd.isna(value)]
    return (statistics.fmean(usable), len(usable)) if usable else (None, 0)


def criterion7_settled_case(
    balance: pd.DataFrame, cash_flow: pd.DataFrame, year: int
) -> str:
    common_n, common_n_status = item_value_status(balance, "common_shares", year)
    common_n1, common_n1_status = item_value_status(balance, "common_shares", year - 1)
    proceeds, proceeds_status = item_value_status(
        cash_flow, "proceeds_from_issue_of_shares", year
    )
    branch, outcome, _ = classify_criterion7_branch(
        common_n,
        common_n1,
        proceeds,
        common_shares_n_status=common_n_status,
        common_shares_n_minus_1_status=common_n1_status,
        issue_proceeds_n_status=proceeds_status,
    )
    if branch == CRITERION7_SCORE_0 and outcome == "SCORES_0":
        return "SHARE_INCREASE_CASH_POSITIVE_SCORE_0"
    if outcome == CRITERION7_NO_SHARE_INCREASE_CASH:
        return CRITERION7_NO_SHARE_INCREASE_CASH
    return branch


def add_fscore_settled_case(cases: dict[str, str]) -> int:
    main_bytes = subprocess.run(
        ["git", "show", "main:data/screener/sprint6_fscore.csv"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    main_frame = pd.read_csv(
        io.BytesIO(main_bytes), dtype=str, keep_default_na=False
    )
    with FSCORE_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        old_fields = [
            field for field in (reader.fieldnames or []) if field != "criterion_7_settled_case"
        ]
        rows = list(reader)
    fields = old_fields.copy()
    insert_at = fields.index("criterion_7_branch") + 1
    fields.insert(insert_at, "criterion_7_settled_case")
    with FSCORE_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            row["criterion_7_settled_case"] = cases[str(row["ticker"]).upper()]
            writer.writerow({field: row.get(field, "") for field in fields})
    written = pd.read_csv(FSCORE_PATH, dtype=str, keep_default_na=False)
    difference_mask = pd.Series(False, index=main_frame.index)
    for column in main_frame.columns:
        difference_mask |= written[column].ne(main_frame[column])
    return int(difference_mask.sum())


def _labels(values: Iterable[int]) -> str:
    return "|".join(str(value) for value in sorted(values))


def _reasons(values: Iterable[tuple[int, str]]) -> str:
    return "|".join(f"{year}:{reason}" for year, reason in values)


def _display(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "EMPTY"
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else format(value, ".17g")
    return str(value).replace("|", "\\|")


def build() -> tuple[
    pd.DataFrame,
    dict[str, dict[str, Any]],
    list[tuple[str, int, str]],
    list[tuple[str, int, str]],
    int,
]:
    survivors = pd.read_csv(SURVIVORS_PATH)
    fscore = pd.read_csv(FSCORE_PATH)
    if len(survivors) != EXPECTED_SURVIVORS or survivors["ticker"].nunique() != EXPECTED_SURVIVORS:
        raise AssertionError("survivor input is not exactly 156 unique tickers")
    if len(fscore) != EXPECTED_SURVIVORS or fscore["ticker"].nunique() != EXPECTED_SURVIVORS:
        raise AssertionError("F-Score input is not exactly 156 unique tickers")
    fscore_by_ticker = fscore.set_index("ticker")
    rows: list[dict[str, Any]] = []
    evidence: dict[str, dict[str, Any]] = {}
    roc_drops: list[tuple[str, int, str]] = []
    margin_drops: list[tuple[str, int, str]] = []
    settled_cases: dict[str, str] = {}
    all_years: set[int] = set()
    for survivor in survivors.to_dict("records"):
        ticker = str(survivor["ticker"]).strip().upper()
        frames: dict[str, pd.DataFrame] = {}
        sources: dict[str, str] = {}
        for statement in ("income_statement", "balance_sheet", "cash_flow"):
            frame, source, exists = latest_annual_frame(ticker, statement, FUNDAMENTALS_ROOT)
            if not exists:
                frame = pd.DataFrame()
            frames[statement] = eligible_annual_rows(frame, EVALUATION_DATE)
            sources[statement] = source
        income = frames["income_statement"]
        balance = frames["balance_sheet"]
        _, _, _, candidate_years = _franchise_years(income, balance)
        all_years.update(candidate_years)
        roc_values, ticker_roc_drops = compute_roc_series(income, balance, candidate_years)
        margin_values, ticker_margin_drops = compute_margin_series(income, candidate_years)
        roc_drops.extend((ticker, year, reason) for year, reason in ticker_roc_drops)
        margin_drops.extend((ticker, year, reason) for year, reason in ticker_margin_drops)
        roc_mean, roc_geometric, roc_geometric_flag = summarize_roc(roc_values)
        margin_mean, margin_std, margin_stability, margin_flag = summarize_margin(margin_values)
        roc_year_set = {item.year for item in roc_values}
        margin_year_set = {item.year for item in margin_values}
        franchise_years = sorted(roc_year_set & margin_year_set)
        status = (
            "READY"
            if len(franchise_years) >= PROPOSED_FRANCHISE_MIN_YEARS
            else "INSUFFICIENT_HISTORY"
        )
        fscore_row = fscore_by_ticker.loc[ticker]
        row: dict[str, Any] = {
            "ticker": ticker,
            "exchange": survivor.get("exchange", ""),
            "icb2": survivor.get("icb2", ""),
            "evaluation_date": EVALUATION_DATE,
            "roc_years_used": len(roc_values),
            "roc_year_labels": _labels(item.year for item in roc_values),
            "roc_unavailable_years": _reasons(ticker_roc_drops),
            "roc_arithmetic_mean": roc_mean,
            "roc_geometric_mean": roc_geometric,
            "roc_geometric_mean_flag": roc_geometric_flag,
            "margin_years_used": len(margin_values),
            "margin_year_labels": _labels(item.year for item in margin_values),
            "margin_dropped_years": _reasons(ticker_margin_drops),
            "margin_mean": margin_mean,
            "margin_population_std": margin_std,
            "margin_stability": margin_stability,
            "margin_stability_flag": margin_flag,
            "franchise_years_used": len(franchise_years),
            "franchise_year_labels": _labels(franchise_years),
            "franchise_history_status": status,
            "franchise_history_flag": "" if status == "READY" else "INSUFFICIENT_HISTORY",
            "fscore_ranking_ratio": fscore_row["fscore_ranking_ratio"],
            "income_source_path": sources["income_statement"],
            "balance_source_path": sources["balance_sheet"],
        }
        for item in roc_values:
            row[f"roc_{item.year}"] = item.roc
        for item in margin_values:
            row[f"gross_margin_{item.year}"] = item.gross_margin
        rows.append(row)
        settled_cases[ticker] = criterion7_settled_case(
            balance, frames["cash_flow"], int(survivor["annual_n"])
        )
        evidence[ticker] = {
            "roc": roc_values,
            "margin": margin_values,
            "roc_drops": ticker_roc_drops,
            "margin_drops": ticker_margin_drops,
            "roc_mean": roc_mean,
            "roc_geometric": roc_geometric,
            "roc_geometric_flag": roc_geometric_flag,
            "margin_mean": margin_mean,
            "margin_std": margin_std,
            "margin_stability": margin_stability,
            "margin_flag": margin_flag,
        }
    output = pd.DataFrame(rows)
    for year in sorted(all_years):
        for prefix in ("roc", "gross_margin"):
            column = f"{prefix}_{year}"
            if column not in output:
                output[column] = float("nan")
    output["fscore_completion_ratio_percentile"] = rank_percentile(
        output["fscore_ranking_ratio"]
    )
    output["roc_arithmetic_mean_percentile"] = rank_percentile(
        output["roc_arithmetic_mean"]
    )
    output["margin_stability_percentile"] = rank_percentile(
        output["margin_stability"],
        maximum_mask=output["margin_stability_flag"].eq("ZERO_MARGIN_VARIANCE"),
    )
    composites = output.apply(
        lambda row: composite_value(
            (
                row["fscore_completion_ratio_percentile"],
                row["roc_arithmetic_mean_percentile"],
                row["margin_stability_percentile"],
            )
        ),
        axis=1,
    )
    output["composite_quality"] = [value[0] for value in composites]
    output["composite_components_used"] = [value[1] for value in composites]
    output["composite_confidence_flag"] = output["composite_components_used"].map(
        lambda value: "" if value == 3 else "LOW_CONFIDENCE_MISSING_COMPONENTS"
    )
    ebit_tickers = set(pd.read_csv(EBIT_TEV_CANDIDATES_PATH)["ticker"].astype(str))
    ep_tickers = set(pd.read_csv(EP_CANDIDATES_PATH)["ticker"].astype(str))
    output["ebit_tev_quality_rank"] = float("nan")
    output["ep_quality_rank"] = float("nan")
    ebit_mask = output["ticker"].isin(ebit_tickers)
    ep_mask = output["ticker"].isin(ep_tickers)
    output.loc[ebit_mask, "ebit_tev_quality_rank"] = output.loc[
        ebit_mask, "composite_quality"
    ].rank(method="average", ascending=False)
    output.loc[ep_mask, "ep_quality_rank"] = output.loc[
        ep_mask, "composite_quality"
    ].rank(method="average", ascending=False)
    if len(output) != EXPECTED_SURVIVORS or output["ticker"].nunique() != EXPECTED_SURVIVORS:
        raise AssertionError("Franchise output is not exactly 156 unique tickers")
    if not output["composite_components_used"].isin((1, 2, 3)).all():
        raise AssertionError("composite denominator outside {1,2,3}")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_PATH, index=False, lineterminator="\n")
    fscore_difference_count = add_fscore_settled_case(settled_cases)
    return output, evidence, roc_drops, margin_drops, fscore_difference_count


def _distribution(series: pd.Series) -> dict[int, int]:
    return {
        int(value): int(count)
        for value, count in sorted(Counter(int(item) for item in series).items())
    }


def _distribution_lines(distribution: dict[int, int]) -> list[str]:
    return [f"| {value} | {count} |" for value, count in distribution.items()]


def _deviation_explanation(
    name: str,
    actual: dict[int, int],
    drops: list[tuple[str, int, str]],
) -> list[str]:
    lines = [f"### {name} deviations from readiness audit", ""]
    if actual == READINESS_DISTRIBUTION:
        lines.append("No deviation from the readiness-audit distribution.")
        return lines
    lines.append(
        "The readiness audit measured input existence only. The production distribution differs because unusable observations below were dropped rather than zero-filled:"
    )
    for ticker, year, reason in drops:
        lines.append(f"- `{ticker} {year}`: `{reason}`.")
    return lines


def _handcheck_lines(ticker: str, evidence: dict[str, Any]) -> list[str]:
    lines = [
        f"## {ticker} hand-check",
        "",
        "### ROC",
        "",
        "| year | complete arithmetic | ROC_t |",
        "|---:|---|---:|",
    ]
    for item in evidence["roc"]:
        arithmetic = (
            f"EBIT={_display(item.pbt)}+abs({_display(item.interest)})={_display(item.ebit)}; "
            f"IC_{item.year}={_display(item.equity)}+{_display(item.short_debt)}+{_display(item.long_debt)}-{_display(item.cash)}={_display(item.invested_capital)}; "
            f"IC_{item.year - 1}={_display(item.prior_equity)}+{_display(item.prior_short_debt)}+{_display(item.prior_long_debt)}-{_display(item.prior_cash)}={_display(item.prior_invested_capital)}; "
            f"average_IC=({_display(item.invested_capital)}+{_display(item.prior_invested_capital)})/2={_display(item.average_invested_capital)}; "
            f"ROC={_display(item.ebit)}/{_display(item.average_invested_capital)}={_display(item.roc)}"
        )
        lines.append(f"| {item.year} | {arithmetic} | {_display(item.roc)} |")
    lines.extend(
        [
            "",
            f"- `roc_arithmetic_mean = {_display(evidence['roc_mean'])}`.",
            f"- `roc_geometric_mean = {_display(evidence['roc_geometric'])}`; flag: `{evidence['roc_geometric_flag'] or 'NONE'}`.",
            "",
            "### Gross-margin stability",
            "",
            "| year | arithmetic | gross_margin |",
            "|---:|---|---:|",
        ]
    )
    for item in evidence["margin"]:
        lines.append(
            f"| {item.year} | {_display(item.gross_profit)}/{_display(item.net_sales)}={_display(item.gross_margin)} | {_display(item.gross_margin)} |"
        )
    margin_values = "+".join(_display(item.gross_margin) for item in evidence["margin"])
    count = len(evidence["margin"])
    lines.extend(
        [
            "",
            f"- `margin_mean = ({margin_values})/{count} = {_display(evidence['margin_mean'])}`.",
            f"- `margin_population_std = {_display(evidence['margin_std'])}` (population convention: divide by n, not n-1).",
            f"- `margin_stability = {_display(evidence['margin_mean'])}/{_display(evidence['margin_std'])} = {_display(evidence['margin_stability'])}`; flag: `{evidence['margin_flag'] or 'NONE'}`.",
        ]
    )
    return lines


def render_report(
    output: pd.DataFrame,
    evidence: dict[str, dict[str, Any]],
    roc_drops: list[tuple[str, int, str]],
    margin_drops: list[tuple[str, int, str]],
    fscore_difference_count: int,
) -> str:
    roc_distribution = _distribution(output["roc_years_used"])
    margin_distribution = _distribution(output["margin_years_used"])
    status_counts = Counter(output["franchise_history_status"].astype(str))
    lines = [
        "# Sprint 6 Franchise Power and composite quality report",
        "",
        f"- Evaluation date: `{EVALUATION_DATE}`.",
        f"- Output rows: `{len(output)}`; unique tickers: `{output['ticker'].nunique()}`.",
        f"- Pre-existing F-Score columns differing from main: `{fscore_difference_count}` rows.",
        "- Margin standard deviation uses the population convention: divide by n, not n-1.",
        "- This annual history is restated data usable for ranking today, not point-in-time evidence, and does not make Sprint 8 backtests point-in-time clean.",
        "",
        "## Readiness-audit comparison",
        "",
        "Readiness audit reference: 7 years: 146, 6: 1, 5: 2, 4: 4, 3: 3; READY: 149; INSUFFICIENT_HISTORY: 7. It measured input existence, not denominator usability.",
        "",
        "### roc_years_used distribution",
        "",
        "| years | tickers |",
        "|---:|---:|",
        *_distribution_lines(roc_distribution),
        "",
        "### margin_years_used distribution",
        "",
        "| years | tickers |",
        "|---:|---:|",
        *_distribution_lines(margin_distribution),
        "",
        "### Franchise history status",
        "",
        "| status | production | readiness audit |",
        "|---|---:|---:|",
        f"| READY | {status_counts['READY']} | {READINESS_STATUS['READY']} |",
        f"| INSUFFICIENT_HISTORY | {status_counts['INSUFFICIENT_HISTORY']} | {READINESS_STATUS['INSUFFICIENT_HISTORY']} |",
        "",
        *_deviation_explanation("ROC", roc_distribution, roc_drops),
        "",
        *_deviation_explanation("Margin", margin_distribution, margin_drops),
        "",
        "## Dropped ROC ticker-years",
        "",
        "| ticker | year | reason |",
        "|---|---:|---|",
    ]
    if roc_drops:
        lines.extend(f"| {ticker} | {year} | `{reason}` |" for ticker, year, reason in roc_drops)
    else:
        lines.append("| NONE |  |  |")
    lines.extend(
        [
            "",
            "## Dropped gross-margin ticker-years",
            "",
            "| ticker | year | reason |",
            "|---|---:|---|",
        ]
    )
    if margin_drops:
        lines.extend(
            f"| {ticker} | {year} | `{reason}` |" for ticker, year, reason in margin_drops
        )
    else:
        lines.append("| NONE |  |  |")
    for ticker in ("VNM", "DBC", "MSN"):
        lines.extend(["", *_handcheck_lines(ticker, evidence[ticker])])
    hqc = evidence["HQC"]
    lines.extend(
        [
            "",
            "## HQC gross-margin hand-check",
            "",
            "| year | status / arithmetic |",
            "|---:|---|",
        ]
    )
    hqc_margin = {item.year: item for item in hqc["margin"]}
    hqc_drops = dict(hqc["margin_drops"])
    for year in sorted(set(hqc_margin) | set(hqc_drops)):
        if year in hqc_drops:
            lines.append(f"| {year} | DROPPED — `{hqc_drops[year]}` |")
        else:
            item = hqc_margin[year]
            lines.append(
                f"| {year} | {_display(item.gross_profit)}/{_display(item.net_sales)}={_display(item.gross_margin)} |"
            )
    lines.extend(
        [
            "",
            f"- `margin_mean = {_display(hqc['margin_mean'])}` from remaining usable years only.",
            f"- `margin_population_std = {_display(hqc['margin_std'])}`.",
            f"- `margin_stability = {_display(hqc['margin_stability'])}`.",
        ]
    )
    for title, rank_column in (
        ("EBIT/TEV candidate-list top 10", "ebit_tev_quality_rank"),
        ("E/P candidate-list top 10", "ep_quality_rank"),
    ):
        lines.extend(
            [
                "",
                f"## {title}",
                "",
                "| rank | ticker | F-Score percentile | ROC percentile | margin-stability percentile | composite_quality |",
                "|---:|---|---:|---:|---:|---:|",
            ]
        )
        top = output.loc[output[rank_column].notna()].sort_values(
            [rank_column, "ticker"]
        ).head(10)
        for row in top.to_dict("records"):
            lines.append(
                f"| {_display(row[rank_column])} | {row['ticker']} | {_display(row['fscore_completion_ratio_percentile'])} | {_display(row['roc_arithmetic_mean_percentile'])} | {_display(row['margin_stability_percentile'])} | {_display(row['composite_quality'])} |"
            )
    return "\n".join(lines) + "\n"


def validation_summary(output: pd.DataFrame) -> dict[str, Any]:
    recomputed = output.apply(
        lambda row: composite_value(
            (
                row["fscore_completion_ratio_percentile"],
                row["roc_arithmetic_mean_percentile"],
                row["margin_stability_percentile"],
            )
        ),
        axis=1,
    )
    mismatches = sum(
        count != int(row["composite_components_used"])
        or value is None
        or not math.isclose(value, float(row["composite_quality"]), rel_tol=1e-12, abs_tol=1e-12)
        for (_, row), (value, count) in zip(output.iterrows(), recomputed)
    )
    ratios = output[["fscore_ranking_ratio", "fscore_completion_ratio_percentile"]].dropna()
    non_positive_roc = output.apply(
        lambda row: any(
            float(row[column]) <= 0
            for column in output.columns
            if column.startswith("roc_")
            and column[4:].isdigit()
            and pd.notna(row[column])
        ),
        axis=1,
    )
    geometric_empty = output["roc_geometric_mean"].isna()
    margin_numeric = pd.to_numeric(output["margin_stability"], errors="coerce")
    return {
        "composite_mismatches": int(mismatches),
        "ratio_distinct": int(ratios["fscore_ranking_ratio"].nunique()),
        "percentile_distinct": int(ratios["fscore_completion_ratio_percentile"].nunique()),
        "margin_infinite": int(pd.Series([math.isinf(value) for value in margin_numeric.dropna()]).sum()),
        "margin_negative": int(margin_numeric.lt(0).sum()),
        "non_positive_roc": int(non_positive_roc.sum()),
        "all_positive_roc": int((~non_positive_roc).sum()),
        "geometric_empty": int(geometric_empty.sum()),
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    output, evidence, roc_drops, margin_drops, fscore_difference_count = build()
    REPORT_PATH.write_text(
        render_report(output, evidence, roc_drops, margin_drops, fscore_difference_count),
        encoding="utf-8",
    )
    validation = validation_summary(output)
    print(f"rows={len(output)};unique={output['ticker'].nunique()}")
    print(f"fscore_preexisting_difference_rows={fscore_difference_count}")
    print(f"roc_years_used_distribution={_distribution(output['roc_years_used'])}")
    print(f"margin_years_used_distribution={_distribution(output['margin_years_used'])}")
    print(
        "franchise_history_status="
        + str(dict(sorted(Counter(output["franchise_history_status"]).items())))
    )
    print(f"composite_recomputation_mismatches={validation['composite_mismatches']}")
    print(
        f"fscore_ratio_distinct={validation['ratio_distinct']};"
        f"fscore_percentile_distinct={validation['percentile_distinct']}"
    )
    print(
        f"margin_stability_infinite={validation['margin_infinite']};"
        f"margin_stability_negative={validation['margin_negative']}"
    )
    print(
        f"non_positive_roc_tickers={validation['non_positive_roc']};"
        f"all_positive_roc_tickers={validation['all_positive_roc']};"
        f"roc_geometric_mean_empty={validation['geometric_empty']}"
    )
    print("external_data_network_calls=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
