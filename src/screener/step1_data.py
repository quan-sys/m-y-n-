"""Read-only cached-data preparation for Sprint 4 Step 1 cleaning formulas."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

from src.screener.step1_cleaning import (
    DistressResult,
    FormulaResult,
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


BALANCE_SHEET = "BALANCE_SHEET"
INCOME_STATEMENT = "INCOME_STATEMENT"
CASH_FLOW = "CASH_FLOW"

STATEMENT_FILES = {
    BALANCE_SHEET: "balance_sheet.parquet",
    INCOME_STATEMENT: "income_statement.parquet",
    CASH_FLOW: "cash_flow.parquet",
}

UNIVERSE_COLUMNS = (
    "ticker",
    "exchange",
    "icb2",
    "icb3",
    "icb4",
    "market_cap",
    "adtv_20d",
    "status",
    "reject_reason",
    "as_of",
    "source",
    "data_status",
)

ANNUAL_COLUMNS = (
    "ticker",
    "company_type",
    "statement_type",
    "period_type",
    "report_period",
    "period_end",
    "available_from",
    "item_id",
    "item",
    "item_en",
    "value",
    "currency",
    "source",
    "as_of",
    "data_status",
)

EVIDENCE_COLUMNS = (
    "ticker",
    "statement",
    "item_id",
    "report_period",
    "value",
    "source",
    "as_of",
    "available_from",
    "data_status",
)

# parameter -> (statement, item_id, N or N_MINUS_1)
FORMULA_INPUT_MAP: dict[str, dict[str, tuple[str, str, str]]] = {
    "STA": {
        "current_assets_n": (BALANCE_SHEET, "current_assets", "N"),
        "current_assets_n_minus_1": (BALANCE_SHEET, "current_assets", "N_MINUS_1"),
        "cash_and_cash_equivalents_n": (
            BALANCE_SHEET,
            "cash_and_cash_equivalents",
            "N",
        ),
        "cash_and_cash_equivalents_n_minus_1": (
            BALANCE_SHEET,
            "cash_and_cash_equivalents",
            "N_MINUS_1",
        ),
        "current_liabilities_n": (BALANCE_SHEET, "current_liabilities", "N"),
        "current_liabilities_n_minus_1": (
            BALANCE_SHEET,
            "current_liabilities",
            "N_MINUS_1",
        ),
        "short_term_borrowings_n": (BALANCE_SHEET, "short_term_borrowings", "N"),
        "short_term_borrowings_n_minus_1": (
            BALANCE_SHEET,
            "short_term_borrowings",
            "N_MINUS_1",
        ),
        "taxes_and_other_payable_to_state_budget_n": (
            BALANCE_SHEET,
            "taxes_and_other_payable_to_state_budget",
            "N",
        ),
        "taxes_and_other_payable_to_state_budget_n_minus_1": (
            BALANCE_SHEET,
            "taxes_and_other_payable_to_state_budget",
            "N_MINUS_1",
        ),
        "depreciation_and_amortization_n": (
            CASH_FLOW,
            "depreciation_and_amortization",
            "N",
        ),
        "total_assets_n": (BALANCE_SHEET, "total_assets", "N"),
        "total_assets_n_minus_1": (BALANCE_SHEET, "total_assets", "N_MINUS_1"),
    },
    "SNOA": {
        "total_assets_n": (BALANCE_SHEET, "total_assets", "N"),
        "total_assets_n_minus_1": (BALANCE_SHEET, "total_assets", "N_MINUS_1"),
        "cash_and_cash_equivalents_n": (
            BALANCE_SHEET,
            "cash_and_cash_equivalents",
            "N",
        ),
        "short_term_investments_n": (BALANCE_SHEET, "short_term_investments", "N"),
        "short_term_borrowings_n": (BALANCE_SHEET, "short_term_borrowings", "N"),
        "long_term_borrowings_n": (BALANCE_SHEET, "long_term_borrowings", "N"),
        "owners_equity_n": (BALANCE_SHEET, "owners_equity", "N"),
    },
    "DSRI": {
        "accounts_receivable_n": (BALANCE_SHEET, "accounts_receivable", "N"),
        "net_sales_n": (INCOME_STATEMENT, "net_sales", "N"),
        "accounts_receivable_n_minus_1": (
            BALANCE_SHEET,
            "accounts_receivable",
            "N_MINUS_1",
        ),
        "net_sales_n_minus_1": (INCOME_STATEMENT, "net_sales", "N_MINUS_1"),
    },
    "GMI": {
        "gross_profit_n": (INCOME_STATEMENT, "gross_profit", "N"),
        "net_sales_n": (INCOME_STATEMENT, "net_sales", "N"),
        "gross_profit_n_minus_1": (INCOME_STATEMENT, "gross_profit", "N_MINUS_1"),
        "net_sales_n_minus_1": (INCOME_STATEMENT, "net_sales", "N_MINUS_1"),
    },
    "AQI": {
        "current_assets_n": (BALANCE_SHEET, "current_assets", "N"),
        "tangible_fixed_assets_n": (BALANCE_SHEET, "tangible_fixed_assets", "N"),
        "total_assets_n": (BALANCE_SHEET, "total_assets", "N"),
        "current_assets_n_minus_1": (BALANCE_SHEET, "current_assets", "N_MINUS_1"),
        "tangible_fixed_assets_n_minus_1": (
            BALANCE_SHEET,
            "tangible_fixed_assets",
            "N_MINUS_1",
        ),
        "total_assets_n_minus_1": (BALANCE_SHEET, "total_assets", "N_MINUS_1"),
    },
    "SGI": {
        "net_sales_n": (INCOME_STATEMENT, "net_sales", "N"),
        "net_sales_n_minus_1": (INCOME_STATEMENT, "net_sales", "N_MINUS_1"),
    },
    "DEPI": {
        "depreciation_and_amortization_n": (
            CASH_FLOW,
            "depreciation_and_amortization",
            "N",
        ),
        "tangible_fixed_assets_n": (BALANCE_SHEET, "tangible_fixed_assets", "N"),
        "depreciation_and_amortization_n_minus_1": (
            CASH_FLOW,
            "depreciation_and_amortization",
            "N_MINUS_1",
        ),
        "tangible_fixed_assets_n_minus_1": (
            BALANCE_SHEET,
            "tangible_fixed_assets",
            "N_MINUS_1",
        ),
    },
    "SGAI": {
        "selling_expenses_n": (INCOME_STATEMENT, "selling_expenses", "N"),
        "general_and_admin_expenses_n": (
            INCOME_STATEMENT,
            "general_and_admin_expenses",
            "N",
        ),
        "net_sales_n": (INCOME_STATEMENT, "net_sales", "N"),
        "selling_expenses_n_minus_1": (
            INCOME_STATEMENT,
            "selling_expenses",
            "N_MINUS_1",
        ),
        "general_and_admin_expenses_n_minus_1": (
            INCOME_STATEMENT,
            "general_and_admin_expenses",
            "N_MINUS_1",
        ),
        "net_sales_n_minus_1": (INCOME_STATEMENT, "net_sales", "N_MINUS_1"),
    },
    "LVGI": {
        "current_liabilities_n": (BALANCE_SHEET, "current_liabilities", "N"),
        "long_term_liabilities_n": (BALANCE_SHEET, "long_term_liabilities", "N"),
        "total_assets_n": (BALANCE_SHEET, "total_assets", "N"),
        "current_liabilities_n_minus_1": (
            BALANCE_SHEET,
            "current_liabilities",
            "N_MINUS_1",
        ),
        "long_term_liabilities_n_minus_1": (
            BALANCE_SHEET,
            "long_term_liabilities",
            "N_MINUS_1",
        ),
        "total_assets_n_minus_1": (BALANCE_SHEET, "total_assets", "N_MINUS_1"),
    },
    "TATA": {
        "net_profit_loss_after_tax_n": (
            INCOME_STATEMENT,
            "net_profit_loss_after_tax",
            "N",
        ),
        "net_cash_inflows_outflows_from_operating_activities_n": (
            CASH_FLOW,
            "net_cash_inflows_outflows_from_operating_activities",
            "N",
        ),
        "total_assets_n": (BALANCE_SHEET, "total_assets", "N"),
    },
    "DISTRESS": {
        "undistributed_earnings_n": (BALANCE_SHEET, "undistributed_earnings", "N"),
        "owners_equity_n": (BALANCE_SHEET, "owners_equity", "N"),
    },
}

FORMULA_FUNCTIONS = {
    "STA": calculate_sta,
    "SNOA": calculate_snoa,
    "DSRI": calculate_dsri,
    "GMI": calculate_gmi,
    "AQI": calculate_aqi,
    "SGI": calculate_sgi,
    "DEPI": calculate_depi,
    "SGAI": calculate_sgai,
    "LVGI": calculate_lvgi,
    "TATA": calculate_tata,
}

M_SCORE_INPUTS = ("DSRI", "GMI", "AQI", "SGI", "DEPI", "SGAI", "LVGI", "TATA")


@dataclass(frozen=True)
class AnnualSelection:
    """Eligible annual rows and the latest consecutive N/N-1 pair."""

    pair: tuple[int, int] | None
    eligible_rows: pd.DataFrame


@dataclass(frozen=True)
class PreparedTicker:
    """Prepared cached inputs and independent formula results for one ticker."""

    ticker: str
    exchange: str
    icb2: str
    pair: tuple[int, int] | None
    eligible_rows: pd.DataFrame
    formula_inputs: dict[str, dict[str, Any]]
    results: dict[str, FormulaResult | DistressResult]


def _require_columns(frame: pd.DataFrame, required: tuple[str, ...], source: Path) -> None:
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def load_accepted_universe(path: str | Path) -> pd.DataFrame:
    """Load only ACCEPTED rows from the existing Sprint 3 universe."""

    source = Path(path)
    frame = pd.read_csv(source)
    _require_columns(frame, UNIVERSE_COLUMNS, source)
    accepted = frame.loc[frame["status"].astype(str).eq("ACCEPTED")].copy()
    accepted["ticker"] = accepted["ticker"].astype(str).str.strip().str.upper()
    if accepted["ticker"].duplicated().any():
        duplicates = accepted.loc[accepted["ticker"].duplicated(False), "ticker"].tolist()
        raise ValueError(f"duplicate ACCEPTED tickers: {duplicates}")
    return accepted.reset_index(drop=True)


def load_reject_history(path: str | Path) -> pd.DataFrame:
    """Load the existing reject history without changing its schema."""

    source = Path(path)
    frame = pd.read_csv(source)
    _require_columns(frame, UNIVERSE_COLUMNS, source)
    return frame.copy()


def load_cached_annual_statements(cache_root: str | Path, ticker: str) -> pd.DataFrame:
    """Load the three existing annual parquet files for one ticker, read-only."""

    normalized_ticker = str(ticker).strip().upper()
    ticker_root = Path(cache_root) / normalized_ticker
    frames: list[pd.DataFrame] = []
    for statement_type, filename in STATEMENT_FILES.items():
        source = ticker_root / filename
        if not source.exists():
            continue
        frame = pd.read_parquet(source)
        _require_columns(frame, ANNUAL_COLUMNS, source)
        if not frame.empty and not frame["statement_type"].astype(str).eq(statement_type).all():
            raise ValueError(f"{source} contains the wrong statement_type")
        frames.append(frame.loc[:, ANNUAL_COLUMNS].copy())
    if not frames:
        return pd.DataFrame(columns=ANNUAL_COLUMNS)
    return pd.concat(frames, ignore_index=True)


def select_latest_eligible_pair(
    rows: pd.DataFrame, evaluation_date: str | date | pd.Timestamp
) -> AnnualSelection:
    """Select latest consecutive annual N/N-1 using only already-available rows."""

    if rows.empty:
        return AnnualSelection(None, pd.DataFrame(columns=ANNUAL_COLUMNS))
    _require_columns(rows, ANNUAL_COLUMNS, Path("<annual rows>"))
    cutoff = pd.Timestamp(evaluation_date)
    available = pd.to_datetime(rows["available_from"], errors="coerce")
    annual = rows["period_type"].astype(str).eq("ANNUAL")
    eligible = rows.loc[annual & available.notna() & available.le(cutoff)].copy()
    years = sorted(
        {
            int(period)
            for period in eligible["report_period"].dropna().astype(str)
            if str(period).isdigit()
        },
        reverse=True,
    )
    available_years = set(years)
    pair = next(((year, year - 1) for year in years if year - 1 in available_years), None)
    if pair is None:
        return AnnualSelection(None, eligible.reset_index(drop=True))
    pair_text = {str(pair[0]), str(pair[1])}
    selected = eligible.loc[eligible["report_period"].astype(str).isin(pair_text)].copy()
    return AnnualSelection(pair, selected.reset_index(drop=True))


def _cached_value(
    rows: pd.DataFrame,
    statement_type: str,
    item_id: str,
    year: int,
) -> Any:
    matches = rows.loc[
        rows["statement_type"].astype(str).eq(statement_type)
        & rows["item_id"].astype(str).eq(item_id)
        & rows["report_period"].astype(str).eq(str(year))
    ]
    if matches.empty:
        return None
    if len(matches) != 1:
        return None
    value = matches.iloc[0]["value"]
    return None if pd.isna(value) else value


def assemble_formula_inputs(
    selection: AnnualSelection, hose_warning: bool | None = None
) -> dict[str, dict[str, Any]]:
    """Assemble each formula's explicit inputs without cross-formula fallback."""

    pair = selection.pair
    assembled: dict[str, dict[str, Any]] = {}
    for formula, parameters in FORMULA_INPUT_MAP.items():
        values: dict[str, Any] = {}
        for parameter, (statement_type, item_id, period_role) in parameters.items():
            if pair is None:
                values[parameter] = None
                continue
            year = pair[0] if period_role == "N" else pair[1]
            values[parameter] = _cached_value(
                selection.eligible_rows, statement_type, item_id, year
            )
        if formula == "DISTRESS":
            values["hose_warning"] = hose_warning
        assembled[formula] = values
    return assembled


