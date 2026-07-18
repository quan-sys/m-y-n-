from __future__ import annotations

import socket

import pandas as pd
import pytest

from src.screener.step1_data import ANNUAL_COLUMNS, select_latest_eligible_pair
from src.screener.step1_pipeline import (
    AUDIT_COLUMNS,
    FILTER_ORDER,
    REJECT_COLUMNS,
    add_formula_flags,
    assign_primary_rejections,
    build_sector_a,
    build_sector_b,
    calculate_filter_stats,
    extend_reject_history,
    guardrail,
    higher_tail_flags,
    run_cleaning_pipeline,
)


def formula_frame(**overrides):
    base = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB", "CCC", "DDD"],
            "exchange": ["HOSE"] * 4,
            "icb2": ["A", "A", "B", "B"],
            "sta": [4.0, 3.0, 2.0, 1.0],
            "snoa": [1.0, 2.0, 3.0, 4.0],
            "m_score": [-2.0] * 4,
            "distress_high_risk": [False] * 4,
            "distress_accumulated_loss": [False] * 4,
            "distress_negative_equity": [False] * 4,
            "distress_hose_warning": [None] * 4,
            "source": ["cache"] * 4,
            "as_of": ["2026-07-18"] * 4,
            "data_status": ["OK"] * 4,
            "raw_formula_inputs": ["{}"] * 4,
        }
    )
    for key, value in overrides.items():
        base[key] = value
    return base


def universe_frame():
    return pd.DataFrame(
        {
            "ticker": ["FIN", "UPC", "AAA", "BBB", "CCC", "DDD"],
            "exchange": ["UPCOM", "UPCOM", "HOSE", "HOSE", "HOSE", "HOSE"],
            "icb2": ["NGÂN HÀNG", "A", "A", "A", "B", "B"],
            "icb3": [""] * 6,
            "icb4": [""] * 6,
            "market_cap": [1.0] * 6,
            "adtv_20d": [1.0] * 6,
            "status": ["ACCEPTED"] * 6,
            "reject_reason": [""] * 6,
            "as_of": ["2026-07-18"] * 6,
            "source": ["universe"] * 6,
            "data_status": ["OK"] * 6,
        }
    )


def assigned(evaluated=None):
    evaluated = formula_frame() if evaluated is None else evaluated
    evaluated, cutoffs = add_formula_flags(evaluated, 0.25, -1.78)
    return assign_primary_rejections(universe_frame(), evaluated, cutoffs, -1.78), evaluated, cutoffs


def test_fixed_filter_order():
    assert FILTER_ORDER == (
        "FINANCIAL_SECTOR_EXCLUDED", "UPCOM_EXCLUDED_V1", "HIGH_ACCRUAL", "M_SCORE_FLAG", "PFD_HIGH_RISK"
    )


def test_first_failure_reason_only():
    rejects, _, _ = assigned(formula_frame(m_score=[0.0] * 4, distress_high_risk=[True] * 4))
    assert rejects["ticker"].is_unique
    assert rejects.loc[rejects.ticker == "AAA", "reason_label"].item() == "HIGH_ACCRUAL"


def test_financial_exclusion_before_upcom():
    rejects, _, _ = assigned()
    assert rejects.loc[rejects.ticker == "FIN", "reason_label"].item() == "FINANCIAL_SECTOR_EXCLUDED"


def test_upcom_exclusion_before_formula_filtering():
    rejects, _, _ = assigned()
    assert rejects.loc[rejects.ticker == "UPC", "reason_label"].item() == "UPCOM_EXCLUDED_V1"


def test_sta_higher_tail_ranking():
    result = higher_tail_flags(pd.Series([1.0, 4.0, 2.0, 3.0]), 0.25)
    assert result.cutoff == 4.0 and result.flags.tolist() == [False, True, False, False]


def test_snoa_higher_tail_ranking():
    result = higher_tail_flags(pd.Series([-1.0, -2.0, 0.0]), 1 / 3)
    assert result.cutoff == 0.0 and result.flags.tolist() == [False, False, True]


def test_independent_valid_populations():
    frame, cuts = add_formula_flags(formula_frame(sta=[4, 3, None, None], snoa=[None, 4, 3, 2]), 0.5, -1.78)
    assert cuts["STA"].valid_count == 2 and cuts["SNOA"].valid_count == 3
    assert frame.sta_flag.tolist() != frame.snoa_flag.tolist()


def test_cutoff_ties_included():
    result = higher_tail_flags(pd.Series([5.0, 4.0, 4.0, 1.0]), 0.5)
    assert result.flags.sum() == 3


def test_sta_only_union():
    frame, _ = add_formula_flags(formula_frame(), 0.25, -1.78)
    assert frame.loc[frame.ticker == "AAA", ["sta_flag", "snoa_flag", "high_accrual_flag"]].values.tolist() == [[True, False, True]]


def test_snoa_only_union():
    frame, _ = add_formula_flags(formula_frame(), 0.25, -1.78)
    assert frame.loc[frame.ticker == "DDD", ["sta_flag", "snoa_flag", "high_accrual_flag"]].values.tolist() == [[False, True, True]]


def test_both_union():
    frame, _ = add_formula_flags(formula_frame(snoa=[4, 3, 2, 1]), 0.25, -1.78)
    assert frame.loc[0, "sta_flag"] and frame.loc[0, "snoa_flag"] and frame.loc[0, "high_accrual_flag"]


