"""Probe VCI VNINDEX daily-history availability without computing performance."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import sys
from typing import Protocol

import pandas as pd


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.build_forward_test_snapshot import (  # noqa: E402
    LiveVciPriceClient,
    PRICE_PROVIDER,
    PRICE_SOURCE,
    _import_vnstock_without_upgrade_check,
)


BENCHMARK_TICKER = "VNINDEX"
PROBE_START = date(2019, 1, 1)
EVALUATION_START = date(2019, 3, 31)
PROBE_END = date(2026, 7, 24)
WIDEST_REQUEST_START = date(1900, 1, 1)
INDEX_UNIT = "INDEX_POINTS"
OUTPUT_COLUMNS = (
    "ticker",
    "date",
    "close_adjusted",
    "close_adjusted_unit",
    "volume",
    "source",
    "as_of",
    "data_status",
)
KNOWN_CLOSES = {
    "2026-07-21": "1730.56",
    "2026-07-24": "1686.11",
}


class RangeClient(Protocol):
    def fetch_history(self, ticker: str, start: date, end: date) -> pd.DataFrame: ...


@dataclass(frozen=True)
class StrategyRecord:
    strategy: str
    requested_start: str
    requested_end: str
    earliest_session: str
    latest_session: str
    session_count: int
    cap_or_truncation: str
    error: str
    history: pd.DataFrame


@dataclass(frozen=True)
class ProbeResult:
    single_range: StrategyRecord
    yearly_records: tuple[StrategyRecord, ...]
    yearly_combined: StrategyRecord
    widest_range: StrategyRecord
    selected: StrategyRecord | None
    calendar_year_counts: dict[int, int]
    known_close_values: dict[str, str]
    coverage_usable: bool
    coverage_reason: str


class LiveVciBenchmarkHistoryClient:
    """Use the snapshot's VnstockClient -> VCI Quote.history call path exactly once per request."""

    def __init__(self) -> None:
        self._snapshot_client = LiveVciPriceClient()

    def fetch_history(self, ticker: str, start: date, end: date) -> pd.DataFrame:
        client = self._snapshot_client._client
        _import_vnstock_without_upgrade_check()
        client._polite_sleep()
        vnstock = client._vnstock_module()
        quote = client._quiet_call(
            getattr(vnstock, "Quote"),
            source=client.quote_source,
            symbol=ticker,
            random_agent=True,
            show_log=False,
        )
        return client._to_frame(
            client._quiet_call(
                quote.history,
                symbol=ticker,
                start=start.isoformat(),
                end=end.isoformat(),
                interval="1D",
            )
        )


def normalise_api_history(history: pd.DataFrame) -> pd.DataFrame:
    if history.empty:
        return pd.DataFrame(columns=("date", "close_adjusted", "volume"))
    date_column = next(
        (column for column in ("time", "date", "trading_date", "tradingDate", "datetime") if column in history),
        None,
    )
    if date_column is None or "close" not in history:
        raise ValueError("unexpected VCI Quote.history shape; missing date or close column")
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(history[date_column], errors="coerce").dt.date,
            "close_adjusted": pd.to_numeric(history["close"], errors="coerce"),
            "volume": pd.to_numeric(history.get("volume"), errors="coerce"),
        }
    )
    frame = frame.loc[frame["date"].notna() & frame["close_adjusted"].notna()].copy()
    frame["date"] = frame["date"].map(date.isoformat)
    return frame.sort_values("date", kind="stable").drop_duplicates("date", keep="last").reset_index(drop=True)


def _cap_or_truncation(history: pd.DataFrame, requested_start: date, requested_end: date) -> str:
    if history.empty:
        return "NO_SESSIONS_RETURNED"
    earliest = date.fromisoformat(str(history.loc[0, "date"]))
    latest = date.fromisoformat(str(history.loc[len(history) - 1, "date"]))
    returned_span_days = (latest - earliest).days
    if earliest > requested_start:
        return (
            f"TRUNCATED_OR_CAPPED: omitted_start_days={(earliest - requested_start).days}; "
            f"returned_span_days={returned_span_days}"
        )
    if latest < requested_end:
        end_gap_days = (requested_end - latest).days
        if end_gap_days <= 3:
            return (
                f"END_SESSION_BEFORE_REQUESTED_DATE: end_gap_days={end_gap_days}; "
                f"possible_non_trading_days; returned_span_days={returned_span_days}"
            )
        return (
            f"ENDED_EARLY: missing_end_days={end_gap_days}; "
            f"returned_span_days={returned_span_days}"
        )
    return f"NO_TRUNCATION_OBSERVED: returned_span_days={returned_span_days}"