def evaluate_formula_inputs(
    formula_inputs: Mapping[str, Mapping[str, Any]],
) -> dict[str, FormulaResult | DistressResult]:
    """Evaluate every formula independently and retain each insufficiency result."""

    results: dict[str, FormulaResult | DistressResult] = {}
    for name, function in FORMULA_FUNCTIONS.items():
        results[name] = function(**formula_inputs[name])
    m_score_values = {
        name.lower(): (
            results[name].value if isinstance(results[name], FormulaResult) else None
        )
        for name in M_SCORE_INPUTS
    }
    results["M_SCORE"] = calculate_m_score(**m_score_values)
    results["DISTRESS"] = calculate_simple_distress(**formula_inputs["DISTRESS"])
    return results


def prepare_ticker_from_cache(
    universe_row: Mapping[str, Any],
    cache_root: str | Path,
    evaluation_date: str | date | pd.Timestamp,
    hose_warning: bool | None = None,
) -> PreparedTicker:
    """Load, select, assemble, and evaluate one cached ticker."""

    ticker = str(universe_row["ticker"]).strip().upper()
    rows = load_cached_annual_statements(cache_root, ticker)
    selection = select_latest_eligible_pair(rows, evaluation_date)
    formula_inputs = assemble_formula_inputs(selection, hose_warning=hose_warning)
    results = evaluate_formula_inputs(formula_inputs)
    return PreparedTicker(
        ticker=ticker,
        exchange=str(universe_row["exchange"]),
        icb2=str(universe_row["icb2"]),
        pair=selection.pair,
        eligible_rows=selection.eligible_rows,
        formula_inputs=formula_inputs,
        results=results,
    )


