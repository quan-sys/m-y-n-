from decimal import Decimal

import pandas as pd

import scripts.build_sprint9_4a_value_candidates as builder


def config(value_cheapest_pct="0.5"):
    return builder.ValueConfig(
        value_cheapest_pct=Decimal(value_cheapest_pct),
        min_candidate_pool_multiple=Decimal("2"),
        selection_ratio_report_threshold=Decimal("0.8"),
    )


def input_rows():
    return pd.DataFrame(
        [
            {
                "evaluation_date": "2024-12-31",
                "quarter": "2024Q4",
                "ticker": "LOW",
                "ebit_tev": "0.01",
                "e_p": "0.01",
                "ebit_tev_eligible": "True",
                "e_p_eligible": "True",
                "price_confidence": "OK",
                "market_cap_status": "OK",
                "valuation_status": "OK",
            },
            {
                "evaluation_date": "2024-12-31",
                "quarter": "2024Q4",
                "ticker": "MID",
                "ebit_tev": "0.05",
                "e_p": "0.05",
                "ebit_tev_eligible": "True",
                "e_p_eligible": "True",
                "price_confidence": "LOW",
                "market_cap_status": "OK",
                "valuation_status": "OK",
            },
            {
                "evaluation_date": "2024-12-31",
                "quarter": "2024Q4",
                "ticker": "HIGH",
                "ebit_tev": "0.20",
                "e_p": "0.20",
                "ebit_tev_eligible": "True",
                "e_p_eligible": "True",
                "price_confidence": "OK",
                "market_cap_status": "UPPER_BOUND",
                "valuation_status": "OK",
            },
        ]
    )


def ranked(frame, *, population_id="ALL", value_config=None):
    return builder.rank_population(
        frame,
        metric="ebit_tev",
        population_id=population_id,
        config=value_config or config(),
        run_date="2026-07-26",
    )


def test_higher_yield_is_rank_one_and_in_cheap_set():
    result = ranked(input_rows()).set_index("ticker")

    assert result.loc["HIGH", "rank_in_population"] == 1
    assert result.loc["HIGH", "percentile"] == Decimal("1")
    assert result.loc["HIGH", "in_cheap_set"]
    assert not result.loc["LOW", "in_cheap_set"]


def test_ties_receive_identical_average_rank_percentile():
    frame = input_rows()
    frame.loc[frame["ticker"].isin(["LOW", "MID"]), "ebit_tev"] = "0.05"

    result = ranked(frame).set_index("ticker")

    assert result.loc["LOW", "rank_in_population"] == Decimal("2.5")
    assert result.loc["LOW", "percentile"] == result.loc["MID", "percentile"]


def test_ineligible_row_is_absent_instead_of_ranked_last():
    frame = input_rows()
    frame.loc[frame["ticker"].eq("LOW"), "ebit_tev_eligible"] = "False"

    result = ranked(frame)

    assert "LOW" not in set(result["ticker"])
    assert len(result) == 2


def test_four_populations_have_expected_different_sizes():
    frame = input_rows()

    sizes = {
        population_id: len(ranked(frame, population_id=population_id))
        for population_id in builder.POPULATIONS
    }

    assert sizes == {
        "ALL": 3,
        "ALL_EX_UPPER_BOUND": 2,
        "PRICE_OK": 2,
        "PRICE_OK_EX_UPPER_BOUND": 1,
    }


def test_cheap_cut_moves_when_imported_config_value_is_monkeypatched(
    monkeypatch,
):
    frame = input_rows()
    original = ranked(frame, value_config=config("0.25")).set_index("ticker")
    monkeypatch.setattr(builder, "load_config", lambda: config("0.75"))
    moved = ranked(frame, value_config=builder.load_config()).set_index("ticker")

    assert not original.loc["MID", "in_cheap_set"]
    assert moved.loc["MID", "in_cheap_set"]
