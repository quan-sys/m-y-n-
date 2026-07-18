"""Pure Sprint 4 Step-1A financial cleaning formulas.

The functions in this module perform no file, network, or configuration I/O.
They report formula-specific insufficiency instead of raising for bad financial
inputs so one unavailable formula does not prevent other checks from running.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any


@dataclass(frozen=True)
class FormulaResult:
    """A numeric formula result or a structured insufficiency result."""

    value: float | None
    reason: str | None = None
    invalid_inputs: tuple[str, ...] = ()

    @property
    def is_sufficient(self) -> bool:
        return self.reason is None


@dataclass(frozen=True)
class DistressResult:
    """The three simple distress signals and their combined state."""

    accumulated_loss: bool | None
    negative_equity: bool | None
    hose_warning: bool | None
    high_risk: bool | None
    reason: str | None = None
    invalid_inputs: tuple[str, ...] = ()

    @property
    def is_sufficient(self) -> bool:
        return self.reason is None


def _insufficient(formula: str, *invalid_inputs: str) -> FormulaResult:
    return FormulaResult(
        value=None,
        reason=f"INSUFFICIENT_DATA_FOR_{formula}",
        invalid_inputs=tuple(dict.fromkeys(invalid_inputs)),
    )


def _numbers(formula: str, **inputs: Any) -> tuple[dict[str, float] | None, FormulaResult | None]:
    values: dict[str, float] = {}
    invalid: list[str] = []
    for name, raw_value in inputs.items():
        if raw_value is None or isinstance(raw_value, (bool, str, bytes, complex)):
            invalid.append(name)
            continue
        try:
            value = float(raw_value)
        except (TypeError, ValueError, OverflowError):
            invalid.append(name)
            continue
        if not math.isfinite(value):
            invalid.append(name)
            continue
        values[name] = value
    if invalid:
        return None, _insufficient(formula, *invalid)
    return values, None


def calculate_sta(
    current_assets_n: float,
    current_assets_n_minus_1: float,
    cash_and_cash_equivalents_n: float,
    cash_and_cash_equivalents_n_minus_1: float,
    current_liabilities_n: float,
    current_liabilities_n_minus_1: float,
    short_term_borrowings_n: float,
    short_term_borrowings_n_minus_1: float,
    taxes_and_other_payable_to_state_budget_n: float,
    taxes_and_other_payable_to_state_budget_n_minus_1: float,
    depreciation_and_amortization_n: float,
    total_assets_n: float,
    total_assets_n_minus_1: float,
) -> FormulaResult:
    """Scaled total accruals from balance-sheet changes."""

    values, error = _numbers(
        "STA",
        current_assets_n=current_assets_n,
        current_assets_n_minus_1=current_assets_n_minus_1,
        cash_and_cash_equivalents_n=cash_and_cash_equivalents_n,
        cash_and_cash_equivalents_n_minus_1=cash_and_cash_equivalents_n_minus_1,
        current_liabilities_n=current_liabilities_n,
        current_liabilities_n_minus_1=current_liabilities_n_minus_1,
        short_term_borrowings_n=short_term_borrowings_n,
        short_term_borrowings_n_minus_1=short_term_borrowings_n_minus_1,
        taxes_and_other_payable_to_state_budget_n=taxes_and_other_payable_to_state_budget_n,
        taxes_and_other_payable_to_state_budget_n_minus_1=(
            taxes_and_other_payable_to_state_budget_n_minus_1
        ),
        depreciation_and_amortization_n=depreciation_and_amortization_n,
        total_assets_n=total_assets_n,
        total_assets_n_minus_1=total_assets_n_minus_1,
    )
    if error:
        return error
    assert values is not None
    average_assets = (values["total_assets_n"] + values["total_assets_n_minus_1"]) / 2.0
    if average_assets == 0:
        return _insufficient("STA", "total_assets_n", "total_assets_n_minus_1")
    change_current_assets = values["current_assets_n"] - values["current_assets_n_minus_1"]
    change_cash = (
        values["cash_and_cash_equivalents_n"]
        - values["cash_and_cash_equivalents_n_minus_1"]
    )
    change_current_liabilities = (
        values["current_liabilities_n"] - values["current_liabilities_n_minus_1"]
    )
    change_short_term_debt = (
        values["short_term_borrowings_n"] - values["short_term_borrowings_n_minus_1"]
    )
    change_taxes_payable = (
        values["taxes_and_other_payable_to_state_budget_n"]
        - values["taxes_and_other_payable_to_state_budget_n_minus_1"]
    )
    accruals = (
        change_current_assets
        - change_cash
        - (change_current_liabilities - change_short_term_debt - change_taxes_payable)
        - values["depreciation_and_amortization_n"]
    )
    return FormulaResult(accruals / average_assets)


def calculate_snoa(
    total_assets_n: float,
    total_assets_n_minus_1: float,
    cash_and_cash_equivalents_n: float,
    short_term_investments_n: float,
    short_term_borrowings_n: float,
    long_term_borrowings_n: float,
    owners_equity_n: float,
) -> FormulaResult:
    """VAS-adjusted scaled net operating assets."""

    values, error = _numbers(
        "SNOA",
        total_assets_n=total_assets_n,
        total_assets_n_minus_1=total_assets_n_minus_1,
        cash_and_cash_equivalents_n=cash_and_cash_equivalents_n,
        short_term_investments_n=short_term_investments_n,
        short_term_borrowings_n=short_term_borrowings_n,
        long_term_borrowings_n=long_term_borrowings_n,
        owners_equity_n=owners_equity_n,
    )
    if error:
        return error
    assert values is not None
    if values["total_assets_n_minus_1"] == 0:
        return _insufficient("SNOA", "total_assets_n_minus_1")
    operating_assets = values["total_assets_n"] - (
        values["cash_and_cash_equivalents_n"] + values["short_term_investments_n"]
    )
    operating_liabilities = values["total_assets_n"] - (
        values["short_term_borrowings_n"]
        + values["long_term_borrowings_n"]
        + values["owners_equity_n"]
    )
    noa = operating_assets - operating_liabilities
    return FormulaResult(noa / values["total_assets_n_minus_1"])


def calculate_dsri(
    accounts_receivable_n: float,
    net_sales_n: float,
    accounts_receivable_n_minus_1: float,
    net_sales_n_minus_1: float,
) -> FormulaResult:
    """Days' sales in receivables index."""

    values, error = _numbers(
        "DSRI",
        accounts_receivable_n=accounts_receivable_n,
        net_sales_n=net_sales_n,
        accounts_receivable_n_minus_1=accounts_receivable_n_minus_1,
        net_sales_n_minus_1=net_sales_n_minus_1,
    )
    if error:
        return error
    assert values is not None
    if values["net_sales_n"] == 0:
        return _insufficient("DSRI", "net_sales_n")
    if values["net_sales_n_minus_1"] == 0:
        return _insufficient("DSRI", "net_sales_n_minus_1")
    previous_ratio = values["accounts_receivable_n_minus_1"] / values["net_sales_n_minus_1"]
    if previous_ratio == 0:
        return _insufficient("DSRI", "accounts_receivable_n_minus_1")
    return FormulaResult((values["accounts_receivable_n"] / values["net_sales_n"]) / previous_ratio)