def _record_request(
    client: RangeClient,
    strategy: str,
    start: date,
    end: date,
) -> StrategyRecord:
    try:
        history = normalise_api_history(client.fetch_history(BENCHMARK_TICKER, start, end))
    except BaseException as error:  # noqa: BLE001 - exact provider errors are probe evidence.
        return StrategyRecord(
            strategy=strategy,
            requested_start=start.isoformat(),
            requested_end=end.isoformat(),
            earliest_session="",
            latest_session="",
            session_count=0,
            cap_or_truncation="NOT_AVAILABLE_AFTER_ERROR",
            error=f"{type(error).__name__}: {error}",
            history=pd.DataFrame(columns=("date", "close_adjusted", "volume")),
        )
    if history.empty:
        return StrategyRecord(
            strategy=strategy,
            requested_start=start.isoformat(),
            requested_end=end.isoformat(),
            earliest_session="",
            latest_session="",
            session_count=0,
            cap_or_truncation="NO_SESSIONS_RETURNED",
            error="",
            history=history,
        )
    return StrategyRecord(
        strategy=strategy,
        requested_start=start.isoformat(),
        requested_end=end.isoformat(),
        earliest_session=str(history.loc[0, "date"]),
        latest_session=str(history.loc[len(history) - 1, "date"]),
        session_count=len(history),
        cap_or_truncation=_cap_or_truncation(history, start, end),
        error="",
        history=history,
    )


def _combine_yearly_records(records: tuple[StrategyRecord, ...]) -> StrategyRecord:
    frames = [record.history for record in records if not record.history.empty]
    combined = (
        pd.concat(frames, ignore_index=True)
        .sort_values("date", kind="stable")
        .drop_duplicates("date", keep="last")
        .reset_index(drop=True)
        if frames
        else pd.DataFrame(columns=("date", "close_adjusted", "volume"))
    )
    errors = " | ".join(f"{record.strategy}: {record.error}" for record in records if record.error)
    if combined.empty:
        return StrategyRecord(
            strategy="ii",
            requested_start=PROBE_START.isoformat(),
            requested_end=PROBE_END.isoformat(),
            earliest_session="",
            latest_session="",
            session_count=0,
            cap_or_truncation="NO_SESSIONS_RETURNED",
            error=errors,
            history=combined,
        )
    return StrategyRecord(
        strategy="ii",
        requested_start=PROBE_START.isoformat(),
        requested_end=PROBE_END.isoformat(),
        earliest_session=str(combined.loc[0, "date"]),
        latest_session=str(combined.loc[len(combined) - 1, "date"]),
        session_count=len(combined),
        cap_or_truncation=_cap_or_truncation(combined, PROBE_START, PROBE_END),
        error=errors,
        history=combined,
    )


def _calendar_year_counts(history: pd.DataFrame) -> dict[int, int]:
    if history.empty:
        return {year: 0 for year in range(2019, 2027)}
    years = pd.to_datetime(history["date"], errors="coerce").dt.year
    return {year: int((years == year).sum()) for year in range(2019, 2027)}


def _known_close_values(history: pd.DataFrame) -> dict[str, str]:
    values: dict[str, str] = {}
    for target_date in KNOWN_CLOSES:
        matching = history.loc[history["date"].eq(target_date), "close_adjusted"]
        values[target_date] = "" if matching.empty else format(float(matching.iloc[-1]), ".15g")
    return values


