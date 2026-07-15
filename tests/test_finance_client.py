from __future__ import annotations

import builtins
import importlib
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from src.data.finance_client import (
    FETCH_STATUS_COLUMNS,
    LAG_ANNUAL,
    LAG_QUARTER,
    LAG_SEMIANNUAL,
    NORMALIZED_COLUMNS,
    STATEMENT_BALANCE_SHEET,
    STATEMENT_CASH_FLOW,
    STATEMENT_INCOME_STATEMENT,
    FinanceClient,
    IdentityConfig,
    load_identity_config,
    normalize_financial_statement,
    parse_report_period,
    validate_large_company_magnitude,
)


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "finance"
LIVE_VALIDATION_REPORT = Path(__file__).resolve().parents[1] / "docs" / "VALIDATE_DUP_RESOLUTION_SPRINT_3.md"


class FixtureFinanceClient(FinanceClient):
    def __init__(self, raw: pd.DataFrame, cache_dir: Path, *, use_cache: bool = True) -> None:
        super().__init__(
            cache_dir=cache_dir,
            min_sleep_seconds=0,
            max_sleep_seconds=0,
            use_cache=use_cache,
        )
        self.raw = raw
        self.fetch_count = 0

    def _fetch_statement(self, ticker: str, period: str, statement_type: str) -> pd.DataFrame:
        self.fetch_count += 1
        return self.raw.copy()


class FailingFinanceClient(FinanceClient):
    def __init__(self, cache_dir: Path, message: str = "fixture API failure") -> None:
        super().__init__(
            cache_dir=cache_dir,
            min_sleep_seconds=0,
            max_sleep_seconds=0,
            use_cache=False,
        )
        self.message = message

    def _fetch_statement(self, ticker: str, period: str, statement_type: str) -> pd.DataFrame:
        raise RuntimeError(self.message)


@pytest.fixture()
def long_shape() -> pd.DataFrame:
    return pd.read_csv(FIXTURES / "synthetic_vci_long_shape.csv")


@pytest.fixture()
def annual_shape(long_shape: pd.DataFrame) -> pd.DataFrame:
    return long_shape.rename(
        columns={
            "2026-Q1": "2025",
            "2025-Q4": "2024",
            "2025-Q3": "2023",
            "2025-Q2": "2022",
        }
    )


@pytest.fixture()
def verified_duplicate_shapes() -> dict[str, pd.DataFrame]:
    raw = pd.read_csv(FIXTURES / "verified_dup_items_vci_2026_07_15.csv")
    return {
        ticker: group.drop(columns="ticker").reset_index(drop=True)
        for ticker, group in raw.groupby("ticker", sort=False)
    }


def validation_report_shape(ticker: str) -> pd.DataFrame:
    """Read verbatim saved raw rows; this fixture path never calls vnstock."""
    lines = LIVE_VALIDATION_REPORT.read_text(encoding="utf-8").splitlines()
    start = lines.index(f"## {ticker}")
    table_start = lines.index("### Verbatim relevant raw rows", start)
    rows: list[list[str]] = []
    for line in lines[table_start + 4 :]:
        if not line.startswith("|"):
            break
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    columns = ["raw_index", "item", "item_en", "item_id", "2026-Q1", "2025-Q4", "2025-Q3", "2025-Q2"]
    frame = pd.DataFrame(rows, columns=columns)
    frame["raw_index"] = frame["raw_index"].astype(int)
    for period in columns[4:]:
        frame[period] = pd.to_numeric(frame[period].replace("NaN", pd.NA), errors="coerce")
    return frame.set_index("raw_index")


def test_long_shape_normalizes_to_required_tidy_schema(long_shape):
    result = normalize_financial_statement(
        long_shape,
        ticker="VNM",
        statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL",
        source="fixture_vci_shape",
        as_of="2026-07-14",
    )

    assert list(result.columns) == NORMALIZED_COLUMNS
    assert len(result) == 8
    assert result["item_id"].nunique() == 2
    assert result["report_period"].tolist()[:4] == ["2026Q1", "2026Q1", "2025Q4", "2025Q4"]
    assert result.loc[result["value"].isna(), "data_status"].eq("MISSING_DATA").all()
    assert result.loc[result["value"].notna(), "data_status"].eq("OK").all()
    assert result["source"].eq("fixture_vci_shape").all()
    assert result["as_of"].eq("2026-07-14").all()


