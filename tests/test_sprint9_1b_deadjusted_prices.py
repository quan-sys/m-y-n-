from __future__ import annotations

import pandas as pd
import pytest

from scripts.build_deadjusted_prices import (
    bonus_factor,
    build_deadjusted,
    cash_dividend_factor,
    rights_factor,
)


def test_bonus_factor_is_one_over_one_plus_b() -> None:
    assert bonus_factor(0.2) == pytest.approx(1 / 1.2)


def test_cash_factor_converts_vnd_dividend_to_thousand_vnd() -> None:
    assert cash_dividend_factor(100.0, 2_000.0) == pytest.approx((100.0 - 2.0) / 100.0)


def test_rights_factor_uses_par_subscription_price() -> None:
    assert rights_factor(40.0, 0.25, 10.0) == pytest.approx(
        (40.0 + 0.25 * 10.0) / (40.0 * 1.25)
    )


def _prices() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["AAA"] * 4,
            "date": ["2020-01-02", "2020-01-03", "2020-01-06", "2020-01-07"],
            "close_adjusted": [80.0, 82.0, 100.0, 101.0],
        }
    )


def _event(
    *,
    event_class: str,
    title: str,
    exright_date: str,
    record_date: str = "",
    public_date: str = "",
    ratio: object = "",
    value: object = "",
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "event_code": "DIV" if event_class == "CASH_DIV_COMPLETE" else "ISS",
                "event_title_en": title,
                "event_title_vi": "",
                "event_class": event_class,
                "exright_date": exright_date,
                "record_date": record_date,
                "public_date": public_date,
                "exercise_ratio": ratio,
                "value_per_share": value,
            }
        ]
    )


def test_most_recent_date_has_factor_one() -> None:
    events = _event(
        event_class="BONUS_OR_STOCK_DIV_COMPLETE",
        title="Share Issue - Bonus Issue ratio 20.0%",
        exright_date="2020-01-06",
        ratio=0.2,
    )
    result, _ = build_deadjusted(_prices(), events)
    latest = result.iloc[-1]
    assert latest["cumulative_factor"] == pytest.approx(1.0)
    assert latest["raw_close"] == pytest.approx(101.0)


def test_rights_low_flag_propagates_before_event_only() -> None:
    events = _event(
        event_class="RIGHTS_NO_SUBSCRIPTION_PRICE",
        title="Share Issue - Rights issue ratio 25.0%",
        exright_date="2020-01-06",
        ratio=0.25,
    )
    result, _ = build_deadjusted(_prices(), events)
    assert result["adjustment_confidence"].tolist() == ["LOW", "LOW", "OK", "OK"]


def test_non_price_events_do_not_change_factors() -> None:
    prices = _prices()
    bonus = _event(
        event_class="BONUS_OR_STOCK_DIV_COMPLETE",
        title="Share Issue - Bonus Issue ratio 20.0%",
        exright_date="2020-01-06",
        ratio=0.2,
    )
    esop = _event(
        event_class="OTHER_UNCLASSIFIED",
        title="Share Issue - ESOP ratio 5.0%",
        exright_date="2020-01-06",
        ratio=0.05,
    )
    without, _ = build_deadjusted(prices, bonus)
    with_esop, _ = build_deadjusted(prices, pd.concat([bonus, esop], ignore_index=True))
    assert with_esop["cumulative_factor"].tolist() == pytest.approx(
        without["cumulative_factor"].tolist()
    )


def test_future_public_date_event_does_not_change_factor_or_confidence() -> None:
    prices = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA"],
            "date": ["2026-07-21", "2026-07-22"],
            "close_adjusted": [100.0, 101.0],
        }
    )
    future = _event(
        event_class="MISSING_EXRIGHT_DATE",
        title="Share Issue - Bonus Issue ratio 20.0%",
        exright_date="",
        public_date="2026-07-23",
        ratio=0.2,
    )
    result, diagnostics = build_deadjusted(prices, future)
    assert result["cumulative_factor"].tolist() == pytest.approx([1.0, 1.0])
    assert result["adjustment_confidence"].tolist() == ["OK", "OK"]
    assert diagnostics.future_events_ignored == 1


def test_historical_public_date_fallback_is_placed_and_low_before_only() -> None:
    historical = _event(
        event_class="MISSING_EXRIGHT_DATE",
        title="Share Issue - Bonus Issue ratio 20.0%",
        exright_date="",
        public_date="2020-01-06",
        ratio=0.2,
    )
    result, diagnostics = build_deadjusted(_prices(), historical)
    assert result["cumulative_factor"].tolist() == pytest.approx(
        [1 / 1.2, 1 / 1.2, 1.0, 1.0]
    )
    assert result["adjustment_confidence"].tolist() == ["LOW", "LOW", "OK", "OK"]
    assert diagnostics.unplaceable_tickers == ()
