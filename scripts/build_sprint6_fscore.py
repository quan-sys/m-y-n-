"""Build the nine settled Piotroski F-Score criteria from local annual data only.

Formulas copied verbatim from docs/SPEC_SPRINT_6.md section 2:
1. ROA > 0, where ROA = net_income_N / total_assets at end of N-1
2. CFO > 0, where CFO = cash flow from operations_N / total_assets at end of N-1
3. delta ROA > 0 (ROA_N > ROA_N-1)
4. CFO (scaled as in 2) > ROA (accrual criterion)
5. long-term leverage decreased: long_term_debt / average total assets,
   ratio_N < ratio_N-1
6. current ratio increased: (current assets / current liabilities),
   ratio_N > ratio_N-1
7. no new common shares issued during year N
8. gross margin increased: gross_margin_N > gross_margin_N-1
9. asset turnover increased: (revenue_N / total_assets at end of N-1) >
   (revenue_N-1 / total_assets at end of N-2)
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_sprint6_readiness import (  # noqa: E402
    CRITERION7_MISSING_INPUT,
    CRITERION7_NO_SHARE_INCREASE_CASH,
    CRITERION7_SCORE_0,
    CRITERION7_SCORE_1,
    CRITERION7_SHARE_INCREASE_NO_CASH,
    EVALUATION_DATE,
    EXPECTED_SURVIVORS,
    FUNDAMENTALS_ROOT,
    SURVIVORS_PATH,
    classify_criterion7_branch,
    eligible_annual_rows,
    item_value_status,
    latest_annual_frame,
)


OUTPUT_PATH = ROOT / "data" / "screener" / "sprint6_fscore.csv"
REPORT_PATH = ROOT / "docs" / "REPORT_SPRINT_6_FSCORE.md"
MIN_SCORED_CRITERIA = 7

NET_INCOME = "net_profit_loss_after_tax"
PARENT_NET_INCOME = "attributable_to_parent_company"
CFO = "net_cash_inflows_outflows_from_operating_activities"
TOTAL_ASSETS = "total_assets"
LONG_TERM_DEBT = "long_term_borrowings"
CURRENT_ASSETS = "current_assets"
CURRENT_LIABILITIES = "current_liabilities"
REVENUE = "net_sales"
GROSS_PROFIT = "gross_profit"
COGS = "cost_of_sales"
ISSUE_PROCEEDS = "proceeds_from_issue_of_shares"
COMMON_SHARES = "common_shares"


@dataclass(frozen=True)
class CriterionResult:
    result: int | None
    flag: str
    terms: tuple[tuple[str, Any], ...]


def _number(frame: pd.DataFrame, item_id: str, year: int, label: str) -> tuple[float | None, str]:
    value, status = item_value_status(frame, item_id, year)
    if status != "OK" or value is None:
        return None, f"{label}_{status if status != 'OK' else 'MISSING'}"
    return float(value), ""


def _terms(**values: Any) -> tuple[tuple[str, Any], ...]:
    return tuple(values.items())


def _unscored(flags: list[str], **terms: Any) -> CriterionResult:
    return CriterionResult(None, "|".join(flag for flag in flags if flag), _terms(**terms))


def _scored(value: bool, **terms: Any) -> CriterionResult:
    return CriterionResult(int(value), "", _terms(**terms))


def _positive_denominator(value: float | None, label: str) -> str:
    return f"{label}_NON_POSITIVE" if value is not None and value <= 0 else ""


def criterion7_score(
    common_n: float | None,
    common_n1: float | None,
    proceeds_n: float | None,
    *,
    common_n_status: str = "OK",
    common_n1_status: str = "OK",
    proceeds_n_status: str = "OK",
) -> tuple[CriterionResult, str, float | None]:
    branch, outcome, flag = classify_criterion7_branch(
        common_n,
        common_n1,
        proceeds_n,
        common_shares_n_status=common_n_status,
        common_shares_n_minus_1_status=common_n1_status,
        issue_proceeds_n_status=proceeds_n_status,
    )
    ratio = (
        proceeds_n / common_n
        if outcome == CRITERION7_NO_SHARE_INCREASE_CASH
        and common_n not in (None, 0)
        and proceeds_n is not None
        else None
    )
    terms = {
        "common_shares_N": common_n,
        "common_shares_N_minus_1": common_n1,
        "proceeds_from_issue_of_shares_N": proceeds_n,
        "branch": branch,
        "settled_case": outcome,
        "issue_proceeds_to_common_shares_ratio": ratio,
    }
    if branch == CRITERION7_SCORE_1:
        return CriterionResult(1, "", _terms(**terms)), branch, ratio
    if branch == CRITERION7_SCORE_0:
        return CriterionResult(0, "", _terms(**terms)), branch, ratio
    return CriterionResult(None, flag, _terms(**terms)), branch, ratio


def finalize_scores(results: list[CriterionResult]) -> dict[str, Any]:
    points = sum(result.result for result in results if result.result is not None)
    scored = sum(result.result is not None for result in results)
    unscored = len(results) - scored
    ratio = points / scored if scored else None
    eligible = scored >= MIN_SCORED_CRITERIA
    return {
        "F_SCORE_POINTS": points,
        "F_SCORE_CRITERIA_SCORED": scored,
        "F_SCORE_CRITERIA_UNSCORED": unscored,
        "fscore_ranking_ratio": ratio,
        "fscore_ranking_eligible": eligible,
        "fscore_confidence_flag": "" if eligible else "LOW_CONFIDENCE_SCORED_DENOMINATOR",
    }


def compute_ticker(
    survivor: dict[str, Any],
    income: pd.DataFrame,
    balance: pd.DataFrame,
    cash_flow: pd.DataFrame,
) -> tuple[dict[str, Any], dict[int, CriterionResult], bool]:
    ticker = str(survivor["ticker"]).strip().upper()
    year_n = int(survivor["annual_n"])
    year_n1 = int(survivor["annual_n_minus_1"])
    year_n2 = year_n1 - 1
    income = eligible_annual_rows(income, EVALUATION_DATE)
    balance = eligible_annual_rows(balance, EVALUATION_DATE)
    cash_flow = eligible_annual_rows(cash_flow, EVALUATION_DATE)

    net_n, net_n_flag = _number(income, NET_INCOME, year_n, "NET_INCOME_N")
    net_n1, net_n1_flag = _number(income, NET_INCOME, year_n1, "NET_INCOME_N_MINUS_1")
    parent_n, parent_n_flag = _number(
        income, PARENT_NET_INCOME, year_n, "PARENT_NET_INCOME_N"
    )
    cfo_n, cfo_n_flag = _number(cash_flow, CFO, year_n, "CFO_N")
    assets_n, assets_n_flag = _number(balance, TOTAL_ASSETS, year_n, "TOTAL_ASSETS_N")
    assets_n1, assets_n1_flag = _number(
        balance, TOTAL_ASSETS, year_n1, "TOTAL_ASSETS_N_MINUS_1"
    )
    assets_n2, assets_n2_flag = _number(
        balance, TOTAL_ASSETS, year_n2, "TOTAL_ASSETS_N_MINUS_2"
    )

    assets_n1_invalid = _positive_denominator(assets_n1, "TOTAL_ASSETS_N_MINUS_1")
    assets_n2_invalid = _positive_denominator(assets_n2, "TOTAL_ASSETS_N_MINUS_2")
    roa_n = net_n / assets_n1 if net_n is not None and assets_n1 and assets_n1 > 0 else None
    roa_n1 = (
        net_n1 / assets_n2 if net_n1 is not None and assets_n2 and assets_n2 > 0 else None
    )
    parent_roa = (
        parent_n / assets_n1
        if not parent_n_flag and parent_n is not None and assets_n1 and assets_n1 > 0
        else None
    )

    common_roa_terms = {
        f"net_income_N[{year_n}]": net_n,
        f"total_assets_N_minus_1[{year_n1}]": assets_n1,
        f"total_assets_N_minus_2[{year_n2}]": assets_n2,
        "ROA_N": roa_n,
    }
    flags_1 = [net_n_flag, assets_n1_flag, assets_n1_invalid]
    criterion_1 = (
        _unscored(flags_1, **common_roa_terms)
        if any(flags_1)
        else _scored(roa_n > 0, **common_roa_terms)
    )

    scaled_cfo = cfo_n / assets_n1 if cfo_n is not None and assets_n1 and assets_n1 > 0 else None
    terms_2 = {
        f"CFO_N[{year_n}]": cfo_n,
        f"total_assets_N_minus_1[{year_n1}]": assets_n1,
        "scaled_CFO_N": scaled_cfo,
    }
    flags_2 = [cfo_n_flag, assets_n1_flag, assets_n1_invalid]
    criterion_2 = (
        _unscored(flags_2, **terms_2)
        if any(flags_2)
        else _scored(scaled_cfo > 0, **terms_2)
    )

    terms_3 = {
        **common_roa_terms,
        f"net_income_N_minus_1[{year_n1}]": net_n1,
        "ROA_N_minus_1": roa_n1,
        "delta_ROA": roa_n - roa_n1 if roa_n is not None and roa_n1 is not None else None,
    }
    flags_3 = [
        net_n_flag,
        net_n1_flag,
        assets_n1_flag,
        assets_n2_flag,
        assets_n1_invalid,
        assets_n2_invalid,
    ]
    criterion_3 = (
        _unscored(flags_3, **terms_3)
        if any(flags_3)
        else _scored(roa_n > roa_n1, **terms_3)
    )

    terms_4 = {
        f"CFO_N[{year_n}]": cfo_n,
        f"net_income_N[{year_n}]": net_n,
        f"total_assets_N_minus_1[{year_n1}]": assets_n1,
        f"total_assets_N_minus_2[{year_n2}]": assets_n2,
        "scaled_CFO_N": scaled_cfo,
        "ROA_N": roa_n,
    }
    flags_4 = [cfo_n_flag, net_n_flag, assets_n1_flag, assets_n1_invalid]
    criterion_4 = (
        _unscored(flags_4, **terms_4)
        if any(flags_4)
        else _scored(scaled_cfo > roa_n, **terms_4)
    )

    debt_n, debt_n_flag = _number(balance, LONG_TERM_DEBT, year_n, "LONG_TERM_DEBT_N")
    debt_n1, debt_n1_flag = _number(
        balance, LONG_TERM_DEBT, year_n1, "LONG_TERM_DEBT_N_MINUS_1"
    )
    avg_assets_n = (
        (assets_n + assets_n1) / 2
        if assets_n is not None and assets_n1 is not None
        else None
    )
    avg_assets_n1 = (
        (assets_n1 + assets_n2) / 2
        if assets_n1 is not None and assets_n2 is not None
        else None
    )
    avg_n_invalid = _positive_denominator(avg_assets_n, "AVERAGE_TOTAL_ASSETS_N")
    avg_n1_invalid = _positive_denominator(avg_assets_n1, "AVERAGE_TOTAL_ASSETS_N_MINUS_1")
    leverage_n = debt_n / avg_assets_n if debt_n is not None and avg_assets_n and avg_assets_n > 0 else None
    leverage_n1 = (
        debt_n1 / avg_assets_n1
        if debt_n1 is not None and avg_assets_n1 and avg_assets_n1 > 0
        else None
    )
    terms_5 = {
        f"long_term_debt_N[{year_n}]": debt_n,
        f"long_term_debt_N_minus_1[{year_n1}]": debt_n1,
        f"total_assets_N[{year_n}]": assets_n,
        f"total_assets_N_minus_1[{year_n1}]": assets_n1,
        f"total_assets_N_minus_2[{year_n2}]": assets_n2,
        "average_total_assets_N": avg_assets_n,
        "average_total_assets_N_minus_1": avg_assets_n1,
        "long_term_leverage_N": leverage_n,
        "long_term_leverage_N_minus_1": leverage_n1,
    }
    flags_5 = [
        debt_n_flag,
        debt_n1_flag,
        assets_n_flag,
        assets_n1_flag,
        assets_n2_flag,
        avg_n_invalid,
        avg_n1_invalid,
    ]
    criterion_5 = (
        _unscored(flags_5, **terms_5)
        if any(flags_5)
        else _scored(leverage_n < leverage_n1, **terms_5)
    )

    current_assets_n, ca_n_flag = _number(balance, CURRENT_ASSETS, year_n, "CURRENT_ASSETS_N")
    current_assets_n1, ca_n1_flag = _number(
        balance, CURRENT_ASSETS, year_n1, "CURRENT_ASSETS_N_MINUS_1"
    )
    current_liabilities_n, cl_n_flag = _number(
        balance, CURRENT_LIABILITIES, year_n, "CURRENT_LIABILITIES_N"
    )
    current_liabilities_n1, cl_n1_flag = _number(
        balance, CURRENT_LIABILITIES, year_n1, "CURRENT_LIABILITIES_N_MINUS_1"
    )
    cl_n_invalid = _positive_denominator(current_liabilities_n, "CURRENT_LIABILITIES_N")
    cl_n1_invalid = _positive_denominator(
        current_liabilities_n1, "CURRENT_LIABILITIES_N_MINUS_1"
    )
    current_ratio_n = (
        current_assets_n / current_liabilities_n
        if current_assets_n is not None and current_liabilities_n and current_liabilities_n > 0
        else None
    )
    current_ratio_n1 = (
        current_assets_n1 / current_liabilities_n1
        if current_assets_n1 is not None
        and current_liabilities_n1
        and current_liabilities_n1 > 0
        else None
    )
    terms_6 = {
        f"current_assets_N[{year_n}]": current_assets_n,
        f"current_liabilities_N[{year_n}]": current_liabilities_n,
        f"current_assets_N_minus_1[{year_n1}]": current_assets_n1,
        f"current_liabilities_N_minus_1[{year_n1}]": current_liabilities_n1,
        "current_ratio_N": current_ratio_n,
        "current_ratio_N_minus_1": current_ratio_n1,
    }
    flags_6 = [ca_n_flag, ca_n1_flag, cl_n_flag, cl_n1_flag, cl_n_invalid, cl_n1_invalid]
    criterion_6 = (
        _unscored(flags_6, **terms_6)
        if any(flags_6)
        else _scored(current_ratio_n > current_ratio_n1, **terms_6)
    )

    common_n, common_n_status = item_value_status(balance, COMMON_SHARES, year_n)
    common_n1, common_n1_status = item_value_status(balance, COMMON_SHARES, year_n1)
    proceeds_n, proceeds_n_status = item_value_status(cash_flow, ISSUE_PROCEEDS, year_n)
    criterion_7, criterion7_branch, issue_ratio = criterion7_score(
        common_n,
        common_n1,
        proceeds_n,
        common_n_status=common_n_status,
        common_n1_status=common_n1_status,
        proceeds_n_status=proceeds_n_status,
    )
    criterion_7 = CriterionResult(
        criterion_7.result,
        criterion_7.flag,
        tuple(
            (
                f"{name}[{year_n}]"
                if name in {"common_shares_N", "proceeds_from_issue_of_shares_N"}
                else f"{name}[{year_n1}]"
                if name == "common_shares_N_minus_1"
                else name,
                value,
            )
            for name, value in criterion_7.terms
        ),
    )

    fallback_used = False

    def gross_margin(year: int, suffix: str) -> tuple[float | None, dict[str, Any], list[str], bool]:
        sales, sales_flag = _number(income, REVENUE, year, f"NET_SALES_{suffix}")
        gross, gross_status = item_value_status(income, GROSS_PROFIT, year)
        cogs, cogs_status = item_value_status(income, COGS, year)
        used = False
        flags: list[str] = [sales_flag, _positive_denominator(sales, f"NET_SALES_{suffix}")]
        if gross_status != "OK" or gross is None:
            if cogs_status == "OK" and cogs is not None and float(cogs) <= 0 and sales is not None:
                gross = sales + float(cogs)
                used = True
            else:
                flags.append(f"GROSS_PROFIT_{suffix}_{gross_status}")
                if cogs_status != "OK":
                    flags.append(f"COGS_{suffix}_{cogs_status}")
                elif cogs is not None and float(cogs) > 0:
                    flags.append(f"COGS_{suffix}_POSITIVE_FALLBACK_FORBIDDEN")
        margin = float(gross) / sales if gross is not None and sales and sales > 0 else None
        terms = {
            f"net_sales_{suffix}[{year}]": sales,
            f"gross_profit_{suffix}[{year}]": gross,
            f"cost_of_sales_{suffix}[{year}]": cogs,
            f"cost_of_sales_sign_{suffix}": (
                "NON_POSITIVE" if cogs_status == "OK" and cogs is not None and float(cogs) <= 0 else "NOT_USED"
            ),
            f"gross_profit_fallback_{suffix}": used,
            f"gross_margin_{suffix}": margin,
        }
        return margin, terms, [flag for flag in flags if flag], used

    margin_n, margin_terms_n, margin_flags_n, fallback_n = gross_margin(year_n, "N")
    margin_n1, margin_terms_n1, margin_flags_n1, fallback_n1 = gross_margin(year_n1, "N_minus_1")
    fallback_used = fallback_n or fallback_n1
    terms_8 = {**margin_terms_n, **margin_terms_n1}
    flags_8 = [*margin_flags_n, *margin_flags_n1]
    criterion_8 = (
        _unscored(flags_8, **terms_8)
        if flags_8
        else _scored(margin_n > margin_n1, **terms_8)
    )

    revenue_n, revenue_n_flag = _number(income, REVENUE, year_n, "REVENUE_N")
    revenue_n1, revenue_n1_flag = _number(income, REVENUE, year_n1, "REVENUE_N_MINUS_1")
    turnover_n = (
        revenue_n / assets_n1
        if revenue_n is not None and assets_n1 and assets_n1 > 0
        else None
    )
    turnover_n1 = (
        revenue_n1 / assets_n2
        if revenue_n1 is not None and assets_n2 and assets_n2 > 0
        else None
    )
    terms_9 = {
        f"revenue_N[{year_n}]": revenue_n,
        f"revenue_N_minus_1[{year_n1}]": revenue_n1,
        f"total_assets_N_minus_1[{year_n1}]": assets_n1,
        f"total_assets_N_minus_2[{year_n2}]": assets_n2,
        "asset_turnover_N": turnover_n,
        "asset_turnover_N_minus_1": turnover_n1,
    }
    flags_9 = [
        revenue_n_flag,
        revenue_n1_flag,
        assets_n1_flag,
        assets_n2_flag,
        assets_n1_invalid,
        assets_n2_invalid,
    ]
    criterion_9 = (
        _unscored(flags_9, **terms_9)
        if any(flags_9)
        else _scored(turnover_n > turnover_n1, **terms_9)
    )

    results = {
        1: criterion_1,
        2: criterion_2,
        3: criterion_3,
        4: criterion_4,
        5: criterion_5,
        6: criterion_6,
        7: criterion_7,
        8: criterion_8,
        9: criterion_9,
    }
    row: dict[str, Any] = {
        "ticker": ticker,
        "exchange": survivor.get("exchange", ""),
        "icb2": survivor.get("icb2", ""),
        "annual_n": year_n,
        "annual_n_minus_1": year_n1,
        "annual_n_minus_2": year_n2,
        "evaluation_date": EVALUATION_DATE,
        "criterion_7_branch": criterion7_branch,
        "roa_parent_only": parent_roa,
        "issue_proceeds_to_common_shares_ratio": issue_ratio,
        "non_positive_revenue_n_minus_1": bool(
            revenue_n1 is not None and revenue_n1 <= 0
        ),
        "cross_step_flag": (
            "SPRINT5_TTM_INCOMPLETE"
            if ticker in {"NTC", "TRC"}
            else "SPRINT5_QUARTERLY_BALANCE_MISSING_TEV_MISSING"
            if ticker == "DBC"
            else ""
        ),
    }
    for number, result in results.items():
        row[f"criterion_{number}_result"] = result.result
        row[f"criterion_{number}_flag"] = result.flag
    row.update(finalize_scores(list(results.values())))
    return row, results, fallback_used


def build() -> tuple[pd.DataFrame, dict[str, dict[int, CriterionResult]], list[str]]:
    survivors = pd.read_csv(SURVIVORS_PATH)
    tickers = survivors["ticker"].astype(str).str.strip().str.upper()
    if len(survivors) != EXPECTED_SURVIVORS or tickers.nunique() != EXPECTED_SURVIVORS:
        raise ValueError(
            f"expected {EXPECTED_SURVIVORS} unique survivors; "
            f"rows={len(survivors)} unique={tickers.nunique()}"
        )
    survivors = survivors.copy()
    survivors["ticker"] = tickers
    rows: list[dict[str, Any]] = []
    handchecks: dict[str, dict[int, CriterionResult]] = {}
    fallback_tickers: list[str] = []
    for survivor in survivors.to_dict("records"):
        ticker = str(survivor["ticker"])
        frames = {}
        for statement in ("income_statement", "balance_sheet", "cash_flow"):
            frame, _, exists = latest_annual_frame(ticker, statement, FUNDAMENTALS_ROOT)
            if not exists:
                frame = pd.DataFrame()
            frames[statement] = frame
        row, evidence, fallback = compute_ticker(
            survivor,
            frames["income_statement"],
            frames["balance_sheet"],
            frames["cash_flow"],
        )
        rows.append(row)
        if ticker in {"VNM", "DBC", "MSN"}:
            handchecks[ticker] = evidence
        if fallback:
            fallback_tickers.append(ticker)
    output = pd.DataFrame(rows)
    if len(output) != EXPECTED_SURVIVORS or output["ticker"].nunique() != EXPECTED_SURVIVORS:
        raise AssertionError("F-Score output is not exactly one row per survivor")
    if not output["F_SCORE_CRITERIA_SCORED"].add(
        output["F_SCORE_CRITERIA_UNSCORED"]
    ).eq(9).all():
        raise AssertionError("scored plus unscored does not equal nine for every row")
    return output, handchecks, fallback_tickers


def _display(value: Any) -> str:
    if value is None or value is pd.NA or (isinstance(value, float) and pd.isna(value)):
        return "EMPTY"
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else format(value, ".17g")
    return str(value).replace("|", "\\|")


def render_report(
    output: pd.DataFrame,
    handchecks: dict[str, dict[int, CriterionResult]],
    fallback_tickers: list[str],
) -> str:
    points = Counter(int(value) for value in output["F_SCORE_POINTS"])
    scored = Counter(int(value) for value in output["F_SCORE_CRITERIA_SCORED"])
    branch_counts = Counter(str(value) for value in output["criterion_7_branch"])
    lines = [
        "# Sprint 6 production F-Score report",
        "",
        f"- Evaluation date: `{EVALUATION_DATE}`.",
        f"- `data/screener/sprint6_fscore.csv` data rows: `{len(output)}`; unique tickers: `{output['ticker'].nunique()}`.",
        "- These annual figures are restated data usable for ranking today, not point-in-time evidence of what was published then.",
        "- Franchise Power, ROC, margin stability, percentiles, composite quality, and candidate-list quality ranking computed: `0`.",
        f"- Gross-profit fallback ticker count: `{len(fallback_tickers)}`.",
        "- Gross-profit fallback ticker list: "
        + (", ".join(f"`{ticker}`" for ticker in fallback_tickers) if fallback_tickers else "`NONE`")
        + ".",
        "",
        "## F_SCORE_POINTS distribution",
        "",
        "| F_SCORE_POINTS | ticker count |",
        "|---:|---:|",
    ]
    for value in sorted(points):
        lines.append(f"| {value} | {points[value]} |")
    lines.extend(
        [
            "",
            "## F_SCORE_CRITERIA_SCORED distribution",
            "",
            "| F_SCORE_CRITERIA_SCORED | ticker count |",
            "|---:|---:|",
        ]
    )
    for value in sorted(scored):
        lines.append(f"| {value} | {scored[value]} |")
    lines.extend(
        [
            "",
            "## Criterion 7 branch counts",
            "",
            "| criterion_7_branch | ticker count |",
            "|---|---:|",
        ]
    )
    for branch in (
        CRITERION7_SCORE_1,
        CRITERION7_SCORE_0,
        CRITERION7_SHARE_INCREASE_NO_CASH,
        CRITERION7_MISSING_INPUT,
    ):
        lines.append(f"| `{branch}` | {branch_counts[branch]} |")
    lines.extend(
        [
            "",
            "## UNSCORED counts",
            "",
            "| criterion | UNSCORED count |",
            "|---:|---:|",
        ]
    )
    for number in range(1, 10):
        lines.append(f"| {number} | {int(output[f'criterion_{number}_result'].isna().sum())} |")
    flag_counts: Counter[str] = Counter()
    for number in range(1, 10):
        for flag in output[f"criterion_{number}_flag"].fillna("").astype(str):
            for part in filter(None, flag.split("|")):
                flag_counts[part] += 1
    lines.extend(["", "| UNSCORED flag | ticker count |", "|---|---:|"])
    if flag_counts:
        for flag in sorted(flag_counts):
            lines.append(f"| `{flag}` | {flag_counts[flag]} |")
    else:
        lines.append("| `NONE` | 0 |")
    non_positive_revenue = output.loc[
        output["non_positive_revenue_n_minus_1"], "ticker"
    ].astype(str).tolist()
    lines.extend(
        [
            "",
            "## Non-positive prior-year revenue",
            "",
            "- Tickers with `non_positive_revenue_n_minus_1 = True`: "
            + (
                ", ".join(f"`{ticker}`" for ticker in non_positive_revenue)
                if non_positive_revenue
                else "`NONE`"
            )
            + ".",
            "- Criterion 8 is UNSCORED for these tickers because the gross-margin denominator is invalid.",
            "- Criterion 9 still scored for these tickers. A non-positive numerator makes its \"turnover increased\" comparison economically unreliable; this is flagged for Sprint 8 and deliberately not changed here.",
            "- When the Sprint 6 Franchise Power margin-stability computation is built later, it must DROP such a year rather than treat its gross margin as zero.",
        ]
    )
    for ticker in ("VNM", "DBC", "MSN"):
        lines.extend(
            [
                "",
                f"## {ticker} hand-check",
                "",
                "| criterion | every intermediate term (raw value and source year) | result | flag |",
                "|---:|---|---:|---|",
            ]
        )
        for number in range(1, 10):
            result = handchecks[ticker][number]
            terms = "; ".join(f"{name}={_display(value)}" for name, value in result.terms)
            lines.append(
                f"| {number} | {terms} | {_display(result.result)} | "
                f"{_display(result.flag) if result.flag else ''} |"
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    output, handchecks, fallback_tickers = build()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_PATH, index=False, lineterminator="\n")
    REPORT_PATH.write_text(
        render_report(output, handchecks, fallback_tickers), encoding="utf-8"
    )
    print(f"rows={len(output)}; unique={output['ticker'].nunique()}")
    print(
        "criterion7_branches="
        + ";".join(
            f"{branch}:{int(output['criterion_7_branch'].eq(branch).sum())}"
            for branch in (
                CRITERION7_SCORE_1,
                CRITERION7_SCORE_0,
                CRITERION7_SHARE_INCREASE_NO_CASH,
                CRITERION7_MISSING_INPUT,
            )
        )
    )
    print(
        "fscore_points_distribution="
        + ";".join(
            f"{value}:{count}"
            for value, count in sorted(Counter(output["F_SCORE_POINTS"]).items())
        )
    )
    print(
        "fscore_scored_distribution="
        + ";".join(
            f"{value}:{count}"
            for value, count in sorted(Counter(output["F_SCORE_CRITERIA_SCORED"]).items())
        )
    )
    print(f"gross_profit_fallback_tickers={'|'.join(fallback_tickers) or 'NONE'}")
    print("external_data_network_calls=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