def test_point_in_time_lags_are_exact():
    quarter = parse_report_period("2026-Q1")
    semiannual = parse_report_period("2026-H1")
    annual = parse_report_period("2025")

    assert quarter.lag_days == LAG_QUARTER == 30
    assert quarter.period_end.isoformat() == "2026-03-31"
    assert semiannual.lag_days == LAG_SEMIANNUAL == 60
    assert semiannual.period_end.isoformat() == "2026-06-30"
    assert annual.lag_days == LAG_ANNUAL == 90
    assert annual.period_end.isoformat() == "2025-12-31"


def test_available_from_is_period_end_plus_quarter_lag(long_shape):
    result = normalize_financial_statement(
        long_shape,
        ticker="VNM",
        statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL",
        source="fixture_vci_shape",
        as_of="2026-07-14",
    )

    q1 = result[result["report_period"] == "2026Q1"]
    assert q1["period_end"].eq("2026-03-31").all()
    assert q1["available_from"].eq("2026-04-30").all()
    assert result["available_from"].notna().all()


def test_item_names_are_not_join_keys(long_shape):
    renamed = long_shape.copy()
    renamed.loc[0, "item"] = "A renamed Vietnamese label"
    renamed.loc[0, "item_en"] = "A renamed English label"

    result = normalize_financial_statement(
        renamed,
        ticker="VNM",
        statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL",
        source="fixture_vci_shape",
        as_of="2026-07-14",
    )

    assert "SYN_BS_001" in set(result["item_id"])
    assert result[result["item_id"] == "SYN_BS_001"]["item"].eq("A renamed Vietnamese label").all()


def test_missing_item_id_fails_honestly(long_shape):
    broken = long_shape.copy()
    broken.loc[0, "item_id"] = ""

    with pytest.raises(ValueError, match="missing item_id"):
        normalize_financial_statement(
            broken,
            ticker="VNM",
            statement_type=STATEMENT_BALANCE_SHEET,
            company_type="NON_FINANCIAL",
            source="fixture_vci_shape",
            as_of="2026-07-14",
        )


def test_duplicate_outside_required_items_is_quarantined_without_summing(long_shape):
    duplicated = pd.concat([long_shape, long_shape.iloc[[0]]], ignore_index=True)
    result = normalize_financial_statement(
        duplicated,
        ticker="VNM",
        statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL",
        source="fixture_vci_shape",
        as_of="2026-07-14",
    )

    assert "SYN_BS_001" not in set(result["item_id"])
    assert "DUPLICATE_ITEM_ID_QUARANTINED" in result.attrs["duplicate_resolution"]["flags"]


def test_non_numeric_source_value_fails_honestly(long_shape):
    broken = long_shape.copy()
    broken["2026-Q1"] = broken["2026-Q1"].astype(object)
    broken.loc[0, "2026-Q1"] = "not-a-number"

    with pytest.raises(ValueError, match="non-numeric values"):
        normalize_financial_statement(
            broken,
            ticker="VNM",
            statement_type=STATEMENT_BALANCE_SHEET,
            company_type="NON_FINANCIAL",
            source="fixture_vci_shape",
            as_of="2026-07-14",
        )


def test_large_company_raw_vnd_magnitude_passes(long_shape):
    result = normalize_financial_statement(
        long_shape,
        ticker="VNM",
        statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL",
        source="fixture_vci_shape",
        as_of="2026-07-14",
    )

    validate_large_company_magnitude(result)


