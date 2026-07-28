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
