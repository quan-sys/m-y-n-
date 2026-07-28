from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.build_sprint7_portfolio import HOLDING_COUNT
from scripts.build_sprint9_4c_gates_as_of import _all_six_pass
from scripts.build_sprint9_5a_rebalance_targets import (
    OUTPUT_COLUMNS,
    WALK_FORWARD_ROLE,
    load_inputs,
    select_eligible_targets,
)


ROOT = Path(__file__).resolve().parents[1]
TARGET_PATH = (
    ROOT
    / "data"
    / "screener"
    / "targets_pit"
    / "2026-07-28"
    / "rebalance_targets_point_in_time.csv.gz"
)


@pytest.fixture(scope="module")
def targets() -> pd.DataFrame:
    return pd.read_csv(TARGET_PATH, keep_default_na=False)


@pytest.fixture(scope="module")
def source_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    return load_inputs()


def _selection_frame(tickers: list[str], ranks: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": tickers,
            "rank_in_population": [str(value) for value in ranks],
            "_rank_numeric": ranks,
        }
    )


def _all_eligible(tickers: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": tickers,
            "eligible": [True] * len(tickers),
            "reason": [""] * len(tickers),
        }
    )


def test_target_schema_has_the_contract_column_order(targets: pd.DataFrame) -> None:
    assert tuple(targets.columns) == OUTPUT_COLUMNS


def test_weights_sum_to_one_for_each_emitted_basket(targets: pd.DataFrame) -> None:
    for _, frame in targets.groupby(["config_id", "rebalance_date"], sort=False):
        assert int(frame["selected_count"].iloc[0]) > 0
        assert pd.to_numeric(frame["weight"]).sum() == pytest.approx(1.0, abs=1e-9)


def test_no_ticker_appears_twice_in_an_emitted_basket(targets: pd.DataFrame) -> None:
    assert not targets.duplicated(["config_id", "rebalance_date", "ticker"]).any()


def test_gated_targets_satisfy_imported_six_gate_predicate(
    targets: pd.DataFrame,
    source_inputs: tuple[pd.DataFrame, pd.DataFrame],
) -> None:
    _, gates = source_inputs
    gate_lookup = {
        (str(row.evaluation_date), str(row.ticker)): row
        for row in gates.loc[gates["grid_role"].eq(WALK_FORWARD_ROLE)].itertuples(index=False)
    }
    gated_targets = targets.loc[targets["gate_setting"].eq("VALUE_PLUS_GATES")]
    assert not gated_targets.empty
    for row in gated_targets.itertuples(index=False):
        assert _all_six_pass(gate_lookup[(str(row.rebalance_date), str(row.ticker))])


def test_every_target_is_from_its_existing_cheap_set(
    targets: pd.DataFrame,
    source_inputs: tuple[pd.DataFrame, pd.DataFrame],
) -> None:
    candidates, _ = source_inputs
    cheap = candidates.loc[candidates["_in_cheap_set"]]
    cheap_keys = set(
        zip(
            cheap["evaluation_date"].astype(str),
            cheap["population_id"].astype(str),
            cheap["metric"].astype(str),
            cheap["ticker"].astype(str),
        )
    )
    for row in targets.itertuples(index=False):
        assert (
            str(row.rebalance_date),
            str(row.population_id),
            str(row.metric),
            str(row.ticker),
        ) in cheap_keys


def test_selection_is_deterministic_when_input_rows_are_shuffled() -> None:
    candidates = _selection_frame(
        ["ZZZ", "AAA", "CCC", "BBB", "DDD"],
        [2.0, 1.0, 2.0, 2.0, 3.0],
    )
    eligibility = _all_eligible(candidates["ticker"].tolist())
    first = select_eligible_targets(
        candidates.sample(frac=1, random_state=101).reset_index(drop=True),
        eligibility,
    )
    second = select_eligible_targets(
        candidates.sample(frac=1, random_state=202).reset_index(drop=True),
        eligibility,
    )
    assert first.selected["ticker"].tolist() == second.selected["ticker"].tolist()


def test_tied_rank_selects_alphabetically_smaller_ticker_first() -> None:
    tickers = ["ZZZ", "AAA"] + [f"B{index:03d}" for index in range(HOLDING_COUNT - 2)]
    ranks = [1.0, 1.0] + [2.0] * (HOLDING_COUNT - 2)
    result = select_eligible_targets(_selection_frame(tickers, ranks), _all_eligible(tickers))
    assert result.selected["ticker"].iloc[0] == "AAA"
    assert result.selected["ticker"].iloc[1] == "ZZZ"


def test_short_basket_keeps_all_twelve_eligible_candidates_with_equal_weights() -> None:
    assert HOLDING_COUNT == 20
    tickers = [f"T{index:03d}" for index in range(12)]
    result = select_eligible_targets(
        _selection_frame(tickers, [float(index + 1) for index in range(len(tickers))]),
        _all_eligible(tickers),
    )
    assert result.short_basket is True
    assert result.selected_count == len(tickers)
    assert len(result.selected) == len(tickers)
    assert all(
        weight == pytest.approx(1 / len(tickers))
        for weight in result.selected["weight"].tolist()
    )
