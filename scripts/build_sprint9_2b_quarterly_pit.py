from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable
from zoneinfo import ZoneInfo

import pandas as pd


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.probe_fundamentals_coverage import classify_universe  # noqa: E402
from src.data.finance_client import (  # noqa: E402
    LAG_QUARTER,
    NORMALIZED_COLUMNS,
    FinanceClient,
)


TIME_ZONE = ZoneInfo("Asia/Ho_Chi_Minh")
UNIVERSE_PATH = ROOT / "data" / "universe.csv"
REPORT_PATH = ROOT / "docs" / "REPORT_SPRINT_9_2B_QUARTERLY_PIT.md"
RUN_STATE_ROOT = ROOT / "data" / "fundamentals" / "run_state"
OUTPUT_ROOT = ROOT / "data" / "fundamentals" / "quarterly_pit"
EXPECTED_TICKER_COUNT = 243
MAX_API_ERROR_SHARE = 0.05
UNIT_MIN_VND = 1_000_000_000
UNIT_MAX_VND = 1_000_000_000_000_000

OUTPUT_COLUMNS = (
    "ticker",
    "quarter",
    "period_end",
    "available_from",
    "statement_type",
    "item_id",
    "value",
    "currency",
    "source",
    "as_of",
    "data_status",
)
STATEMENTS = ("balance_sheet", "income_statement", "cash_flow")
STATEMENT_METHODS = {
    "balance_sheet": FinanceClient.get_balance_sheet,
    "income_statement": FinanceClient.get_income_statement,
    "cash_flow": FinanceClient.get_cash_flow,
}
KEY_ITEMS = {
    "income_statement": (
        "net_accounting_profit_loss_before_tax",
        "interest_expenses",
        "financial_expenses",
        "attributable_to_parent_company",
    ),
    "balance_sheet": (
        "short_term_borrowings",
        "long_term_borrowings",
        "cash_and_cash_equivalents",
        "minority_interests",
    ),
}
ALL_KEY_ITEMS = tuple(
    item_id
    for statement in ("income_statement", "balance_sheet")
    for item_id in KEY_ITEMS[statement]
)
RESTATED_LIMITATION = """Data fetched today is AS-RESTATED, not as-originally-
reported. For past quarters this is an unfixable look-ahead bias that `available_from` does NOT
remove: the DATE the number became public is modelled, but the VALUE is today's restated value.
This table is therefore QUASI point-in-time and is valid for RELATIVE walk-forward comparison only."""


def derive_available_from(period_end: str | date) -> str:
    parsed = pd.Timestamp(period_end).date()
    return (parsed + timedelta(days=LAG_QUARTER)).isoformat()


def quarter_ordinal(value: str) -> int:
    match = re.fullmatch(r"(\d{4})Q([1-4])", normalize_quarter(value))
    if not match:
        raise ValueError(f"invalid quarter: {value}")
    return int(match.group(1)) * 4 + int(match.group(2)) - 1


def quarter_from_ordinal(value: int) -> str:
    year, zero_based_quarter = divmod(value, 4)
    return f"{year}Q{zero_based_quarter + 1}"


def normalize_quarter(value: str) -> str:
    return str(value).strip().upper().replace("-", "")


def internal_gap_quarters(quarters: Iterable[str]) -> list[str]:
    ordinals = sorted({quarter_ordinal(value) for value in quarters})
    if len(ordinals) < 2:
        return []
    observed = set(ordinals)
    return [
        quarter_from_ordinal(value)
        for value in range(ordinals[0], ordinals[-1] + 1)
        if value not in observed
    ]


