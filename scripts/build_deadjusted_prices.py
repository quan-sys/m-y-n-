from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
PAR_THOUSAND_VND = 10.0
PRICE_EVENT_CLASSES = {
    "BONUS_OR_STOCK_DIV_COMPLETE",
    "CASH_DIV_COMPLETE",
    "RIGHTS_NO_SUBSCRIPTION_PRICE",
    "MISSING_EXRIGHT_DATE",
}
NON_PRICE_TITLE_MARKERS = ("esop", "private placement")
OUTPUT_COLUMNS = (
    "ticker",
    "date",
    "raw_close",
    "cumulative_factor",
    "adjustment_confidence",
)


@dataclass(frozen=True)
class BuildDiagnostics:
    unplaceable_tickers: tuple[str, ...]
    moved_out_of_unplaceable: tuple[str, ...]
    excluded_non_price_events: int
    future_events_ignored: int
    rights_sensitivity_percent: tuple[float, ...]


def bonus_factor(ratio: float) -> float:
    return 1.0 / (1.0 + float(ratio))


def cash_dividend_factor(raw_pre_close: float, dividend_vnd: float) -> float:
    dividend_thousand = float(dividend_vnd) / 1000.0
    return (float(raw_pre_close) - dividend_thousand) / float(raw_pre_close)


def rights_factor(raw_pre_close: float, ratio: float, subscription_thousand: float) -> float:
    close = float(raw_pre_close)
    rights_ratio = float(ratio)
    return (close + rights_ratio * float(subscription_thousand)) / (
        close * (1.0 + rights_ratio)
    )


def _text(row: pd.Series, *columns: str) -> str:
    return " ".join(str(row.get(column, "") or "") for column in columns).lower()


def _positive(value: object) -> bool:
    number = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    return bool(pd.notna(number) and float(number) > 0)


def is_price_event(row: pd.Series) -> bool:
    if str(row.get("event_class", "")) not in PRICE_EVENT_CLASSES:
        return False
    code = str(row.get("event_code", "")).upper()
    title = _text(row, "event_title_en", "event_title_vi")
    if code == "ISS" and any(marker in title for marker in NON_PRICE_TITLE_MARKERS):
        return False
    if code == "ISS" and not _positive(row.get("exercise_ratio")):
        return False
    if code == "DIV":
        return _positive(row.get("value_per_share"))
    return (
        "bonus issue" in title
        or "stock dividend" in title
        or "rights issue" in title
    )


def event_kind(row: pd.Series) -> str:
    title = _text(row, "event_title_en", "event_title_vi")
    if str(row.get("event_code", "")).upper() == "DIV":
        return "CASH"
    if "rights issue" in title:
        return "RIGHTS"
    if "bonus issue" in title or "stock dividend" in title:
        return "BONUS"
    raise ValueError(f"unsupported price event: {row.get('ticker')} {row.get('id')}")