def calculate_gmi(
    gross_profit_n: float,
    net_sales_n: float,
    gross_profit_n_minus_1: float,
    net_sales_n_minus_1: float,
) -> FormulaResult:
    """Gross margin index."""

    values, error = _numbers(
        "GMI",
        gross_profit_n=gross_profit_n,
        net_sales_n=net_sales_n,
        gross_profit_n_minus_1=gross_profit_n_minus_1,
        net_sales_n_minus_1=net_sales_n_minus_1,
    )
    if error:
        return error
    assert values is not None
    if values["net_sales_n"] == 0:
        return _insufficient("GMI", "net_sales_n")
    if values["net_sales_n_minus_1"] == 0:
        return _insufficient("GMI", "net_sales_n_minus_1")
    current_margin = values["gross_profit_n"] / values["net_sales_n"]
    if current_margin == 0:
        return _insufficient("GMI", "gross_profit_n")
    previous_margin = values["gross_profit_n_minus_1"] / values["net_sales_n_minus_1"]
    return FormulaResult(previous_margin / current_margin)


def calculate_aqi(
    current_assets_n: float,
    tangible_fixed_assets_n: float,
    total_assets_n: float,
    current_assets_n_minus_1: float,
    tangible_fixed_assets_n_minus_1: float,
    total_assets_n_minus_1: float,
) -> FormulaResult:
    """Asset quality index using frozen tangible fixed assets for PP&E."""

    values, error = _numbers(
        "AQI",
        current_assets_n=current_assets_n,
        tangible_fixed_assets_n=tangible_fixed_assets_n,
        total_assets_n=total_assets_n,
        current_assets_n_minus_1=current_assets_n_minus_1,
        tangible_fixed_assets_n_minus_1=tangible_fixed_assets_n_minus_1,
        total_assets_n_minus_1=total_assets_n_minus_1,
    )
    if error:
        return error
    assert values is not None
    if values["total_assets_n"] == 0:
        return _insufficient("AQI", "total_assets_n")
    if values["total_assets_n_minus_1"] == 0:
        return _insufficient("AQI", "total_assets_n_minus_1")
    current_quality = 1.0 - (
        values["current_assets_n"] + values["tangible_fixed_assets_n"]
    ) / values["total_assets_n"]
    previous_quality = 1.0 - (
        values["current_assets_n_minus_1"] + values["tangible_fixed_assets_n_minus_1"]
    ) / values["total_assets_n_minus_1"]
    if previous_quality == 0:
        return _insufficient("AQI", "asset_quality_n_minus_1")
    return FormulaResult(current_quality / previous_quality)


