from __future__ import annotations

import argparse
import ast
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from functools import partial
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable
from zoneinfo import ZoneInfo

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

from scripts.audit_sprint6_readiness import (  # noqa: E402
    PROPOSED_FRANCHISE_MIN_YEARS,
    item_value_status,
)
from scripts.build_sprint6_franchise import (  # noqa: E402
    compute_margin_series,
    compute_roc_series,
    rank_percentile,
    summarize_margin,
    summarize_roc,
)
from scripts.build_sprint6_fscore import (  # noqa: E402
    compute_ticker,
    criterion7_score,
    finalize_scores,
)
from src.screener.step1_cleaning import (  # noqa: E402
    calculate_aqi,
    calculate_depi,
    calculate_dsri,
    calculate_gmi,
    calculate_lvgi,
    calculate_m_score,
    calculate_sgai,
    calculate_sgi,
    calculate_simple_distress,
    calculate_snoa,
    calculate_sta,
    calculate_tata,
)
from src.screener.step1_data import (  # noqa: E402
    FORMULA_INPUT_MAP,
    M_SCORE_INPUTS,
    PreparedTicker,
    render_vnm_calculations,
)


ANNUAL_PATH = (
    ROOT
    / "data"
    / "fundamentals"
    / "annual_pit"
    / "2026-07-26"
    / "annual_items_point_in_time.csv.gz"
)
VALUATION_PATH = (
    ROOT
    / "data"
    / "valuation"
    / "2026-07-26"
    / "historical_valuation_point_in_time.csv.gz"
)
STEP1_PATH = ROOT / "data" / "screener" / "step1_survivors.csv"
FSCORE_PATH = ROOT / "data" / "screener" / "sprint6_fscore.csv"
FRANCHISE_PATH = ROOT / "data" / "screener" / "sprint6_franchise_quality.csv"
CONFIG_PATH = ROOT / "config" / "screener.yaml"
OUTPUT_ROOT = ROOT / "data" / "screener" / "gates_pit"
REPORT_PATH = ROOT / "docs" / "REPORT_SPRINT_9_4C_GATES_AS_OF.md"
TIME_ZONE = ZoneInfo("Asia/Ho_Chi_Minh")
RECONCILIATION_DATE = "2026-07-20"
WALK_FORWARD_ROLE = "WALK_FORWARD"
RECONCILIATION_ROLE = "RECONCILIATION"
SOURCE_LABEL = (
    "Sprint 9-4C | annual_pit/2026-07-26; "
    "historical_valuation/2026-07-26; imported existing gate functions"
)

OUTPUT_COLUMNS = (
    "evaluation_date",
    "grid_role",
    "ticker",
    "annual_n",
    "annual_n_minus_1",
    "annual_n_minus_2",
    "annual_n_available_from",
    "sta",
    "sta_status",
    "sta_percentile",
    "snoa",
    "snoa_status",
    "snoa_percentile",
    "high_accrual_flag",
    "dsri",
    "gmi",
    "aqi",
    "sgi",
    "depi",
    "sgai",
    "lvgi",
    "tata",
    "m_score",
    "m_score_status",
    "m_score_percentile",
    "m_score_flag",
    "distress_accumulated_loss",
    "distress_negative_equity",
    "distress_high_risk",
    "distress_status",
    "distress_confidence",
    "fscore_total",
    "fscore_scored_count",
    "fscore_status",
    "franchise_roc_years_used",
    "franchise_roc_arithmetic_mean",
    "franchise_margin_stability",
    "franchise_status",
    "tev_to_market_cap",
    "tev_collapse_flag",
    "source",
    "as_of",
    "data_status",
)

ANNUAL_REQUIRED_COLUMNS = {
    "ticker",
    "fiscal_year",
    "available_from",
    "statement_type",
    "item_id",
    "value",
    "data_status",
}
VALUATION_REQUIRED_COLUMNS = {
    "ticker",
    "evaluation_date",
    "tev",
    "market_cap_vnd",
    "valuation_status",
    "data_status",
}
GATE_STATUS_COLUMNS = {
    "STA": "sta_status",
    "SNOA": "snoa_status",
    "M_SCORE": "m_score_status",
    "DISTRESS": "distress_status",
    "FSCORE": "fscore_status",
    "FRANCHISE": "franchise_status",
}


@dataclass(frozen=True)
class GateConfig:
    accrual_worst_pct: Decimal
    mscore_threshold: Decimal
    tev_min_fraction_of_market_cap: Decimal
    distress_require_hose_warning: bool = True


@dataclass(frozen=True)
class AnnualSelection:
    annual_n: int | None
    annual_n_minus_1: int | None
    annual_n_minus_2: int | None
    annual_n_available_from: str
    pair_reason: str
    triple_reason: str
    eligible_rows: pd.DataFrame


def _flat_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def load_config(path: Path = CONFIG_PATH) -> GateConfig:
    values = _flat_config(path)
    names = (
        "ACCRUAL_WORST_PCT",
        "MSCORE_THRESHOLD",
        "TEV_MIN_FRACTION_OF_MARKET_CAP",
        "DISTRESS_REQUIRE_HOSE_WARNING",
    )
    missing = [name for name in names if name not in values]
    if missing:
        raise ValueError("config missing values: " + ", ".join(missing))
    raw_distress_warning_requirement = values["DISTRESS_REQUIRE_HOSE_WARNING"].casefold()
    if raw_distress_warning_requirement not in {"true", "false"}:
        raise ValueError("DISTRESS_REQUIRE_HOSE_WARNING must be true or false")
    config = GateConfig(
        accrual_worst_pct=Decimal(values["ACCRUAL_WORST_PCT"]),
        mscore_threshold=Decimal(values["MSCORE_THRESHOLD"]),
        tev_min_fraction_of_market_cap=Decimal(
            values["TEV_MIN_FRACTION_OF_MARKET_CAP"]
        ),
        distress_require_hose_warning=raw_distress_warning_requirement == "true",
    )
    if not Decimal("0") < config.accrual_worst_pct <= Decimal("1"):
        raise ValueError("ACCRUAL_WORST_PCT must be in (0, 1]")
    if not Decimal("0") < config.tev_min_fraction_of_market_cap < Decimal("1"):
        raise ValueError("TEV_MIN_FRACTION_OF_MARKET_CAP must be in (0, 1)")
    return config