def select_price_events(events: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    allowed = events[events["event_class"].isin(PRICE_EVENT_CLASSES)].copy()
    mask = allowed.apply(is_price_event, axis=1)
    return allowed[mask].copy(), int((~mask).sum())


def _resolve_event_dates(
    ticker_events: pd.DataFrame,
    trading_dates: pd.DatetimeIndex,
) -> tuple[pd.DataFrame, bool]:
    ticker_events = ticker_events.copy()
    ticker_events["_date_fallback"] = False
    ticker_events["_future_event"] = False
    resolved: list[pd.Timestamp | pd.NaT] = []
    unplaceable = False
    max_price_date = trading_dates.max()
    for _, event in ticker_events.iterrows():
        exright_date = pd.to_datetime(event.get("exright_date"), errors="coerce")
        record_date = pd.to_datetime(event.get("record_date"), errors="coerce")
        public_date = pd.to_datetime(event.get("public_date"), errors="coerce")
        if pd.notna(exright_date):
            placement_date = exright_date
            placement_source = "exright_date"
        elif pd.notna(record_date):
            placement_date = record_date
            placement_source = "record_date"
        elif pd.notna(public_date):
            placement_date = public_date
            placement_source = "public_date"
        else:
            resolved.append(pd.NaT)
            unplaceable = True
            continue

        if placement_date > max_price_date:
            resolved.append(placement_date)
            ticker_events.loc[event.name, "_future_event"] = True
            continue

        if placement_source == "record_date":
            candidates = trading_dates[trading_dates >= placement_date]
            if len(candidates) == 0:
                resolved.append(placement_date)
                ticker_events.loc[event.name, "_date_fallback"] = True
                continue
            placement_date = candidates[0]

        resolved.append(placement_date)
        ticker_events.loc[event.name, "_date_fallback"] = placement_source != "exright_date"
    ticker_events["_resolved_exdate"] = pd.to_datetime(
        pd.Series(resolved, index=ticker_events.index), errors="coerce"
    )
    return ticker_events, unplaceable


def _validated_factor(value: float, ticker: str, event_date: pd.Timestamp) -> float:
    if not np.isfinite(value) or value <= 0:
        raise ValueError(f"non-positive event factor for {ticker} on {event_date.date()}: {value}")
    return float(value)


def reconstruct_ticker(
    ticker_prices: pd.DataFrame,
    ticker_events: pd.DataFrame,
) -> tuple[pd.DataFrame, bool, int, list[float]]:
    prices = ticker_prices.copy()
    price_dates = pd.to_datetime(prices["date"], errors="raise")
    adjusted = pd.to_numeric(prices["close_adjusted"], errors="raise").to_numpy(float)
    if len(prices) == 0:
        raise ValueError("ticker price frame is empty")
    trading_dates = pd.DatetimeIndex(price_dates)
    events, unplaceable = _resolve_event_dates(ticker_events.copy(), trading_dates)
    future_count = int(events["_future_event"].sum())
    events = events[
        events["_resolved_exdate"].notna() & ~events["_future_event"]
    ].copy()

    cumulative = np.ones(len(prices), dtype=float)
    cumulative_alt = np.ones(len(prices), dtype=float)
    confidence = np.full(len(prices), "LOW" if unplaceable else "OK", dtype=object)
    running = 1.0
    running_alt = 1.0

    grouped = list(events.groupby("_resolved_exdate", sort=True))
    for event_date, same_day in reversed(grouped):
        before = np.flatnonzero(trading_dates < event_date)
        if len(before) == 0:
            continue
        pre_index = int(before[-1])
        raw_pre = adjusted[pre_index] / running
        raw_pre_alt = adjusted[pre_index] / running_alt
        group_factor = 1.0
        group_factor_alt = 1.0
        group_low = bool(same_day["_date_fallback"].any())

        for _, event in same_day.iterrows():
            kind = event_kind(event)
            if kind == "BONUS":
                factor = bonus_factor(float(event["exercise_ratio"]))
                factor_alt = factor
            elif kind == "CASH":
                factor = cash_dividend_factor(raw_pre, float(event["value_per_share"]))
                factor_alt = cash_dividend_factor(raw_pre_alt, float(event["value_per_share"]))
            else:
                ratio = float(event["exercise_ratio"])
                factor = rights_factor(raw_pre, ratio, PAR_THOUSAND_VND)
                factor_alt = rights_factor(raw_pre_alt, ratio, 0.5 * raw_pre_alt)
                group_low = True
            group_factor *= _validated_factor(factor, str(prices["ticker"].iloc[0]), event_date)
            group_factor_alt *= _validated_factor(
                factor_alt, str(prices["ticker"].iloc[0]), event_date
            )

        affected = trading_dates < event_date
        cumulative[affected] *= group_factor
        cumulative_alt[affected] *= group_factor_alt
        if group_low:
            confidence[affected] = "LOW"
        running *= group_factor
        running_alt *= group_factor_alt

    raw_close = adjusted / cumulative
    raw_close_alt = adjusted / cumulative_alt
    changed = ~np.isclose(cumulative, cumulative_alt, rtol=0, atol=1e-15)
    sensitivity_values = np.zeros(int(changed.sum()), dtype=float)
    changed_raw = raw_close[changed]
    changed_alt = raw_close_alt[changed]
    np.divide(
        np.abs(changed_alt - changed_raw) * 100.0,
        np.abs(changed_raw),
        out=sensitivity_values,
        where=np.abs(changed_raw) > 0,
    )
    sensitivity = sensitivity_values.tolist()
    output = pd.DataFrame(
        {
            "ticker": prices["ticker"].astype(str).to_numpy(),
            "date": prices["date"].astype(str).to_numpy(),
            "raw_close": raw_close,
            "cumulative_factor": cumulative,
            "adjustment_confidence": confidence,
        },
        columns=OUTPUT_COLUMNS,
    )
    return output, unplaceable, future_count, sensitivity


def build_deadjusted(prices: pd.DataFrame, events: pd.DataFrame) -> tuple[pd.DataFrame, BuildDiagnostics]:
    required_price = {"ticker", "date", "close_adjusted"}
    required_event = {
        "ticker", "event_code", "event_title_en", "event_title_vi", "event_class",
        "exright_date", "record_date", "public_date", "exercise_ratio", "value_per_share",
    }
    if missing := sorted(required_price.difference(prices.columns)):
        raise ValueError("price cache missing columns: " + ", ".join(missing))
    if missing := sorted(required_event.difference(events.columns)):
        raise ValueError("event cache missing columns: " + ", ".join(missing))
    if prices.duplicated(["ticker", "date"]).any():
        raise ValueError("input price cache has duplicate ticker-date rows")

    selected, excluded = select_price_events(events)
    legacy_unplaceable = set(
        selected.loc[
            pd.to_datetime(selected["exright_date"], errors="coerce").isna()
            & pd.to_datetime(selected["record_date"], errors="coerce").isna(),
            "ticker",
        ].astype(str)
    )
    events_by_ticker = {ticker: frame for ticker, frame in selected.groupby("ticker", sort=False)}
    outputs: list[pd.DataFrame] = []
    unplaceable: list[str] = []
    future_count = 0
    sensitivity: list[float] = []
    for ticker, ticker_prices in prices.groupby("ticker", sort=False):
        ticker_events = events_by_ticker.get(ticker, selected.iloc[0:0])
        output, ticker_unplaceable, ticker_future, ticker_sensitivity = reconstruct_ticker(
            ticker_prices, ticker_events
        )
        outputs.append(output)
        if ticker_unplaceable:
            unplaceable.append(str(ticker))
        future_count += ticker_future
        sensitivity.extend(ticker_sensitivity)
    result = pd.concat(outputs, ignore_index=True)
    if len(result) != len(prices):
        raise ValueError("output row count differs from input price row count")
    if set(result["adjustment_confidence"]) - {"OK", "LOW"}:
        raise ValueError("invalid adjustment_confidence value")
    diagnostics = BuildDiagnostics(
        tuple(sorted(unplaceable)),
        tuple(sorted(legacy_unplaceable.difference(unplaceable))),
        excluded,
        future_count,
        tuple(sensitivity),
    )
    return result, diagnostics


def gzip_csv_bytes(frame: pd.DataFrame) -> bytes:
    csv_text = frame.to_csv(
        index=False,
        columns=OUTPUT_COLUMNS,
        lineterminator="\n",
        float_format="%.12g",
    )
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as compressed:
        compressed.write(csv_text.encode("utf-8"))
    return buffer.getvalue()


def write_reproducibly(frame: pd.DataFrame, path: Path) -> tuple[str, str]:
    payload_first = gzip_csv_bytes(frame)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload_first)
    sha_first = hashlib.sha256(path.read_bytes()).hexdigest()
    payload_second = gzip_csv_bytes(frame)
    path.write_bytes(payload_second)
    sha_second = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha_first != sha_second:
        raise ValueError("gzip output is not byte-reproducible")
    return sha_first, sha_second


