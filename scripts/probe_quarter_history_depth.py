from __future__ import annotations

import sys
import time
from typing import Any

import pandas as pd
from vnstock.api.financial import Finance


STATEMENT_METHODS = ("balance_sheet", "income_statement", "cash_flow")
NON_PERIOD_COLUMNS = {"item", "item_en", "item_id"}
POLITE_SLEEP_SECONDS = 2.8


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


def _period_columns(raw: Any) -> list[str]:
    frame = raw if isinstance(raw, pd.DataFrame) else pd.DataFrame(raw)
    return [str(column) for column in frame.columns if str(column) not in NON_PERIOD_COLUMNS]


def _row_count(raw: Any) -> int:
    return len(raw if isinstance(raw, pd.DataFrame) else pd.DataFrame(raw))


def main() -> int:
    _configure_console()
    finance = Finance(
        source="VCI",
        symbol="VNM",
        period="quarter",
        get_all=True,
        show_log=False,
    )
    high_level_methods = {
        "balance_sheet": finance.balance_sheet,
        "income_statement": finance.income_statement,
        "cash_flow": finance.cash_flow,
    }
    first_call = True

    for method_name in STATEMENT_METHODS:
        if not first_call:
            time.sleep(POLITE_SLEEP_SECONDS)
        high_level = high_level_methods[method_name](
            period="quarter",
            lang="en",
            dropna=False,
            show_log=False,
        )
        first_call = False
        high_periods = _period_columns(high_level)
        print(f"{method_name} high_level_periods={high_periods}")
        print(f"{method_name} high_level_n_periods={len(high_periods)}")

        time.sleep(POLITE_SLEEP_SECONDS)
        low_level = finance.provider._get_financial_report(
            method_name,
            period="quarter",
            lang="en",
            get_all=True,
            dropna=False,
            show_log=False,
            limit=200,
        )
        low_periods = _period_columns(low_level)
        print(f"{method_name} low_level_periods={low_periods}")
        print(f"{method_name} low_level_n_periods={len(low_periods)}")

        time.sleep(POLITE_SLEEP_SECONDS)
        raw_mode = finance.provider._get_report(
            report_type=method_name,
            period="quarter",
            mode="raw",
            limit=100000,
            show_log=False,
        )
        print(f"{method_name} raw_mode_rows={_row_count(raw_mode)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