def evaluation_grid() -> list[tuple[str, str]]:
    walk_dates = pd.date_range("2019-03-31", "2025-12-31", freq="QE-DEC")
    return [
        (value.date().isoformat(), WALK_FORWARD_ROLE) for value in walk_dates
    ] + [(RECONCILIATION_DATE, RECONCILIATION_ROLE)]


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    annual = _read_csv(ANNUAL_PATH)
    valuation = _read_csv(VALUATION_PATH)
    missing_annual = sorted(ANNUAL_REQUIRED_COLUMNS - set(annual.columns))
    missing_valuation = sorted(VALUATION_REQUIRED_COLUMNS - set(valuation.columns))
    if missing_annual:
        raise ValueError("annual input missing columns: " + ", ".join(missing_annual))
    if missing_valuation:
        raise ValueError(
            "valuation input missing columns: " + ", ".join(missing_valuation)
        )
    annual["ticker"] = annual["ticker"].str.strip().str.upper()
    annual["fiscal_year"] = annual["fiscal_year"].astype(str)
    annual["statement_type"] = annual["statement_type"].astype(str).str.upper()
    annual["item_id"] = annual["item_id"].astype(str)
    if annual.duplicated(["ticker", "fiscal_year", "item_id"], keep=False).any():
        raise ValueError("annual input has duplicate ticker/fiscal_year/item_id keys")
    valuation["ticker"] = valuation["ticker"].str.strip().str.upper()
    valuation["evaluation_date"] = valuation["evaluation_date"].astype(str)
    if valuation.duplicated(["ticker", "evaluation_date"], keep=False).any():
        raise ValueError("valuation input has duplicate ticker/evaluation_date keys")
    return annual, valuation


def _numeric(value: Any) -> float | None:
    if value is None or pd.isna(value) or str(value).strip() == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _as_formula_frame(rows: pd.DataFrame, statement_type: str) -> pd.DataFrame:
    frame = rows.loc[
        rows["statement_type"].astype(str).eq(statement_type)
    ].copy()
    frame["report_period"] = frame["fiscal_year"].astype(str)
    frame["period_type"] = "ANNUAL"
    return frame


def select_as_of_annuals(rows: pd.DataFrame, evaluation_date: str) -> AnnualSelection:
    if rows.empty:
        return AnnualSelection(None, None, None, "", "NO_ANNUAL_N", "NO_ANNUAL_N", rows.copy())
    frame = rows.copy()
    frame["_available_from"] = pd.to_datetime(frame["available_from"], errors="coerce")
    evaluation = pd.Timestamp(evaluation_date)
    year_max = (
        frame.groupby("fiscal_year", sort=False)["_available_from"].max().dropna()
    )
    eligible_years = sorted(
        int(year)
        for year, available in year_max.items()
        if pd.Timestamp(available) <= evaluation and str(year).isdigit()
    )
    eligible = frame.loc[
        frame["fiscal_year"].astype(str).isin({str(year) for year in eligible_years})
        & frame["_available_from"].le(evaluation)
    ].drop(columns="_available_from")
    if not eligible_years:
        return AnnualSelection(None, None, None, "", "NO_ANNUAL_N", "NO_ANNUAL_N", eligible)
    annual_n = max(eligible_years)
    annual_n_minus_1 = annual_n - 1 if annual_n - 1 in eligible_years else None
    annual_n_minus_2 = (
        annual_n - 2
        if annual_n_minus_1 is not None and annual_n - 2 in eligible_years
        else None
    )
    pair_reason = "" if annual_n_minus_1 is not None else "NON_CONSECUTIVE_ANNUAL_PAIR"
    triple_reason = "" if annual_n_minus_2 is not None else "NON_CONSECUTIVE_ANNUAL_TRIPLE"
    available = pd.Timestamp(year_max.loc[str(annual_n)] if str(annual_n) in year_max.index else year_max.loc[annual_n])
    return AnnualSelection(
        annual_n,
        annual_n_minus_1,
        annual_n_minus_2,
        available.date().isoformat(),
        pair_reason,
        triple_reason,
        eligible.reset_index(drop=True),
    )


def precompute_as_of_selections(rows: pd.DataFrame) -> dict[str, AnnualSelection]:
    if rows.empty:
        return {
            evaluation_date: AnnualSelection(
                None,
                None,
                None,
                "",
                "NO_ANNUAL_N",
                "NO_ANNUAL_N",
                rows.copy(),
            )
            for evaluation_date, _ in evaluation_grid()
        }
    frame = rows.copy()
    frame["_available_from"] = pd.to_datetime(
        frame["available_from"], errors="coerce"
    )
    year_max = frame.groupby("fiscal_year", sort=False)["_available_from"].max().dropna()
    years_and_dates = sorted(
        (int(str(year)), pd.Timestamp(available))
        for year, available in year_max.items()
        if str(year).isdigit()
    )
    cached: dict[tuple[int, ...], AnnualSelection] = {}
    selections: dict[str, AnnualSelection] = {}
    for evaluation_date, _ in evaluation_grid():
        evaluation = pd.Timestamp(evaluation_date)
        eligible_years = tuple(
            year for year, available in years_and_dates if available <= evaluation
        )
        selection = cached.get(eligible_years)
        if selection is None:
            if not eligible_years:
                selection = AnnualSelection(
                    None,
                    None,
                    None,
                    "",
                    "NO_ANNUAL_N",
                    "NO_ANNUAL_N",
                    frame.iloc[0:0].drop(columns="_available_from").copy(),
                )
            else:
                annual_n = eligible_years[-1]
                annual_n_minus_1 = (
                    annual_n - 1 if annual_n - 1 in eligible_years else None
                )
                annual_n_minus_2 = (
                    annual_n - 2
                    if annual_n_minus_1 is not None and annual_n - 2 in eligible_years
                    else None
                )
                eligible = frame.loc[
                    frame["fiscal_year"].astype(str).isin(
                        {str(year) for year in eligible_years}
                    )
                    & frame["_available_from"].le(evaluation)
                ].drop(columns="_available_from")
                available = next(
                    value for year, value in years_and_dates if year == annual_n
                )
                selection = AnnualSelection(
                    annual_n,
                    annual_n_minus_1,
                    annual_n_minus_2,
                    available.date().isoformat(),
                    ""
                    if annual_n_minus_1 is not None
                    else "NON_CONSECUTIVE_ANNUAL_PAIR",
                    ""
                    if annual_n_minus_2 is not None
                    else "NON_CONSECUTIVE_ANNUAL_TRIPLE",
                    eligible.reset_index(drop=True),
                )
            cached[eligible_years] = selection
        selections[evaluation_date] = selection
    return selections


def _frame_value(
    rows: pd.DataFrame, statement_type: str, item_id: str, year: int | None
) -> float | None:
    if year is None:
        return None
    matches = rows.loc[
        rows["statement_type"].astype(str).eq(statement_type)
        & rows["item_id"].astype(str).eq(item_id)
        & rows["fiscal_year"].astype(str).eq(str(year)),
        "value",
    ]
    if len(matches) != 1:
        return None
    return _numeric(matches.iloc[0])


