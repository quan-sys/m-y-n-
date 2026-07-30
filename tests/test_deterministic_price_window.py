from datetime import date, timedelta

import pandas as pd

from src.data.vnstock_client import VnstockClient


class RecordingQuote:
    history_calls: list[dict[str, object]] = []

    def __init__(self, **_: object) -> None:
        pass

    def history(self, **kwargs: object) -> pd.DataFrame:
        self.history_calls.append(kwargs)
        return pd.DataFrame([{"time": "2026-07-30", "close": 42.5}])


class FixtureVnstock:
    Quote = RecordingQuote


def _client(as_of_date: date | None) -> VnstockClient:
    client = object.__new__(VnstockClient)
    client.quote_source = "VCI"
    client.as_of_date = as_of_date
    client._polite_sleep = lambda: None
    client._vnstock_module = lambda: FixtureVnstock
    client._quiet_call = lambda method, **kwargs: method(**kwargs)
    client._to_frame = lambda value: value
    return client


def _request_window(as_of_date: date | None, months: int = 1) -> tuple[str, str]:
    RecordingQuote.history_calls.clear()
    _client(as_of_date)._fetch_price_history("HAG", months)
    call = RecordingQuote.history_calls[-1]
    return str(call["start"]), str(call["end"])


def test_fixed_as_of_date_is_passed_to_quote_history() -> None:
    assert _request_window(date(2025, 3, 14)) == ("2025-02-01", "2025-03-14")


def test_fixed_as_of_date_produces_identical_windows() -> None:
    assert _request_window(date(2025, 3, 14), months=3) == _request_window(date(2025, 3, 14), months=3)


def test_unset_as_of_date_uses_today() -> None:
    _, end = _request_window(None)
    assert end == date.today().isoformat()


def test_one_month_window_starts_41_days_before_end() -> None:
    start, end = _request_window(date(2025, 3, 14))
    assert date.fromisoformat(end) - date.fromisoformat(start) == timedelta(days=41)


def test_as_of_date_is_not_today() -> None:
    assert date(2025, 3, 14) < date.today()
