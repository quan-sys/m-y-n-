"""Fixture-only and read-only evidence checks for Sprint 4 Step 1 preparation."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import re
import socket

import pandas as pd
import pytest

from src.screener.step1_cleaning import DistressResult, FormulaResult, calculate_simple_distress
from src.screener.step1_data import (
    ANNUAL_COLUMNS,
    BALANCE_SHEET,
    CASH_FLOW,
    EVIDENCE_COLUMNS,
    FORMULA_INPUT_MAP,
    INCOME_STATEMENT,
    STATEMENT_FILES,
    AnnualSelection,
    assemble_formula_inputs,
    build_vnm_evidence,
    evaluate_formula_inputs,
    load_cached_annual_statements,
    prepare_ticker_from_cache,
    select_latest_eligible_pair,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "docs" / "VNM_FORMULA_EVIDENCE_SPRINT_4.csv"
CALCULATIONS_PATH = ROOT / "docs" / "VNM_FORMULA_CALCULATIONS_SPRINT_4.md"

ITEM_VALUES = {
    "total_assets": {2025: 1_000.0, 2024: 900.0},
    "current_assets": {2025: 500.0, 2024: 450.0},
    "cash_and_cash_equivalents": {2025: 100.0, 2024: 90.0},
    "current_liabilities": {2025: 300.0, 2024: 280.0},
    "short_term_borrowings": {2025: 50.0, 2024: 40.0},
    "taxes_and_other_payable_to_state_budget": {2025: 10.0, 2024: 9.0},
    "depreciation_and_amortization": {2025: 20.0, 2024: 18.0},
    "short_term_investments": {2025: 60.0, 2024: 55.0},
    "long_term_borrowings": {2025: 100.0, 2024: 90.0},
    "owners_equity": {2025: 550.0, 2024: 490.0},
    "accounts_receivable": {2025: 120.0, 2024: 100.0},
    "net_sales": {2025: 800.0, 2024: 700.0},
    "gross_profit": {2025: 300.0, 2024: 250.0},
    "tangible_fixed_assets": {2025: 200.0, 2024: 180.0},
    "selling_expenses": {2025: -50.0, 2024: -45.0},
    "general_and_admin_expenses": {2025: -30.0, 2024: -25.0},
    "long_term_liabilities": {2025: 100.0, 2024: 90.0},
    "net_profit_loss_after_tax": {2025: 80.0, 2024: 70.0},
    "net_cash_inflows_outflows_from_operating_activities": {2025: 70.0, 2024: 60.0},
    "undistributed_earnings": {2025: 100.0, 2024: 80.0},
}


def annual_rows(
    years: tuple[int, ...] = (2025, 2024),
    *,
    ticker: str = "FIX",
    future_year: int | None = None,
) -> pd.DataFrame:
    requirements = {
        (statement, item_id)
        for mapping in FORMULA_INPUT_MAP.values()
        for statement, item_id, _ in mapping.values()
    }
    records = []
    for statement, item_id in sorted(requirements):
        for year in years:
            values = ITEM_VALUES.get(item_id, {})
            value = values.get(year, values.get(2025, 1.0))
            available_from = (
                f"{year + 1}-12-31" if year == future_year else f"{year + 1}-03-31"
            )
            records.append(
                {
                    "ticker": ticker,
                    "company_type": "NON_FINANCIAL",
                    "statement_type": statement,
                    "period_type": "ANNUAL",
                    "report_period": str(year),
                    "period_end": f"{year}-12-31",
                    "available_from": available_from,
                    "item_id": item_id,
                    "item": item_id,
                    "item_en": item_id,
                    "value": value,
                    "currency": "VND",
                    "source": "saved_fixture",
                    "as_of": "2026-07-18",
                    "data_status": "OK",
                }
            )
    return pd.DataFrame(records, columns=ANNUAL_COLUMNS)


def test_accumulated_loss_true_with_missing_equity() -> None:
    result = calculate_simple_distress(-1, None, None)
    assert result == DistressResult(
        True,
        None,
        None,
        True,
        "INSUFFICIENT_DATA_FOR_DISTRESS",
        ("owners_equity_n", "hose_warning"),
    )


def test_negative_equity_true_with_missing_undistributed_earnings() -> None:
    result = calculate_simple_distress(None, -1, None)
    assert result == DistressResult(
        None,
        True,
        None,
        True,
        "INSUFFICIENT_DATA_FOR_DISTRESS",
        ("undistributed_earnings_n", "hose_warning"),
    )


def test_warning_true_with_both_financial_inputs_missing() -> None:
    result = calculate_simple_distress(None, None, True)
    assert result == DistressResult(
        None,
        None,
        True,
        True,
        "INSUFFICIENT_DATA_FOR_DISTRESS",
        ("undistributed_earnings_n", "owners_equity_n"),
    )


def test_all_distress_signals_known_and_false() -> None:
    assert calculate_simple_distress(1, 1, False) == DistressResult(False, False, False, False)


def test_no_true_distress_signal_with_unavailable_input() -> None:
    result = calculate_simple_distress(1, None, False)
    assert result == DistressResult(
        False,
        None,
        False,
        None,
        "INSUFFICIENT_DATA_FOR_DISTRESS",
        ("owners_equity_n",),
    )


def test_invalid_non_boolean_warning_is_unavailable() -> None:
    result = calculate_simple_distress(1, 1, "YES")
    assert result == DistressResult(
        False,
        False,
        None,
        None,
        "INSUFFICIENT_DATA_FOR_DISTRESS",
        ("hose_warning",),
    )


def test_latest_eligible_consecutive_pair() -> None:
    rows = annual_rows((2026, 2025, 2024), future_year=2026)
    selection = select_latest_eligible_pair(rows, "2026-07-18")
    assert selection.pair == (2025, 2024)


def test_future_available_from_rows_are_excluded() -> None:
    rows = annual_rows((2026, 2025, 2024), future_year=2026)
    selection = select_latest_eligible_pair(rows, "2026-07-18")
    assert "2026" not in set(selection.eligible_rows["report_period"].astype(str))


def test_non_consecutive_annual_periods_have_no_pair() -> None:
    selection = select_latest_eligible_pair(annual_rows((2025, 2023)), "2026-07-18")
    assert selection.pair is None


def test_selection_preserves_provenance_columns() -> None:
    selection = select_latest_eligible_pair(annual_rows(), "2026-07-18")
    for column in ("source", "as_of", "available_from", "data_status"):
        assert column in selection.eligible_rows
        assert selection.eligible_rows[column].notna().all()
    assert selection.eligible_rows["source"].eq("saved_fixture").all()


def test_formula_specific_missing_data_does_not_blanket_fail() -> None:
    rows = annual_rows()
    rows = rows.loc[
        ~(
            rows["statement_type"].eq(CASH_FLOW)
            & rows["item_id"].eq("depreciation_and_amortization")
            & rows["report_period"].eq("2025")
        )
    ]
    selection = select_latest_eligible_pair(rows, "2026-07-18")
    results = evaluate_formula_inputs(assemble_formula_inputs(selection))
    assert results["STA"].reason == "INSUFFICIENT_DATA_FOR_STA"
    assert results["DEPI"].reason == "INSUFFICIENT_DATA_FOR_DEPI"
    for formula in ("SNOA", "DSRI", "GMI", "AQI", "SGI", "SGAI", "LVGI", "TATA"):
        result = results[formula]
        assert isinstance(result, FormulaResult) and result.is_sufficient


def test_one_missing_formula_does_not_suppress_other_results() -> None:
    rows = annual_rows()
    rows = rows.loc[~rows["item_id"].eq("accounts_receivable")]
    selection = select_latest_eligible_pair(rows, "2026-07-18")
    results = evaluate_formula_inputs(assemble_formula_inputs(selection, hose_warning=False))
    assert results["DSRI"].reason == "INSUFFICIENT_DATA_FOR_DSRI"
    assert results["SNOA"].is_sufficient
    assert results["DISTRESS"].is_sufficient


def test_cached_preparation_makes_no_network_call(tmp_path: Path, monkeypatch) -> None:
    ticker_root = tmp_path / "FIX"
    ticker_root.mkdir()
    rows = annual_rows()
    for statement_type, filename in STATEMENT_FILES.items():
        rows.loc[rows["statement_type"].eq(statement_type)].to_parquet(
            ticker_root / filename, index=False
        )

    def forbidden_network(*args, **kwargs):
        raise AssertionError("network call attempted")

    monkeypatch.setattr(socket, "create_connection", forbidden_network)
    prepared = prepare_ticker_from_cache(
        {"ticker": "FIX", "exchange": "HOSE", "icb2": "TEST"},
        tmp_path,
        "2026-07-18",
        hose_warning=False,
    )
    assert prepared.pair == (2025, 2024)
    assert prepared.results["SNOA"].is_sufficient


def test_cached_statement_loader_preserves_provenance(tmp_path: Path) -> None:
    ticker_root = tmp_path / "FIX"
    ticker_root.mkdir()
    rows = annual_rows()
    for statement_type, filename in STATEMENT_FILES.items():
        rows.loc[rows["statement_type"].eq(statement_type)].to_parquet(
            ticker_root / filename, index=False
        )
    loaded = load_cached_annual_statements(tmp_path, "FIX")
    assert loaded.loc[:, ["source", "as_of", "available_from", "data_status"]].equals(
        rows.loc[:, ["source", "as_of", "available_from", "data_status"]].reset_index(drop=True)
    )


def test_vnm_evidence_schema_and_row_count() -> None:
    evidence = pd.read_csv(EVIDENCE_PATH, dtype={"report_period": str})
    assert tuple(evidence.columns) == EVIDENCE_COLUMNS
    assert len(evidence) == 33
    assert evidence["ticker"].eq("VNM").all()
    assert evidence[["source", "as_of", "available_from", "data_status"]].notna().all().all()


def evidence_value(evidence: pd.DataFrame, statement: str, item_id: str, period: str) -> int:
    rows = evidence.loc[
        evidence["statement"].eq(statement)
        & evidence["item_id"].eq(item_id)
        & evidence["report_period"].astype(str).eq(period)
    ]
    assert len(rows) == 1
    return int(rows.iloc[0]["value"])


def test_vnm_evidence_snoa_algebraic_identity() -> None:
    evidence = pd.read_csv(EVIDENCE_PATH, dtype={"report_period": str})
    assets = evidence_value(evidence, BALANCE_SHEET, "total_assets", "2025")
    cash = evidence_value(evidence, BALANCE_SHEET, "cash_and_cash_equivalents", "2025")
    investments = evidence_value(evidence, BALANCE_SHEET, "short_term_investments", "2025")
    short_debt = evidence_value(evidence, BALANCE_SHEET, "short_term_borrowings", "2025")
    long_debt = evidence_value(evidence, BALANCE_SHEET, "long_term_borrowings", "2025")
    equity = evidence_value(evidence, BALANCE_SHEET, "owners_equity", "2025")
    operating_assets = assets - cash - investments
    operating_liabilities = assets - short_debt - long_debt - equity
    identity_noa = short_debt + long_debt + equity - cash - investments
    assert operating_assets - operating_liabilities == identity_noa == 20_789_916_524_918


def test_vnm_intermediate_m_score_arithmetic() -> None:
    text = CALCULATIONS_PATH.read_text(encoding="utf-8")
    products = [
        Decimal(value)
        for value in re.findall(r"\| [-0-9.]+ × (?:DSRI|GMI|AQI|SGI|DEPI|SGAI|TATA|LVGI) \([^)]*\) \| `([^`]+)` \|", text)
    ]
    printed_sum = Decimal(
        re.search(r"\| Sum of printed components \| `([^`]+)` \|", text).group(1)
    )
    function_score = Decimal(
        re.search(r"\| M-Score \(formula function\) \| `([^`]+)` \|", text).group(1)
    )
    assert len(products) == 8
    assert Decimal("-4.840") + sum(products) == printed_sum
    assert float(printed_sum) == pytest.approx(float(function_score), rel=1e-15)
