from decimal import Decimal

import pandas as pd
import pytest

import scripts.build_sprint9_4c_gates_as_of as builder


def annual_row(
    *,
    ticker="AAA",
    fiscal_year=2024,
    available_from="2025-03-31",
    statement_type="BALANCE_SHEET",
    item_id="total_assets",
    value="1",
):
    return {
        "ticker": ticker,
        "fiscal_year": str(fiscal_year),
        "available_from": available_from,
        "statement_type": statement_type,
        "item_id": item_id,
        "value": str(value),
        "data_status": "OK",
    }


def formula_input_rows():
    records = {}
    for mappings in builder.FORMULA_INPUT_MAP.values():
        for statement_type, item_id, period_role in mappings.values():
            fiscal_year = 2024 if period_role == "N" else 2023
            key = (statement_type, item_id, fiscal_year)
            records.setdefault(
                key,
                annual_row(
                    fiscal_year=fiscal_year,
                    available_from="2025-03-31",
                    statement_type=statement_type,
                    item_id=item_id,
                ),
            )
    return pd.DataFrame(records.values())


def test_as_of_selection_excludes_a_later_available_year():
    rows = pd.DataFrame(
        [
            annual_row(fiscal_year=2022, available_from="2023-03-31"),
            annual_row(fiscal_year=2023, available_from="2024-03-31"),
            annual_row(fiscal_year=2024, available_from="2025-03-31"),
        ]
    )

    selection = builder.select_as_of_annuals(rows, "2024-12-31")

    assert selection.annual_n == 2023
    assert selection.annual_n_minus_1 == 2022
    assert selection.annual_n_available_from == "2024-03-31"


def test_non_consecutive_years_remain_unscored_with_a_named_reason():
    rows = pd.DataFrame(
        [
            annual_row(fiscal_year=2021, available_from="2022-03-31"),
            annual_row(fiscal_year=2023, available_from="2024-03-31"),
        ]
    )

    selection = builder.select_as_of_annuals(rows, "2024-12-31")
    results, _ = builder.calculate_step1_gates(selection.eligible_rows, selection)
    _, _, fscore_status = builder.calculate_fscore(selection.eligible_rows, selection)

    assert selection.pair_reason == "NON_CONSECUTIVE_ANNUAL_PAIR"
    assert results["STA"].value is None
    assert builder._result_status(results["STA"], selection.pair_reason) == (
        "UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR"
    )
    assert fscore_status == "UNSCORED_NON_CONSECUTIVE_ANNUAL_TRIPLE"