def test_suspicious_thousand_or_million_scale_fails(long_shape):
    suspicious = long_shape.copy()
    for column in ["2026-Q1", "2025-Q4", "2025-Q3", "2025-Q2"]:
        suspicious[column] = 1_000_000
    result = normalize_financial_statement(
        suspicious,
        ticker="VNM",
        statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL",
        source="fixture_vci_shape",
        as_of="2026-07-14",
    )

    with pytest.raises(ValueError, match="below 1e9 VND"):
        validate_large_company_magnitude(result)


def test_all_three_statement_methods_cover_quarter_and_year_modes(long_shape, annual_shape, tmp_path):
    quarter_client = FixtureFinanceClient(long_shape, tmp_path / "quarter", use_cache=False)
    annual_client = FixtureFinanceClient(annual_shape, tmp_path / "year", use_cache=False)

    methods = (
        ("get_balance_sheet", STATEMENT_BALANCE_SHEET),
        ("get_income_statement", STATEMENT_INCOME_STATEMENT),
        ("get_cash_flow", STATEMENT_CASH_FLOW),
    )
    for method_name, statement_type in methods:
        quarter = getattr(quarter_client, method_name)(
            "VNM", "quarter", company_type="NON_FINANCIAL"
        )
        annual = getattr(annual_client, method_name)("VNM", "year", company_type="NON_FINANCIAL")

        assert set(quarter.data["statement_type"]) == {statement_type}
        assert set(quarter.data["period_type"]) == {"QUARTER"}
        assert set(annual.data["statement_type"]) == {statement_type}
        assert set(annual.data["period_type"]) == {"ANNUAL"}

    assert quarter_client.fetch_count == 3
    assert annual_client.fetch_count == 3


def test_company_types_and_different_schema_sizes_remain_separate(long_shape, tmp_path):
    bank_shape = long_shape.iloc[[0]].copy()
    non_financial_client = FixtureFinanceClient(long_shape, tmp_path / "non_financial")
    bank_client = FixtureFinanceClient(bank_shape, tmp_path / "bank")

    non_financial = non_financial_client.get_balance_sheet(
        "VNM", "quarter", company_type="NON_FINANCIAL"
    )
    bank = bank_client.get_balance_sheet("VCB", "quarter", company_type="BANK")

    assert len(non_financial.data) == 8
    assert len(bank.data) == 4
    assert non_financial.data["company_type"].eq("NON_FINANCIAL").all()
    assert bank.data["company_type"].eq("BANK").all()


def test_raw_response_is_preserved_when_outside_duplicate_is_quarantined(long_shape, tmp_path):
    duplicated = pd.concat([long_shape, long_shape.iloc[[0]]], ignore_index=True)
    client = FixtureFinanceClient(duplicated, tmp_path, use_cache=False)

    result = client.get_balance_sheet("VNM", "quarter", company_type="NON_FINANCIAL")

    assert result.ok
    assert result.status == "OK"
    assert "DUPLICATE_ITEM_ID_QUARANTINED" in result.metadata["duplicate_resolution"]["flags"]
    assert result.metadata["returned_period_count"] == 4
    assert result.metadata["raw_shape"] == [3, 7]
    assert len(list(tmp_path.rglob("raw.parquet"))) == 1
    assert len(list(tmp_path.rglob("normalized.parquet"))) == 1
    assert len(list(tmp_path.rglob("failure.json"))) == 0


@pytest.mark.parametrize("ticker", ["HPG", "FPT"])
def test_verbatim_required_duplicates_resolve_by_reported_values(
    ticker, verified_duplicate_shapes
):
    result = normalize_financial_statement(
        verified_duplicate_shapes[ticker],
        ticker=ticker,
        statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL",
        source="verbatim_vci_2026_07_15",
        as_of="2026-07-15",
    )
    audit = result.attrs["duplicate_resolution"]

    assert not audit["ambiguous"]
    assert "DUPLICATE_RESOLVED_BY_IDENTITY" in audit["flags"]
    assert "DUPLICATE_RESOLVED_NON_NAN" in audit["flags"]
    assert result[result["item_id"] == "short_term_investments"]["value"].max() > 1e12
    assert result[result["item_id"] == "preferred_shares"]["value"].fillna(0).eq(0).all()


