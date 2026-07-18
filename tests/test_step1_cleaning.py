"""Fixture-only hand checks for the Sprint 4 Step-1A formula engine.

The VNM inputs below are copied from the saved annual cache (2025 and 2024).
Expected values are literal constants calculated independently with Decimal;
the tests make no API, network, or file-system call.
"""

from __future__ import annotations

import inspect
import math

import pytest

from src.screener.step1_cleaning import (
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


VNM_2025 = {
    "total_assets": 53_312_370_717_301,
    "current_assets": 36_261_180_908_033,
    "cash_and_cash_equivalents": 1_794_879_718_871,
    "short_term_investments": 21_354_863_600_460,
    "accounts_receivable": 6_027_719_081_073,
    "current_liabilities": 18_520_286_019_795,
    "short_term_borrowings": 9_393_736_731_992,
    "taxes_and_other_payable_to_state_budget": 1_803_999_103_453,
    "long_term_borrowings": 62_907_826_150,
    "long_term_liabilities": 309_069_411_399,
    "tangible_fixed_assets": 11_618_118_961_976,
    "owners_equity": 34_483_015_286_107,
    "net_sales": 63_645_886_756_227,
    "gross_profit": 26_209_474_194_531,
    "selling_expenses": -13_641_689_163_684,
    "general_and_admin_expenses": -1_904_069_825_709,
    "net_profit_loss_after_tax": 9_413_589_732_469,
    "depreciation_and_amortization": 2_116_245_292_358,
    "net_cash_inflows_outflows_from_operating_activities": 8_668_137_048_520,
}

VNM_2024 = {
    "total_assets": 55_049_061_537_061,
    "current_assets": 37_553_650_065_098,
    "cash_and_cash_equivalents": 2_225_943_732_075,
    "short_term_investments": 23_260_088_671_767,
    "accounts_receivable": 6_233_758_612_009,
    "current_liabilities": 18_459_546_837_640,
    "short_term_borrowings": 9_115_435_107_250,
    "taxes_and_other_payable_to_state_budget": 1_014_478_141_379,
    "long_term_borrowings": 157_903_902_450,
    "long_term_liabilities": 415_111_869_758,
    "tangible_fixed_assets": 11_520_200_967_499,
    "owners_equity": 36_174_402_829_663,
    "net_sales": 61_782_609_528_445,
    "gross_profit": 25_590_176_323_124,
    "selling_expenses": -13_357_706_796_806,
    "general_and_admin_expenses": -1_827_916_838_987,
    "net_profit_loss_after_tax": 9_452_892_989_948,
    "depreciation_and_amortization": 2_095_159_644_941,
    "net_cash_inflows_outflows_from_operating_activities": 9_685_937_539_346,
}


def sta_inputs(scale: float = 1.0) -> dict[str, float]:
    return {
        "current_assets_n": VNM_2025["current_assets"] * scale,
        "current_assets_n_minus_1": VNM_2024["current_assets"] * scale,
        "cash_and_cash_equivalents_n": VNM_2025["cash_and_cash_equivalents"] * scale,
        "cash_and_cash_equivalents_n_minus_1": VNM_2024["cash_and_cash_equivalents"] * scale,
        "current_liabilities_n": VNM_2025["current_liabilities"] * scale,
        "current_liabilities_n_minus_1": VNM_2024["current_liabilities"] * scale,
        "short_term_borrowings_n": VNM_2025["short_term_borrowings"] * scale,
        "short_term_borrowings_n_minus_1": VNM_2024["short_term_borrowings"] * scale,
        "taxes_and_other_payable_to_state_budget_n": (
            VNM_2025["taxes_and_other_payable_to_state_budget"] * scale
        ),
        "taxes_and_other_payable_to_state_budget_n_minus_1": (
            VNM_2024["taxes_and_other_payable_to_state_budget"] * scale
        ),
        "depreciation_and_amortization_n": VNM_2025["depreciation_and_amortization"] * scale,
        "total_assets_n": VNM_2025["total_assets"] * scale,
        "total_assets_n_minus_1": VNM_2024["total_assets"] * scale,
    }


def snoa_inputs(scale: float = 1.0) -> dict[str, float]:
    return {
        "total_assets_n": VNM_2025["total_assets"] * scale,
        "total_assets_n_minus_1": VNM_2024["total_assets"] * scale,
        "cash_and_cash_equivalents_n": VNM_2025["cash_and_cash_equivalents"] * scale,
        "short_term_investments_n": VNM_2025["short_term_investments"] * scale,
        "short_term_borrowings_n": VNM_2025["short_term_borrowings"] * scale,
        "long_term_borrowings_n": VNM_2025["long_term_borrowings"] * scale,
        "owners_equity_n": VNM_2025["owners_equity"] * scale,
    }


def test_sta_hand_computed() -> None:
    # Accruals = -1,970,567,031,558; average assets = 54,180,716,127,181.
    assert calculate_sta(**sta_inputs()).value == pytest.approx(-0.0363702655190528169)


def test_snoa_hand_computed() -> None:
    # NOA = 20,789,916,524,918; beginning assets = 55,049,061,537,061.
    assert calculate_snoa(**snoa_inputs()).value == pytest.approx(0.3776615975718583964)


def test_snoa_algebraic_identity() -> None:
    operating_assets = (
        VNM_2025["total_assets"]
        - VNM_2025["cash_and_cash_equivalents"]
        - VNM_2025["short_term_investments"]
    )
    operating_liabilities = (
        VNM_2025["total_assets"]
        - VNM_2025["short_term_borrowings"]
        - VNM_2025["long_term_borrowings"]
        - VNM_2025["owners_equity"]
    )
    direct_noa = (
        VNM_2025["short_term_borrowings"]
        + VNM_2025["long_term_borrowings"]
        + VNM_2025["owners_equity"]
        - VNM_2025["cash_and_cash_equivalents"]
        - VNM_2025["short_term_investments"]
    )
    assert operating_assets - operating_liabilities == direct_noa == 20_789_916_524_918


def test_snoa_ignores_minority_and_preferred_fields_outside_function() -> None:
    baseline_fixture = {**snoa_inputs(), "minority_interests": 1, "preferred_shares": 2}
    garbage_fixture = {
        **baseline_fixture,
        "minority_interests": 10**100,
        "preferred_shares": -(10**100),
    }
    accepted = set(inspect.signature(calculate_snoa).parameters)
    assert "minority_interests" not in accepted
    assert "preferred_shares" not in accepted
    baseline = calculate_snoa(**{k: v for k, v in baseline_fixture.items() if k in accepted})
    with_garbage = calculate_snoa(**{k: v for k, v in garbage_fixture.items() if k in accepted})
    assert baseline == with_garbage


def test_dsri_hand_computed() -> None:
    # (6,027,719,081,073 / 63,645,886,756,227) / (6,233,758,612,009 / 61,782,609,528,445).
    result = calculate_dsri(
        VNM_2025["accounts_receivable"],
        VNM_2025["net_sales"],
        VNM_2024["accounts_receivable"],
        VNM_2024["net_sales"],
    )
    assert result.value == pytest.approx(0.9386397215835655378)


def test_gmi_hand_computed() -> None:
    result = calculate_gmi(
        VNM_2025["gross_profit"],
        VNM_2025["net_sales"],
        VNM_2024["gross_profit"],
        VNM_2024["net_sales"],
    )
    assert result.value == pytest.approx(1.0058172136635434611)


def test_aqi_hand_computed_with_tangible_fixed_assets() -> None:
    # AQ_N = 0.10191013406816765; AQ_N-1 = 0.10854336727323270.
    result = calculate_aqi(
        VNM_2025["current_assets"],
        VNM_2025["tangible_fixed_assets"],
        VNM_2025["total_assets"],
        VNM_2024["current_assets"],
        VNM_2024["tangible_fixed_assets"],
        VNM_2024["total_assets"],
    )
    assert result.value == pytest.approx(0.9388886362041134293)


def test_sgi_hand_computed() -> None:
    result = calculate_sgi(VNM_2025["net_sales"], VNM_2024["net_sales"])
    assert result.value == pytest.approx(1.0301586035618022661)


def test_depi_hand_computed() -> None:
    result = calculate_depi(
        VNM_2025["depreciation_and_amortization"],
        VNM_2025["tangible_fixed_assets"],
        VNM_2024["depreciation_and_amortization"],
        VNM_2024["tangible_fixed_assets"],
    )
    assert result.value == pytest.approx(0.9986896024368139957)


def test_sgai_hand_computed() -> None:
    result = calculate_sgai(
        VNM_2025["selling_expenses"],
        VNM_2025["general_and_admin_expenses"],
        VNM_2025["net_sales"],
        VNM_2024["selling_expenses"],
        VNM_2024["general_and_admin_expenses"],
        VNM_2024["net_sales"],
    )
    assert result.value == pytest.approx(0.9937455672464139089)


def test_lvgi_hand_computed() -> None:
    result = calculate_lvgi(
        VNM_2025["current_liabilities"],
        VNM_2025["long_term_liabilities"],
        VNM_2025["total_assets"],
        VNM_2024["current_liabilities"],
        VNM_2024["long_term_liabilities"],
        VNM_2024["total_assets"],
    )
    assert result.value == pytest.approx(1.0300973508827059577)


def test_tata_hand_computed() -> None:
    result = calculate_tata(
        VNM_2025["net_profit_loss_after_tax"],
        VNM_2025["net_cash_inflows_outflows_from_operating_activities"],
        VNM_2025["total_assets"],
    )
    assert result.value == pytest.approx(0.0139827337242589500)


VNM_INDICES = {
    "dsri": 0.9386397215835655378,
    "gmi": 1.0058172136635434611,
    "aqi": 0.9388886362041134293,
    "sgi": 1.0301586035618022661,
    "depi": 0.9986896024368139957,
    "sgai": 0.9937455672464139089,
    "lvgi": 1.0300973508827059577,
    "tata": 0.0139827337242589500,
}


def test_m_score_hand_computed() -> None:
    # Literal substitution into the nine frozen coefficients gives -2.4746590398541661.
    assert calculate_m_score(**VNM_INDICES).value == pytest.approx(-2.4746590398541661150)


def test_accumulated_loss_distress() -> None:
    result = calculate_simple_distress(-1, 100, False)
    assert (result.accumulated_loss, result.high_risk) == (True, True)


def test_negative_equity_distress() -> None:
    result = calculate_simple_distress(1, -100, False)
    assert (result.negative_equity, result.high_risk) == (True, True)


def test_warning_list_distress() -> None:
    result = calculate_simple_distress(1, 100, True)
    assert (result.hose_warning, result.high_risk) == (True, True)


def test_missing_warning_list_stays_unavailable() -> None:
    result = calculate_simple_distress(1, 100, None)
    assert result.hose_warning is None
    assert result.high_risk is None
    assert result.reason == "INSUFFICIENT_DATA_FOR_DISTRESS"
    assert result.invalid_inputs == ("hose_warning",)


@pytest.mark.parametrize(
    ("function", "kwargs", "reason", "invalid_name"),
    [
        (calculate_sta, {**sta_inputs(), "current_assets_n": None}, "INSUFFICIENT_DATA_FOR_STA", "current_assets_n"),
        (calculate_snoa, {**snoa_inputs(), "owners_equity_n": None}, "INSUFFICIENT_DATA_FOR_SNOA", "owners_equity_n"),
        (calculate_dsri, {"accounts_receivable_n": None, "net_sales_n": 1, "accounts_receivable_n_minus_1": 1, "net_sales_n_minus_1": 1}, "INSUFFICIENT_DATA_FOR_DSRI", "accounts_receivable_n"),
        (calculate_gmi, {"gross_profit_n": None, "net_sales_n": 1, "gross_profit_n_minus_1": 1, "net_sales_n_minus_1": 1}, "INSUFFICIENT_DATA_FOR_GMI", "gross_profit_n"),
        (calculate_aqi, {"current_assets_n": None, "tangible_fixed_assets_n": 1, "total_assets_n": 3, "current_assets_n_minus_1": 1, "tangible_fixed_assets_n_minus_1": 1, "total_assets_n_minus_1": 3}, "INSUFFICIENT_DATA_FOR_AQI", "current_assets_n"),
        (calculate_sgi, {"net_sales_n": None, "net_sales_n_minus_1": 1}, "INSUFFICIENT_DATA_FOR_SGI", "net_sales_n"),
        (calculate_depi, {"depreciation_and_amortization_n": None, "tangible_fixed_assets_n": 1, "depreciation_and_amortization_n_minus_1": 1, "tangible_fixed_assets_n_minus_1": 1}, "INSUFFICIENT_DATA_FOR_DEPI", "depreciation_and_amortization_n"),
        (calculate_sgai, {"selling_expenses_n": None, "general_and_admin_expenses_n": 1, "net_sales_n": 1, "selling_expenses_n_minus_1": 1, "general_and_admin_expenses_n_minus_1": 1, "net_sales_n_minus_1": 1}, "INSUFFICIENT_DATA_FOR_SGAI", "selling_expenses_n"),
        (calculate_lvgi, {"current_liabilities_n": None, "long_term_liabilities_n": 1, "total_assets_n": 2, "current_liabilities_n_minus_1": 1, "long_term_liabilities_n_minus_1": 1, "total_assets_n_minus_1": 2}, "INSUFFICIENT_DATA_FOR_LVGI", "current_liabilities_n"),
        (calculate_tata, {"net_profit_loss_after_tax_n": None, "net_cash_inflows_outflows_from_operating_activities_n": 1, "total_assets_n": 1}, "INSUFFICIENT_DATA_FOR_TATA", "net_profit_loss_after_tax_n"),
        (calculate_m_score, {**VNM_INDICES, "dsri": None}, "INSUFFICIENT_DATA_FOR_M_SCORE", "dsri"),
    ],
)
def test_each_formula_reports_its_own_missing_input(function, kwargs, reason, invalid_name) -> None:
    result = function(**kwargs)
    assert result.reason == reason
    assert result.invalid_inputs == (invalid_name,)


def test_non_numeric_input_is_not_coerced_to_zero() -> None:
    result = calculate_sgi("missing", 1)
    assert result.reason == "INSUFFICIENT_DATA_FOR_SGI"
    assert result.invalid_inputs == ("net_sales_n",)


def test_zero_denominator_is_insufficient() -> None:
    result = calculate_sgi(10, 0)
    assert result.reason == "INSUFFICIENT_DATA_FOR_SGI"
    assert result.invalid_inputs == ("net_sales_n_minus_1",)


@pytest.mark.parametrize("bad_value", [math.nan, math.inf, -math.inf])
def test_nan_and_infinity_are_insufficient(bad_value: float) -> None:
    result = calculate_sgi(bad_value, 1)
    assert result.reason == "INSUFFICIENT_DATA_FOR_SGI"
    assert result.invalid_inputs == ("net_sales_n",)


def ratio_values(scale: float) -> tuple[float, ...]:
    sta = calculate_sta(**sta_inputs(scale)).value
    snoa = calculate_snoa(**snoa_inputs(scale)).value
    dsri = calculate_dsri(
        VNM_2025["accounts_receivable"] * scale,
        VNM_2025["net_sales"] * scale,
        VNM_2024["accounts_receivable"] * scale,
        VNM_2024["net_sales"] * scale,
    ).value
    gmi = calculate_gmi(
        VNM_2025["gross_profit"] * scale,
        VNM_2025["net_sales"] * scale,
        VNM_2024["gross_profit"] * scale,
        VNM_2024["net_sales"] * scale,
    ).value
    aqi = calculate_aqi(
        VNM_2025["current_assets"] * scale,
        VNM_2025["tangible_fixed_assets"] * scale,
        VNM_2025["total_assets"] * scale,
        VNM_2024["current_assets"] * scale,
        VNM_2024["tangible_fixed_assets"] * scale,
        VNM_2024["total_assets"] * scale,
    ).value
    sgi = calculate_sgi(VNM_2025["net_sales"] * scale, VNM_2024["net_sales"] * scale).value
    depi = calculate_depi(
        VNM_2025["depreciation_and_amortization"] * scale,
        VNM_2025["tangible_fixed_assets"] * scale,
        VNM_2024["depreciation_and_amortization"] * scale,
        VNM_2024["tangible_fixed_assets"] * scale,
    ).value
    sgai = calculate_sgai(
        VNM_2025["selling_expenses"] * scale,
        VNM_2025["general_and_admin_expenses"] * scale,
        VNM_2025["net_sales"] * scale,
        VNM_2024["selling_expenses"] * scale,
        VNM_2024["general_and_admin_expenses"] * scale,
        VNM_2024["net_sales"] * scale,
    ).value
    lvgi = calculate_lvgi(
        VNM_2025["current_liabilities"] * scale,
        VNM_2025["long_term_liabilities"] * scale,
        VNM_2025["total_assets"] * scale,
        VNM_2024["current_liabilities"] * scale,
        VNM_2024["long_term_liabilities"] * scale,
        VNM_2024["total_assets"] * scale,
    ).value
    tata = calculate_tata(
        VNM_2025["net_profit_loss_after_tax"] * scale,
        VNM_2025["net_cash_inflows_outflows_from_operating_activities"] * scale,
        VNM_2025["total_assets"] * scale,
    ).value
    assert all(value is not None for value in (sta, snoa, dsri, gmi, aqi, sgi, depi, sgai, lvgi, tata))
    return sta, snoa, dsri, gmi, aqi, sgi, depi, sgai, lvgi, tata  # type: ignore[return-value]


@pytest.mark.parametrize("scale", [1_000.0, 1_000_000_000.0])
def test_unit_consistency_for_all_ratio_metrics(scale: float) -> None:
    assert ratio_values(scale) == pytest.approx(ratio_values(1.0), rel=1e-12, abs=1e-15)
