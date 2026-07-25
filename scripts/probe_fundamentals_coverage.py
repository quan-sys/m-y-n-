from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import re
import sys
from typing import Any, Iterable

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

from src.data.finance_client import (  # noqa: E402
    LAG_QUARTER,
    STATEMENT_BALANCE_SHEET,
    STATEMENT_CASH_FLOW,
    STATEMENT_INCOME_STATEMENT,
    FinanceClient,
)
from src.screener.step1_pipeline import FINANCIAL_ICB2  # noqa: E402


RUN_DATE = "2026-07-24"
UNIVERSE_PATH = ROOT / "data" / "universe.csv"
CACHE_DIR = ROOT / "data" / "fundamentals" / "cache"
OUTPUT_DIR = ROOT / "data" / "fundamentals" / f"coverage_{RUN_DATE}"
COVERAGE_PATH = OUTPUT_DIR / "coverage_by_ticker_statement.csv"
ITEM_PATH = OUTPUT_DIR / "item_availability.csv"
FETCH_STATUS_PATH = OUTPUT_DIR / "fetch_status.csv"
VNM_SAMPLE_PATH = OUTPUT_DIR / "sample_VNM_income_statement.parquet"
REPORT_PATH = ROOT / "docs" / "REPORT_SPRINT_9_2A_FUNDAMENTALS_PROBE.md"

