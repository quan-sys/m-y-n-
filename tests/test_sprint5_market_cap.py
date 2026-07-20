from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.fetch_sprint5_market_cap import (
    calculate_market_cap_vnd,
    guard_market_cap_inputs,
    record_passes_contract,
    run_full_universe,
)


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


def test_calibrated_guard_logic_and_vnd_product_without_times_1000() -> None:
    assert guard_market_cap_inputs(None, 2_000_000) == ["MISSING_INPUT"]
    assert guard_market_cap_inputs(999, 2_000_000) == ["PRICE_OUT_OF_RANGE"]
    assert guard_market_cap_inputs(1_000_001, 2_000_000) == ["PRICE_OUT_OF_RANGE"]
    assert guard_market_cap_inputs(10_000, 1_000_000) == ["SHARES_SUSPECT"]
    assert guard_market_cap_inputs(10_000, 2_000_000) == []
    assert calculate_market_cap_vnd(10_000, 2_000_000) == 20_000_000_000


def _survivors(path: Path, tickers: list[str]) -> None:
    pd.DataFrame({"ticker": tickers}).to_csv(path, index=False)


def test_full_universe_resume_reuses_checkpoint_without_live_calls(tmp_path: Path) -> None:
    tickers = ["AAA", "BBB", "CCC"]
    survivors = tmp_path / "survivors.csv"
    output = tmp_path / "universe_market_cap.csv"
    _survivors(survivors, tickers)
    board_calls: list[list[str]] = []
    overview_calls: list[str] = []

    def board(batch: list[str]) -> pd.DataFrame:
        board_calls.append(batch)
        return pd.DataFrame(
            [{"symbol": ticker, "close_price": 10_000, "TD": "17/07/2026"} for ticker in batch]
        )

    def overview(ticker: str) -> pd.DataFrame:
        overview_calls.append(ticker)
        return pd.DataFrame(
            [{"symbol": ticker, "outstanding_shares": 2_000_000, "as_of_date": "2025-12-31"}]
        )

    first = run_full_universe(
        survivors_path=survivors,
        output_path=output,
        expected_count=3,
        sleep_seconds=0,
        sleep_fn=lambda _: None,
        board_fetcher=board,
        overview_fetcher=overview,
    )
    assert first["api_calls"] == 4
    assert first["cache_hits"] == 0
    assert first["selected_coverage"] == 3

    board_calls.clear()
    overview_calls.clear()
    second = run_full_universe(
        survivors_path=survivors,
        output_path=output,
        expected_count=3,
        sleep_seconds=0,
        sleep_fn=lambda _: None,
        board_fetcher=board,
        overview_fetcher=overview,
    )
    assert second["api_calls"] == 0
    assert second["cache_hits"] == 3
    assert board_calls == []
    assert overview_calls == []


def test_price_board_batches_never_exceed_50_tickers(tmp_path: Path) -> None:
    tickers = [f"T{index:03d}" for index in range(101)]
    survivors = tmp_path / "survivors.csv"
    output = tmp_path / "universe_market_cap.csv"
    _survivors(survivors, tickers)
    batch_sizes: list[int] = []

    def board(batch: list[str]) -> pd.DataFrame:
        batch_sizes.append(len(batch))
        return pd.DataFrame(
            [{"symbol": ticker, "close_price": 10_000, "TD": "17/07/2026"} for ticker in batch]
        )

    result = run_full_universe(
        survivors_path=survivors,
        output_path=output,
        expected_count=101,
        sleep_seconds=0,
        sleep_fn=lambda _: None,
        board_fetcher=board,
        overview_fetcher=lambda ticker: pd.DataFrame(
            [{"symbol": ticker, "outstanding_shares": 2_000_000, "as_of_date": "2025-12-31"}]
        ),
    )
    assert batch_sizes == [50, 50, 1]
    assert result["selected_coverage"] == 101
