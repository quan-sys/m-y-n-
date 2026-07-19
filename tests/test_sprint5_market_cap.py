from __future__ import annotations

from scripts.fetch_sprint5_market_cap import record_passes_contract


def test_direct_market_cap_requires_vnd_unit_and_as_of() -> None:
    record = {
        "supplies_direct_market_cap": True,
        "explicit_market_cap_unit_evidence": "NONE_IN_PUBLIC_RETURN_OR_METHOD_DOCSTRING",
        "as_of_fields": [],
    }
    assert record_passes_contract(record) is False
    record["explicit_market_cap_unit_evidence"] = "VND"
    record["as_of_fields"] = ["quote_as_of"]
    assert record_passes_contract(record) is True


def test_proxy_requires_explicit_price_unit_true_outstanding_shares_and_as_of() -> None:
    record = {
        "supplies_current_unadjusted_price": True,
        "explicit_price_unit_evidence": "NONE_IN_PUBLIC_RETURN_OR_METHOD_DOCSTRING",
        "supplies_true_shares_outstanding": True,
        "as_of_fields": ["trading_date"],
    }
    assert record_passes_contract(record) is False
    record["explicit_price_unit_evidence"] = "THOUSAND_VND"
    assert record_passes_contract(record) is True
    record["supplies_true_shares_outstanding"] = False
    assert record_passes_contract(record) is False


def test_already_vnd_price_is_an_explicit_valid_unit_without_scale_guessing() -> None:
    record = {
        "supplies_current_unadjusted_price": True,
        "explicit_price_unit_evidence": "VND",
        "supplies_true_shares_outstanding": True,
        "as_of_fields": ["trading_date"],
    }
    assert record_passes_contract(record) is True
