from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.vnstock_client import VnstockClient  # noqa: E402


FETCH_STATUSES = ("OK", "EMPTY_NO_EVENTS", "FETCH_ERROR", "NOT_ATTEMPTED")
EVENT_CLASSES = (
    "BONUS_OR_STOCK_DIV_COMPLETE",
    "CASH_DIV_COMPLETE",
    "RIGHTS_NO_SUBSCRIPTION_PRICE",
    "MISSING_EXRIGHT_DATE",
    "ZERO_OR_NULL_RATIO",
    "OTHER_UNCLASSIFIED",
)
BLOCKING_CLASSES = (
    "RIGHTS_NO_SUBSCRIPTION_PRICE",
    "MISSING_EXRIGHT_DATE",
    "OTHER_UNCLASSIFIED",
)
PAGE_SIZE = 50
FROM_DATE = "20160101"
ANALYSIS_START_YEAR = 2018
ANALYSIS_END_YEAR = 2025
COVERAGE_COLUMNS = (
    "ticker",
    "fetch_status",
    "fetch_error_class",
    "pages_fetched",
    "provider_rows",
    *EVENT_CLASSES,
    "factor_reconstructable",
)


def read_universe(path: Path) -> list[str]:
    frame = pd.read_csv(path)
    if "ticker" not in frame.columns:
        raise ValueError(f"universe has no ticker column: {path}")
    tickers = [str(value).strip().upper() for value in frame["ticker"] if str(value).strip()]
    if len(tickers) != 378:
        raise ValueError(f"expected 378 universe tickers, found {len(tickers)}")
    if len(tickers) != len(set(tickers)):
        raise ValueError("universe contains duplicate tickers")
    return tickers


def _blank(value: object) -> bool:
    return pd.isna(value) or str(value).strip() == ""


