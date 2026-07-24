from __future__ import annotations

import pandas as pd
import pytest

from scripts.probe_corporate_actions_coverage import (
    classify_event,
    factor_verdict,
    fetch_ticker_events,
)


@pytest.mark.parametrize(
    ("row", "expected"),
    [
        (
            {
                "event_code": "ISS",
                "event_title_en": "Share Issue - Bonus Issue ratio 20.0%",
                "exercise_ratio": 0.2,
                "exright_date": "2020-09-29",
            },
            "BONUS_OR_STOCK_DIV_COMPLETE",
        ),
        (
            {
                "event_code": "DIV",
                "event_title_en": "Cash Dividend",
                "value_per_share": 1000,
                "exright_date": "2024-05-02",
            },
            "CASH_DIV_COMPLETE",
        ),
        (
            {
                "event_code": "ISS",
                "event_title_en": "Share Issue - Rights issue ratio 20.0%",
                "exercise_ratio": 0.2,
                "value_per_share": "",
                "exright_date": "2019-06-17",
            },
            "RIGHTS_NO_SUBSCRIPTION_PRICE",
        ),
        (
            {
                "event_code": "ISS",
                "event_title_en": "Share Issue - Stock dividend ratio 10.0%",
                "exercise_ratio": 0.1,
                "exright_date": "",
            },
            "MISSING_EXRIGHT_DATE",
        ),
        (
            {
                "event_code": "ISS",
                "event_title_en": "Share Issue - ESOP",
                "exercise_ratio": 0,
                "exright_date": "2023-05-08",
            },
            "ZERO_OR_NULL_RATIO",
        ),
        (
            {
                "event_code": "ISS",
                "event_title_en": "Share Issue - ESOP ratio 0.5%",
                "exercise_ratio": 0.005,
                "exright_date": "2025-05-07",
            },
            "OTHER_UNCLASSIFIED",
        ),
    ],
)
def test_each_event_class(row: dict[str, object], expected: str) -> None:
    assert classify_event(pd.Series(row)) == expected


def test_empty_no_events_is_clean() -> None:
    assert factor_verdict({}, "EMPTY_NO_EVENTS") == "CLEAN"


def test_fetcher_forces_real_vci_shape_and_paginates_50_plus_1() -> None:
    calls: list[dict[str, object]] = []
    raw_rows = [
        {
            "eventCode": "DIV",
            "eventTitleEn": "Cash Dividend",
            "ticker": "AAA",
            "publicDate": "2024-01-01T00:00:00",
            "exrightDate": "2024-01-02T00:00:00",
            "valuePerShare": 1000.0,
        }
        for _ in range(51)
    ]

    class FakeProvider:
        def _fetch_events(self, **kwargs: object) -> list[dict[str, object]]:
            calls.append(kwargs)
            page = int(kwargs["page"])
            return raw_rows[page * 50 : (page + 1) * 50]

    class FakeCompany:
        def __init__(self) -> None:
            self.provider = FakeProvider()

        def events(self) -> pd.DataFrame:
            frame = pd.DataFrame(self.provider._fetch_events())
            frame.columns = [
                "".join(("_" + char.lower()) if char.isupper() else char for char in column)
                for column in frame.columns
            ]
            for column in ("public_date", "exright_date"):
                frame[column] = pd.to_datetime(frame[column]).dt.strftime("%Y-%m-%d")
            return frame

    company = FakeCompany()

    class FakeModule:
        @staticmethod
        def Company(**kwargs: object) -> FakeCompany:
            assert kwargs == {
                "source": "VCI",
                "symbol": "AAA",
                "random_agent": True,
                "show_log": False,
            }
            return company

    class FakeClient:
        @staticmethod
        def _vnstock_module() -> FakeModule:
            return FakeModule()

        @staticmethod
        def _quiet_call(function: object, *args: object, **kwargs: object) -> object:
            return function(*args, **kwargs)  # type: ignore[operator]

        @staticmethod
        def _polite_sleep() -> None:
            return None

        @staticmethod
        def _to_frame(value: object) -> pd.DataFrame:
            return value.copy()  # type: ignore[union-attr]

    rows, pages, provider_rows = fetch_ticker_events(
        "AAA",
        FakeClient(),  # type: ignore[arg-type]
        "20260724",
    )

    assert pages == 2
    assert provider_rows == 51
    assert len(rows) == 51
    assert set(rows["event_class"]) == {"CASH_DIV_COMPLETE"}
    assert calls == [
        {
            "event_codes": "DIV,ISS",
            "from_date": "20160101",
            "to_date": "20260724",
            "page": 0,
            "size": 50,
        },
        {
            "event_codes": "DIV,ISS",
            "from_date": "20160101",
            "to_date": "20260724",
            "page": 1,
            "size": 50,
        },
    ]