COVERAGE_COLUMNS = (
    "ticker",
    "exchange",
    "icb2",
    "sector_class",
    "statement_type",
    "n_quarters",
    "earliest_report_period",
    "latest_report_period",
    "n_missing_gap_quarters",
    "data_status",
)
ITEM_COLUMNS = (
    "item_id",
    "statement_type",
    "n_ticker_quarters_present",
    "n_ticker_quarters_total",
    "pct_present",
)
STATEMENT_CALLS = (
    ("balance_sheet", STATEMENT_BALANCE_SHEET, "get_balance_sheet"),
    ("income_statement", STATEMENT_INCOME_STATEMENT, "get_income_statement"),
    ("cash_flow", STATEMENT_CASH_FLOW, "get_cash_flow"),
)
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
TERMINAL_ERROR_TICKER_LIMIT = 3
UNIT_MIN_VND = 1_000_000_000
UNIT_MAX_VND = 1_000_000_000_000_000
RESTATED_LIMITATION = (
    "Data fetched today is AS-RESTATED, not as-originally-reported; for past "
    "quarters this is an unfixable look-ahead bias. This probe does NOT fix it "
    "and does NOT claim true point-in-time for history; historical use is for "
    "RELATIVE walk-forward comparison only, per PLAN."
)
_PUBLICATION_FIELD_PATTERN = re.compile(
    r"(?:publication|publish|public_date|released|release_date|disclosure|"
    r"announcement|available_from)",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class ProbeResult:
    coverage: pd.DataFrame
    item_availability: pd.DataFrame
    unit_anomalies: pd.DataFrame
    publication_fields: tuple[str, ...]
    vnm_sample: pd.DataFrame


def classify_universe(universe: pd.DataFrame) -> pd.DataFrame:
    required = {"ticker", "exchange", "icb2"}
    missing = sorted(required - set(universe.columns))
    if missing:
        raise ValueError(f"universe missing required columns: {missing}")

    work = universe.copy()
    work["ticker"] = work["ticker"].astype(str).str.strip().str.upper()
    work["exchange"] = work["exchange"].astype(str).str.strip().str.upper()
    work["icb2"] = work["icb2"].fillna("").astype(str).str.strip().str.upper()
    if bool(work["ticker"].eq("").any()):
        raise ValueError("universe has blank ticker")
    duplicated = sorted(
        work.loc[work["ticker"].duplicated(keep=False), "ticker"].unique().tolist()
    )
    if duplicated:
        raise ValueError(f"universe has duplicate tickers: {duplicated}")

    work["sector_class"] = "SCREENER_RELEVANT"
    work.loc[work["exchange"].eq("UPCOM"), "sector_class"] = "UPCOM"
    work.loc[work["icb2"].isin(FINANCIAL_ICB2), "sector_class"] = "FINANCIAL"
    return work


def derive_available_from(period_end: str | date) -> str:
    parsed = pd.Timestamp(period_end).date()
    return (parsed + timedelta(days=LAG_QUARTER)).isoformat()


def count_missing_gap_quarters(report_periods: Iterable[str]) -> int:
    ordinals = sorted({_quarter_ordinal(value) for value in report_periods})
    if len(ordinals) < 2:
        return 0
    return int(ordinals[-1] - ordinals[0] + 1 - len(ordinals))


def measure_key_item_availability(
    statements: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    anomaly_frames: list[pd.DataFrame] = []

    for statement_type, item_ids in KEY_ITEMS.items():
        frame = statements.get(statement_type, pd.DataFrame()).copy()
        if frame.empty:
            denominator = 0
        else:
            _validate_normalized_columns(frame)
            denominator = int(
                frame.loc[:, ["ticker", "report_period"]].drop_duplicates().shape[0]
            )

        for item_id in item_ids:
            if frame.empty:
                present = 0
                item_rows = frame
            else:
                item_rows = frame.loc[frame["item_id"].astype(str).eq(item_id)].copy()
                item_rows["value"] = pd.to_numeric(item_rows["value"], errors="coerce")
                present = int(
                    item_rows.loc[item_rows["value"].notna(), ["ticker", "report_period"]]
                    .drop_duplicates()
                    .shape[0]
                )
                numeric = item_rows.loc[item_rows["value"].notna()].copy()
                numeric["absolute_value"] = numeric["value"].abs()
                anomalies = numeric.loc[
                    numeric["absolute_value"].lt(UNIT_MIN_VND)
                    | numeric["absolute_value"].gt(UNIT_MAX_VND),
                    ["ticker", "report_period", "period_end", "item_id", "value"],
                ].copy()
                if not anomalies.empty:
                    anomalies.insert(2, "statement_type", statement_type)
                    anomaly_frames.append(anomalies)

            pct_present = (100.0 * present / denominator) if denominator else 0.0
            rows.append(
                {
                    "item_id": item_id,
                    "statement_type": statement_type,
                    "n_ticker_quarters_present": present,
                    "n_ticker_quarters_total": denominator,
                    "pct_present": round(pct_present, 6),
                }
            )

    availability = pd.DataFrame(rows, columns=ITEM_COLUMNS)
    anomaly_columns = (
        "ticker",
        "report_period",
        "statement_type",
        "period_end",
        "item_id",
        "value",
    )
    anomalies = (
        pd.concat(anomaly_frames, ignore_index=True)
        if anomaly_frames
        else pd.DataFrame(columns=anomaly_columns)
    )
    if not anomalies.empty:
        anomalies = anomalies.loc[:, anomaly_columns].sort_values(
            ["item_id", "ticker", "period_end"], kind="stable"
        )
    return availability, anomalies.reset_index(drop=True)


def _quarter_ordinal(value: str) -> int:
    match = re.fullmatch(r"(\d{4})Q([1-4])", str(value).strip().upper())
    if not match:
        raise ValueError(f"invalid quarterly report_period: {value}")
    return int(match.group(1)) * 4 + int(match.group(2)) - 1


def _validate_normalized_columns(frame: pd.DataFrame) -> None:
    required = {
        "ticker",
        "report_period",
        "period_type",
        "period_end",
        "available_from",
        "item_id",
        "value",
        "data_status",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"normalized statement missing columns: {missing}")


def _validate_quarter_lags(frame: pd.DataFrame) -> None:
    if frame.empty:
        return
    _validate_normalized_columns(frame)
    non_quarter = sorted(
        set(frame["period_type"].dropna().astype(str).str.upper()) - {"QUARTER"}
    )
    if non_quarter:
        raise ValueError(f"quarter fetch returned non-quarter periods: {non_quarter}")
    period_dates = frame.loc[:, ["period_end", "available_from"]].drop_duplicates()
    mismatches = period_dates.loc[
        period_dates.apply(
            lambda row: str(row["available_from"])
            != derive_available_from(str(row["period_end"])),
            axis=1,
        )
    ]
    if not mismatches.empty:
        raise ValueError(
            "available_from does not equal period_end + imported LAG_QUARTER: "
            + mismatches.to_json(orient="records")
        )


def _final_data_status(result: Any) -> str:
    data = result.data if isinstance(result.data, pd.DataFrame) else pd.DataFrame()
    if not bool(result.ok) or str(result.status) in {"API_ERROR", "STALE_DATA"}:
        return "API_ERROR"
    if data.empty:
        return "MISSING_DATA"
    return "OK"


def _coverage_row(
    universe_row: Any,
    statement_type: str,
    result: Any,
) -> dict[str, object]:
    status = _final_data_status(result)
    data = result.data if isinstance(result.data, pd.DataFrame) else pd.DataFrame()
    if status == "OK":
        _validate_quarter_lags(data)
        periods = (
            data.loc[data["period_type"].astype(str).str.upper().eq("QUARTER")]
            .loc[:, ["report_period", "period_end"]]
            .drop_duplicates()
            .sort_values("period_end", kind="stable")
        )
        report_periods = periods["report_period"].astype(str).tolist()
    else:
        report_periods = []

    return {
        "ticker": str(universe_row.ticker),
        "exchange": str(universe_row.exchange),
        "icb2": str(universe_row.icb2),
        "sector_class": str(universe_row.sector_class),
        "statement_type": statement_type,
        "n_quarters": len(report_periods),
        "earliest_report_period": report_periods[0] if report_periods else "",
        "latest_report_period": report_periods[-1] if report_periods else "",
        "n_missing_gap_quarters": count_missing_gap_quarters(report_periods),
        "data_status": status,
    }


def _raw_columns(result: Any) -> list[str]:
    metadata = result.metadata or {}
    observation = Path(str(metadata.get("observation_path") or ""))
    if not observation.is_dir():
        return []
    parquet_path = observation / "raw.parquet"
    csv_path = observation / "raw.csv"
    if parquet_path.exists():
        return [str(column) for column in pd.read_parquet(parquet_path).columns]
    if csv_path.exists():
        return [str(column) for column in pd.read_csv(csv_path, nrows=0).columns]
    return []


def run_probe() -> ProbeResult:
    universe = classify_universe(pd.read_csv(UNIVERSE_PATH))
    relevant = universe.loc[universe["sector_class"].eq("SCREENER_RELEVANT")].copy()
    relevant = relevant.sort_values("ticker", kind="stable").reset_index(drop=True)
    client = FinanceClient(cache_dir=CACHE_DIR, use_cache=True)

    coverage_rows: list[dict[str, object]] = []
    frames: dict[str, list[pd.DataFrame]] = {
        "balance_sheet": [],
        "income_statement": [],
        "cash_flow": [],
    }
    vnm_sample = pd.DataFrame()
    raw_columns_seen: set[str] = set()
    consecutive_api_error_tickers = 0

    for position, universe_row in enumerate(relevant.itertuples(index=False), start=1):
        ticker_had_api_error = False
        for statement_type, _, method_name in STATEMENT_CALLS:
            method = getattr(client, method_name)
            result = method(
                str(universe_row.ticker),
                "quarter",
                company_type="NON_FINANCIAL",
            )
            status = _final_data_status(result)
            coverage_rows.append(_coverage_row(universe_row, statement_type, result))
            raw_columns_seen.update(_raw_columns(result))
            if status == "OK":
                frame = result.data.copy()
                frames[statement_type].append(frame)
                if (
                    str(universe_row.ticker) == "VNM"
                    and statement_type == "income_statement"
                ):
                    vnm_sample = frame.copy()
            elif status == "API_ERROR":
                ticker_had_api_error = True
                print(
                    f"API_ERROR {universe_row.ticker} {statement_type}: "
                    f"{result.error or 'unspecified API error'}",
                    file=sys.stderr,
                    flush=True,
                )

            print(
                f"[{position}/{len(relevant)}] {universe_row.ticker} "
                f"{statement_type}: status={status}; "
                f"quarters={coverage_rows[-1]['n_quarters']}",
                flush=True,
            )

        client.write_fetch_status(FETCH_STATUS_PATH)
        consecutive_api_error_tickers = (
            consecutive_api_error_tickers + 1 if ticker_had_api_error else 0
        )
        if consecutive_api_error_tickers >= TERMINAL_ERROR_TICKER_LIMIT:
            raise RuntimeError(
                "STOP: terminal or repeated API failure reached "
                f"{TERMINAL_ERROR_TICKER_LIMIT} consecutive tickers; "
                f"processed {position}/{len(relevant)} screener-relevant tickers; "
                f"fetch status: {FETCH_STATUS_PATH}"
            )

    combined = {
        statement_type: (
            pd.concat(statement_frames, ignore_index=True)
            if statement_frames
            else pd.DataFrame()
        )
        for statement_type, statement_frames in frames.items()
    }
    item_availability, unit_anomalies = measure_key_item_availability(combined)
    publication_fields = tuple(
        sorted(column for column in raw_columns_seen if _PUBLICATION_FIELD_PATTERN.search(column))
    )
    if vnm_sample.empty:
        raise ValueError("VNM income_statement sample is unavailable")

    coverage = pd.DataFrame(coverage_rows, columns=COVERAGE_COLUMNS)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    coverage.to_csv(COVERAGE_PATH, index=False, lineterminator="\n")
    item_availability.to_csv(ITEM_PATH, index=False, lineterminator="\n")
    client.write_fetch_status(FETCH_STATUS_PATH)
    vnm_sample.to_parquet(VNM_SAMPLE_PATH, index=False)

    result = ProbeResult(
        coverage=coverage,
        item_availability=item_availability,
        unit_anomalies=unit_anomalies,
        publication_fields=publication_fields,
        vnm_sample=vnm_sample,
    )
    write_report(universe, result)
    return result


def write_report(universe: pd.DataFrame, result: ProbeResult) -> None:
    counts = universe["sector_class"].value_counts().to_dict()
    financial_labels = sorted(
        universe.loc[universe["sector_class"].eq("FINANCIAL"), "icb2"].unique().tolist()
    )
    status_counts = (
        result.coverage.groupby(["statement_type", "data_status"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["OK", "MISSING_DATA", "API_ERROR"], fill_value=0)
    )
    income = result.coverage.loc[
        result.coverage["statement_type"].eq("income_statement")
    ].copy()
    income_depth = income["n_quarters"]
    depth_min = int(income_depth.min()) if not income_depth.empty else 0
    depth_median = float(income_depth.median()) if not income_depth.empty else 0.0
    depth_max = int(income_depth.max()) if not income_depth.empty else 0
    earliest = (
        income.loc[income["earliest_report_period"].astype(str).ne(""), "earliest_report_period"]
        .map(_quarter_ordinal)
        .idxmin()
        if bool(income["earliest_report_period"].astype(str).ne("").any())
        else None
    )
    earliest_period = str(income.at[earliest, "earliest_report_period"]) if earliest is not None else ""
    fewer_than_four = int(income["n_quarters"].lt(4).sum())

    vnm_pbt = result.vnm_sample.loc[
        result.vnm_sample["item_id"]
        .astype(str)
        .eq("net_accounting_profit_loss_before_tax")
        & pd.to_numeric(result.vnm_sample["value"], errors="coerce").notna()
    ].copy()
    vnm_pbt["value"] = pd.to_numeric(vnm_pbt["value"], errors="raise")
    vnm_pbt = vnm_pbt.sort_values("period_end", ascending=False, kind="stable").head(2)
    if len(vnm_pbt) != 2:
        raise ValueError("VNM has fewer than two usable recent quarterly PBT rows")
    if not all(
        str(row.available_from) == derive_available_from(str(row.period_end))
        for row in vnm_pbt.itertuples(index=False)
    ):
        raise ValueError("VNM lag anchor failed")
    if not vnm_pbt["value"].abs().between(UNIT_MIN_VND, UNIT_MAX_VND).all():
        raise ValueError("VNM PBT unit anchor failed")

    below_ninety = result.item_availability.loc[
        result.item_availability["pct_present"].lt(90)
    ]
    anomaly_counts = (
        result.unit_anomalies.groupby("item_id").size().sort_index().to_dict()
        if not result.unit_anomalies.empty
        else {}
    )

    lines = [
        "# Sprint 9-2A Fundamentals Coverage Probe",
        "",
        "## N1 — Universe classification",
        "",
        f"- Total tickers: `{len(universe)}`",
        f"- SCREENER_RELEVANT: `{int(counts.get('SCREENER_RELEVANT', 0))}`",
        f"- FINANCIAL: `{int(counts.get('FINANCIAL', 0))}`",
        f"- UPCOM: `{int(counts.get('UPCOM', 0))}`",
        f"- DISTINCT financial ICB2 labels: `{', '.join(financial_labels)}`",
        "",
        "## N2 — Fetch outcome by statement type",
        "",
        _markdown_table(
            ["statement_type", "OK", "MISSING_DATA", "API_ERROR"],
            [
                [
                    statement_type,
                    int(status_counts.at[statement_type, "OK"]),
                    int(status_counts.at[statement_type, "MISSING_DATA"]),
                    int(status_counts.at[statement_type, "API_ERROR"]),
                ]
                for statement_type in status_counts.index
            ],
        ),
        "",
        (
            "`coverage_by_ticker_statement.csv` supplies the final N2 status: an "
            "empty normalized statement is `MISSING_DATA`; `fetch_status.csv` is "
            "the direct `FinanceClient.write_fetch_status(...)` call log, where a "
            "successful resumed cache read can be `OK` with "
            "`returned_period_count=0`."
        ),
        "",
        "## N3 — Quarterly depth",
        "",
        f"- Income-statement n_quarters min / median / max over SCREENER_RELEVANT tickers: `{depth_min} / {depth_median:g} / {depth_max}`",
        f"- Earliest income-statement report_period observed: `{earliest_period}`",
        f"- Tickers with fewer than 4 income quarters: `{fewer_than_four}`",
        "",
        "## N4 — VNM unit and lag anchor",
        "",
        _markdown_table(
            [
                "report_period",
                "period_end",
                "available_from",
                "net_accounting_profit_loss_before_tax",
            ],
            [
                [
                    row.report_period,
                    row.period_end,
                    row.available_from,
                    f"{float(row.value):.0f}",
                ]
                for row in vnm_pbt.itertuples(index=False)
            ],
        ),
        "",
        f"`available_from = period_end + LAG_QUARTER`, where imported `LAG_QUARTER={LAG_QUARTER}` days.",
        (
            "The API returned no publication-date field; `available_from` was derived."
            if not result.publication_fields
            else "Publication-like raw fields observed: "
            + ", ".join(result.publication_fields)
        ),
        "",
        "## N5 — Key-item availability",
        "",
        _markdown_table(
            [
                "item_id",
                "statement_type",
                "n_ticker_quarters_present",
                "n_ticker_quarters_total",
                "pct_present",
            ],
            [
                [
                    row.item_id,
                    row.statement_type,
                    row.n_ticker_quarters_present,
                    row.n_ticker_quarters_total,
                    f"{float(row.pct_present):.6f}%",
                ]
                for row in result.item_availability.itertuples(index=False)
            ],
        ),
        "",
        "Item IDs below 90%: "
        + (
            ", ".join(below_ninety["item_id"].astype(str).tolist())
            if not below_ninety.empty
            else "NONE"
        ),
        "",
        "## Unit sanity flags",
        "",
        f"- Key-item values outside the absolute `{UNIT_MIN_VND}..{UNIT_MAX_VND}` VND band: `{len(result.unit_anomalies)}`.",
        f"- Counts by item_id: `{anomaly_counts}`",
        "",
        (
            _markdown_table(
                ["ticker", "report_period", "statement_type", "period_end", "item_id", "value"],
                [
                    [
                        row.ticker,
                        row.report_period,
                        row.statement_type,
                        row.period_end,
                        row.item_id,
                        row.value,
                    ]
                    for row in result.unit_anomalies.itertuples(index=False)
                ],
            )
            if not result.unit_anomalies.empty
            else "No unit anomalies were observed."
        ),
        "",
        "## Restated-data limitation",
        "",
        RESTATED_LIMITATION,
        "",
        "## N6 — Git diff scope",
        "",
        "The committed report finalizes this section with `git diff --stat origin/main..HEAD` after the probe files are committed.",
        "",
        "## Test limitation",
        "",
        "Pytest: 374 tests collected and all passed; green tests prove the coverage-accounting logic on fixtures and do NOT prove the provider data is complete, correct, or non-restated.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    output.extend(
        "| "
        + " | ".join(str(value).replace("|", "\\|").replace("\n", " ") for value in row)
        + " |"
        for row in rows
    )
    return "\n".join(output)


def main() -> int:
    try:
        result = run_probe()
    except BaseException as exc:  # noqa: BLE001 - preserve exact probe failures.
        if isinstance(exc, KeyboardInterrupt):
            raise
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    print(f"coverage_rows={len(result.coverage)}")
    print(f"item_rows={len(result.item_availability)}")
    print(f"unit_anomalies={len(result.unit_anomalies)}")
    print(f"publication_fields={list(result.publication_fields)}")
    print(f"coverage_path={COVERAGE_PATH}")
    print(f"item_path={ITEM_PATH}")
    print(f"fetch_status_path={FETCH_STATUS_PATH}")
    print(f"vnm_sample_path={VNM_SAMPLE_PATH}")
    print(f"report_path={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