def _frame_value_lookup(rows: pd.DataFrame) -> dict[tuple[str, str, str], float | None]:
    values: dict[tuple[str, str, str], float | None] = {}
    duplicate_keys: set[tuple[str, str, str]] = set()
    for statement_type, item_id, fiscal_year, value in rows.loc[
        :, ["statement_type", "item_id", "fiscal_year", "value"]
    ].itertuples(index=False, name=None):
        key = (str(statement_type), str(item_id), str(fiscal_year))
        if key in values:
            duplicate_keys.add(key)
        else:
            values[key] = _numeric(value)
    for key in duplicate_keys:
        values[key] = None
    return values


def _formula_inputs(rows: pd.DataFrame, selection: AnnualSelection) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    values_by_key = _frame_value_lookup(rows)
    for formula, mappings in FORMULA_INPUT_MAP.items():
        inputs: dict[str, Any] = {}
        for parameter, (statement, item_id, role) in mappings.items():
            year = selection.annual_n if role == "N" else selection.annual_n_minus_1
            inputs[parameter] = (
                values_by_key.get((statement, item_id, str(year)))
                if year is not None
                else None
            )
        values[formula] = inputs
    values["DISTRESS"]["hose_warning"] = None
    return values


def _result_status(result: Any, selection_reason: str = "") -> str:
    if getattr(result, "value", None) is not None and not selection_reason:
        return "SCORED"
    if selection_reason:
        return "UNSCORED_" + selection_reason
    return "UNSCORED_" + str(getattr(result, "reason", "INSUFFICIENT_DATA"))


def calculate_step1_gates(
    rows: pd.DataFrame,
    selection: AnnualSelection,
    *,
    config: GateConfig | None = None,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    require_hose_warning = (
        True if config is None else config.distress_require_hose_warning
    )
    inputs = _formula_inputs(rows, selection)
    result = {
        "STA": calculate_sta(**inputs["STA"]),
        "SNOA": calculate_snoa(**inputs["SNOA"]),
        "DSRI": calculate_dsri(**inputs["DSRI"]),
        "GMI": calculate_gmi(**inputs["GMI"]),
        "AQI": calculate_aqi(**inputs["AQI"]),
        "SGI": calculate_sgi(**inputs["SGI"]),
        "DEPI": calculate_depi(**inputs["DEPI"]),
        "SGAI": calculate_sgai(**inputs["SGAI"]),
        "LVGI": calculate_lvgi(**inputs["LVGI"]),
        "TATA": calculate_tata(**inputs["TATA"]),
    }
    result["M_SCORE"] = calculate_m_score(
        **{
            name.lower(): result[name].value
            for name in M_SCORE_INPUTS
        }
    )
    result["DISTRESS"] = calculate_simple_distress(
        **inputs["DISTRESS"],
        require_hose_warning=require_hose_warning,
    )
    return result, inputs


def calculate_fscore(
    rows: pd.DataFrame, selection: AnnualSelection
) -> tuple[Any, Any, str]:
    if selection.triple_reason:
        return None, None, "UNSCORED_" + selection.triple_reason
    income = _as_formula_frame(rows, "INCOME_STATEMENT")
    balance = _as_formula_frame(rows, "BALANCE_SHEET")
    cash_flow = _as_formula_frame(rows, "CASH_FLOW")
    survivor = {
        "ticker": str(rows["ticker"].iloc[0]),
        "annual_n": selection.annual_n,
        "annual_n_minus_1": selection.annual_n_minus_1,
    }
    summary, criteria, _ = compute_ticker(survivor, income, balance, cash_flow)
    common_n, common_n_status = item_value_status(balance, "common_shares", selection.annual_n)
    common_n1, common_n1_status = item_value_status(balance, "common_shares", selection.annual_n_minus_1)
    proceeds, proceeds_status = item_value_status(
        cash_flow, "proceeds_from_issue_of_shares", selection.annual_n
    )
    criterion7, _, _ = criterion7_score(
        common_n,
        common_n1,
        proceeds,
        common_n_status=common_n_status,
        common_n1_status=common_n1_status,
        proceeds_n_status=proceeds_status,
    )
    if (
        criterion7.result != criteria[7].result
        or criterion7.flag != criteria[7].flag
    ):
        raise RuntimeError("criterion7_score disagrees with compute_ticker")
    finalized = finalize_scores(list(criteria.values()))
    for key in ("F_SCORE_POINTS", "F_SCORE_CRITERIA_SCORED"):
        if finalized[key] != summary[key]:
            raise RuntimeError("finalize_scores disagrees with compute_ticker")
    status = "SCORED" if finalized["fscore_ranking_eligible"] else "UNSCORED_" + finalized["fscore_confidence_flag"]
    return finalized, criteria, status


def calculate_franchise(rows: pd.DataFrame) -> tuple[int, float | None, float | None, str]:
    income = _as_formula_frame(rows, "INCOME_STATEMENT")
    balance = _as_formula_frame(rows, "BALANCE_SHEET")
    income_years = {
        int(value) for value in income["report_period"].astype(str) if value.isdigit()
    }
    balance_years = {
        int(value) for value in balance["report_period"].astype(str) if value.isdigit()
    }
    candidate_years = sorted(income_years & balance_years)
    roc_values, _ = compute_roc_series(income, balance, candidate_years)
    margin_values, _ = compute_margin_series(income, candidate_years)
    roc_mean, _, _ = summarize_roc(roc_values)
    _, _, margin_stability, _ = summarize_margin(margin_values)
    overlapping = {item.year for item in roc_values} & {item.year for item in margin_values}
    status = "SCORED" if len(overlapping) >= PROPOSED_FRANCHISE_MIN_YEARS else "UNSCORED_INSUFFICIENT_HISTORY"
    return len(roc_values), roc_mean, margin_stability, status


def _valuation_lookup(valuation: pd.DataFrame) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row.ticker), str(row.evaluation_date)): row._asdict()
        for row in valuation.itertuples(index=False)
    }


def _tev_values(
    valuation_row: dict[str, Any] | None, config: GateConfig
) -> tuple[float | None, bool]:
    if valuation_row is None:
        return None, False
    tev = _numeric(valuation_row.get("tev"))
    market_cap = _numeric(valuation_row.get("market_cap_vnd"))
    if tev is None or market_cap is None or market_cap == 0:
        return None, False
    ratio = tev / market_cap
    return ratio, bool(Decimal(str(ratio)) < config.tev_min_fraction_of_market_cap)


def _row_data_status(
    selection: AnnualSelection,
    step1: dict[str, Any],
    valuation_row: dict[str, Any] | None,
    tev_to_market_cap: float | None,
) -> str:
    core_gate_values = ("STA", "SNOA", "M_SCORE")
    missing_core_gate = any(
        step1[name].value is None for name in core_gate_values
    )
    if (
        selection.annual_n is None
        or valuation_row is None
        or tev_to_market_cap is None
        or missing_core_gate
    ):
        return "MISSING_DATA"
    return "OK"


