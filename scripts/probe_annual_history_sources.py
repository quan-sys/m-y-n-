"""Read-only annual-history probe for the five owner-approved tickers and sources."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
import time
from typing import Any, Callable

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "docs" / "SPRINT_6_HISTORY_SOURCE_PROBE.md"
TICKERS = ("VNM", "FPT", "HPG", "DBC", "NTC")
SOURCES = ("VCI", "TCBS")
STATEMENTS = (
    ("BALANCE_SHEET", "balance_sheet"),
    ("INCOME_STATEMENT", "income_statement"),
    ("CASH_FLOW", "cash_flow"),
)
EXTENDED_PARAMETER_NAME = "limit"
EXTENDED_PARAMETER_VALUE = 100

CHECKLIST_BY_STATEMENT = {
    "BALANCE_SHEET": (
        "total_assets",
        "long_term_borrowings",
        "current_assets",
        "current_liabilities",
        "common_shares",
        "owners_equity",
        "short_term_borrowings",
        "cash_and_cash_equivalents",
    ),
    "INCOME_STATEMENT": (
        "net_profit_loss_after_tax",
        "net_sales",
        "gross_profit",
        "cost_of_sales",
    ),
    "CASH_FLOW": (
        "net_cash_inflows_outflows_from_operating_activities",
        "proceeds_from_issue_of_shares",
    ),
}


@dataclass
class ProbeRecord:
    ticker: str
    source: str
    statement: str
    default_periods: tuple[str, ...] = ()
    default_item_ids: tuple[str, ...] = ()
    extended_periods: tuple[str, ...] = ()
    extended_item_ids: tuple[str, ...] = ()
    default_error: str = ""
    extended_error: str = ""
    parameter_name: str = EXTENDED_PARAMETER_NAME
    parameter_value: int = EXTENDED_PARAMETER_VALUE
    parameter_returns_more_history: bool = False


def parse_period_list(frame: pd.DataFrame) -> tuple[str, ...]:
    """Return every annual period column exactly in provider-returned order."""

    return tuple(
        str(column)
        for column in frame.columns
        if re.fullmatch(r"\d{4}", str(column).strip())
    )


def parse_item_ids(frame: pd.DataFrame) -> tuple[str, ...]:
    if frame.empty or "item_id" not in frame.columns:
        return ()
    return tuple(
        sorted(
            {
                str(value).strip()
                for value in frame["item_id"].dropna()
                if str(value).strip()
            }
        )
    )


def quote_error(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"


def is_rate_limit_response(error: str) -> bool:
    lowered = error.lower()
    return any(
        marker in lowered
        for marker in (
            "429",
            "rate limit",
            "ratelimit",
            "too many requests",
            "quá nhiều yêu cầu",
        )
    )


class DelayedCaller:
    def __init__(self, delay_seconds: float) -> None:
        self.delay_seconds = delay_seconds
        self.last_call_finished: float | None = None

    def call(self, function: Callable[[], pd.DataFrame]) -> pd.DataFrame:
        if self.last_call_finished is not None:
            elapsed = time.monotonic() - self.last_call_finished
            remaining = self.delay_seconds - elapsed
            if remaining > 0:
                time.sleep(remaining)
        try:
            return function()
        finally:
            self.last_call_finished = time.monotonic()


def _provider_frame(
    provider: Any,
    report_type: str,
    *,
    limit: int | None,
) -> pd.DataFrame:
    value = provider._get_financial_report(
        report_type,
        period="year",
        lang="en",
        mode="final",
        style="readable",
        get_all=False,
        dropna=False,
        show_log=False,
        limit=limit,
    )
    if value is None:
        return pd.DataFrame()
    if isinstance(value, pd.DataFrame):
        return value.copy()
    return pd.DataFrame(value)


def run_probe(delay_seconds: float) -> tuple[list[ProbeRecord], str]:
    from vnstock.api.financial import Finance

    records: list[ProbeRecord] = []
    caller = DelayedCaller(delay_seconds)
    rate_limit_error = ""
    stop = False
    for source in SOURCES:
        for ticker in TICKERS:
            if stop:
                for statement, _ in STATEMENTS:
                    records.append(
                        ProbeRecord(
                            ticker=ticker,
                            source=source,
                            statement=statement,
                            default_error=(
                                "NOT_RUN_AFTER_RATE_LIMIT: " + rate_limit_error
                            ),
                            extended_error=(
                                "NOT_RUN_AFTER_RATE_LIMIT: " + rate_limit_error
                            ),
                        )
                    )
                continue
            try:
                adapter = Finance(
                    source=source,
                    symbol=ticker,
                    period="year",
                    get_all=True,
                    show_log=False,
                )
                provider = adapter.provider
            except BaseException as exc:  # provider errors are evidence
                error = quote_error(exc)
                if is_rate_limit_response(error):
                    rate_limit_error = error
                    stop = True
                for statement, _ in STATEMENTS:
                    records.append(
                        ProbeRecord(
                            ticker=ticker,
                            source=source,
                            statement=statement,
                            default_error=error,
                            extended_error=error,
                        )
                    )
                continue

            for statement, report_type in STATEMENTS:
                record = ProbeRecord(
                    ticker=ticker,
                    source=source,
                    statement=statement,
                )
                try:
                    default = caller.call(
                        lambda report_type=report_type: _provider_frame(
                            provider, report_type, limit=None
                        )
                    )
                    record.default_periods = parse_period_list(default)
                    record.default_item_ids = parse_item_ids(default)
                    if default.empty:
                        record.default_error = "EMPTY_RESPONSE"
                except BaseException as exc:
                    record.default_error = quote_error(exc)
                    if is_rate_limit_response(record.default_error):
                        rate_limit_error = record.default_error
                        stop = True
                        record.extended_error = (
                            "NOT_RUN_AFTER_RATE_LIMIT: " + rate_limit_error
                        )
                        records.append(record)
                        break

                try:
                    extended = caller.call(
                        lambda report_type=report_type: _provider_frame(
                            provider, report_type, limit=EXTENDED_PARAMETER_VALUE
                        )
                    )
                    record.extended_periods = parse_period_list(extended)
                    record.extended_item_ids = parse_item_ids(extended)
                    if extended.empty:
                        record.extended_error = "EMPTY_RESPONSE"
                except BaseException as exc:
                    record.extended_error = quote_error(exc)
                    if is_rate_limit_response(record.extended_error):
                        rate_limit_error = record.extended_error
                        stop = True
                record.parameter_returns_more_history = (
                    len(record.extended_periods) > len(record.default_periods)
                )
                records.append(record)
                if stop:
                    break
            if stop:
                completed = {(row.source, row.ticker, row.statement) for row in records}
                for statement, _ in STATEMENTS:
                    key = (source, ticker, statement)
                    if key not in completed:
                        records.append(
                            ProbeRecord(
                                ticker=ticker,
                                source=source,
                                statement=statement,
                                default_error=(
                                    "NOT_RUN_AFTER_RATE_LIMIT: " + rate_limit_error
                                ),
                                extended_error=(
                                    "NOT_RUN_AFTER_RATE_LIMIT: " + rate_limit_error
                                ),
                            )
                        )
    expected = len(TICKERS) * len(SOURCES) * len(STATEMENTS)
    if len(records) != expected:
        raise AssertionError(f"expected {expected} probe records; found {len(records)}")
    return records, rate_limit_error


def _json_list(values: tuple[str, ...] | list[str]) -> str:
    return json.dumps(list(values), ensure_ascii=False)


def _md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_report(records: list[ProbeRecord], rate_limit_error: str) -> str:
    lookup = {
        (record.source, record.ticker, record.statement): record
        for record in records
    }
    lines = [
        "# Sprint 6 annual-history source probe",
        "",
        "This is a read-only provider probe. It writes nothing under `data/fundamentals/`, changes no production source, and computes no existing output.",
        "",
        f"- Tickers, exactly `{len(TICKERS)}`: `{', '.join(TICKERS)}`.",
        f"- Sources, exactly `{len(SOURCES)}`: `{', '.join(SOURCES)}`.",
        f"- Statements per source/ticker: `{len(STATEMENTS)}` annual statements.",
        f"- Delay between provider calls: `{PROBE_DELAY_TEXT}` seconds.",
        f"- Extended-history parameter tried: `{EXTENDED_PARAMETER_NAME}={EXTENDED_PARAMETER_VALUE}` on the provider's `_get_financial_report` interface; the default is `limit=None`, which the installed VCI provider implements as `4`.",
        "- No provider other than VCI or TCBS was attempted.",
        "",
        "## 1. Full annual period lists returned",
        "",
        "Every list below is the complete provider-returned annual period-column list in returned order; `[]` means no periods were returned.",
        "",
        "| source | ticker | statement | default periods | default count | limit=100 periods | limit=100 count | more than default | default error | limit=100 error |",
        "|---|---|---|---|---:|---|---:|---|---|---|",
    ]
    for source in SOURCES:
        for ticker in TICKERS:
            for statement, _ in STATEMENTS:
                row = lookup[(source, ticker, statement)]
                lines.append(
                    f"| {source} | {ticker} | {statement} | "
                    f"`{_json_list(row.default_periods)}` | {len(row.default_periods)} | "
                    f"`{_json_list(row.extended_periods)}` | {len(row.extended_periods)} | "
                    f"{row.parameter_returns_more_history} | "
                    f"`{_md(row.default_error)}` | `{_md(row.extended_error)}` |"
                )

    lines.extend(
        [
            "",
            "## 2. VCI versus TCBS checklist item_id coverage",
            "",
            "The checklist contains the eleven section 2.1 normalized fields plus the four section 3.1 ROC balance entries. `long_term_borrowings` appears in both source sections, so there are `14` unique item_id values. Comparison uses the `limit=100` response when available, otherwise the default response.",
            "",
            "| ticker | statement | checklist | present in both | only in VCI | only in TCBS | missing from both |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    tcbs_covers_all = True
    for ticker in TICKERS:
        for statement, _ in STATEMENTS:
            checklist = set(CHECKLIST_BY_STATEMENT[statement])
            vci = lookup[("VCI", ticker, statement)]
            tcbs = lookup[("TCBS", ticker, statement)]
            vci_items = set(vci.extended_item_ids or vci.default_item_ids) & checklist
            tcbs_items = set(tcbs.extended_item_ids or tcbs.default_item_ids) & checklist
            both = sorted(vci_items & tcbs_items)
            only_vci = sorted(vci_items - tcbs_items)
            only_tcbs = sorted(tcbs_items - vci_items)
            missing = sorted(checklist - (vci_items | tcbs_items))
            if tcbs_items != checklist:
                tcbs_covers_all = False
            lines.append(
                f"| {ticker} | {statement} | `{_json_list(sorted(checklist))}` | "
                f"`{_json_list(both)}` | `{_json_list(only_vci)}` | "
                f"`{_json_list(only_tcbs)}` | `{_json_list(missing)}` |"
            )

    lines.extend(
        [
            "",
            "## 3. Errors, empty responses, and rate limits",
            "",
        ]
    )
    errors = [
        record
        for record in records
        if record.default_error or record.extended_error
    ]
    if errors:
        for record in errors:
            lines.append(
                f"- `{record.source} {record.ticker} {record.statement}` default: "
                f"`{_md(record.default_error)}`; `limit=100`: "
                f"`{_md(record.extended_error)}`."
            )
    else:
        lines.append("- `NONE`.")
    lines.append(
        f"- Rate-limit stop response: `{_md(rate_limit_error) if rate_limit_error else 'NONE'}`."
    )

    max_depth = {
        source: max(
            max(len(record.default_periods), len(record.extended_periods))
            for record in records
            if record.source == source
        )
        for source in SOURCES
    }
    tcbs_all_empty = all(
        not record.default_periods and not record.extended_periods
        for record in records
        if record.source == "TCBS"
    )
    lines.extend(
        [
            "",
            "## Owner decision required",
            "",
            f"- Maximum annual history depth observed for VCI: `{max_depth['VCI']}`.",
            f"- Maximum annual history depth observed for TCBS: `{max_depth['TCBS']}`.",
            f"- TCBS returned no annual period for all five tickers and all three statements: `{tcbs_all_empty}`.",
            f"- TCBS item_id set covers every field required by the current spec checklist: `{tcbs_covers_all}`.",
            "- This section makes no recommendation. It states only the measured probe results and leaves the provider/history decision to the owner.",
            "",
        ]
    )
    return "\n".join(lines)


PROBE_DELAY_TEXT = "2.8"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delay-seconds", type=float, default=2.8)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args(argv)
    if args.delay_seconds < 0:
        parser.error("--delay-seconds must be non-negative")
    return args


def main(argv: list[str] | None = None) -> int:
    global PROBE_DELAY_TEXT
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    args = parse_args(argv)
    PROBE_DELAY_TEXT = format(args.delay_seconds, "g")
    records, rate_limit_error = run_probe(args.delay_seconds)
    args.output.write_text(render_report(records, rate_limit_error), encoding="utf-8")
    for source in SOURCES:
        maximum = max(
            max(len(record.default_periods), len(record.extended_periods))
            for record in records
            if record.source == source
        )
        print(f"{source}_maximum_annual_history_depth={maximum}")
    print(f"records={len(records)}")
    print(f"rate_limit={rate_limit_error or 'NONE'}")
    print("fundamentals_cache_writes=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