def _evidence_requirements() -> list[tuple[str, str, str]]:
    requirements: list[tuple[str, str, str]] = []
    for formula in FORMULA_FUNCTIONS:
        for requirement in FORMULA_INPUT_MAP[formula].values():
            if requirement not in requirements:
                requirements.append(requirement)
    return requirements


def build_vnm_evidence(prepared: PreparedTicker) -> pd.DataFrame:
    """Build the exact cached input rows used by VNM's ten raw formulas."""

    if prepared.ticker != "VNM" or prepared.pair is None:
        raise ValueError("VNM evidence requires a prepared VNM consecutive annual pair")
    records: list[dict[str, Any]] = []
    for statement_type, item_id, period_role in _evidence_requirements():
        year = prepared.pair[0] if period_role == "N" else prepared.pair[1]
        matches = prepared.eligible_rows.loc[
            prepared.eligible_rows["statement_type"].astype(str).eq(statement_type)
            & prepared.eligible_rows["item_id"].astype(str).eq(item_id)
            & prepared.eligible_rows["report_period"].astype(str).eq(str(year))
        ]
        if len(matches) != 1 or pd.isna(matches.iloc[0]["value"]):
            raise ValueError(f"missing unique VNM evidence row: {statement_type}:{year}:{item_id}")
        row = matches.iloc[0]
        numeric = float(row["value"])
        value: int | float = int(numeric) if numeric.is_integer() else numeric
        records.append(
            {
                "ticker": "VNM",
                "statement": statement_type,
                "item_id": item_id,
                "report_period": str(year),
                "value": value,
                "source": str(row["source"]),
                "as_of": str(row["as_of"]),
                "available_from": str(row["available_from"]),
                "data_status": str(row["data_status"]),
            }
        )
    return pd.DataFrame(records, columns=EVIDENCE_COLUMNS)