def calculate_sgi(net_sales_n: float, net_sales_n_minus_1: float) -> FormulaResult:
    """Sales growth index."""

    values, error = _numbers(
        "SGI", net_sales_n=net_sales_n, net_sales_n_minus_1=net_sales_n_minus_1
    )
    if error:
        return error
    assert values is not None
    if values["net_sales_n_minus_1"] == 0:
        return _insufficient("SGI", "net_sales_n_minus_1")
    return FormulaResult(values["net_sales_n"] / values["net_sales_n_minus_1"])


def calculate_depi(
    depreciation_and_amortization_n: float,
    tangible_fixed_assets_n: float,
    depreciation_and_amortization_n_minus_1: float,
    tangible_fixed_assets_n_minus_1: float,
) -> FormulaResult:
    """Depreciation index."""

    values, error = _numbers(
        "DEPI",
        depreciation_and_amortization_n=depreciation_and_amortization_n,
        tangible_fixed_assets_n=tangible_fixed_assets_n,
        depreciation_and_amortization_n_minus_1=depreciation_and_amortization_n_minus_1,
        tangible_fixed_assets_n_minus_1=tangible_fixed_assets_n_minus_1,
    )
    if error:
        return error
    assert values is not None
    current_base = values["depreciation_and_amortization_n"] + values["tangible_fixed_assets_n"]
    previous_base = (
        values["depreciation_and_amortization_n_minus_1"]
        + values["tangible_fixed_assets_n_minus_1"]
    )
    if current_base == 0:
        return _insufficient(
            "DEPI", "depreciation_and_amortization_n", "tangible_fixed_assets_n"
        )
    if previous_base == 0:
        return _insufficient(
            "DEPI",
            "depreciation_and_amortization_n_minus_1",
            "tangible_fixed_assets_n_minus_1",
        )
    current_rate = values["depreciation_and_amortization_n"] / current_base
    if current_rate == 0:
        return _insufficient("DEPI", "depreciation_and_amortization_n")
    previous_rate = values["depreciation_and_amortization_n_minus_1"] / previous_base
    return FormulaResult(previous_rate / current_rate)


def calculate_sgai(
    selling_expenses_n: float,
    general_and_admin_expenses_n: float,
    net_sales_n: float,
    selling_expenses_n_minus_1: float,
    general_and_admin_expenses_n_minus_1: float,
    net_sales_n_minus_1: float,
) -> FormulaResult:
    """Sales, general and administrative expenses index."""

    values, error = _numbers(
        "SGAI",
        selling_expenses_n=selling_expenses_n,
        general_and_admin_expenses_n=general_and_admin_expenses_n,
        net_sales_n=net_sales_n,
        selling_expenses_n_minus_1=selling_expenses_n_minus_1,
        general_and_admin_expenses_n_minus_1=general_and_admin_expenses_n_minus_1,
        net_sales_n_minus_1=net_sales_n_minus_1,
    )
    if error:
        return error
    assert values is not None
    if values["net_sales_n"] == 0:
        return _insufficient("SGAI", "net_sales_n")
    if values["net_sales_n_minus_1"] == 0:
        return _insufficient("SGAI", "net_sales_n_minus_1")
    current_ratio = (
        values["selling_expenses_n"] + values["general_and_admin_expenses_n"]
    ) / values["net_sales_n"]
    previous_ratio = (
        values["selling_expenses_n_minus_1"]
        + values["general_and_admin_expenses_n_minus_1"]
    ) / values["net_sales_n_minus_1"]
    if previous_ratio == 0:
        return _insufficient(
            "SGAI", "selling_expenses_n_minus_1", "general_and_admin_expenses_n_minus_1"
        )
    return FormulaResult(current_ratio / previous_ratio)