@pytest.mark.parametrize("ticker", ["VNM", "HDG"])
def test_saved_live_rows_resolve_via_per_item_margin(ticker):
    result = normalize_financial_statement(
        validation_report_shape(ticker),
        ticker=ticker,
        statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL",
        source="saved_live_validation_2026_07_15",
        as_of="2026-07-15",
    )
    audit = result.attrs["duplicate_resolution"]

    assert not result.empty
    assert not audit["ambiguous"]
    assert "DUPLICATE_RESOLVED_BY_IDENTITY" in audit["flags"]
    assert any(
        event.get("flag") == "IDENTITY_PER_ITEM_MARGIN"
        and event.get("passed") is True
        for event in audit["events"]
    )


def test_preferred_multiple_informative_candidates_are_ambiguous(verified_duplicate_shapes):
    raw = verified_duplicate_shapes["VNM"].copy()
    preferred = raw.index[raw["item_id"] == "preferred_shares"]
    raw.loc[preferred[0], ["2026-Q1", "2025-Q4", "2025-Q3", "2025-Q2"]] = 1

    result = normalize_financial_statement(
        raw, ticker="VNM", statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL", source="failure_fixture", as_of="2026-07-15"
    )

    assert result.empty
    assert result.attrs["duplicate_resolution"]["ambiguous"]
    assert "REQUIRED_ITEM_AMBIGUOUS" in result.attrs["duplicate_resolution"]["flags"]


def test_preferred_zero_informative_candidates_are_ambiguous(verified_duplicate_shapes):
    raw = verified_duplicate_shapes["VNM"].copy()
    periods = ["2026-Q1", "2025-Q4", "2025-Q3", "2025-Q2"]
    raw.loc[raw["item_id"] == "preferred_shares", periods] = float("nan")

    result = normalize_financial_statement(
        raw, ticker="VNM", statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL", source="failure_fixture", as_of="2026-07-15"
    )

    assert result.empty
    assert "REQUIRED_ITEM_AMBIGUOUS" in result.attrs["duplicate_resolution"]["flags"]


def test_positive_resolved_preferred_value_requires_owner_review(verified_duplicate_shapes):
    raw = verified_duplicate_shapes["HPG"].copy()
    periods = ["2026-Q1", "2025-Q4", "2025-Q3", "2025-Q2"]
    informative = raw.index[
        raw["item_id"].eq("preferred_shares") & raw[periods].notna().any(axis=1)
    ][0]
    raw.loc[informative, "2026-Q1"] = 1

    result = normalize_financial_statement(
        raw, ticker="HPG", statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL", source="positive_fixture", as_of="2026-07-15"
    )

    assert "PREFERRED_POSITIVE_REVIEW" in result.attrs["duplicate_resolution"]["flags"]


def test_client_reports_ambiguous_statement_without_api_error(
    verified_duplicate_shapes, tmp_path
):
    ambiguous = validation_report_shape("C32")
    client = FixtureFinanceClient(ambiguous, tmp_path, use_cache=False)

    result = client.get_balance_sheet("C32", "quarter", company_type="NON_FINANCIAL")

    assert result.ok
    assert result.status == "REQUIRED_ITEM_AMBIGUOUS"
    assert result.data.empty
    assert result.metadata["duplicate_resolution"]["ambiguous"]
    assert len(list(tmp_path.rglob("raw.parquet"))) == 1


def test_identity_margin_failure_never_selects(verified_duplicate_shapes):
    raw = verified_duplicate_shapes["VNM"].copy()
    sti = list(raw.index[raw["item_id"] == "short_term_investments"])
    periods = ["2026-Q1", "2025-Q4", "2025-Q3", "2025-Q2"]
    current_assets = raw.loc[raw["item_id"] == "current_assets", periods].iloc[0].astype(float)
    raw.loc[sti[1], periods] = raw.loc[sti[0], periods].astype(float) + 0.011 * current_assets

    result = normalize_financial_statement(
        raw, ticker="VNM", statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL", source="margin_fixture", as_of="2026-07-15"
    )

    assert result.empty
    assert result.attrs["duplicate_resolution"]["ambiguous"]
    assert any(
        str(event.get("reason", "")).startswith("per-item margin and immaterial difference not met")
        for event in result.attrs["duplicate_resolution"]["events"]
    )


