import pandas as pd

from scripts import diagnose_interest_sign_population as diagnosis


def test_ttm_flagged_quarter_is_contaminated_even_when_not_calendar_quarter():
    targets = pd.DataFrame(
        [
            {
                "config_id": "ALL__ebit_tev__VALUE_ONLY",
                "rebalance_date": "2024-06-30",
                "ticker": "AAA",
                "rank_in_population": "1",
                "ttm_quarters": "2023Q3|2023Q4|2024Q1|2024Q2",
            }
        ]
    )
    flagged_population = pd.DataFrame(
        [{"ticker": "AAA", "quarter": "2024Q1"}]
    )

    target_windows = diagnosis._targets_with_quarter(targets)
    contaminated = target_windows.merge(
        flagged_population,
        on=["ticker", "quarter"],
        how="inner",
        validate="many_to_one",
    )

    assert len(contaminated) == 1


def test_diagnose_counts_ttm_flagged_quarters_in_production_path(monkeypatch):
    fundamentals = pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "quarter": "2024Q1",
                "item_id": "interest_expenses",
                "value": "-10",
            },
            {
                "ticker": "AAA",
                "quarter": "2024Q1",
                "item_id": "financial_expenses",
                "value": "-1",
            },
        ]
    )
    contaminated_targets = pd.DataFrame(
        {
            "config_id": ["TEST"] * 509,
            "metric": ["ebit_tev"] * 509,
            "rebalance_date": ["2024-06-30"] * 509,
            "ticker": ["AAA"] * 509,
            "rank_in_population": ["1"] * 509,
        }
    )
    clean_targets = pd.DataFrame(
        {
            "config_id": ["TEST"] * 2371,
            "metric": ["ebit_tev"] * 2371,
            "rebalance_date": ["2024-06-30"] * 2371,
            "ticker": ["BBB"] * 2371,
            "rank_in_population": ["1"] * 2371,
        }
    )
    targets = pd.concat([contaminated_targets, clean_targets], ignore_index=True)
    valuation = pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "evaluation_date": "2024-06-30",
                "ttm_quarters": "2023Q3|2023Q4|2024Q1|2024Q2",
                "ttm_pbt": "0",
                "ttm_interest_magnitude": "0",
                "ebit_proxy_vas": "0",
                "tev": "1",
                "ebit_tev": "0",
            },
            {
                "ticker": "BBB",
                "evaluation_date": "2024-06-30",
                "ttm_quarters": "2023Q3|2023Q4|2024Q2|2024Q3",
                "ttm_pbt": "0",
                "ttm_interest_magnitude": "0",
                "ebit_proxy_vas": "0",
                "tev": "1",
                "ebit_tev": "0",
            },
        ]
    )
    inputs = iter([fundamentals, targets, valuation, pd.DataFrame()])

    monkeypatch.setattr(diagnosis, "_read_csv", lambda _path: next(inputs))
    monkeypatch.setattr(diagnosis, "_named_rows", lambda _population: pd.DataFrame())
    monkeypatch.setattr(diagnosis, "_hqc_net_sales", lambda _annual: {})
    monkeypatch.setattr(
        diagnosis,
        "_hag_sensitivity_rows",
        lambda *_args: [],
    )

    result = diagnosis.diagnose()

    assert len(result.target_hits) == 509