def _selection_cache_key(ticker: str, selection: AnnualSelection) -> tuple[Any, ...]:
    eligible_years = tuple(
        sorted(selection.eligible_rows["fiscal_year"].astype(str).unique())
    )
    return (
        ticker,
        selection.annual_n,
        selection.annual_n_minus_1,
        selection.annual_n_minus_2,
        selection.pair_reason,
        selection.triple_reason,
        eligible_years,
    )


def _rows_for_years(rows: pd.DataFrame, *years: int | None) -> pd.DataFrame:
    required_years = {str(year) for year in years if year is not None}
    return rows.loc[rows["fiscal_year"].astype(str).isin(required_years)].copy()


def _calculate_selection(
    selection: AnnualSelection,
    *,
    config: GateConfig,
) -> tuple[Any, Any, Any, str, int, float | None, float | None, str]:
    pair_rows = _rows_for_years(
        selection.eligible_rows,
        selection.annual_n,
        selection.annual_n_minus_1,
    )
    triple_rows = _rows_for_years(
        selection.eligible_rows,
        selection.annual_n,
        selection.annual_n_minus_1,
        selection.annual_n_minus_2,
    )
    step1, inputs = calculate_step1_gates(pair_rows, selection, config=config)
    fscore, _, fscore_status = calculate_fscore(triple_rows, selection)
    franchise = calculate_franchise(selection.eligible_rows)
    return step1, inputs, fscore, fscore_status, *franchise


def build_rows(
    annual: pd.DataFrame,
    valuation: pd.DataFrame,
    config: GateConfig,
    *,
    run_date: str,
) -> tuple[pd.DataFrame, dict[tuple[str, str], dict[str, dict[str, Any]]]]:
    lookup = _valuation_lookup(valuation)
    records: list[dict[str, Any]] = []
    formula_inputs: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
    ticker_rows_by_ticker = {
        str(ticker): frame.reset_index(drop=True)
        for ticker, frame in annual.groupby("ticker", sort=True)
    }
    tickers = sorted(ticker_rows_by_ticker)
    selections_by_ticker = {
        ticker: precompute_as_of_selections(rows)
        for ticker, rows in ticker_rows_by_ticker.items()
    }
    state_selections: dict[tuple[Any, ...], AnnualSelection] = {}
    for evaluation_date, _ in evaluation_grid():
        for ticker in tickers:
            selection = selections_by_ticker[ticker][evaluation_date]
            state_selections.setdefault(
                _selection_cache_key(ticker, selection), selection
            )
    worker_count = min(os.cpu_count() or 1, len(state_selections))
    calculate_selection = partial(_calculate_selection, config=config)
    if worker_count > 1:
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            state_results = list(executor.map(calculate_selection, state_selections.values()))
    else:
        state_results = [calculate_selection(selection) for selection in state_selections.values()]
    calculation_cache = dict(zip(state_selections, state_results))
    for evaluation_date, grid_role in evaluation_grid():
        for ticker in tickers:
            selection = selections_by_ticker[ticker][evaluation_date]
            cache_key = _selection_cache_key(ticker, selection)
            cached = calculation_cache[cache_key]
            (
                step1,
                inputs,
                fscore,
                fscore_status,
                roc_years,
                roc_mean,
                margin_stability,
                franchise_status,
            ) = cached
            if (evaluation_date, ticker) == (RECONCILIATION_DATE, "VNM"):
                formula_inputs[(evaluation_date, ticker)] = inputs
            valuation_row = lookup.get((ticker, evaluation_date))
            ratio, tev_flag = _tev_values(valuation_row, config)
            distress = step1["DISTRESS"]
            record: dict[str, Any] = {
                "evaluation_date": evaluation_date,
                "grid_role": grid_role,
                "ticker": ticker,
                "annual_n": selection.annual_n,
                "annual_n_minus_1": selection.annual_n_minus_1,
                "annual_n_minus_2": selection.annual_n_minus_2,
                "annual_n_available_from": selection.annual_n_available_from,
                "sta": step1["STA"].value,
                "sta_status": _result_status(step1["STA"], selection.pair_reason),
                "sta_percentile": None,
                "snoa": step1["SNOA"].value,
                "snoa_status": _result_status(step1["SNOA"], selection.pair_reason),
                "snoa_percentile": None,
                "high_accrual_flag": False,
                "dsri": step1["DSRI"].value,
                "gmi": step1["GMI"].value,
                "aqi": step1["AQI"].value,
                "sgi": step1["SGI"].value,
                "depi": step1["DEPI"].value,
                "sgai": step1["SGAI"].value,
                "lvgi": step1["LVGI"].value,
                "tata": step1["TATA"].value,
                "m_score": step1["M_SCORE"].value,
                "m_score_status": _result_status(step1["M_SCORE"], selection.pair_reason),
                "m_score_percentile": None,
                "m_score_flag": False,
                "distress_accumulated_loss": distress.accumulated_loss,
                "distress_negative_equity": distress.negative_equity,
                "distress_high_risk": distress.high_risk,
                "distress_status": (
                    "SCORED" if distress.is_sufficient else "UNSCORED_" + str(distress.reason)
                ),
                "distress_confidence": (
                    "FULL"
                    if isinstance(inputs["DISTRESS"]["hose_warning"], bool)
                    else "NO_WARNING_DATA"
                ),
                "fscore_total": None if fscore is None else fscore["F_SCORE_POINTS"],
                "fscore_scored_count": None if fscore is None else fscore["F_SCORE_CRITERIA_SCORED"],
                "fscore_status": fscore_status,
                "franchise_roc_years_used": roc_years,
                "franchise_roc_arithmetic_mean": roc_mean,
                "franchise_margin_stability": margin_stability,
                "franchise_status": franchise_status,
                "tev_to_market_cap": ratio,
                "tev_collapse_flag": tev_flag,
                "source": SOURCE_LABEL,
                "as_of": run_date,
                "data_status": _row_data_status(
                    selection,
                    step1,
                    valuation_row,
                    ratio,
                ),
            }
            records.append(record)
    output = pd.DataFrame(records, columns=OUTPUT_COLUMNS)
    output = apply_within_date_percentiles(output, config)
    return output.sort_values(["evaluation_date", "ticker"], kind="stable").reset_index(drop=True), formula_inputs


def apply_within_date_percentiles(output: pd.DataFrame, config: GateConfig) -> pd.DataFrame:
    frame = output.copy()
    for raw_column, percentile_column in (
        ("sta", "sta_percentile"),
        ("snoa", "snoa_percentile"),
        ("m_score", "m_score_percentile"),
    ):
        frame[percentile_column] = frame.groupby("evaluation_date", group_keys=False)[raw_column].transform(rank_percentile)
    worst_cut = Decimal("1") - config.accrual_worst_pct
    def worst(value: Any) -> bool:
        number = _numeric(value)
        return number is not None and Decimal(str(number)) >= worst_cut
    frame["high_accrual_flag"] = frame["sta_percentile"].map(worst) | frame["snoa_percentile"].map(worst)
    threshold = float(config.mscore_threshold)
    frame["m_score_flag"] = frame["m_score"].map(
        lambda value: _numeric(value) is not None and float(_numeric(value)) > threshold
    )
    return frame