def test_non_identical_duplicate_identity_input_is_ambiguous(verified_duplicate_shapes):
    raw = verified_duplicate_shapes["HPG"].copy()
    cash = raw[raw["item_id"] == "cash_and_cash_equivalents"].iloc[[0]].copy()
    cash.loc[:, "2026-Q1"] = float(cash.iloc[0]["2026-Q1"]) + 1
    raw = pd.concat([raw, cash], ignore_index=True)

    result = normalize_financial_statement(
        raw, ticker="HPG", statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL", source="conflict_fixture", as_of="2026-07-15"
    )

    assert result.empty
    assert result.attrs["duplicate_resolution"]["ambiguous"]


def test_identical_duplicate_identity_input_is_allowed_and_logged(verified_duplicate_shapes):
    raw = verified_duplicate_shapes["FPT"].copy()
    cash = raw[raw["item_id"] == "cash_and_cash_equivalents"].iloc[[0]].copy()
    raw = pd.concat([raw, cash], ignore_index=True)

    result = normalize_financial_statement(
        raw, ticker="FPT", statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL", source="identical_fixture", as_of="2026-07-15"
    )

    assert not result.empty
    assert any(
        event.get("flag") == "DUPLICATE_VERIFIED_IDENTICAL"
        for event in result.attrs["duplicate_resolution"]["events"]
    )


def test_hid_resolves_identical_rows_from_saved_live_report():
    result = normalize_financial_statement(
        validation_report_shape("HID"), ticker="HID",
        statement_type=STATEMENT_BALANCE_SHEET, company_type="NON_FINANCIAL",
        source="saved_live_validation_2026_07_15", as_of="2026-07-15"
    )

    assert not result.empty
    assert "DUPLICATE_VERIFIED_IDENTICAL" in result.attrs["duplicate_resolution"]["flags"]


@pytest.mark.parametrize("ticker", ["DRC", "TLH", "CTF"])
def test_saved_live_rows_use_immaterial_path_only_when_they_qualify(ticker):
    result = normalize_financial_statement(
        validation_report_shape(ticker), ticker=ticker,
        statement_type=STATEMENT_BALANCE_SHEET, company_type="NON_FINANCIAL",
        source="saved_live_validation_2026_07_15", as_of="2026-07-15"
    )
    audit = result.attrs["duplicate_resolution"]
    materiality_events = [
        event for event in audit["events"] if event.get("flag") == "DUPLICATE_MATERIALITY_CHECK"
    ]

    assert materiality_events
    qualifies = all(
        event["maximum_relative_difference"] is not None
        and event["maximum_relative_difference"] <= 0.01
        for event in materiality_events
    )
    if qualifies:
        assert not result.empty
        assert "DUPLICATE_RESOLVED_IMMATERIAL" in audit["flags"]
    else:
        assert result.empty
        assert "REQUIRED_ITEM_AMBIGUOUS" in audit["flags"]


@pytest.mark.parametrize("ticker", ["C32", "VCS", "PVC"])
def test_saved_poor_identity_fits_remain_ambiguous(ticker):
    result = normalize_financial_statement(
        validation_report_shape(ticker), ticker=ticker,
        statement_type=STATEMENT_BALANCE_SHEET, company_type="NON_FINANCIAL",
        source="saved_live_validation_2026_07_15", as_of="2026-07-15"
    )

    assert result.empty
    assert "REQUIRED_ITEM_AMBIGUOUS" in result.attrs["duplicate_resolution"]["flags"]
    assert any(
        event.get("reason") == "identity tolerance not met"
        for event in result.attrs["duplicate_resolution"]["events"]
    )


def test_named_identity_thresholds_are_loaded_from_config():
    assert load_identity_config() == IdentityConfig(0.01, 3, 5.0, 0.01)