def test_percentile_for_one_date_does_not_use_another_date():
    config = builder.load_config()
    baseline_rows = pd.DataFrame(
        [
            {
                "evaluation_date": "2024-03-31",
                "ticker": "AAA",
                "sta": "1",
                "snoa": "1",
                "m_score": "1",
            },
            {
                "evaluation_date": "2024-03-31",
                "ticker": "BBB",
                "sta": "2",
                "snoa": "2",
                "m_score": "2",
            },
        ]
    )
    combined_rows = pd.concat(
        [
            baseline_rows,
            pd.DataFrame(
                [
                    {
                        "evaluation_date": "2025-03-31",
                        "ticker": "CCC",
                        "sta": "999",
                        "snoa": "999",
                        "m_score": "999",
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    baseline = builder.apply_within_date_percentiles(baseline_rows, config)
    combined = builder.apply_within_date_percentiles(combined_rows, config)

    assert combined.loc[combined["ticker"].eq("AAA"), "sta_percentile"].iloc[0] == (
        baseline.loc[baseline["ticker"].eq("AAA"), "sta_percentile"].iloc[0]
    )
    assert combined.loc[combined["ticker"].eq("BBB"), "m_score_percentile"].iloc[0] == (
        baseline.loc[baseline["ticker"].eq("BBB"), "m_score_percentile"].iloc[0]
    )


def test_imported_config_changes_accrual_and_mscore_flags(monkeypatch):
    base = builder.load_config()
    rows = pd.DataFrame(
        [
            {
                "evaluation_date": "2024-03-31",
                "ticker": "LOW",
                "sta": "0",
                "snoa": "0",
                "m_score": float(base.mscore_threshold - Decimal("1")),
            },
            {
                "evaluation_date": "2024-03-31",
                "ticker": "MID",
                "sta": "1",
                "snoa": "1",
                "m_score": float(base.mscore_threshold + Decimal("1")),
            },
            {
                "evaluation_date": "2024-03-31",
                "ticker": "HIGH",
                "sta": "2",
                "snoa": "2",
                "m_score": float(base.mscore_threshold - Decimal("1")),
            },
        ]
    )
    moved = builder.GateConfig(
        accrual_worst_pct=base.accrual_worst_pct * Decimal("5"),
        mscore_threshold=base.mscore_threshold + Decimal("2"),
        tev_min_fraction_of_market_cap=base.tev_min_fraction_of_market_cap,
    )

    baseline = builder.apply_within_date_percentiles(rows, base).set_index("ticker")
    monkeypatch.setattr(builder, "load_config", lambda: moved)
    changed = builder.apply_within_date_percentiles(rows, builder.load_config()).set_index(
        "ticker"
    )

    assert not bool(baseline.loc["MID", "high_accrual_flag"])
    assert bool(changed.loc["MID", "high_accrual_flag"])
    assert bool(baseline.loc["MID", "m_score_flag"])
    assert not bool(changed.loc["MID", "m_score_flag"])


def test_tev_collapse_flag_below_imported_fraction_keeps_the_output_row(monkeypatch):
    config = builder.load_config()
    market_cap = Decimal("100")
    evaluation_date = "2025-12-31"
    valuation = pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "evaluation_date": evaluation_date,
                "tev": str(market_cap * config.tev_min_fraction_of_market_cap / Decimal("2")),
                "market_cap_vnd": str(market_cap),
            }
        ]
    )
    monkeypatch.setattr(
        builder,
        "evaluation_grid",
        lambda: [(evaluation_date, builder.WALK_FORWARD_ROLE)],
    )

    output, _ = builder.build_rows(
        formula_input_rows(), valuation, config, run_date="fixture-run"
    )

    assert len(output) == 1
    assert bool(output.loc[0, "tev_collapse_flag"])
    assert output.loc[0, "ticker"] == "AAA"


def test_calculate_step1_gates_calls_the_imported_formula_symbol(monkeypatch):
    rows = formula_input_rows()
    selection = builder.AnnualSelection(
        annual_n=2024,
        annual_n_minus_1=2023,
        annual_n_minus_2=None,
        annual_n_available_from="2025-03-31",
        pair_reason="",
        triple_reason="NON_CONSECUTIVE_ANNUAL_TRIPLE",
        eligible_rows=rows,
    )
    original = builder.calculate_sta
    calls = []

    def wrapped(*args, **kwargs):
        calls.append((args, kwargs))
        return original(*args, **kwargs)

    monkeypatch.setattr(builder, "calculate_sta", wrapped)
    results, _ = builder.calculate_step1_gates(rows, selection)

    assert len(calls) == 1
    assert results["STA"].value is not None


def test_build_rows_emits_no_warning_data_confidence(monkeypatch):
    config = builder.load_config()
    evaluation_date = "2025-12-31"
    valuation = pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "evaluation_date": evaluation_date,
                "tev": "1",
                "market_cap_vnd": "1",
            }
        ]
    )
    monkeypatch.setattr(
        builder,
        "evaluation_grid",
        lambda: [(evaluation_date, builder.WALK_FORWARD_ROLE)],
    )

    output, _ = builder.build_rows(
        formula_input_rows(), valuation, config, run_date="fixture-run"
    )

    assert output.columns.get_loc("distress_confidence") == (
        output.columns.get_loc("distress_status") + 1
    )
    assert output.loc[0, "distress_confidence"] == "NO_WARNING_DATA"
    assert output.loc[0, "distress_status"] == "SCORED"


def test_load_config_parses_distress_warning_requirement_case_insensitively(tmp_path):
    config_path = tmp_path / "screener.yaml"
    config_text = builder.CONFIG_PATH.read_text(encoding="utf-8")
    config_path.write_text(
        config_text.replace(
            "DISTRESS_REQUIRE_HOSE_WARNING: false",
            "DISTRESS_REQUIRE_HOSE_WARNING: TRUE",
        ),
        encoding="utf-8",
    )

    assert builder.load_config(config_path).distress_require_hose_warning is True

    config_path.write_text(
        config_text.replace(
            "DISTRESS_REQUIRE_HOSE_WARNING: false",
            "DISTRESS_REQUIRE_HOSE_WARNING: unknown",
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="DISTRESS_REQUIRE_HOSE_WARNING"):
        builder.load_config(config_path)