def _coverage_reason(history: pd.DataFrame, year_counts: dict[int, int], known_values: dict[str, str]) -> str:
    if history.empty:
        return "no successful strategy returned a usable session"
    earliest = date.fromisoformat(str(history.loc[0, "date"]))
    latest = date.fromisoformat(str(history.loc[len(history) - 1, "date"]))
    if earliest > EVALUATION_START:
        return f"earliest session {earliest.isoformat()} is after {EVALUATION_START.isoformat()}"
    if latest < PROBE_END:
        return f"latest session {latest.isoformat()} is before {PROBE_END.isoformat()}"
    short_full_years = [str(year) for year in range(2019, 2026) if year_counts[year] < 200]
    if short_full_years:
        return "calendar years below 200 sessions: " + ", ".join(short_full_years)
    mismatches = [
        target_date
        for target_date, expected in KNOWN_CLOSES.items()
        if known_values.get(target_date) != expected
    ]
    if mismatches:
        return "known benchmark closes mismatch or are absent: " + ", ".join(mismatches)
    return "continuous coverage and both committed benchmark closes were reproduced"


def _select_best(records: tuple[StrategyRecord, ...]) -> StrategyRecord | None:
    available = [record for record in records if not record.history.empty]
    if not available:
        return None
    return min(
        available,
        key=lambda record: (
            date.fromisoformat(record.earliest_session),
            -date.fromisoformat(record.latest_session).toordinal(),
            -record.session_count,
            record.strategy,
        ),
    )


def run_probe(client: RangeClient) -> ProbeResult:
    single_range = _record_request(client, "i", PROBE_START, PROBE_END)
    yearly_records = tuple(
        _record_request(
            client,
            f"ii-{year}",
            date(year, 1, 1),
            PROBE_END if year == PROBE_END.year else date(year, 12, 31),
        )
        for year in range(PROBE_START.year, PROBE_END.year + 1)
    )
    yearly_combined = _combine_yearly_records(yearly_records)
    widest_range = _record_request(client, "iii", WIDEST_REQUEST_START, PROBE_END)
    selected = _select_best((single_range, yearly_combined, widest_range))
    selected_history = selected.history if selected is not None else pd.DataFrame()
    year_counts = _calendar_year_counts(selected_history)
    known_values = _known_close_values(selected_history)
    reason = _coverage_reason(selected_history, year_counts, known_values)
    return ProbeResult(
        single_range=single_range,
        yearly_records=yearly_records,
        yearly_combined=yearly_combined,
        widest_range=widest_range,
        selected=selected,
        calendar_year_counts=year_counts,
        known_close_values=known_values,
        coverage_usable=reason == "continuous coverage and both committed benchmark closes were reproduced",
        coverage_reason=reason,
    )


def _table(rows: list[StrategyRecord]) -> str:
    lines = [
        "| strategy | requested start | requested end | earliest session returned | latest session returned | session count | cap or truncation | exact error text |",
        "|---|---|---|---|---|---:|---|---|",
    ]
    lines.extend(
        "| {strategy} | {start} | {end} | {earliest} | {latest} | {count} | {cap} | {error} |".format(
            strategy=record.strategy,
            start=record.requested_start,
            end=record.requested_end,
            earliest=record.earliest_session or "EMPTY",
            latest=record.latest_session or "EMPTY",
            count=record.session_count,
            cap=record.cap_or_truncation.replace("|", "\\|"),
            error=record.error.replace("|", "\\|") or "NONE",
        )
        for record in rows
    )
    return "\n".join(lines)


def verdict(result: ProbeResult) -> str:
    if result.coverage_usable and result.selected is not None:
        return (
            "VNINDEX daily history IS obtainable back to "
            f"{result.selected.earliest_session} using strategy {result.selected.strategy}."
        )
    earliest = result.selected.earliest_session if result.selected is not None else "NO_SESSION"
    return f"VNINDEX daily history is NOT obtainable earlier than {earliest}; the limiting factor is {result.coverage_reason}."


