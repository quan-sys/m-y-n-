from types import SimpleNamespace

import pandas as pd

from scripts.analyze_sprint6_annual_history import (
    compare_restatements,
    coverage_record,
)
from scripts.audit_sprint6_readiness import (
    CRITERION7_MISSING_INPUT,
    CRITERION7_NO_SHARE_INCREASE_CASH,
    CRITERION7_SCORE_0,
    PROPOSED_FRANCHISE_MIN_YEARS,
    audit_ticker_from_frames,
    classify_criterion7_branch,
)
from src.data.finance_client import (
    ANNUAL_HISTORY_LIMIT,
    FinanceClient,
    STATEMENT_BALANCE_SHEET,
)


def test_annual_fetch_uses_extended_limit_and_quarterly_path_is_unchanged(monkeypatch, tmp_path):
    calls: list[tuple[str, dict]] = []

    class Provider:
        def _get_financial_report(self, report_type, **kwargs):
            calls.append((report_type, kwargs))
            return pd.DataFrame()

    class FakeFinance:
        def __init__(self, **kwargs):
            self.provider = Provider()

        def balance_sheet(self, **kwargs):
            calls.append(("public_balance_sheet", kwargs))
            return pd.DataFrame()

    monkeypatch.setattr(
        "src.data.finance_client.importlib.import_module",
        lambda name: SimpleNamespace(Finance=FakeFinance),
    )
    client = FinanceClient(
        cache_dir=tmp_path,
        min_sleep_seconds=0,
        max_sleep_seconds=0,
        use_cache=False,
    )

    client._fetch_statement("VNM", "year", STATEMENT_BALANCE_SHEET)
    client._fetch_statement("VNM", "quarter", STATEMENT_BALANCE_SHEET)

    assert calls[0] == (
        "balance_sheet",
        {
            "period": "year",
            "lang": "en",
            "get_all": True,
            "dropna": False,
            "show_log": False,
            "limit": ANNUAL_HISTORY_LIMIT,
        },
    )
    assert calls[1][0] == "public_balance_sheet"
    assert "limit" not in calls[1][1]


def test_fourth_criterion7_branch_scores_zero_and_records_no_missing_label():
    branch, outcome, flag = classify_criterion7_branch(100, 100, 25)

    assert branch == CRITERION7_SCORE_0
    assert outcome == CRITERION7_NO_SHARE_INCREASE_CASH
    assert flag == ""


def test_missing_input_label_only_covers_invalid_inputs():
    branch, outcome, flag = classify_criterion7_branch(
        None,
        100,
        25,
        common_shares_n_status="MISSING",
    )

    assert branch == CRITERION7_MISSING_INPUT
    assert outcome == "UNSCORED"
    assert flag == "COMMON_SHARES_N_MISSING"
    valid_branch, _, valid_flag = classify_criterion7_branch(100, 100, 25)
    assert valid_branch != CRITERION7_MISSING_INPUT
    assert "VALID_INPUT_COMBINATION_NOT_SETTLED" not in valid_flag


def test_restatement_comparator_preserves_old_and_new_values_without_threshold():
    old = pd.DataFrame(
        [
            {
                "ticker": "VNM",
                "statement_type": "BALANCE_SHEET",
                "report_period": "2022",
                "item_id": "total_assets",
                "value": 100,
            },
            {
                "ticker": "VNM",
                "statement_type": "BALANCE_SHEET",
                "report_period": "2023",
                "item_id": "total_assets",
                "value": 200,
            },
        ]
    )
    new = old.copy()
    new.loc[new["report_period"].eq("2022"), "value"] = 101

    compared = compare_restatements(old, new, item_ids=("total_assets",))

    assert len(compared) == 2
    changed = compared.loc[compared["differs"]].iloc[0]
    assert changed["old_value"] == 100
    assert changed["new_value"] == 101
    assert changed["relative_difference"] == 0.01


def test_coverage_counter_keeps_ticker_missing_early_years():
    rows = []
    for year in ("2020", "2021", "2022", "2023", "2024", "2025"):
        rows.append(
            {
                "report_period": year,
                "available_from": f"{int(year) + 1}-03-31",
            }
        )
    frame = pd.DataFrame(rows)

    record = coverage_record(
        "MISS",
        {
            "balance_sheet": frame,
            "income_statement": frame,
            "cash_flow": frame,
        },
    )

    assert record["balance_sheet_periods"] == "2020|2021|2022|2023|2024|2025"
    assert record["balance_sheet_period_count"] == 6
    assert record["balance_sheet_eligible_period_count"] == 6
    assert record["balance_sheet_usable_consecutive_roc_years"] == 5


def _franchise_frames(usable_years: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    period_count = usable_years + 1
    years = tuple(range(2026 - period_count, 2026))

    def rows(statement_type: str, items: tuple[str, ...]) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "ticker": "MIN",
                    "statement_type": statement_type,
                    "period_type": "YEAR",
                    "report_period": str(year),
                    "available_from": f"{year + 1}-03-31",
                    "item_id": item,
                    "value": year * 100 + index + 1,
                    "data_status": "OK",
                }
                for year in years
                for index, item in enumerate(items)
            ]
        )

    return (
        rows(
            "INCOME_STATEMENT",
            (
                "net_accounting_profit_loss_before_tax",
                "interest_expenses",
                "net_sales",
                "gross_profit",
            ),
        ),
        rows(
            "BALANCE_SHEET",
            (
                "owners_equity",
                "short_term_borrowings",
                "long_term_borrowings",
                "cash_and_cash_equivalents",
            ),
        ),
        pd.DataFrame(),
    )


def _franchise_result(usable_years: int) -> dict:
    income, balance, cash_flow = _franchise_frames(usable_years)
    return audit_ticker_from_frames(
        {
            "ticker": "MIN",
            "annual_n": 2025,
            "annual_n_minus_1": 2024,
        },
        income,
        balance,
        cash_flow,
    )


def test_franchise_history_below_named_minimum_is_insufficient():
    result = _franchise_result(PROPOSED_FRANCHISE_MIN_YEARS - 1)

    assert result["franchise_years_used"] == PROPOSED_FRANCHISE_MIN_YEARS - 1
    assert result["franchise_history_status"] == "INSUFFICIENT_HISTORY"


def test_franchise_history_at_named_minimum_is_ready():
    result = _franchise_result(PROPOSED_FRANCHISE_MIN_YEARS)

    assert result["franchise_years_used"] == PROPOSED_FRANCHISE_MIN_YEARS
    assert result["franchise_history_status"] == "READY"
