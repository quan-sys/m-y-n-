import pandas as pd

from scripts.build_sprint7_portfolio import (
    AS_OF,
    QUALITY_COMPONENT_COLUMNS,
    _finalize_holdings,
    parse_args,
    report_root,
)


SECOND_AS_OF = "2025-06-30"


def _holdings() -> pd.DataFrame:
    row = {
        "portfolio_rank": 1,
        "ticker": "AAA",
        "exchange": "HOSE",
        "icb2": "Industrials",
        "candidate_list_membership": "EBIT_TEV",
        "value_metric_name": "ebit_tev",
        "value_metric_value": 1.0,
        "value_rank": 1.0,
        "composite_quality": 0.9,
        "franchise_history_status": "READY",
        "quality_rank": 1.0,
        "adtv_20d": 100.0,
        "adtv_20d_numeric": 100.0,
        "cross_step_flag": "",
        "franchise_history_flag": "",
        "composite_confidence_flag": "",
        "fscore_confidence_flag": "",
        "criterion_7_flag": "",
        "non_positive_revenue_n_minus_1": False,
        "candidate_source_path": "data/screener/step2_candidates_ebit_tev.csv",
        "quality_source_path": "data/screener/sprint6_franchise_quality.csv",
        "survivor_source_path": "data/screener/step1_survivors.csv",
        "survivor_source": "fixture",
        "survivor_as_of": "fixture",
    }
    row.update({column: 0.9 for column in QUALITY_COMPONENT_COLUMNS})
    return pd.DataFrame([row])


def test_default_as_of_matches_current_literal() -> None:
    assert parse_args([]).as_of == "2026-07-20"


def test_explicit_as_of_controls_report_directory_and_holdings_metadata() -> None:
    as_of = parse_args(["--as-of", SECOND_AS_OF]).as_of
    output = _finalize_holdings(
        _holdings(),
        portfolio_name="EBIT_TEV",
        as_of=as_of,
        liquidity_adtv_days=3.0,
        portfolio_capital_vnd=1_000.0,
        sector_cycle={"Industrials": "NEUTRAL"},
        sector_cycle_source="fixture",
    )

    assert str(report_root(as_of)).endswith(SECOND_AS_OF)
    assert output["portfolio_id"].str.startswith("SPRINT7_EBIT_TEV_").all()
    assert output["portfolio_id"].str.endswith(SECOND_AS_OF).all()
    assert output["as_of"].eq(SECOND_AS_OF).all()


def test_second_as_of_is_not_the_default() -> None:
    assert SECOND_AS_OF != AS_OF