def test_missing_sta_with_valid_snoa():
    frame, _ = add_formula_flags(formula_frame(sta=[None] * 4), 0.25, -1.78)
    assert frame.loc[3, "snoa_flag"] and frame.loc[3, "high_accrual_flag"]


def test_missing_snoa_with_valid_sta():
    frame, _ = add_formula_flags(formula_frame(snoa=[None] * 4), 0.25, -1.78)
    assert frame.loc[0, "sta_flag"] and frame.loc[0, "high_accrual_flag"]


def test_insufficient_values_excluded_from_percentile_population():
    result = higher_tail_flags(pd.Series([4.0, None, float("nan"), 1.0]), 0.5)
    assert result.valid_count == 2 and result.cutoff == 4.0


def test_m_score_exact_threshold_not_flagged():
    frame, _ = add_formula_flags(formula_frame(m_score=[-1.78] * 4), 0.25, -1.78)
    assert not frame.m_score_flag.any()


def test_m_score_above_threshold_flagged():
    frame, _ = add_formula_flags(formula_frame(m_score=[-1.779, -2, -2, -2]), 0.25, -1.78)
    assert frame.m_score_flag.tolist() == [True, False, False, False]


def test_known_distress_signal_with_other_missing_inputs():
    frame = formula_frame(distress_high_risk=[True, False, False, False], distress_accumulated_loss=[True, None, None, None])
    rejects, _, _ = assigned(frame)
    assert rejects.loc[rejects.ticker == "AAA", "reason_label"].item() == "HIGH_ACCRUAL"
    frame.loc[0, "sta"], frame.loc[0, "snoa"] = -9, -9
    rejects, _, _ = assigned(frame)
    assert rejects.loc[rejects.ticker == "AAA", "reason_label"].item() == "PFD_HIGH_RISK"


def test_missing_warning_does_not_cause_rejection():
    frame = formula_frame(sta=[0, 1, 2, 3], snoa=[0, 1, 2, 3])
    frame, cuts = add_formula_flags(frame, 0.25, -1.78)
    rejects = assign_primary_rejections(universe_frame(), frame, cuts, -1.78)
    assert "BBB" not in set(rejects.ticker)


def test_diagnostic_a_arithmetic():
    rejects, evaluated, _ = assigned()
    diag = build_sector_a(evaluated, rejects)
    assert diag["formula_stage_universe_count"].sum() == 4
    assert diag["universe_weight"].sum() == pytest.approx(1.0)


def test_diagnostic_b_thin_sector_rate():
    frame, _ = add_formula_flags(formula_frame(icb2=["A", "B", "C", "D"]), 0.10, -1.78)
    diag = build_sector_b(frame, 0.10)
    assert (diag.per_sector_cut_count == 1).all()
    assert (diag.effective_cut_percentage == 1.0).all()


def test_greater_than_30_percent_guard():
    rejects = pd.DataFrame({"ticker": ["A", "B"], "reason_label": ["HIGH_ACCRUAL"] * 2, "trigger_value": [1, 2], "threshold_or_cutoff": [0, 0]})
    stats = pd.DataFrame({"filter_stage": [3], "filter": ["HIGH_ACCRUAL"], "entering": [4], "removed": [2], "removal_pct": [0.5]})
    evaluated = formula_frame().assign(ticker=["A", "B", "C", "D"])
    triggered, details = guardrail(stats, rejects, evaluated)
    assert triggered and len(details) == 2


def test_survivor_schema(monkeypatch):
    evaluated = formula_frame().assign(annual_n=2025, annual_n_minus_1=2024, available_from="2026-03-31")
    monkeypatch.setattr("src.screener.step1_pipeline.evaluate_formula_stage", lambda *args: evaluated)
    result = run_cleaning_pipeline(universe_frame(), "unused", "2026-07-18", 0.25, -1.78)
    required = {"ticker", "annual_n", "sta", "snoa", "m_score", "sta_percentile", "source", "available_from"}
    assert required <= set(result.survivors.columns).union(result.evaluated.columns)


def test_detailed_reject_schema():
    rejects, _, _ = assigned()
    assert tuple(rejects.columns) == REJECT_COLUMNS


def test_preservation_of_historical_reject_rows():
    history = universe_frame().iloc[:1].copy()
    new_rejects, _, _ = assigned()
    final, proof = extend_reject_history(history, new_rejects.iloc[:1], universe_frame())
    pd.testing.assert_frame_equal(history, final.iloc[:1][history.columns], check_dtype=False)
    assert proof["historical_rows_preserved"] and all(column in final for column in AUDIT_COLUMNS)


def test_future_available_from_exclusion():
    rows = pd.DataFrame(
        [["AAA", "balance_sheet", "total_assets", 1, "VND", "ANNUAL", "2025", "2026-08-01", "2026-07-18", "x", "OK", "", "", "", ""]],
        columns=ANNUAL_COLUMNS,
    )
    assert select_latest_eligible_pair(rows, "2026-07-18").eligible_rows.empty


def test_unit_consistency():
    values = pd.Series([1.0, 2.0, 3.0, 4.0])
    assert higher_tail_flags(values, 0.25).flags.equals(higher_tail_flags(values * 1_000_000_000, 0.25).flags)


def test_no_network_access(monkeypatch):
    monkeypatch.setattr(socket, "create_connection", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("network forbidden")))
    assert higher_tail_flags(pd.Series([1.0, 2.0]), 0.5).cutoff == 2.0