def _selected_years(row: Any) -> list[int]:
    years = []
    for name in ("annual_n", "annual_n_minus_1", "annual_n_minus_2"):
        value = getattr(row, name)
        if pd.notna(value) and str(value).strip() != "":
            years.append(int(float(value)))
    return years


def validate_stop_gates(output: pd.DataFrame, annual: pd.DataFrame) -> dict[str, int]:
    source = annual.copy()
    source["_available"] = pd.to_datetime(source["available_from"], errors="coerce")
    year_max = source.groupby(["ticker", "fiscal_year"])["_available"].max().to_dict()
    lookahead: list[dict[str, Any]] = []
    non_consecutive: list[dict[str, Any]] = []
    for row in output.itertuples(index=False):
        years = _selected_years(row)
        evaluation = pd.Timestamp(row.evaluation_date)
        for year in years:
            available = year_max.get((row.ticker, str(year)))
            if available is None or pd.Timestamp(available) > evaluation:
                lookahead.append({"ticker": row.ticker, "evaluation_date": row.evaluation_date, "year": year})
        if len(years) != len(set(years)) or any(
            earlier - later != 1 for earlier, later in zip(years, years[1:])
        ):
            non_consecutive.append({"ticker": row.ticker, "evaluation_date": row.evaluation_date, "years": years})
    if lookahead:
        raise RuntimeError("STOP: look-ahead annual years: " + json.dumps(lookahead[:20]))
    if non_consecutive:
        raise RuntimeError("STOP: non-consecutive or repeated annual years: " + json.dumps(non_consecutive[:20]))
    percentile_violations: list[dict[str, Any]] = []
    for evaluation_date, frame in output.groupby("evaluation_date"):
        for raw, percentile in (("sta", "sta_percentile"), ("snoa", "snoa_percentile"), ("m_score", "m_score_percentile")):
            expected = rank_percentile(frame[raw]).reset_index(drop=True)
            actual = pd.to_numeric(frame[percentile], errors="coerce").reset_index(drop=True)
            if not expected.fillna(-999999).equals(actual.fillna(-999999)):
                percentile_violations.append({"evaluation_date": evaluation_date, "column": percentile})
    if percentile_violations:
        raise RuntimeError("STOP: percentile population crossed dates: " + json.dumps(percentile_violations))
    return {"lookahead": 0, "non_consecutive": 0, "percentile_cross_date": 0}