def calculate_lvgi(
    current_liabilities_n: float,
    long_term_liabilities_n: float,
    total_assets_n: float,
    current_liabilities_n_minus_1: float,
    long_term_liabilities_n_minus_1: float,
    total_assets_n_minus_1: float,
) -> FormulaResult:
    """Leverage index."""

    values, error = _numbers(
        "LVGI",
        current_liabilities_n=current_liabilities_n,
        long_term_liabilities_n=long_term_liabilities_n,
        total_assets_n=total_assets_n,
        current_liabilities_n_minus_1=current_liabilities_n_minus_1,
        long_term_liabilities_n_minus_1=long_term_liabilities_n_minus_1,
        total_assets_n_minus_1=total_assets_n_minus_1,
    )
    if error:
        return error
    assert values is not None
    if values["total_assets_n"] == 0:
        return _insufficient("LVGI", "total_assets_n")
    if values["total_assets_n_minus_1"] == 0:
        return _insufficient("LVGI", "total_assets_n_minus_1")
    current_leverage = (
        values["current_liabilities_n"] + values["long_term_liabilities_n"]
    ) / values["total_assets_n"]
    previous_leverage = (
        values["current_liabilities_n_minus_1"]
        + values["long_term_liabilities_n_minus_1"]
    ) / values["total_assets_n_minus_1"]
    if previous_leverage == 0:
        return _insufficient(
            "LVGI", "current_liabilities_n_minus_1", "long_term_liabilities_n_minus_1"
        )
    return FormulaResult(current_leverage / previous_leverage)


def calculate_tata(
    net_profit_loss_after_tax_n: float,
    net_cash_inflows_outflows_from_operating_activities_n: float,
    total_assets_n: float,
) -> FormulaResult:
    """Total accruals to total assets using frozen after-tax income."""

    values, error = _numbers(
        "TATA",
        net_profit_loss_after_tax_n=net_profit_loss_after_tax_n,
        net_cash_inflows_outflows_from_operating_activities_n=(
            net_cash_inflows_outflows_from_operating_activities_n
        ),
        total_assets_n=total_assets_n,
    )
    if error:
        return error
    assert values is not None
    if values["total_assets_n"] == 0:
        return _insufficient("TATA", "total_assets_n")
    accruals = (
        values["net_profit_loss_after_tax_n"]
        - values["net_cash_inflows_outflows_from_operating_activities_n"]
    )
    return FormulaResult(accruals / values["total_assets_n"])


def calculate_m_score(
    dsri: float,
    gmi: float,
    aqi: float,
    sgi: float,
    depi: float,
    sgai: float,
    lvgi: float,
    tata: float,
) -> FormulaResult:
    """Beneish M-Score with the frozen specification coefficients."""

    values, error = _numbers(
        "M_SCORE",
        dsri=dsri,
        gmi=gmi,
        aqi=aqi,
        sgi=sgi,
        depi=depi,
        sgai=sgai,
        lvgi=lvgi,
        tata=tata,
    )
    if error:
        return error
    assert values is not None
    score = (
        -4.840
        + 0.920 * values["dsri"]
        + 0.528 * values["gmi"]
        + 0.404 * values["aqi"]
        + 0.892 * values["sgi"]
        + 0.115 * values["depi"]
        - 0.172 * values["sgai"]
        + 4.679 * values["tata"]
        - 0.327 * values["lvgi"]
    )
    return FormulaResult(score)


def calculate_simple_distress(
    undistributed_earnings_n: float,
    owners_equity_n: float,
    hose_warning: bool | None,
) -> DistressResult:
    """Evaluate accumulated loss, negative equity, and a supplied HoSE warning."""

    earnings_values, earnings_error = _numbers(
        "DISTRESS", undistributed_earnings_n=undistributed_earnings_n
    )
    equity_values, equity_error = _numbers(
        "DISTRESS", owners_equity_n=owners_equity_n
    )
    invalid: list[str] = []
    if earnings_error:
        invalid.extend(earnings_error.invalid_inputs)
    if equity_error:
        invalid.extend(equity_error.invalid_inputs)
    warning_value: bool | None
    if hose_warning is None:
        warning_value = None
        invalid.append("hose_warning")
    elif isinstance(hose_warning, bool):
        warning_value = hose_warning
    else:
        warning_value = None
        invalid.append("hose_warning")

    accumulated_loss = (
        None
        if earnings_values is None
        else earnings_values["undistributed_earnings_n"] < 0
    )
    negative_equity = (
        None if equity_values is None else equity_values["owners_equity_n"] < 0
    )
    known_signals = (accumulated_loss, negative_equity, warning_value)
    if any(signal is True for signal in known_signals):
        high_risk: bool | None = True
    elif all(signal is False for signal in known_signals):
        high_risk = False
    else:
        high_risk = None
    reason = "INSUFFICIENT_DATA_FOR_DISTRESS" if invalid else None
    return DistressResult(
        accumulated_loss=accumulated_loss,
        negative_equity=negative_equity,
        hose_warning=warning_value,
        high_risk=high_risk,
        reason=reason,
        invalid_inputs=tuple(dict.fromkeys(invalid)),
    )