def _decimal(value: Any) -> Decimal:
    numeric = float(value)
    return Decimal(str(int(numeric))) if numeric.is_integer() else Decimal(str(numeric))


def _display(value: Decimal | float | int | bool | None | str) -> str:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, float):
        return repr(value)
    return str(value)


def _table(rows: list[tuple[str, Any]]) -> list[str]:
    lines = ["| Term | Value |", "|---|---:|"]
    lines.extend(f"| {name} | `{_display(value)}` |" for name, value in rows)
    return lines


def render_vnm_calculations(prepared: PreparedTicker) -> str:
    """Render VNM raw values and every required intermediate calculation."""

    if prepared.ticker != "VNM" or prepared.pair is None:
        raise ValueError("VNM calculations require a consecutive annual pair")
    getcontext().prec = 50
    inputs = prepared.formula_inputs
    results = prepared.results
    lines = [
        "# VNM formula calculations — Sprint 4",
        "",
        f"Cached annual pair: N={prepared.pair[0]}, N−1={prepared.pair[1]}. Values are raw VND.",
        "No public-site cross-check and no live API call were used.",
        "",
        "## Raw inputs",
        "",
    ]
    evidence = build_vnm_evidence(prepared)
    lines.extend(
        [
            "| statement | item_id | period | value | source | as_of | available_from | data_status |",
            "|---|---|---:|---:|---|---|---|---|",
        ]
    )
    for row in evidence.to_dict("records"):
        lines.append(
            f"| {row['statement']} | {row['item_id']} | {row['report_period']} | "
            f"{row['value']} | {row['source']} | {row['as_of']} | "
            f"{row['available_from']} | {row['data_status']} |"
        )

    sta = {key: _decimal(value) for key, value in inputs["STA"].items()}
    delta_ca = sta["current_assets_n"] - sta["current_assets_n_minus_1"]
    delta_cash = sta["cash_and_cash_equivalents_n"] - sta["cash_and_cash_equivalents_n_minus_1"]
    delta_cl = sta["current_liabilities_n"] - sta["current_liabilities_n_minus_1"]
    delta_std = sta["short_term_borrowings_n"] - sta["short_term_borrowings_n_minus_1"]
    delta_tax = (
        sta["taxes_and_other_payable_to_state_budget_n"]
        - sta["taxes_and_other_payable_to_state_budget_n_minus_1"]
    )
    accruals = (
        delta_ca
        - delta_cash
        - (delta_cl - delta_std - delta_tax)
        - sta["depreciation_and_amortization_n"]
    )
    average_assets = (sta["total_assets_n"] + sta["total_assets_n_minus_1"]) / Decimal(2)
    lines.extend(["", "## STA", ""])
    lines.extend(
        _table(
            [
                ("ΔCurrent Assets", delta_ca),
                ("ΔCash", delta_cash),
                ("ΔCurrent Liabilities", delta_cl),
                ("ΔShort-term Debt", delta_std),
                ("ΔTaxes Payable", delta_tax),
                ("Depreciation", sta["depreciation_and_amortization_n"]),
                ("Accruals", accruals),
                ("Average Total Assets", average_assets),
                ("STA (exact Decimal)", accruals / average_assets),
                ("STA (formula function)", results["STA"].value),
            ]
        )
    )

    snoa = {key: _decimal(value) for key, value in inputs["SNOA"].items()}
    operating_assets = (
        snoa["total_assets_n"]
        - snoa["cash_and_cash_equivalents_n"]
        - snoa["short_term_investments_n"]
    )
    operating_liabilities = (
        snoa["total_assets_n"]
        - snoa["short_term_borrowings_n"]
        - snoa["long_term_borrowings_n"]
        - snoa["owners_equity_n"]
    )
    noa_operating = operating_assets - operating_liabilities
    noa_identity = (
        snoa["short_term_borrowings_n"]
        + snoa["long_term_borrowings_n"]
        + snoa["owners_equity_n"]
        - snoa["cash_and_cash_equivalents_n"]
        - snoa["short_term_investments_n"]
    )
    lines.extend(["", "## SNOA", ""])
    lines.extend(
        _table(
            [
                ("Operating Assets", operating_assets),
                ("Operating Liabilities", operating_liabilities),
                ("NOA from Operating Assets − Operating Liabilities", noa_operating),
                ("NOA from financing identity", noa_identity),
                ("NOA identity exact match", noa_operating == noa_identity),
                ("Beginning Total Assets", snoa["total_assets_n_minus_1"]),
                ("SNOA (exact Decimal)", noa_operating / snoa["total_assets_n_minus_1"]),
                ("SNOA (formula function)", results["SNOA"].value),
            ]
        )
    )

    dsri = {key: _decimal(value) for key, value in inputs["DSRI"].items()}
    receivables_ratio_n = dsri["accounts_receivable_n"] / dsri["net_sales_n"]
    receivables_ratio_previous = (
        dsri["accounts_receivable_n_minus_1"] / dsri["net_sales_n_minus_1"]
    )
    gmi = {key: _decimal(value) for key, value in inputs["GMI"].items()}
    margin_n = gmi["gross_profit_n"] / gmi["net_sales_n"]
    margin_previous = gmi["gross_profit_n_minus_1"] / gmi["net_sales_n_minus_1"]
    aqi = {key: _decimal(value) for key, value in inputs["AQI"].items()}
    quality_n = Decimal(1) - (
        aqi["current_assets_n"] + aqi["tangible_fixed_assets_n"]
    ) / aqi["total_assets_n"]
    quality_previous = Decimal(1) - (
        aqi["current_assets_n_minus_1"] + aqi["tangible_fixed_assets_n_minus_1"]
    ) / aqi["total_assets_n_minus_1"]
    sgi = {key: _decimal(value) for key, value in inputs["SGI"].items()}
    depi = {key: _decimal(value) for key, value in inputs["DEPI"].items()}
    dep_rate_n = depi["depreciation_and_amortization_n"] / (
        depi["depreciation_and_amortization_n"] + depi["tangible_fixed_assets_n"]
    )
    dep_rate_previous = depi["depreciation_and_amortization_n_minus_1"] / (
        depi["depreciation_and_amortization_n_minus_1"]
        + depi["tangible_fixed_assets_n_minus_1"]
    )
    sgai = {key: _decimal(value) for key, value in inputs["SGAI"].items()}
    sga_n = sgai["selling_expenses_n"] + sgai["general_and_admin_expenses_n"]
    sga_previous = (
        sgai["selling_expenses_n_minus_1"]
        + sgai["general_and_admin_expenses_n_minus_1"]
    )
    sga_ratio_n = sga_n / sgai["net_sales_n"]
    sga_ratio_previous = sga_previous / sgai["net_sales_n_minus_1"]
    lvgi = {key: _decimal(value) for key, value in inputs["LVGI"].items()}
    liabilities_n = lvgi["current_liabilities_n"] + lvgi["long_term_liabilities_n"]
    liabilities_previous = (
        lvgi["current_liabilities_n_minus_1"] + lvgi["long_term_liabilities_n_minus_1"]
    )
    leverage_n = liabilities_n / lvgi["total_assets_n"]
    leverage_previous = liabilities_previous / lvgi["total_assets_n_minus_1"]
    tata = {key: _decimal(value) for key, value in inputs["TATA"].items()}
    tata_accruals = (
        tata["net_profit_loss_after_tax_n"]
        - tata["net_cash_inflows_outflows_from_operating_activities_n"]
    )
    lines.extend(["", "## Beneish sub-indices", ""])
    lines.extend(
        _table(
            [
                ("DSRI receivables/sales N", receivables_ratio_n),
                ("DSRI receivables/sales N−1", receivables_ratio_previous),
                ("DSRI", results["DSRI"].value),
                ("GMI gross margin N", margin_n),
                ("GMI gross margin N−1", margin_previous),
                ("GMI", results["GMI"].value),
                ("AQI asset quality N", quality_n),
                ("AQI asset quality N−1", quality_previous),
                ("AQI", results["AQI"].value),
                ("SGI sales N", sgi["net_sales_n"]),
                ("SGI sales N−1", sgi["net_sales_n_minus_1"]),
                ("SGI", results["SGI"].value),
                ("DEPI depreciation rate N", dep_rate_n),
                ("DEPI depreciation rate N−1", dep_rate_previous),
                ("DEPI", results["DEPI"].value),
                ("SGAI SGA N", sga_n),
                ("SGAI SGA N−1", sga_previous),
                ("SGAI SGA/sales N", sga_ratio_n),
                ("SGAI SGA/sales N−1", sga_ratio_previous),
                ("SGAI", results["SGAI"].value),
                ("LVGI liabilities N", liabilities_n),
                ("LVGI liabilities N−1", liabilities_previous),
                ("LVGI leverage N", leverage_n),
                ("LVGI leverage N−1", leverage_previous),
                ("LVGI", results["LVGI"].value),
                ("TATA after-tax income", tata["net_profit_loss_after_tax_n"]),
                ("TATA operating cash flow", tata["net_cash_inflows_outflows_from_operating_activities_n"]),
                ("TATA income − operating cash flow", tata_accruals),
                ("TATA total assets", tata["total_assets_n"]),
                ("TATA", results["TATA"].value),
            ]
        )
    )

    coefficient_rows: list[tuple[str, Any]] = [("Constant", Decimal("-4.840"))]
    coefficients = {
        "DSRI": Decimal("0.920"),
        "GMI": Decimal("0.528"),
        "AQI": Decimal("0.404"),
        "SGI": Decimal("0.892"),
        "DEPI": Decimal("0.115"),
        "SGAI": Decimal("-0.172"),
        "TATA": Decimal("4.679"),
        "LVGI": Decimal("-0.327"),
    }
    component_sum = Decimal("-4.840")
    for name, coefficient in coefficients.items():
        result = results[name]
        assert isinstance(result, FormulaResult) and result.value is not None
        product = coefficient * Decimal(str(result.value))
        component_sum += product
        coefficient_rows.append((f"{coefficient} × {name} ({result.value})", product))
    coefficient_rows.extend(
        [
            ("Sum of printed components", component_sum),
            ("M-Score (formula function)", results["M_SCORE"].value),
        ]
    )
    lines.extend(["", "## Total M-Score", ""])
    lines.extend(_table(coefficient_rows))

    distress_inputs = inputs["DISTRESS"]
    distress = results["DISTRESS"]
    assert isinstance(distress, DistressResult)
    lines.extend(["", "## Distress", ""])
    lines.extend(
        _table(
            [
                ("Undistributed earnings", int(float(distress_inputs["undistributed_earnings_n"]))),
                ("Owners' equity", int(float(distress_inputs["owners_equity_n"]))),
                ("Supplied warning value", distress_inputs["hose_warning"]),
                ("Accumulated-loss signal", distress.accumulated_loss),
                ("Negative-equity signal", distress.negative_equity),
                ("HoSE-warning signal", distress.hose_warning),
                ("Combined high-risk state", distress.high_risk),
                ("Insufficiency reason", distress.reason),
                ("Invalid inputs", ",".join(distress.invalid_inputs)),
            ]
        )
    )
    return "\n".join(lines) + "\n"


def write_vnm_evidence(
    prepared: PreparedTicker, csv_path: str | Path, markdown_path: str | Path
) -> tuple[int, Path, Path]:
    """Write only the owner-requested VNM evidence artifacts."""

    evidence = build_vnm_evidence(prepared)
    csv_output = Path(csv_path)
    markdown_output = Path(markdown_path)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    evidence.to_csv(csv_output, index=False, lineterminator="\n")
    markdown_output.write_text(render_vnm_calculations(prepared), encoding="utf-8")
    return len(evidence), csv_output, markdown_output