def build_report(
    result: pd.DataFrame,
    input_prices: pd.DataFrame,
    diagnostics: BuildDiagnostics,
    sha_first: str,
    sha_second: str,
) -> str:
    merged = result.merge(
        input_prices[["ticker", "date", "close_adjusted"]],
        on=["ticker", "date"],
        how="left",
        validate="one_to_one",
    )
    vnm_window = merged[
        (merged["ticker"] == "VNM")
        & (merged["date"] >= "2020-09-25")
        & (merged["date"] <= "2020-10-01")
    ][["date", "raw_close", "close_adjusted", "cumulative_factor"]]
    latest_date = merged.loc[merged["ticker"] == "VNM", "date"].max()
    latest = merged[(merged["ticker"] == "VNM") & (merged["date"] == latest_date)].iloc[0]
    vnm_pre = vnm_window[vnm_window["date"] < "2020-09-29"].iloc[-1]
    vnm_ex = vnm_window[vnm_window["date"] >= "2020-09-29"].iloc[0]
    vnm_backward_step = (vnm_pre["raw_close"] / vnm_ex["raw_close"] - 1.0) * 100.0
    confidence_counts = result["adjustment_confidence"].value_counts()
    low_tickers = result.loc[result["adjustment_confidence"] == "LOW", "ticker"].nunique()
    sensitivity = np.asarray(diagnostics.rights_sensitivity_percent, dtype=float)
    sensitivity_median = float(np.median(sensitivity)) if len(sensitivity) else 0.0
    sensitivity_max = float(np.max(sensitivity)) if len(sensitivity) else 0.0
    lines = [
        "# Sprint 9-1B De-adjusted Prices",
        "",
        "This is a local reconstruction over cached adjusted prices and cached corporate actions. No provider call, market capitalisation, valuation, or portfolio computation was made.",
        "",
        "## N1. VNM around the 2020-09-29 bonus ex-date",
        "",
        vnm_window.to_csv(index=False, lineterminator="\n", float_format="%.12g").rstrip(),
        f"- backward raw-price step from ex-date to prior trading day: {vnm_backward_step:.12g}%",
        "",
        "## N2. VNM most recent invariant",
        "",
        f"- date: {latest_date}",
        f"- raw_close: {latest['raw_close']:.12g}",
        f"- adjusted_close: {latest['close_adjusted']:.12g}",
        f"- cumulative_factor: {latest['cumulative_factor']:.12g}",
        f"- absolute_difference: {abs(latest['raw_close'] - latest['close_adjusted']):.12g}",
        f"- equals_within_1e-6: {abs(latest['raw_close'] - latest['close_adjusted']) <= 1e-6}",
        "",
        "## N3. Confidence",
        "",
        f"- OK ticker-dates: {int(confidence_counts.get('OK', 0))}",
        f"- LOW ticker-dates: {int(confidence_counts.get('LOW', 0))}",
        f"- distinct tickers with any LOW date: {low_tickers}",
        f"- UNPLACEABLE_EVENT tickers: {len(diagnostics.unplaceable_tickers)}",
        f"- UNPLACEABLE_EVENT list: {', '.join(diagnostics.unplaceable_tickers) if diagnostics.unplaceable_tickers else 'none'}",
        f"- tickers moved OUT of UNPLACEABLE: {len(diagnostics.moved_out_of_unplaceable)}",
        f"- moved-out list: {', '.join(diagnostics.moved_out_of_unplaceable) if diagnostics.moved_out_of_unplaceable else 'none'}",
        "",
        "## N4. Rights sensitivity",
        "",
        f"- affected ticker-dates: {len(sensitivity)}",
        f"- median percentage difference: {sensitivity_median:.12g}",
        f"- max percentage difference: {sensitivity_max:.12g}",
        "- Rights comparisons where both reconstructed prices are zero are recorded as 0% difference.",
        "",
        "## N5. Reproducibility",
        "",
        f"- sha256 first write: {sha_first}",
        f"- sha256 second write: {sha_second}",
        "",
        "## Exclusions and placement",
        "",
        f"- excluded non-price events: {diagnostics.excluded_non_price_events}",
        f"- future events after the price-cache end ignored: {diagnostics.future_events_ignored}",
        "- ESOP, private placements, and zero/null-ratio ISS rows were excluded before factor construction.",
        "- Adding or removing those excluded rows therefore produces an exact zero difference in all cumulative factors.",
        "",
        "## Scope",
        "",
        "The exact `git diff --stat main..HEAD` is reported after commit.",
        "",
    ]
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reconstruct unadjusted close prices locally.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    price_path = repo_root / "data" / "price_history" / "2026-07-22" / "daily_close.csv.gz"
    event_path = repo_root / "data" / "corporate_actions" / "2026-07-24" / "events_raw.csv"
    output_path = repo_root / "data" / "price_history" / "2026-07-24" / "deadjusted_close.csv.gz"
    report_path = repo_root / "docs" / "REPORT_SPRINT_9_1B_DEADJUST.md"
    prices = pd.read_csv(price_path, dtype={"ticker": str, "date": str})
    events = pd.read_csv(event_path, dtype={"ticker": str}, keep_default_na=False)
    result, diagnostics = build_deadjusted(prices, events)
    sha_first, sha_second = write_reproducibly(result, output_path)
    report = build_report(result, prices, diagnostics, sha_first, sha_second)
    report_path.write_text(report, encoding="utf-8", newline="\n")
    print(f"SHA256_FIRST={sha_first}")
    print(f"SHA256_SECOND={sha_second}")
    print(f"OUTPUT={output_path}")
    print(f"REPORT={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
