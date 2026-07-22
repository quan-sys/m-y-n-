from __future__ import annotations

import argparse
import json
import sys
import tempfile
from decimal import Decimal, getcontext
from pathlib import Path
from zoneinfo import ZoneInfo

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

from src.data.finance_client import FinanceClient  # noqa: E402


FETCH_STATUSES = ("OK", "EMPTY_RESPONSE", "FETCH_ERROR", "NOT_ATTEMPTED")
CHARTER_FIELD = ("Vốn góp", "Paid-in capital", "paid_in_capital")
TREASURY_FIELD = ("Cổ phiếu quỹ", "Treasury shares", "treasury_shares")
RELATED_FIELDS = (
    CHARTER_FIELD,
    TREASURY_FIELD,
    ("Cổ phiếu ưu đãi", "Preferred shares", "preferred_shares"),
    ("Cổ phiếu phổ thông", "Common shares", "common_shares"),
)
RESULT_COLUMNS = (
    "ticker",
    "year",
    "charter_capital_raw",
    "treasury_shares_raw",
    "field_name_used",
    "treasury_field_name",
    "fetch_status",
    "fetch_error_class",
    "provider_field_list_json",
)
PAR_VALUE = Decimal("10000")
getcontext().prec = 50


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


def _raw_text(value: object) -> str:
    return "" if pd.isna(value) else str(value)


def provider_field_records(raw: pd.DataFrame) -> list[dict[str, str]]:
    required = {"item", "item_en", "item_id"}
    missing = sorted(required.difference(raw.columns))
    if missing:
        raise ValueError("provider response missing field columns: " + ", ".join(missing))
    return [
        {
            "item": _raw_text(row.item),
            "item_en": _raw_text(row.item_en),
            "item_id": _raw_text(row.item_id),
        }
        for row in raw[["item", "item_en", "item_id"]].itertuples(index=False)
    ]


def _single_field_row(raw: pd.DataFrame, field: tuple[str, str, str]) -> pd.Series | None:
    item, item_en, item_id = field
    matches = raw[
        (raw["item"].astype(str) == item)
        & (raw["item_en"].astype(str) == item_en)
        & (raw["item_id"].astype(str) == item_id)
    ]
    if matches.empty:
        return None
    if len(matches) != 1:
        raise ValueError(f"provider returned duplicate exact field: {item_en}")
    return matches.iloc[0]


def extract_annual_rows(ticker: str, raw: pd.DataFrame) -> list[dict[str, str]]:
    fields = provider_field_records(raw)
    charter = _single_field_row(raw, CHARTER_FIELD)
    treasury = _single_field_row(raw, TREASURY_FIELD)
    years = [column for column in raw.columns if str(column).isdigit() and len(str(column)) == 4]
    rows: list[dict[str, str]] = []
    field_json = json.dumps(fields, ensure_ascii=False, separators=(",", ":")) if ticker == "VNM" else ""
    for year in years:
        rows.append(
            {
                "ticker": ticker,
                "year": str(year),
                "charter_capital_raw": _raw_text(charter[year]) if charter is not None else "",
                "treasury_shares_raw": _raw_text(treasury[year]) if treasury is not None else "",
                "field_name_used": CHARTER_FIELD[1] if charter is not None else "",
                "treasury_field_name": TREASURY_FIELD[1] if treasury is not None else "",
                "fetch_status": "OK",
                "fetch_error_class": "",
                "provider_field_list_json": field_json,
            }
        )
    return rows


def _placeholder(ticker: str, status: str, error_class: str = "") -> dict[str, str]:
    if status not in FETCH_STATUSES:
        raise ValueError(f"invalid fetch status: {status}")
    return {
        "ticker": ticker,
        "year": "",
        "charter_capital_raw": "",
        "treasury_shares_raw": "",
        "field_name_used": "",
        "treasury_field_name": "",
        "fetch_status": status,
        "fetch_error_class": error_class,
        "provider_field_list_json": "",
    }


def load_or_initialize(path: Path, tickers: list[str]) -> pd.DataFrame:
    if path.exists():
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
        missing = sorted(set(RESULT_COLUMNS).difference(frame.columns))
        if missing:
            raise ValueError("existing result missing columns: " + ", ".join(missing))
        unknown = sorted(set(frame["fetch_status"]).difference(FETCH_STATUSES))
        if unknown:
            raise ValueError("existing result has invalid status: " + ", ".join(unknown))
        return frame[list(RESULT_COLUMNS)]
    return pd.DataFrame([_placeholder(ticker, "NOT_ATTEMPTED") for ticker in tickers], columns=RESULT_COLUMNS)