def select_key_item_rows(
    statement_frames: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    selected: list[pd.DataFrame] = []
    for statement_name, item_ids in KEY_ITEMS.items():
        frame = statement_frames.get(statement_name, pd.DataFrame())
        if frame.empty:
            continue
        missing = sorted(set(NORMALIZED_COLUMNS) - set(frame.columns))
        if missing:
            raise ValueError(
                f"{statement_name} normalized cache missing columns: {missing}"
            )
        rows = frame.loc[frame["item_id"].astype(str).isin(item_ids)].copy()
        if not rows.empty:
            selected.append(rows)

    if not selected:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    combined = pd.concat(selected, ignore_index=True)
    combined["quarter"] = combined["report_period"].map(normalize_quarter)
    combined["statement_type"] = combined["statement_type"].astype(str).str.upper()
    output = combined.rename(columns={"report_period": "_report_period"}).loc[
        :, OUTPUT_COLUMNS
    ]
    output = output.sort_values(
        ["ticker", "quarter", "item_id"], kind="stable"
    ).reset_index(drop=True)
    duplicated = output.duplicated(["ticker", "quarter", "item_id"], keep=False)
    if bool(duplicated.any()):
        keys = output.loc[
            duplicated, ["ticker", "quarter", "item_id"]
        ].drop_duplicates()
        raise ValueError(
            "duplicate output keys: " + keys.to_json(orient="records")
        )
    return output


def _run_paths(run_date: str) -> dict[str, Path]:
    run_root = RUN_STATE_ROOT / run_date
    return {
        "run_root": run_root,
        "normalized": run_root / "normalized",
        "status": run_root / "status",
        "finance_cache": run_root / "finance_cache",
        "output": OUTPUT_ROOT
        / run_date
        / "quarterly_items_point_in_time.csv.gz",
    }


def _statement_path(paths: dict[str, Path], ticker: str, statement: str) -> Path:
    return paths["normalized"] / ticker / f"{statement}.parquet"


def _status_path(paths: dict[str, Path], ticker: str, statement: str) -> Path:
    return paths["status"] / ticker / f"{statement}.json"


def _write_parquet_atomic(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.parquet")
    frame.to_parquet(temporary, index=False)
    temporary.replace(path)


def _write_json_atomic(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.json")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.replace(path)


def _effective_status(result: Any) -> str:
    metadata = result.metadata or {}
    return str(metadata.get("data_status") or result.status)


def _status_record(
    ticker: str,
    statement: str,
    result: Any,
    frame: pd.DataFrame,
) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "statement": statement,
        "data_status": _effective_status(result),
        "ok": bool(result.ok),
        "error": str(result.error or ""),
        "source": str(result.source or ""),
        "as_of": str(result.as_of or ""),
        "n_quarters": (
            int(frame["report_period"].astype(str).map(normalize_quarter).nunique())
            if not frame.empty
            else 0
        ),
        "cache_state": str((result.metadata or {}).get("cache_state") or ""),
    }


def relevant_tickers() -> list[str]:
    universe = classify_universe(pd.read_csv(UNIVERSE_PATH))
    tickers = sorted(
        universe.loc[
            universe["sector_class"].eq("SCREENER_RELEVANT"), "ticker"
        ]
        .astype(str)
        .tolist()
    )
    if len(tickers) != EXPECTED_TICKER_COUNT:
        raise ValueError(
            f"expected {EXPECTED_TICKER_COUNT} SCREENER_RELEVANT tickers, got {len(tickers)}"
        )
    if "VNM" not in tickers:
        raise ValueError("VNM is missing from the SCREENER_RELEVANT universe")
    return tickers


def _load_status(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_statement_cache(
    paths: dict[str, Path], ticker: str, statement: str
) -> tuple[pd.DataFrame, dict[str, Any]]:
    frame_path = _statement_path(paths, ticker, statement)
    status_path = _status_path(paths, ticker, statement)
    if not frame_path.exists() or not status_path.exists():
        raise FileNotFoundError(
            f"incomplete run-state cache for {ticker} {statement}: "
            f"{frame_path} / {status_path}"
        )
    return pd.read_parquet(frame_path), _load_status(status_path)


def fetch_all(tickers: list[str], paths: dict[str, Path]) -> None:
    client = FinanceClient(cache_dir=paths["finance_cache"], use_cache=True)
    fetch_order = ["VNM", *[ticker for ticker in tickers if ticker != "VNM"]]

    for position, ticker in enumerate(fetch_order, start=1):
        for statement in STATEMENTS:
            frame_path = _statement_path(paths, ticker, statement)
            status_path = _status_path(paths, ticker, statement)
            if frame_path.exists() and status_path.exists():
                cached = pd.read_parquet(frame_path)
                cached_status = _load_status(status_path)
                print(
                    f"[{position}/{len(tickers)}] {ticker} {statement}: "
                    f"RESUME status={cached_status['data_status']}; "
                    f"quarters={cached_status['n_quarters']}",
                    flush=True,
                )
                frame = cached
                status = cached_status
            else:
                method = STATEMENT_METHODS[statement]
                result = method(
                    client,
                    ticker,
                    "quarter",
                    company_type="NON_FINANCIAL",
                )
                frame = (
                    result.data.copy()
                    if isinstance(result.data, pd.DataFrame)
                    else pd.DataFrame(columns=NORMALIZED_COLUMNS)
                )
                if frame.empty:
                    frame = pd.DataFrame(columns=NORMALIZED_COLUMNS)
                status = _status_record(ticker, statement, result, frame)
                _write_parquet_atomic(frame, frame_path)
                _write_json_atomic(status, status_path)
                print(
                    f"[{position}/{len(tickers)}] {ticker} {statement}: "
                    f"status={status['data_status']}; "
                    f"quarters={status['n_quarters']}; "
                    f"cache_state={status['cache_state']}",
                    flush=True,
                )

            if ticker == "VNM" and statement == "income_statement":
                n_quarters = (
                    int(
                        frame["report_period"]
                        .astype(str)
                        .map(normalize_quarter)
                        .nunique()
                    )
                    if not frame.empty
                    else 0
                )
                if n_quarters < 12:
                    raise RuntimeError(
                        "STOP: VNM income_statement returned fewer than 12 quarters: "
                        f"{n_quarters}"
                    )


def load_run_state(
    tickers: list[str], paths: dict[str, Path]
) -> tuple[dict[str, dict[str, pd.DataFrame]], list[dict[str, Any]]]:
    frames: dict[str, dict[str, pd.DataFrame]] = {}
    statuses: list[dict[str, Any]] = []
    for ticker in tickers:
        frames[ticker] = {}
        for statement in STATEMENTS:
            frame, status = _load_statement_cache(paths, ticker, statement)
            frames[ticker][statement] = frame
            statuses.append(status)
    return frames, statuses


def assemble_output(
    tickers: list[str],
    frames: dict[str, dict[str, pd.DataFrame]],
) -> pd.DataFrame:
    ticker_frames = [
        select_key_item_rows(frames[ticker])
        for ticker in tickers
    ]
    non_empty = [frame for frame in ticker_frames if not frame.empty]
    output = (
        pd.concat(non_empty, ignore_index=True)
        if non_empty
        else pd.DataFrame(columns=OUTPUT_COLUMNS)
    )
    output = output.loc[:, OUTPUT_COLUMNS].sort_values(
        ["ticker", "quarter", "item_id"], kind="stable"
    ).reset_index(drop=True)
    return output


def validate_stop_gates(
    output: pd.DataFrame,
    tickers: list[str],
    statuses: list[dict[str, Any]],
    frames: dict[str, dict[str, pd.DataFrame]],
) -> None:
    vnm_income = frames["VNM"]["income_statement"]
    vnm_quarters = (
        int(vnm_income["report_period"].astype(str).map(normalize_quarter).nunique())
        if not vnm_income.empty
        else 0
    )
    if vnm_quarters < 12:
        raise RuntimeError(
            f"STOP: VNM income_statement returned fewer than 12 quarters: {vnm_quarters}"
        )

    api_error_tickers = sorted(
        {
            str(record["ticker"])
            for record in statuses
            if str(record["data_status"]) == "API_ERROR"
        }
    )
    if len(api_error_tickers) / len(tickers) > MAX_API_ERROR_SHARE:
        raise RuntimeError(
            "STOP: more than 5 percent of tickers ended in API_ERROR for at least "
            f"one statement: {len(api_error_tickers)}/{len(tickers)}; "
            f"tickers={api_error_tickers}"
        )

    if output.empty:
        raise RuntimeError("STOP: assembled quarterly output is empty")
    period_end = pd.to_datetime(output["period_end"], errors="raise")
    available_from = pd.to_datetime(output["available_from"], errors="raise")
    invalid = output.loc[
        available_from.le(period_end),
        ["ticker", "quarter", "period_end", "available_from", "item_id"],
    ]
    if not invalid.empty:
        raise RuntimeError(
            "STOP: available_from is on or before period_end: "
            + invalid.to_json(orient="records")
        )


def write_deterministic_gzip_csv(frame: pd.DataFrame, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as binary:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=binary,
            compresslevel=9,
            mtime=0,
        ) as compressed:
            with io.TextIOWrapper(
                compressed, encoding="utf-8", newline=""
            ) as text:
                frame.to_csv(text, index=False, lineterminator="\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend(
        "| "
        + " | ".join(
            str(value).replace("|", "\\|").replace("\n", " ") for value in row
        )
        + " |"
        for row in rows
    )
    return "\n".join(lines)


def _raw_value(value: Any) -> str:
    if pd.isna(value):
        return ""
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return format(number, ".17g")


def _r2_rows(output: pd.DataFrame) -> list[list[Any]]:
    work = output.copy()
    work["calendar_year"] = work["quarter"].str[:4]
    denominator = (
        work.loc[:, ["calendar_year", "ticker", "quarter"]]
        .drop_duplicates()
        .groupby("calendar_year")
        .size()
        .to_dict()
    )
    rows: list[list[Any]] = []
    for item_id in ALL_KEY_ITEMS:
        item_rows = work.loc[
            work["item_id"].eq(item_id) & pd.to_numeric(
                work["value"], errors="coerce"
            ).notna()
        ]
        present = (
            item_rows.loc[:, ["calendar_year", "ticker", "quarter"]]
            .drop_duplicates()
            .groupby("calendar_year")
            .size()
            .to_dict()
        )
        for year in sorted(denominator):
            total = int(denominator[year])
            count = int(present.get(year, 0))
            rows.append(
                [item_id, year, count, total, f"{100.0 * count / total:.6f}%"]
            )
    return rows


def _gap_rows(
    output: pd.DataFrame, tickers: list[str]
) -> list[tuple[str, list[str]]]:
    observed = {
        ticker: output.loc[output["ticker"].eq(ticker), "quarter"].tolist()
        for ticker in tickers
    }
    return [
        (ticker, gaps)
        for ticker in tickers
        if (gaps := internal_gap_quarters(observed[ticker]))
    ]


def _vnm_table(output: pd.DataFrame) -> tuple[list[str], list[list[str]]]:
    vnm = output.loc[output["ticker"].eq("VNM")].copy()
    ordered_quarters = sorted(
        vnm["quarter"].unique().tolist(), key=quarter_ordinal
    )
    selected_quarters = [
        *ordered_quarters[:4],
        *[quarter for quarter in ordered_quarters[-4:] if quarter not in ordered_quarters[:4]],
    ]
    pivot = vnm.pivot(index="item_id", columns="quarter", values="value")
    rows: list[list[str]] = []
    for item_id in ALL_KEY_ITEMS:
        rows.append(
            [
                item_id,
                *[
                    _raw_value(pivot.at[item_id, quarter])
                    if item_id in pivot.index and quarter in pivot.columns
                    else ""
                    for quarter in selected_quarters
                ],
            ]
        )
    return selected_quarters, rows


def write_report(
    *,
    run_date: str,
    output: pd.DataFrame,
    output_path: Path,
    sha256: str,
    tickers: list[str],
    statuses: list[dict[str, Any]],
) -> None:
    depth = (
        output.loc[:, ["ticker", "quarter"]]
        .drop_duplicates()
        .groupby("ticker")
        .size()
        .reindex(tickers, fill_value=0)
    )
    earliest = min(output["quarter"].unique(), key=quarter_ordinal)
    latest = max(output["quarter"].unique(), key=quarter_ordinal)
    gaps = _gap_rows(output, tickers)
    ambiguous = sorted(
        (
            str(record["ticker"]),
            str(record["statement"]),
        )
        for record in statuses
        if str(record["data_status"]) == "REQUIRED_ITEM_AMBIGUOUS"
    )
    numeric = pd.to_numeric(output["value"], errors="coerce")
    below = output.loc[numeric.notna() & numeric.abs().lt(UNIT_MIN_VND)].copy()
    above = output.loc[numeric.notna() & numeric.abs().gt(UNIT_MAX_VND)].copy()
    vnm_quarters, vnm_rows = _vnm_table(output)

    lines = [
        "# Sprint 9-2B Quarterly Quasi Point-in-Time Fundamentals",
        "",
        "## Restated-data limitation",
        "",
        *[f"> {line}" for line in RESTATED_LIMITATION.splitlines()],
        "",
        "## R1 — Quarterly depth",
        "",
        f"- Tickers measured: `{len(tickers)}`.",
        f"- Minimum: `{int(depth.min())}`.",
        f"- 25th percentile: `{float(depth.quantile(0.25)):g}`.",
        f"- Median: `{float(depth.median()):g}`.",
        f"- Maximum: `{int(depth.max())}`.",
        f"- Tickers with fewer than 8 quarters: `{int(depth.lt(8).sum())}`.",
        f"- Earliest quarter in the table: `{earliest}`.",
        f"- Latest quarter in the table: `{latest}`.",
        "",
        "## R2 — Item presence by calendar year",
        "",
        "Presence requires a non-null value; the denominator is the distinct ticker-quarters present in the output for that calendar year.",
        "",
        _markdown_table(
            [
                "item_id",
                "calendar_year",
                "present_ticker_quarters",
                "ticker_quarters_in_year",
                "pct_present",
            ],
            _r2_rows(output),
        ),
        "",
        "## R3 — Internal quarter gaps",
        "",
        f"- Tickers with an internal gap: `{len(gaps)}`.",
        "- First 20 tickers and their gap quarters: "
        + (
            "; ".join(
                f"`{ticker}: {','.join(gap_quarters)}`"
                for ticker, gap_quarters in gaps[:20]
            )
            if gaps
            else "NONE"
        ),
        "- An internal gap breaks any 4-quarter TTM window that spans it.",
        "",
        "## R4 — Required-item ambiguity",
        "",
        f"- Ticker-statements with fetch status `REQUIRED_ITEM_AMBIGUOUS`: `{len(ambiguous)}`.",
        "- List: "
        + (
            ", ".join(f"`{ticker}/{statement}`" for ticker, statement in ambiguous)
            if ambiguous
            else "NONE"
        ),
        "",
        "## R5 — Unit buckets",
        "",
        f"- Below 1e9 VND in absolute magnitude (small-cap, informational): `{len(below)}`.",
        f"- Above 1e15 VND in absolute magnitude (genuine anomaly): `{len(above)}`.",
        "",
        (
            _markdown_table(
                ["ticker", "quarter", "item_id", "value"],
                [
                    [
                        row.ticker,
                        row.quarter,
                        row.item_id,
                        _raw_value(row.value),
                    ]
                    for row in above.itertuples(index=False)
                ],
            )
            if not above.empty
            else "Values above 1e15 VND: NONE"
        ),
        "",
        "## R6 — VNM oldest and newest raw values",
        "",
        _markdown_table(
            ["item_id", *vnm_quarters],
            vnm_rows,
        ),
        "",
        "## R7 — Output identity and run date",
        "",
        f"- RUN_DATE: `{run_date}`.",
        f"- Output: `{output_path.relative_to(ROOT).as_posix()}`.",
        f"- Uncompressed row count: `{len(output)}`.",
        f"- SHA-256 of the gzipped file: `{sha256}`.",
        "- Resumption is detected per ticker-statement: an existing normalized parquet file plus its matching status JSON causes that provider call to be skipped; a ticker is complete when all three pairs exist.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Sprint 9-2B quarterly quasi point-in-time fundamentals."
    )
    parser.add_argument("--run-date", help="Asia/Ho_Chi_Minh run date (YYYY-MM-DD).")
    parser.add_argument(
        "--assemble-only",
        action="store_true",
        help="Reassemble from a completed per-ticker cache without provider calls.",
    )
    args = parser.parse_args(argv)
    if args.assemble_only and not args.run_date:
        parser.error("--assemble-only requires --run-date")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_date = args.run_date or datetime.now(TIME_ZONE).date().isoformat()
    print(f"RUN_DATE={run_date}", flush=True)
    paths = _run_paths(run_date)
    tickers = relevant_tickers()

    if not args.assemble_only:
        fetch_all(tickers, paths)

    frames, statuses = load_run_state(tickers, paths)
    output = assemble_output(tickers, frames)
    validate_stop_gates(output, tickers, statuses, frames)
    sha256 = write_deterministic_gzip_csv(output, paths["output"])
    write_report(
        run_date=run_date,
        output=output,
        output_path=paths["output"],
        sha256=sha256,
        tickers=tickers,
        statuses=statuses,
    )
    print(f"SHA256={sha256}")
    print(f"ROW_COUNT={len(output)}")
    print(f"OUTPUT={paths['output']}")
    print(f"REPORT={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