def test_content_addressed_cache_is_reused_without_api_call(long_shape, tmp_path):
    first = FixtureFinanceClient(long_shape, tmp_path)
    first_result = first.get_balance_sheet("VNM", "quarter", company_type="NON_FINANCIAL")
    second = FixtureFinanceClient(long_shape, tmp_path)
    second_result = second.get_balance_sheet("VNM", "quarter", company_type="NON_FINANCIAL")

    assert first_result.ok
    assert first.fetch_count == 1
    assert second_result.ok
    assert second.fetch_count == 0
    assert second_result.metadata["cache_state"] == "CACHED"
    assert len(list(tmp_path.rglob("raw.parquet"))) == 1


def test_changed_same_day_observation_does_not_overwrite_old_cache(long_shape, tmp_path):
    first = FixtureFinanceClient(long_shape, tmp_path, use_cache=False)
    first.get_balance_sheet("VNM", "quarter", company_type="NON_FINANCIAL")
    changed = long_shape.copy()
    changed.loc[0, "2026-Q1"] = 38_757_016_956_727
    second = FixtureFinanceClient(changed, tmp_path, use_cache=False)
    second.get_balance_sheet("VNM", "quarter", company_type="NON_FINANCIAL")

    assert len(list(tmp_path.rglob("raw.parquet"))) == 2


def test_api_error_is_explicit_and_secret_is_redacted(tmp_path):
    secret = "this-is-a-secret-value"
    client = FailingFinanceClient(tmp_path, message=f"api_key={secret}")

    result = client.get_balance_sheet("VNM", "quarter")

    assert not result.ok
    assert result.status == "API_ERROR"
    assert secret not in result.error
    assert "[REDACTED]" in result.error
    status = client.fetch_status_frame()
    assert list(status.columns) == FETCH_STATUS_COLUMNS
    assert status.iloc[0]["data_status"] == "API_ERROR"
    assert secret not in status.iloc[0]["error"]


def test_stale_cache_is_used_after_source_failure(long_shape, tmp_path):
    seed = FixtureFinanceClient(long_shape, tmp_path, use_cache=False)
    seed.get_balance_sheet("VNM", "quarter", company_type="NON_FINANCIAL")
    failing = FailingFinanceClient(tmp_path)

    result = failing.get_balance_sheet("VNM", "quarter", company_type="NON_FINANCIAL")

    assert result.ok
    assert result.status == "STALE_DATA"
    assert not result.data.empty


def test_public_vnstock_api_module_and_no_ratio_endpoint_are_used(monkeypatch, long_shape, tmp_path):
    calls: list[tuple[str, str]] = []

    class FakeFinance:
        def __init__(self, source, symbol, period, get_all, show_log):
            calls.append(("init", f"{source}:{symbol}:{period}:{get_all}:{show_log}"))

        def balance_sheet(self, **kwargs):
            calls.append(("balance_sheet", str(kwargs)))
            return long_shape

    def fake_import(name: str):
        calls.append(("import", name))
        return SimpleNamespace(Finance=FakeFinance)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    client = FinanceClient(cache_dir=tmp_path, min_sleep_seconds=0, max_sleep_seconds=0, use_cache=False)

    result = client.get_balance_sheet("VNM", "quarter", company_type="NON_FINANCIAL")

    assert result.ok
    assert ("import", "vnstock.api.financial") in calls
    assert any(call[0] == "balance_sheet" for call in calls)
    assert all(call[0] != "ratio" for call in calls)


def test_fixture_normalization_does_not_import_real_vnstock(monkeypatch, long_shape):
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "vnstock" or name.startswith("vnstock."):
            raise AssertionError("finance unit tests must not import vnstock")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    result = normalize_financial_statement(
        long_shape,
        ticker="VNM",
        statement_type=STATEMENT_BALANCE_SHEET,
        company_type="NON_FINANCIAL",
        source="fixture_vci_shape",
        as_of="2026-07-14",
    )
    assert not result.empty