def replace_ticker_rows(frame: pd.DataFrame, ticker: str, rows: list[dict[str, str]]) -> pd.DataFrame:
    retained = frame[frame["ticker"] != ticker]
    return pd.concat([retained, pd.DataFrame(rows, columns=RESULT_COLUMNS)], ignore_index=True)


def write_results(frame: pd.DataFrame, path: Path, ticker_order: list[str]) -> None:
    order = {ticker: index for index, ticker in enumerate(ticker_order)}
    output = frame.copy()
    output["_ticker_order"] = output["ticker"].map(order)
    output["_year_order"] = pd.to_numeric(output["year"], errors="coerce").fillna(-1)
    output = output.sort_values(["_ticker_order", "_year_order"], kind="stable").drop(
        columns=["_ticker_order", "_year_order"]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    output.to_csv(temporary, index=False, lineterminator="\n")
    temporary.replace(path)


def status_counts(frame: pd.DataFrame) -> dict[str, int]:
    by_ticker = frame.groupby("ticker", sort=False)["fetch_status"].first()
    return {status: int((by_ticker == status).sum()) for status in FETCH_STATUSES}


def _decimal(value: str) -> Decimal | None:
    text = str(value).strip()
    if not text:
        return None
    try:
        number = Decimal(text)
    except Exception:
        return None
    return number if number.is_finite() else None


def _crosscheck(results: pd.DataFrame, market_cap_path: Path) -> dict[str, object]:
    market = pd.read_csv(market_cap_path, dtype={"ticker": str})
    population = market[market["shares_outstanding"].notna()].copy()
    if len(market) != 157 or len(population) != 156:
        raise ValueError(
            f"expected market-cap cross-check population 157/156, found {len(market)}/{len(population)}"
        )
    latest: dict[str, tuple[int, Decimal]] = {}
    for row in results[results["fetch_status"] == "OK"].itertuples(index=False):
        capital = _decimal(row.charter_capital_raw)
        if capital is None or not str(row.year).isdigit():
            continue
        year = int(row.year)
        prior = latest.get(row.ticker)
        if prior is None or year > prior[0]:
            latest[row.ticker] = (year, capital)

    computed: list[dict[str, object]] = []
    for row in population.itertuples(index=False):
        ticker = str(row.ticker).strip().upper()
        shares = _decimal(str(row.shares_outstanding))
        capital_entry = latest.get(ticker)
        if shares is None or shares == 0 or capital_entry is None:
            continue
        year, capital = capital_entry
        implied = capital / shares
        deviation = abs(implied - PAR_VALUE) / PAR_VALUE
        computed.append(
            {"ticker": ticker, "year": year, "implied_par": implied, "deviation": deviation}
        )

    implied_values = sorted(item["implied_par"] for item in computed)
    median: Decimal | None = None
    if implied_values:
        middle = len(implied_values) // 2
        median = (
            implied_values[middle]
            if len(implied_values) % 2
            else (implied_values[middle - 1] + implied_values[middle]) / Decimal(2)
        )
    return {
        "population": 156,
        "computed": len(computed),
        "missing": 156 - len(computed),
        "within_1pct": sum(item["deviation"] <= Decimal("0.01") for item in computed),
        "within_5pct": sum(item["deviation"] <= Decimal("0.05") for item in computed),
        "within_10pct": sum(item["deviation"] <= Decimal("0.10") for item in computed),
        "beyond_10pct": sum(item["deviation"] > Decimal("0.10") for item in computed),
        "outside_5pct": sum(item["deviation"] > Decimal("0.05") for item in computed),
        "median": median,
        "outliers": sorted(computed, key=lambda item: item["deviation"], reverse=True)[:10],
    }


def _nonzero_treasury_tickers(results: pd.DataFrame) -> list[str]:
    tickers: set[str] = set()
    for row in results[results["fetch_status"] == "OK"].itertuples(index=False):
        value = _decimal(row.treasury_shares_raw)
        if value is not None and value != 0:
            tickers.add(row.ticker)
    return sorted(tickers)


def build_report(results: pd.DataFrame, market_cap_path: Path, run_date: str) -> str:
    counts = status_counts(results)
    if counts["NOT_ATTEMPTED"]:
        raise ValueError("cannot build final report while tickers remain NOT_ATTEMPTED")
    vnm_fields_text = next(
        (value for value in results.loc[results["ticker"] == "VNM", "provider_field_list_json"] if value),
        "",
    )
    fields = json.loads(vnm_fields_text) if vnm_fields_text else []
    crosscheck = _crosscheck(results, market_cap_path)
    treasury_tickers = _nonzero_treasury_tickers(results)
    outside_ratio = Decimal(crosscheck["outside_5pct"]) / Decimal(crosscheck["population"])
    missing_charter_tickers = sorted(
        ticker
        for ticker, group in results[results["fetch_status"] == "OK"].groupby("ticker")
        if not any(_decimal(value) is not None for value in group["charter_capital_raw"])
    )
    years = sorted(
        {int(value) for value in results["year"] if str(value).isdigit()}
    )
    if not fields or crosscheck["computed"] == 0 or outside_ratio > Decimal("0.10"):
        verdict = "SHARE_COUNT_HISTORY_NOT_AVAILABLE"
        verdict_detail = "The exact fields were fetched, but the measured par-value derivation is not usable."
    elif counts["FETCH_ERROR"] or counts["EMPTY_RESPONSE"] or missing_charter_tickers or treasury_tickers:
        verdict = "SHARE_COUNT_HISTORY_PARTIAL"
        verdict_detail = (
            f"Field {CHARTER_FIELD[1]} covers years {years[0]}-{years[-1]} where returned; "
            f"missing-field tickers={','.join(missing_charter_tickers) or 'NONE'}, "
            f"non-zero-treasury tickers={','.join(treasury_tickers) or 'NONE'}."
        )
    else:
        verdict = "SHARE_COUNT_HISTORY_DERIVABLE"
        verdict_detail = f"Field {CHARTER_FIELD[1]} covers years {years[0]}-{years[-1]}."

    lines = [
        "# Sprint 8A-2 Share Count Coverage",
        "",
        "historical market capitalisation equals share count times price. Sprint 8A obtained the price history. The repository holds exactly one share count per ticker, in `data/market_cap/2026-07-19/universe_market_cap.csv`, so historical market capitalisation, and therefore historical EBIT/TEV and E/P, cannot be computed. Sprint 8C rule C2 already records this. Retroactively adjusted prices already absorb bonus issues and splits, but they do NOT absorb shares issued for cash, which is precisely the behaviour F-Score criterion 7 exists to detect and which is large in this universe.",
        "",
        f"The artifact directory `data/share_count/{run_date}/` is by download date and is NOT immutable, unlike `data/forward_test/`.",
        "",
        "## Provider field names",
        "",
    ]
    lines.extend(
        f"- item={field['item']} | item_en={field['item_en']} | item_id={field['item_id']}"
        for field in fields
    )
    lines.extend(["", "## Share-capital candidates", ""])
    lines.extend(
        f"- item={item} | item_en={item_en} | item_id={item_id}"
        for item, item_en, item_id in RELATED_FIELDS
    )
    lines.extend(["", "## Fetch status", ""])
    lines.extend(f"- {status}: {counts[status]}" for status in FETCH_STATUSES)
    lines.extend(
        [
            "",
            "## Par-value cross-check",
            "",
            f"- population: {crosscheck['population']}",
            f"- computable: {crosscheck['computed']}",
            f"- not_computable: {crosscheck['missing']}",
            f"- within_1pct_of_10000: {crosscheck['within_1pct']}",
            f"- within_5pct_of_10000: {crosscheck['within_5pct']}",
            f"- within_10pct_of_10000: {crosscheck['within_10pct']}",
            f"- beyond_10pct_of_10000: {crosscheck['beyond_10pct']}",
            f"- outside_5pct_of_10000: {crosscheck['outside_5pct']}",
            f"- median_implied_par: {crosscheck['median'] if crosscheck['median'] is not None else 'ABSENT'}",
            "",
            "### Ten furthest implied par values",
            "",
            "| ticker | latest_year | implied_par |",
            "|---|---:|---:|",
        ]
    )
    lines.extend(
        f"| {item['ticker']} | {item['year']} | {item['implied_par']} |"
        for item in crosscheck["outliers"]
    )
    assumption_holds = outside_ratio <= Decimal("0.10")
    lines.extend(
        [
            "",
            (
                "The 10,000 VND par-value assumption HOLDS under the specified 5% test."
                if assumption_holds
                else "The 10,000 VND par-value assumption DOES NOT HOLD and the derivation is NOT usable."
            ),
            "",
            f"Tickers with a non-zero treasury-share value in any returned year: {len(treasury_tickers)}.",
            "",
            "## VNM",
            "",
            "| year | charter_capital_raw | treasury_shares_raw | implied_share_count | field_name_used |",
            "|---|---:|---:|---:|---|",
        ]
    )
    vnm_rows = results[(results["ticker"] == "VNM") & (results["fetch_status"] == "OK")]
    vnm_implied: list[str] = []
    for row in vnm_rows.itertuples(index=False):
        capital = _decimal(row.charter_capital_raw)
        implied = capital / PAR_VALUE if capital is not None else None
        implied_text = str(implied) if implied is not None else "ABSENT"
        vnm_implied.append(implied_text)
        lines.append(
            f"| {row.year or 'ABSENT'} | {row.charter_capital_raw or 'ABSENT'} | "
            f"{row.treasury_shares_raw or 'ABSENT'} | {implied_text} | "
            f"{row.field_name_used or 'ABSENT'} |"
        )
    changes = len(set(vnm_implied)) > 1
    lines.extend(
        [
            "",
            (
                "VNM's implied share count changes across returned years."
                if changes
                else "VNM's implied share count does not change across returned years."
            ),
            "",
            "## Verdict",
            "",
            verdict,
            "",
            verdict_detail,
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe annual share-capital history without valuation.")
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
    tickers = read_universe(repo_root / "data" / "universe.csv")
    output_path = repo_root / "data" / "share_count" / run_date / "annual_share_capital.csv"
    report_path = repo_root / "docs" / "REPORT_SPRINT_8A2_SHARE_COUNT_COVERAGE.md"
    results = load_or_initialize(output_path, tickers)
    statuses = results.groupby("ticker", sort=False)["fetch_status"].first().to_dict()
    remaining = [ticker for ticker in tickers if statuses.get(ticker) == "NOT_ATTEMPTED"]
    if args.tickers:
        wanted = {str(ticker).strip().upper() for ticker in args.tickers}
        unknown = sorted(wanted.difference(tickers))
        if unknown:
            raise ValueError("requested tickers are outside the universe: " + ", ".join(unknown))
        remaining = [ticker for ticker in remaining if ticker in wanted]
    selected = remaining[: args.batch_size or None]

    with tempfile.TemporaryDirectory(prefix="sprint8a2-share-count-") as temporary:
        temporary_root = Path(temporary)
        for index, ticker in enumerate(selected, start=1):
            try:
                client = FinanceClient(
                    cache_dir=temporary_root / ticker,
                    use_cache=False,
                )
                result = client.get_balance_sheet(ticker, "year")
                raw_paths = list((temporary_root / ticker).rglob("raw.parquet"))
                if not raw_paths:
                    rows = [_placeholder(ticker, "FETCH_ERROR", str(result.status))]
                else:
                    raw = pd.read_parquet(raw_paths[0])
                    rows = (
                        [_placeholder(ticker, "EMPTY_RESPONSE")]
                        if raw.empty
                        else extract_annual_rows(ticker, raw)
                    )
                results = replace_ticker_rows(results, ticker, rows)
                write_results(results, output_path, tickers)
                print(
                    f"FETCHED {index}/{len(selected)} {ticker} "
                    f"rows={len(rows)} status={rows[0]['fetch_status']}",
                    flush=True,
                )
                error_text = str(result.error or "").lower()
                if rows[0]["fetch_status"] == "FETCH_ERROR" and any(
                    token in error_text for token in ("429", "rate limit", "too many requests")
                ):
                    print(f"RATE_LIMIT_STOP {ticker}: {result.error}", file=sys.stderr, flush=True)
                    break
            except BaseException as exc:  # noqa: BLE001 - preserve explicit fetch status.
                if isinstance(exc, KeyboardInterrupt):
                    raise
                results = replace_ticker_rows(
                    results,
                    ticker,
                    [_placeholder(ticker, "FETCH_ERROR", type(exc).__name__)],
                )
                write_results(results, output_path, tickers)
                print(f"FETCH_ERROR {ticker}: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)

    counts = status_counts(results)
    for status in FETCH_STATUSES:
        print(f"FETCH_STATUS {status}={counts[status]}")
    if counts["NOT_ATTEMPTED"] == 0:
        report = build_report(
            results,
            repo_root / "data" / "market_cap" / "2026-07-19" / "universe_market_cap.csv",
            run_date,
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")
        print(f"REPORT={report_path}")
    print(f"OUTPUT={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