def _number(value: object) -> float | None:
    if _blank(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if pd.notna(number) else None


def classify_event(row: pd.Series | dict[str, object]) -> str:
    values = row if isinstance(row, dict) else row.to_dict()
    event_code = str(values.get("event_code", "")).strip().upper()
    title = " ".join(
        str(values.get(column, "") or "")
        for column in ("event_title_en", "event_title_vi", "event_name_en", "event_name_vi")
    ).lower()
    ratio = _number(values.get("exercise_ratio"))
    cash = _number(values.get("value_per_share"))
    has_exright = not _blank(values.get("exright_date"))

    if event_code == "ISS" and "rights issue" in title and ratio is not None and ratio > 0 and cash is None:
        return "RIGHTS_NO_SUBSCRIPTION_PRICE"
    if ((event_code == "ISS" and ratio is not None and ratio > 0) or
            (event_code == "DIV" and cash is not None and cash > 0)) and not has_exright:
        return "MISSING_EXRIGHT_DATE"
    if event_code == "ISS" and (ratio is None or ratio == 0):
        return "ZERO_OR_NULL_RATIO"
    if (
        event_code == "ISS"
        and ("bonus issue" in title or "stock dividend" in title)
        and ratio is not None
        and ratio > 0
        and has_exright
    ):
        return "BONUS_OR_STOCK_DIV_COMPLETE"
    if event_code == "DIV" and cash is not None and cash > 0 and has_exright:
        return "CASH_DIV_COMPLETE"
    return "OTHER_UNCLASSIFIED"


def effective_year(row: pd.Series | dict[str, object]) -> int | None:
    values = row if isinstance(row, dict) else row.to_dict()
    selected = values.get("exright_date")
    if _blank(selected):
        selected = values.get("public_date")
    timestamp = pd.to_datetime(selected, errors="coerce")
    return None if pd.isna(timestamp) else int(timestamp.year)


def factor_verdict(class_counts: dict[str, int], fetch_status: str) -> str:
    if fetch_status == "EMPTY_NO_EVENTS":
        return "CLEAN"
    return (
        "HAS_BLOCKING_HOLE"
        if any(class_counts.get(name, 0) > 0 for name in BLOCKING_CLASSES)
        else "CLEAN"
    )


def _empty_coverage_row(ticker: str) -> dict[str, object]:
    return {
        "ticker": ticker,
        "fetch_status": "NOT_ATTEMPTED",
        "fetch_error_class": "",
        "pages_fetched": 0,
        "provider_rows": 0,
        **{name: 0 for name in EVENT_CLASSES},
        "factor_reconstructable": "CLEAN",
    }


def load_or_initialize_coverage(path: Path, tickers: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame([_empty_coverage_row(ticker) for ticker in tickers], columns=COVERAGE_COLUMNS)
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = sorted(set(COVERAGE_COLUMNS).difference(frame.columns))
    if missing:
        raise ValueError("existing coverage cache missing columns: " + ", ".join(missing))
    unknown = sorted(set(frame["fetch_status"]).difference(FETCH_STATUSES))
    if unknown:
        raise ValueError("invalid fetch_status values: " + ", ".join(unknown))
    if set(frame["ticker"]) != set(tickers) or len(frame) != len(tickers):
        raise ValueError("existing coverage cache does not match the 378-ticker universe")
    return frame[list(COVERAGE_COLUMNS)]


def load_raw_events(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False) if path.exists() else pd.DataFrame()


def _atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False, lineterminator="\n")
    temporary.replace(path)


def _replace_ticker_raw(raw: pd.DataFrame, ticker: str, rows: pd.DataFrame) -> pd.DataFrame:
    retained = raw[raw["ticker"] != ticker].copy() if "ticker" in raw.columns else pd.DataFrame()
    return pd.concat([retained, rows], ignore_index=True, sort=False)


def _replace_coverage(
    coverage: pd.DataFrame, ticker: str, row: dict[str, object], ticker_order: list[str]
) -> pd.DataFrame:
    updated = coverage.copy()
    updated.loc[updated["ticker"] == ticker, list(row)] = list(row.values())
    order = {value: index for index, value in enumerate(ticker_order)}
    return updated.sort_values("ticker", key=lambda values: values.map(order), kind="stable")


def _call_forced_events_page(
    company: Any,
    client: VnstockClient,
    page: int,
    to_date: str,
) -> pd.DataFrame:
    provider = company.provider
    original = provider._fetch_events

    def forced_fetch_events(*args: Any, **kwargs: Any) -> list[dict[str, object]]:
        return original(
            event_codes="DIV,ISS",
            from_date=FROM_DATE,
            to_date=to_date,
            page=page,
            size=PAGE_SIZE,
        )

    provider._fetch_events = forced_fetch_events
    try:
        client._polite_sleep()
        return client._to_frame(client._quiet_call(company.events))
    finally:
        provider._fetch_events = original


def fetch_ticker_events(
    ticker: str,
    client: VnstockClient,
    to_date: str,
) -> tuple[pd.DataFrame, int, int]:
    vnstock = client._vnstock_module()
    company = client._quiet_call(
        vnstock.Company,
        source="VCI",
        symbol=ticker,
        random_agent=True,
        show_log=False,
    )
    pages: list[pd.DataFrame] = []
    provider_rows = 0
    page = 0
    while True:
        frame = _call_forced_events_page(company, client, page, to_date)
        count = len(frame)
        provider_rows += count
        if count:
            pages.append(frame)
        if count < PAGE_SIZE:
            break
        page += 1
    events = pd.concat(pages, ignore_index=True, sort=False) if pages else pd.DataFrame()
    if events.empty:
        return events, page + 1, provider_rows
    if "event_code" not in events.columns:
        raise ValueError("provider events frame has no event_code column")
    kept = events[events["event_code"].astype(str).str.upper().isin({"ISS", "DIV"})].copy()
    kept["ticker"] = ticker
    kept["event_class"] = kept.apply(classify_event, axis=1)
    kept["effective_year"] = kept.apply(effective_year, axis=1)
    return kept, page + 1, provider_rows


def _coverage_row(
    ticker: str,
    fetch_status: str,
    rows: pd.DataFrame,
    pages_fetched: int,
    provider_rows: int,
    error_class: str = "",
) -> dict[str, object]:
    in_window = rows[rows["effective_year"].between(ANALYSIS_START_YEAR, ANALYSIS_END_YEAR)] if not rows.empty else rows
    counts = {name: int((in_window["event_class"] == name).sum()) if not in_window.empty else 0 for name in EVENT_CLASSES}
    return {
        "ticker": ticker,
        "fetch_status": fetch_status,
        "fetch_error_class": error_class,
        "pages_fetched": pages_fetched,
        "provider_rows": provider_rows,
        **counts,
        "factor_reconstructable": factor_verdict(counts, fetch_status),
    }


def read_clean_basket(repo_root: Path) -> set[str]:
    survivors = pd.read_csv(repo_root / "data" / "screener" / "step1_survivors.csv")
    rejects = pd.read_csv(repo_root / "data" / "screener" / "step1_rejects.csv")
    retained_rejects = rejects[
        ~rejects["reason_label"].isin({"UPCOM_EXCLUDED_V1", "FINANCIAL_SECTOR_EXCLUDED"})
    ]
    tickers = set(survivors["ticker"].astype(str).str.upper())
    tickers.update(retained_rejects["ticker"].astype(str).str.upper())
    if len(tickers) != 243:
        raise ValueError(f"expected clean basket of 243, found {len(tickers)}")
    return tickers


def build_report(
    raw: pd.DataFrame,
    coverage: pd.DataFrame,
    clean_basket: set[str],
    run_date: str,
) -> str:
    if int((coverage["fetch_status"] == "NOT_ATTEMPTED").sum()) != 0:
        raise ValueError("cannot build report while NOT_ATTEMPTED is non-zero")
    window = raw[
        pd.to_numeric(raw["effective_year"], errors="coerce").between(
            ANALYSIS_START_YEAR, ANALYSIS_END_YEAR
        )
    ].copy()
    status_counts = coverage["fetch_status"].value_counts()
    class_counts = window["event_class"].value_counts()
    full_verdicts = coverage["factor_reconstructable"].value_counts()
    clean_coverage = coverage[coverage["ticker"].isin(clean_basket)]
    clean_verdicts = clean_coverage["factor_reconstructable"].value_counts()

    def blocking_counts(frame: pd.DataFrame) -> dict[str, int]:
        return {name: int((pd.to_numeric(frame[name], errors="coerce") > 0).sum()) for name in BLOCKING_CLASSES}

    rights = sorted(coverage.loc[pd.to_numeric(coverage["RIGHTS_NO_SUBSCRIPTION_PRICE"], errors="coerce") > 0, "ticker"])
    missing = sorted(coverage.loc[pd.to_numeric(coverage["MISSING_EXRIGHT_DATE"], errors="coerce") > 0, "ticker"])
    vnm = window[window["ticker"] == "VNM"].sort_values(
        ["effective_year", "exright_date", "public_date"], kind="stable"
    )
    other = window[window["event_class"] == "OTHER_UNCLASSIFIED"]
    lines = [
        "# Sprint 9-1A VCI Events Coverage",
        "",
        f"Run date: {run_date}",
        "",
        "This cache measures provider coverage only. It does not build an adjustment factor, reconstruct raw prices, or compute market capitalisation or valuation.",
        "",
        "The universe is today's 378 tickers, so this measurement has survivorship bias: delisted historical companies are absent.",
        "",
        "## Pagination method",
        "",
        f"For every ticker, the script instantiated `vnstock.Company(source=\"VCI\", symbol=TICKER)` and called `Company.events()` once per page while forcing the underlying VCI request to `event_codes=DIV,ISS`, `from_date={FROM_DATE}`, `to_date={run_date.replace('-', '')}`, `page=0,1,...`, and `size={PAGE_SIZE}`. It stopped only when a page returned fewer than {PAGE_SIZE} rows; therefore an exact {PAGE_SIZE}-row page was followed by another request, and an empty next page verified the end.",
        "",
        "## N1. Fetch status",
        "",
    ]
    lines.extend(f"- {status}: {int(status_counts.get(status, 0))}" for status in FETCH_STATUSES)
    lines.extend(["- NOT_ATTEMPTED is zero: confirmed", "", "## N2. 2018-2025 ISS/DIV classes", ""])
    lines.append(f"- total: {len(window)}")
    lines.extend(f"- {name}: {int(class_counts.get(name, 0))}" for name in EVENT_CLASSES)
    lines.extend(
        [
            "",
            "## N3. Per-ticker reconstructability",
            "",
            "The clean basket is the union of `step1_survivors.csv` and downstream rejects after excluding `UPCOM_EXCLUDED_V1` and `FINANCIAL_SECTOR_EXCLUDED`; it contains 243 tickers.",
            "",
            "| population | CLEAN | HAS_BLOCKING_HOLE |",
            "|---|---:|---:|",
            f"| Full universe (378) | {int(full_verdicts.get('CLEAN', 0))} | {int(full_verdicts.get('HAS_BLOCKING_HOLE', 0))} |",
            f"| Clean basket (243) | {int(clean_verdicts.get('CLEAN', 0))} | {int(clean_verdicts.get('HAS_BLOCKING_HOLE', 0))} |",
            "",
            "Blocking-class ticker counts:",
            "",
        ]
    )
    full_blocking = blocking_counts(coverage)
    basket_blocking = blocking_counts(clean_coverage)
    lines.extend(
        f"- {name}: full_universe={full_blocking[name]}, clean_basket={basket_blocking[name]}"
        for name in BLOCKING_CLASSES
    )
    lines.extend(
        [
            "",
            "## N4. Blocking ticker lists",
            "",
            f"- RIGHTS_NO_SUBSCRIPTION_PRICE ({len(rights)}): {', '.join(rights) if rights else 'none'}",
            f"- MISSING_EXRIGHT_DATE ({len(missing)}): {', '.join(missing) if missing else 'none'}",
            "",
            "## N5. VNM complete kept ISS/DIV list, 2018-2025",
            "",
        ]
    )
    vnm_columns = [
        "event_code", "event_title_en", "public_date", "exright_date",
        "exercise_ratio", "value_per_share", "event_class",
    ]
    lines.append(vnm[vnm_columns].to_csv(index=False, lineterminator="\n").rstrip())
    lines.extend(["", "## OTHER_UNCLASSIFIED rows", ""])
    if other.empty:
        lines.append("none")
    else:
        lines.append(other.to_csv(index=False, lineterminator="\n").rstrip())
    lines.extend(
        [
            "",
            "## N6. Scope and verification",
            "",
            "Classification precedence for overlapping definitions was: rights issue without subscription price, missing ex-rights date, zero/null ISS ratio, complete bonus/stock dividend, complete cash dividend, then other. The more specific missing-subscription-price class therefore wins when a rights row also lacks an ex-rights date.",
            "",
            "The exact `git diff --stat main..HEAD` is reported after commit.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure VCI corporate-action event coverage.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--run-date")
    parser.add_argument("--batch-size", type=int, default=0)
    parser.add_argument("--tickers", nargs="*")
    args = parser.parse_args(argv)
    if args.batch_size < 0:
        parser.error("--batch-size must be zero or positive")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    run_date = args.run_date or pd.Timestamp.now(tz=ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
    to_date = run_date.replace("-", "")
    output_dir = repo_root / "data" / "corporate_actions" / run_date
    raw_path = output_dir / "events_raw.csv"
    coverage_path = output_dir / "events_coverage_by_ticker.csv"
    report_path = repo_root / "docs" / "REPORT_SPRINT_9_1A_EVENTS_COVERAGE.md"
    tickers = read_universe(repo_root / "data" / "universe.csv")
    coverage = load_or_initialize_coverage(coverage_path, tickers)
    raw = load_raw_events(raw_path)
    remaining = coverage.loc[coverage["fetch_status"] == "NOT_ATTEMPTED", "ticker"].tolist()
    if args.tickers:
        wanted = {str(ticker).strip().upper() for ticker in args.tickers}
        unknown = sorted(wanted.difference(tickers))
        if unknown:
            raise ValueError("requested tickers are outside the universe: " + ", ".join(unknown))
        remaining = [ticker for ticker in remaining if ticker in wanted]
    selected = remaining[: args.batch_size or None]
    client = VnstockClient(cache_dir=output_dir / ".unused_client_cache", use_cache=False)

    for index, ticker in enumerate(selected, start=1):
        try:
            rows, pages, provider_rows = fetch_ticker_events(ticker, client, to_date)
            status = "EMPTY_NO_EVENTS" if rows.empty else "OK"
            raw = _replace_ticker_raw(raw, ticker, rows)
            row = _coverage_row(ticker, status, rows, pages, provider_rows)
        except BaseException as exc:  # noqa: BLE001 - every ticker must receive a terminal status.
            if isinstance(exc, KeyboardInterrupt):
                raise
            rows = pd.DataFrame()
            row = _coverage_row(ticker, "FETCH_ERROR", rows, 0, 0, type(exc).__name__)
            print(f"FETCH_ERROR {ticker}: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        coverage = _replace_coverage(coverage, ticker, row, tickers)
        _atomic_csv(raw, raw_path)
        _atomic_csv(coverage, coverage_path)
        print(
            f"FETCHED {index}/{len(selected)} {ticker} status={row['fetch_status']} "
            f"pages={row['pages_fetched']} kept={len(rows)}",
            flush=True,
        )

    counts = coverage["fetch_status"].value_counts()
    for status in FETCH_STATUSES:
        print(f"FETCH_STATUS {status}={int(counts.get(status, 0))}")
    if int(counts.get("NOT_ATTEMPTED", 0)) == 0:
        report = build_report(raw, coverage, read_clean_basket(repo_root), run_date)
        report_path.write_text(report, encoding="utf-8", newline="\n")
        print(f"REPORT={report_path}")
    print(f"RAW_OUTPUT={raw_path}")
    print(f"COVERAGE_OUTPUT={coverage_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