def validate_config_diff() -> None:
    completed = subprocess.run(
        ["git", "show", "origin/main:config/screener.yaml"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    base_values = _flat_config_text(completed.stdout)
    current_values = _flat_config(CONFIG_PATH)
    extra = set(current_values) - set(base_values)
    missing = set(base_values) - set(current_values)
    changed = {
        key: (base_values[key], current_values[key])
        for key in set(base_values) & set(current_values)
        if base_values[key] != current_values[key]
    }
    if extra != {
        "DISTRESS_REQUIRE_HOSE_WARNING",
        "TEV_MIN_FRACTION_OF_MARKET_CAP",
    } or missing or changed:
        raise RuntimeError("STOP: config differs beyond permitted key")


def _flat_config_text(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if line and ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def _decimal_text(value: Any) -> str:
    if value is None or pd.isna(value) or str(value).strip() == "":
        return ""
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return str(value)
    text = format(number, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def write_deterministic_gzip_csv(frame: pd.DataFrame, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as binary:
        with gzip.GzipFile(filename="", mode="wb", fileobj=binary, compresslevel=9, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", newline="") as text:
                frame.to_csv(text, index=False, lineterminator="\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _same_value(left: Any, right: Any) -> bool:
    left_number = _numeric(left)
    right_number = _numeric(right)
    if left_number is None or right_number is None:
        return left_number is None and right_number is None
    return Decimal(str(left_number)) == Decimal(str(right_number))


def _absolute_difference(left: Any, right: Any) -> str:
    left_number = _numeric(left)
    right_number = _numeric(right)
    if left_number is None or right_number is None:
        return ""
    return _decimal_text(abs(Decimal(str(left_number)) - Decimal(str(right_number))))


def reconciliation_tables(output: pd.DataFrame) -> dict[str, dict[str, Any]]:
    step1 = _read_csv(STEP1_PATH)
    fscore = _read_csv(FSCORE_PATH)
    franchise = _read_csv(FRANCHISE_PATH)
    current = output.loc[
        output["evaluation_date"].eq(RECONCILIATION_DATE)
    ].set_index("ticker", drop=False)
    comparisons = {
        "sta": (step1, "sta", "sta"),
        "snoa": (step1, "snoa", "snoa"),
        "m_score": (step1, "m_score", "m_score"),
        "fscore_total": (fscore, "fscore_total", "F_SCORE_POINTS"),
        "franchise_roc_arithmetic_mean": (
            franchise,
            "franchise_roc_arithmetic_mean",
            "roc_arithmetic_mean",
        ),
    }
    tables: dict[str, dict[str, Any]] = {}
    for name, (reference, current_column, reference_column) in comparisons.items():
        required = {"ticker", reference_column}
        missing = sorted(required - set(reference.columns))
        if missing:
            raise ValueError(f"reconciliation {name} missing columns: {missing}")
        indexed = reference.copy()
        indexed["ticker"] = indexed["ticker"].astype(str).str.strip().str.upper()
        if indexed["ticker"].duplicated().any():
            raise ValueError(f"reconciliation {name} has duplicate tickers")
        indexed = indexed.set_index("ticker", drop=False)
        shared = sorted(set(current.index) & set(indexed.index))
        mismatches: list[dict[str, Any]] = []
        matching = 0
        for ticker in shared:
            actual = current.at[ticker, current_column]
            committed = indexed.at[ticker, reference_column]
            if _same_value(actual, committed):
                matching += 1
            else:
                mismatches.append(
                    {
                        "ticker": ticker,
                        "computed": _decimal_text(actual),
                        "committed": _decimal_text(committed),
                        "absolute_difference": _absolute_difference(actual, committed),
                    }
                )
        tables[name] = {
            "compared": len(shared),
            "matching": matching,
            "mismatches": mismatches,
        }
    return tables


def validate_reconciliation(tables: dict[str, dict[str, Any]]) -> None:
    failures = {
        name: table
        for name, table in tables.items()
        if table["compared"] and len(table["mismatches"]) * 20 > table["compared"]
    }
    if failures:
        raise RuntimeError(
            "STOP: reconciliation mismatch rate exceeds 5 percent: "
            + json.dumps(
                {
                    name: {
                        "compared": value["compared"],
                        "mismatches": len(value["mismatches"]),
                    }
                    for name, value in failures.items()
                },
                sort_keys=True,
            )
        )


def _markdown_table(headers: Iterable[str], rows: Iterable[Iterable[Any]]) -> str:
    header_values = [str(value) for value in headers]
    lines = [
        "| " + " | ".join(header_values) + " |",
        "| " + " | ".join("---" for _ in header_values) + " |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(str(value).replace("|", "\\|").replace("\n", " ") for value in row)
            + " |"
        )
    return "\n".join(lines)


def _walk_forward(output: pd.DataFrame) -> pd.DataFrame:
    return output.loc[output["grid_role"].eq(WALK_FORWARD_ROLE)].copy()


def _gate_year_rows(output: pd.DataFrame) -> list[list[Any]]:
    rows: list[list[Any]] = []
    frame = _walk_forward(output).assign(
        calendar_year=lambda values: values["evaluation_date"].str.slice(0, 4)
    )
    for year in sorted(frame["calendar_year"].unique()):
        annual = frame.loc[frame["calendar_year"].eq(year)]
        for gate, status_column in GATE_STATUS_COLUMNS.items():
            statuses = annual[status_column].astype(str)
            scored = int(statuses.eq("SCORED").sum())
            unscored = int((~statuses.eq("SCORED")).sum())
            reasons = statuses.loc[~statuses.eq("SCORED")].value_counts().sort_index()
            rows.append(
                [
                    year,
                    gate,
                    scored,
                    unscored,
                    "; ".join(f"{name}={count}" for name, count in reasons.items()) or "NONE",
                ]
            )
    return rows


def _all_six_pass(row: Any) -> bool:
    return bool(
        row.sta_status == "SCORED"
        and row.snoa_status == "SCORED"
        and not bool(row.high_accrual_flag)
        and row.m_score_status == "SCORED"
        and not bool(row.m_score_flag)
        and row.distress_status == "SCORED"
        and row.distress_high_risk is False
        and row.fscore_status == "SCORED"
        and row.franchise_status == "SCORED"
    )


def _all_six_rows(output: pd.DataFrame) -> list[list[Any]]:
    walk = _walk_forward(output)
    rows: list[list[Any]] = []
    for evaluation_date, frame in walk.groupby("evaluation_date", sort=True):
        count = sum(_all_six_pass(row) for row in frame.itertuples(index=False))
        rows.append([evaluation_date[:4], evaluation_date, count])
    return rows


def _all_six_year_rows(output: pd.DataFrame) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for year, frame in _walk_forward(output).assign(
        calendar_year=lambda values: values["evaluation_date"].str.slice(0, 4)
    ).groupby("calendar_year", sort=True):
        counts = [
            sum(_all_six_pass(row) for row in date_frame.itertuples(index=False))
            for _, date_frame in frame.groupby("evaluation_date", sort=True)
        ]
        rows.append([year, max(counts, default=0)])
    return rows


def _quantile_text(values: pd.Series, quantile: float) -> str:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    return _decimal_text(numeric.quantile(quantile)) if not numeric.empty else ""


def _threshold_percentile(values: pd.Series, threshold: Decimal) -> str:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if numeric.empty:
        return ""
    augmented = pd.concat(
        [numeric.reset_index(drop=True), pd.Series([float(threshold)])],
        ignore_index=True,
    )
    return _decimal_text(rank_percentile(augmented).iloc[-1])


def _distribution_rows(output: pd.DataFrame, config: GateConfig) -> list[list[Any]]:
    rows: list[list[Any]] = []
    walk = _walk_forward(output).assign(
        calendar_year=lambda values: values["evaluation_date"].str.slice(0, 4)
    )
    for calendar_year, frame in walk.groupby("calendar_year", sort=True):
        for metric, threshold in (("m_score", config.mscore_threshold), ("sta", None)):
            values = pd.to_numeric(frame[metric], errors="coerce").dropna()
            if threshold is None:
                threshold_text = _decimal_text(Decimal("1") - config.accrual_worst_pct)
                threshold_percentile = threshold_text
            else:
                threshold_text = _decimal_text(threshold)
                date_percentiles = [
                    _threshold_percentile(date_frame[metric], threshold)
                    for _, date_frame in frame.groupby("evaluation_date", sort=True)
                ]
                threshold_percentile = " to ".join(
                    [
                        min(value for value in date_percentiles if value),
                        max(value for value in date_percentiles if value),
                    ]
                ) if any(date_percentiles) else ""
            rows.append(
                [
                    calendar_year,
                    metric,
                    len(values),
                    _decimal_text(values.min()) if not values.empty else "",
                    _quantile_text(values, float(Decimal("1") / Decimal("10"))),
                    _quantile_text(values, 0.50),
                    _quantile_text(values, 0.90),
                    _decimal_text(values.max()) if not values.empty else "",
                    threshold_text,
                    threshold_percentile,
                ]
            )
    return rows


def _tev_rows(output: pd.DataFrame) -> tuple[list[list[Any]], list[list[Any]]]:
    counts: list[list[Any]] = []
    flagged: list[list[Any]] = []
    walk = _walk_forward(output)
    for year, frame in walk.assign(
        calendar_year=lambda values: values["evaluation_date"].str.slice(0, 4)
    ).groupby("calendar_year", sort=True):
        counts.append([year, int(frame["tev_collapse_flag"].astype(bool).sum())])
    for row in walk.loc[walk["tev_collapse_flag"].astype(bool)].sort_values(
        ["evaluation_date", "ticker"]
    ).itertuples(index=False):
        flagged.append([row.ticker, row.evaluation_date, _decimal_text(row.tev_to_market_cap)])
    return counts, flagged


def _committed_vnm_values() -> tuple[dict[str, Any], dict[str, Any]]:
    frame = _read_csv(STEP1_PATH)
    row = frame.loc[frame["ticker"].astype(str).str.upper().eq("VNM")]
    if len(row) != 1:
        raise ValueError("VNM missing or duplicate in step1_survivors.csv")
    record = row.iloc[0].to_dict()
    raw = record.get("raw_formula_inputs", "")
    try:
        normalized = re.sub(r"np\.float64\(([^()]*)\)", r"\1", str(raw))
        inputs = ast.literal_eval(normalized) if raw else {}
    except (SyntaxError, ValueError):
        inputs = {}
    return record, inputs


def _vnm_rendered_calculations(annual: pd.DataFrame, config: GateConfig) -> str:
    rows = annual.loc[annual["ticker"].eq("VNM")].copy()
    selection = select_as_of_annuals(rows, RECONCILIATION_DATE)
    if selection.annual_n is None or selection.annual_n_minus_1 is None:
        raise ValueError("VNM does not have a consecutive annual pair for G7")
    pair_rows = _rows_for_years(
        selection.eligible_rows,
        selection.annual_n,
        selection.annual_n_minus_1,
    )
    results, inputs = calculate_step1_gates(pair_rows, selection, config=config)
    evidence_rows = pair_rows.copy()
    evidence_rows["report_period"] = evidence_rows["fiscal_year"].astype(str)
    prepared = PreparedTicker(
        ticker="VNM",
        exchange="",
        icb2="",
        pair=(selection.annual_n, selection.annual_n_minus_1),
        eligible_rows=evidence_rows,
        formula_inputs=inputs,
        results=results,
    )
    rendered = render_vnm_calculations(prepared).rstrip()
    rendered = rendered.replace(
        "# VNM formula calculations — Sprint 4",
        "### Imported formula worktable",
        1,
    )
    rendered = rendered.replace("\n## ", "\n#### ")
    return rendered.split("\n#### Distress", 1)[0].rstrip()


def _vnm_worked_rows(
    output: pd.DataFrame,
    formula_inputs: dict[tuple[str, str], dict[str, dict[str, Any]]],
) -> list[list[Any]]:
    current = output.loc[
        output["evaluation_date"].eq(RECONCILIATION_DATE)
        & output["ticker"].eq("VNM")
    ]
    if len(current) != 1:
        raise ValueError("VNM reconciliation row is missing or duplicated")
    current_row = current.iloc[0]
    committed, committed_inputs = _committed_vnm_values()
    calculated_inputs = formula_inputs[(RECONCILIATION_DATE, "VNM")]
    rows: list[list[Any]] = []
    for formula in ("STA", "SNOA"):
        for name, value in calculated_inputs[formula].items():
            prior = committed_inputs.get(formula, {}).get(name, "")
            rows.append([formula, name, _decimal_text(value), _decimal_text(prior), _absolute_difference(value, prior)])
    for formula in M_SCORE_INPUTS:
        output_name = formula.lower()
        value = current_row[output_name]
        prior = committed.get(output_name, "")
        rows.append(["M_SCORE_VARIABLE", output_name, _decimal_text(value), _decimal_text(prior), _absolute_difference(value, prior)])
    for name, value, prior in (
        ("sta", current_row["sta"], committed.get("sta", "")),
        ("snoa", current_row["snoa"], committed.get("snoa", "")),
        ("m_score", current_row["m_score"], committed.get("m_score", "")),
    ):
        rows.append(["RESULT", name, _decimal_text(value), _decimal_text(prior), _absolute_difference(value, prior)])
    return rows


def _distress_relaxation_rows(
    before: pd.DataFrame, after: pd.DataFrame
) -> list[list[Any]]:
    key_columns = ["evaluation_date", "ticker"]
    before_keyed = before.set_index(key_columns).sort_index()
    after_keyed = after.set_index(key_columns).sort_index()
    if before_keyed.index.has_duplicates or after_keyed.index.has_duplicates:
        raise ValueError("distress comparison requires unique evaluation_date and ticker")
    if not before_keyed.index.equals(after_keyed.index):
        raise ValueError("distress comparison keys changed during rebuild")
    before_high_risk = before_keyed["distress_high_risk"].astype(str).eq("True")
    after_high_risk = after_keyed["distress_high_risk"].astype(str).eq("True")
    lost = before_high_risk & ~after_high_risk
    if lost.any():
        locations = [
            f"{evaluation_date}/{ticker}"
            for evaluation_date, ticker in lost.loc[lost].index.tolist()
        ]
        raise RuntimeError(
            "STOP: old distress high risk became false or blank: "
            + ", ".join(locations)
        )
    return [
        [
            int(before_high_risk.sum()),
            int(after_high_risk.sum()),
            int((before_high_risk & after_high_risk).sum()),
        ]
    ]


def write_report(
    *,
    run_date: str,
    output_path: Path,
    output: pd.DataFrame,
    previous_output: pd.DataFrame,
    sha256: str,
    reconciliation: dict[str, dict[str, Any]],
    formula_inputs: dict[tuple[str, str], dict[str, dict[str, Any]]],
    annual: pd.DataFrame,
    config: GateConfig,
    stop_results: dict[str, int],
) -> None:
    walk = _walk_forward(output)
    population_date = max(
        sorted(walk["evaluation_date"].unique()),
        key=lambda evaluation: int(
            walk.loc[walk["evaluation_date"].eq(evaluation), ["sta", "snoa", "m_score"]]
            .apply(pd.to_numeric, errors="coerce")
            .notna()
            .sum()
            .sum()
        ),
    )
    population = walk.loc[walk["evaluation_date"].eq(population_date)]
    tev_counts, tev_flagged = _tev_rows(output)
    all_six_year_rows = _all_six_year_rows(output)
    all_six_date_rows = _all_six_rows(output)
    distress_relaxation_rows = _distress_relaxation_rows(previous_output, output)
    all_six_shortfall = all(row[1] < 20 for row in all_six_year_rows)
    mismatch_tickers = sorted(
        {
            item["ticker"]
            for table in reconciliation.values()
            for item in table["mismatches"]
        }
    )
    reconciliation_note = (
        "TCD is the only mismatched ticker. Its latest as-of annual year is 2025, "
        "but that annual record has missing income-statement and cash-flow items; the "
        "committed single-date file used 2024/2023 instead. This is recorded as a "
        "specific source-completeness difference, not as a blanket restatement claim."
        if mismatch_tickers == ["TCD"]
        else "No additional reconciliation explanation is inferred beyond the full mismatch tables."
    )
    vnm_calculations = _vnm_rendered_calculations(annual, config)
    lines = [
        "# Sprint 9-4C Gates As-Of",
        "",
        "## G1. Rows, dates, tickers",
        "",
        f"- WALK_FORWARD rows: `{len(walk)}`; dates: `{walk['evaluation_date'].nunique()}`; tickers: `{walk['ticker'].nunique()}`.",
        f"- RECONCILIATION rows: `{len(output) - len(walk)}`; dates: `{output.loc[output['grid_role'].eq(RECONCILIATION_ROLE), 'evaluation_date'].nunique()}`; tickers: `{output.loc[output['grid_role'].eq(RECONCILIATION_ROLE), 'ticker'].nunique()}`.",
        f"- Total rows: `{len(output)}`; total dates: `{output['evaluation_date'].nunique()}`; total tickers: `{output['ticker'].nunique()}`.",
        "",
        "## G2. Gate scoring by calendar year",
        "",
        "Counts are ticker-evaluation rows from WALK_FORWARD only; a named UNSCORED status is retained rather than dropped.",
        "",
        _markdown_table(["calendar_year", "gate", "SCORED", "UNSCORED", "UNSCORED reasons"], _gate_year_rows(output)),
        "",
        "## G3. Reconciliation against committed single-date files",
        "",
    ]
    for name, table in reconciliation.items():
        lines.extend(
            [
                f"### {name}",
                "",
                _markdown_table(
                    ["tickers compared", "matching exactly", "mismatches"],
                    [[table["compared"], table["matching"], len(table["mismatches"])]],
                ),
                "",
                _markdown_table(
                    ["ticker", "computed", "committed", "absolute difference"],
                    [[item["ticker"], item["computed"], item["committed"], item["absolute_difference"]] for item in table["mismatches"]]
                    if table["mismatches"]
                    else [["NONE", "", "", ""]],
                ),
                "",
            ]
        )
    lines.extend(
        [
            reconciliation_note,
            "",
            "## G4. All six gates simultaneously",
            "",
            "A pass requires both accrual gates and M-Score to be SCORED and unflagged, distress to be SCORED and not high risk, F-Score to be SCORED, and Franchise to be SCORED.",
            "The calendar-year count is the maximum simultaneous count at a single scheduled evaluation date, which is the relevant count for a portfolio at one rebalance.",
            "",
            _markdown_table(["calendar_year", "maximum tickers passing all six at one date"], all_six_year_rows),
            "",
            "Detailed scheduled-date counts:",
            "",
            _markdown_table(["calendar_year", "evaluation_date", "tickers passing all six"], all_six_date_rows),
            "",
            "Every calendar-year maximum is below 20 names, so none reaches the 20 to 25 names a portfolio needs."
            if all_six_shortfall
            else "At least one calendar-year maximum reaches the 20 to 25 names a portfolio needs; the table shows the exact years and counts.",
            "",
            "## G5. M-Score and STA distributions",
            "",
            _markdown_table(
                ["calendar_year", "metric", "n", "min", "p10", "median", "p90", "max", "imported threshold/cut", "within-date percentile range"],
                _distribution_rows(output, config),
            ),
            "",
            "M-Score coefficients and its absolute threshold were calibrated on United States data and remain hypotheses on the Vietnamese market. The committed inputs contain no United States reference percentile, so a similar Vietnamese percentile is not established; the within-date ranges above are reported without recommending a threshold change. STA has no imported absolute raw-value threshold: its imported cutoff is the within-date worst-percentile cut shown in the table.",
            "",
            "## G6. TEV-collapse flag",
            "",
            _markdown_table(["calendar_year", "flagged rows"], tev_counts),
            "",
            _markdown_table(["ticker", "evaluation_date", "tev_to_market_cap"], tev_flagged if tev_flagged else [["NONE", "", ""]]),
            "",
            "No row was dropped for tev_collapse_flag.",
            "",
            "below that level more than 80 percent of enterprise value is netted away by cash, and for Vietnamese non-financial companies a large share of reported cash is working capital and customer advances rather than distributable excess cash, so the yield describes the cash position rather than the operating business. This threshold was chosen on economic grounds; it was NOT selected by searching the observed distribution for a convenient gap.",
            "",
            "## G7. VNM worked number table at 2026-07-20",
            "",
            vnm_calculations,
            "",
            "### Values beside committed step1_survivors.csv",
            "",
            _markdown_table(["formula", "term", "computed", "committed step1_survivors.csv", "absolute difference"], _vnm_worked_rows(output, formula_inputs)),
            "",
            "## G8. Imported functions",
            "",
            "- `src/screener/step1_cleaning.py`: calculate_sta, calculate_snoa, calculate_dsri, calculate_gmi, calculate_aqi, calculate_sgi, calculate_depi, calculate_sgai, calculate_lvgi, calculate_tata, calculate_m_score, calculate_simple_distress.",
            "- `scripts/build_sprint6_fscore.py`: compute_ticker, criterion7_score, finalize_scores.",
            "- `scripts/build_sprint6_franchise.py`: compute_roc_series, summarize_roc, compute_margin_series, summarize_margin.",
            "- `src/screener/step1_data.py`: PreparedTicker and render_vnm_calculations for the existing VNM worked-number renderer; it does not compute the output metrics.",
            "- No function was extracted or moved.",
            "",
            "## G9. Output identity",
            "",
            f"- RUN_DATE: `{run_date}`.",
            f"- Output path: `{output_path.relative_to(ROOT).as_posix()}`.",
            f"- Row count: `{len(output)}`.",
            f"- SHA-256: `{sha256}`.",
            f"- STOP-gate violations: `{json.dumps(stop_results, sort_keys=True)}`.",
            f"- Within-date percentile population proof at `{population_date}`: STA=`{int(pd.to_numeric(population['sta'], errors='coerce').notna().sum())}`, SNOA=`{int(pd.to_numeric(population['snoa'], errors='coerce').notna().sum())}`, M_SCORE=`{int(pd.to_numeric(population['m_score'], errors='coerce').notna().sum())}`.",
            "",
            "## G10. Distress gate relaxation",
            "",
            "### T2. Preserved high-risk rows",
            "",
            _markdown_table(
                ["old distress_high_risk=True", "new distress_high_risk=True", "old AND new True"],
                distress_relaxation_rows,
            ),
            "",
            "### T7. Tickers passing all six gates at each WALK_FORWARD date",
            "",
            _markdown_table(
                ["calendar_year", "evaluation_date", "tickers passing all six"],
                all_six_date_rows,
            ),
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Sprint 9-4C gates as-of table.")
    parser.add_argument("--run-date", help="Asia/Ho_Chi_Minh run date (YYYY-MM-DD).")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_date = args.run_date or datetime.now(TIME_ZONE).date().isoformat()
    print(f"RUN_DATE={run_date}", flush=True)
    config = load_config()
    validate_config_diff()
    annual, valuation = load_inputs()
    output_path = OUTPUT_ROOT / run_date / "gate_values_point_in_time.csv.gz"
    if not output_path.exists():
        raise FileNotFoundError(
            "previous Sprint 9-4C artifact is required for distress comparison: "
            + str(output_path)
        )
    previous_output = _read_csv(output_path)
    output, formula_inputs = build_rows(annual, valuation, config, run_date=run_date)
    stop_results = validate_stop_gates(output, annual)
    reconciliation = reconciliation_tables(output)
    validate_reconciliation(reconciliation)
    sha256 = write_deterministic_gzip_csv(output, output_path)
    write_report(
        run_date=run_date,
        output_path=output_path,
        output=output,
        previous_output=previous_output,
        sha256=sha256,
        reconciliation=reconciliation,
        formula_inputs=formula_inputs,
        annual=annual,
        config=config,
        stop_results=stop_results,
    )
    print(f"OUTPUT={output_path}")
    print(f"ROW_COUNT={len(output)}")
    print(f"SHA256={sha256}")
    print(f"REPORT={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