def render_report(result: ProbeResult, run_date: date, persisted_path: str | None) -> str:
    selected_name = result.selected.strategy if result.selected is not None else "NONE"
    selected_history = result.selected.history if result.selected is not None else pd.DataFrame()
    lines = [
        "# VNINDEX benchmark-history probe",
        "",
        f"Run date: `{run_date.isoformat()}`.",
        "",
        "This probe uses the same VnstockClient -> VCI Quote.history path as `build_forward_test_snapshot.py`, makes no performance calculation, and does not fill missing sessions.",
        "",
        "## Strategy i — one request for 2019-01-01 to 2026-07-24",
        "",
        _table([result.single_range]),
        "",
        "## Strategy ii — one request per calendar year, concatenated",
        "",
        _table(list(result.yearly_records)),
        "",
        "Combined strategy ii result:",
        "",
        _table([result.yearly_combined]),
        "",
        "## Strategy iii — one 1900-01-01 request, reporting returned depth without retrying",
        "",
        _table([result.widest_range]),
        "",
        "## Selected series and calendar-year session counts",
        "",
        f"- Selected strategy: `{selected_name}`.",
        f"- Selected series session count: `{len(selected_history)}`.",
        "",
        "| calendar year | session count | below 200 |",
        "|---:|---:|---|",
    ]
    lines.extend(
        f"| {year} | {count} | {'YES' if count < 200 else 'NO'} |"
        for year, count in result.calendar_year_counts.items()
    )
    lines.extend(
        [
            "",
            "Years below 200 sessions: "
            + ", ".join(str(year) for year, count in result.calendar_year_counts.items() if count < 200)
            + "; 2026 is a partial calendar year ending at 2026-07-24, so its count is not treated as a full-year coverage failure.",
            "",
            "## Committed-value reproduction",
            "",
            "| date | close retrieved | expected committed close | exact match |",
            "|---|---:|---:|---|",
        ]
    )
    lines.extend(
        f"| {target_date} | {result.known_close_values[target_date] or 'MISSING'} | {expected} | "
        f"{'YES' if result.known_close_values[target_date] == expected else 'NO'} |"
        for target_date, expected in KNOWN_CLOSES.items()
    )
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            verdict(result),
            "",
            "## Persistence",
            "",
            (
                f"Data file written: `{persisted_path}`."
                if persisted_path is not None
                else "No data file was written because the coverage-and-committed-close requirement was not met."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_benchmark_daily_close(history: pd.DataFrame, output_path: Path, run_date: date) -> None:
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite benchmark data file: {output_path}")
    output = history.copy()
    output.insert(0, "ticker", BENCHMARK_TICKER)
    output["close_adjusted_unit"] = INDEX_UNIT
    output["source"] = PRICE_SOURCE
    output["as_of"] = run_date.isoformat()
    output["data_status"] = "OK"
    output = output.loc[:, OUTPUT_COLUMNS].sort_values(["ticker", "date"], kind="stable")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(
        output_path,
        index=False,
        lineterminator="\n",
        compression={"method": "gzip", "compresslevel": 6, "mtime": 0},
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--run-date", type=date.fromisoformat, default=date.today())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    result = run_probe(LiveVciBenchmarkHistoryClient())
    persisted_path: Path | None = None
    if result.coverage_usable and result.selected is not None:
        persisted_path = repo_root / "data" / "price_history" / args.run_date.isoformat() / "benchmark_daily_close.csv.gz"
        write_benchmark_daily_close(result.selected.history, persisted_path, args.run_date)
    report_path = repo_root / "docs" / "PROBE_BENCHMARK_HISTORY.md"
    report_path.write_text(
        render_report(
            result,
            args.run_date,
            persisted_path.relative_to(repo_root).as_posix() if persisted_path is not None else None,
        ),
        encoding="utf-8",
        newline="\n",
    )
    for record in (result.single_range, result.yearly_combined, result.widest_range):
        print(
            f"STRATEGY_{record.strategy}=start:{record.requested_start};end:{record.requested_end};"
            f"earliest:{record.earliest_session or 'EMPTY'};latest:{record.latest_session or 'EMPTY'};"
            f"sessions:{record.session_count};error:{record.error or 'NONE'}"
        )
    for target_date in KNOWN_CLOSES:
        print(f"VNINDEX_CLOSE_{target_date}={result.known_close_values[target_date] or 'MISSING'}")
    print(f"VERDICT={verdict(result)}")
    print(
        "DATA_FILE="
        + (persisted_path.relative_to(repo_root).as_posix() if persisted_path is not None else "NOT_WRITTEN")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
