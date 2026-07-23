from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.build_sprint8a3_point_in_time_shares import (  # noqa: E402
    TreasuryUpperBound,
    treasury_fraction_upper_bound,
)


RUN_DATE = "2026-07-22"
REASONS = (
    "BOUND_OK",
    "BELOW_PAR_EXCLUDED",
    "PRICES_MISSING",
    "PAID_IN_CAPITAL_MISSING",
)
OUTPUT_COLUMNS = (
    "ticker",
    "year",
    "paid_in_capital_vnd",
    "treasury_cash_vnd",
    "upper_bound_fraction",
    "below_par_excluded",
    "reason",
)


def _decimal(value: object) -> Decimal | None:
    text = str(value).strip()
    if not text:
        return None
    try:
        number = Decimal(text)
    except Exception:
        return None
    return number if number.is_finite() else None


def classify_treasury_year(
    ticker: str,
    year: str,
    paid_in_capital_vnd: object,
    treasury_cash_vnd: object,
    fiscal_year_prices: pd.DataFrame,
) -> dict[str, str]:
    paid = _decimal(paid_in_capital_vnd)
    if paid is None or paid <= 0:
        return _output_row(
            ticker,
            year,
            paid_in_capital_vnd,
            treasury_cash_vnd,
            "",
            False,
            "PAID_IN_CAPITAL_MISSING",
        )

    traded = fiscal_year_prices[
        (pd.to_numeric(fiscal_year_prices["volume"], errors="coerce").fillna(0) > 0)
        & pd.to_numeric(fiscal_year_prices["close"], errors="coerce").notna()
    ]
    if traded.empty:
        return _output_row(
            ticker,
            year,
            paid_in_capital_vnd,
            treasury_cash_vnd,
            "",
            False,
            "PRICES_MISSING",
        )

    bound: TreasuryUpperBound = treasury_fraction_upper_bound(
        paid_in_capital_vnd,
        treasury_cash_vnd,
        fiscal_year_prices,
    )
    if bound.below_par_excluded:
        return _output_row(
            ticker,
            year,
            paid_in_capital_vnd,
            treasury_cash_vnd,
            "",
            True,
            "BELOW_PAR_EXCLUDED",
        )
    if bound.value is None:
        raise ValueError(
            f"bound function returned no value without an exclusion for {ticker} {year}"
        )
    return _output_row(
        ticker,
        year,
        paid_in_capital_vnd,
        treasury_cash_vnd,
        format(bound.value, "f"),
        False,
        "BOUND_OK",
    )


def _output_row(
    ticker: str,
    year: str,
    paid_in_capital_vnd: object,
    treasury_cash_vnd: object,
    upper_bound_fraction: str,
    below_par_excluded: bool,
    reason: str,
) -> dict[str, str]:
    return {
        "ticker": str(ticker),
        "year": str(year),
        "paid_in_capital_vnd": str(paid_in_capital_vnd),
        "treasury_cash_vnd": str(treasury_cash_vnd),
        "upper_bound_fraction": upper_bound_fraction,
        "below_par_excluded": "true" if below_par_excluded else "false",
        "reason": reason,
    }


def build_treasury_bounds(capital: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    treasury_numeric = pd.to_numeric(capital["treasury_shares_raw"], errors="coerce")
    selected = capital[
        (capital["fetch_status"] == "OK")
        & capital["treasury_shares_raw"].astype(str).str.strip().ne("")
        & treasury_numeric.notna()
        & treasury_numeric.ne(0)
    ].copy()

    price_data = prices.copy()
    price_data["_date"] = pd.to_datetime(price_data["date"], errors="coerce")
    price_data["_year"] = price_data["_date"].dt.year.astype("Int64").astype(str)
    price_frames = {
        (ticker, year): group[["close_adjusted", "volume"]].rename(
            columns={"close_adjusted": "close"}
        )
        for (ticker, year), group in price_data.groupby(["ticker", "_year"], sort=False)
    }

    rows = [
        classify_treasury_year(
            ticker=str(row.ticker),
            year=str(row.year),
            paid_in_capital_vnd=row.charter_capital_raw,
            treasury_cash_vnd=row.treasury_shares_raw,
            fiscal_year_prices=price_frames.get(
                (str(row.ticker), str(row.year)),
                pd.DataFrame(columns=["close", "volume"]),
            ),
        )
        for row in selected.itertuples(index=False)
    ]
    output = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    unknown = sorted(set(output["reason"]).difference(REASONS))
    if unknown:
        raise ValueError("invalid treasury-bound reason: " + ", ".join(unknown))
    invalid_blank = output[
        (output["reason"] != "BOUND_OK") & output["upper_bound_fraction"].ne("")
    ]
    if not invalid_blank.empty:
        raise ValueError("non-BOUND_OK row has an upper-bound fraction")
    bound_values = pd.to_numeric(
        output.loc[output["reason"] == "BOUND_OK", "upper_bound_fraction"],
        errors="coerce",
    )
    if bound_values.isna().any() or bool((bound_values <= 0).any()):
        raise ValueError("BOUND_OK row has a missing or non-positive fraction")
    return output


def reason_counts(bounds: pd.DataFrame) -> dict[str, int]:
    return {reason: int((bounds["reason"] == reason).sum()) for reason in REASONS}


def _decimal_quantile(values: list[Decimal], percentile: Decimal) -> Decimal:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot compute a quantile of an empty list")
    position = Decimal(len(ordered) - 1) * percentile
    lower = int(position)
    upper = lower if position == lower else lower + 1
    weight = position - Decimal(lower)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def bound_statistics(bounds: pd.DataFrame) -> dict[str, Decimal | int]:
    values = [
        value
        for value in (
            _decimal(raw)
            for raw in bounds.loc[
                bounds["reason"] == "BOUND_OK", "upper_bound_fraction"
            ]
        )
        if value is not None
    ]
    return {
        "count": len(values),
        "min": min(values),
        "median": _decimal_quantile(values, Decimal("0.5")),
        "p90": _decimal_quantile(values, Decimal("0.9")),
        "max": max(values),
        "share_below_1pct": Decimal(sum(value < Decimal("0.01") for value in values))
        / Decimal(len(values)),
    }


def render_report(bounds: pd.DataFrame) -> str:
    counts = reason_counts(bounds)
    statistics = bound_statistics(bounds)
    below_par_tickers = sorted(
        bounds.loc[bounds["reason"] == "BELOW_PAR_EXCLUDED", "ticker"].unique()
    )
    abt = bounds[(bounds["ticker"] == "ABT") & (bounds["year"] == "2018")]
    if len(abt) != 1:
        raise ValueError(f"expected one ABT 2018 row, found {len(abt)}")
    abt_row = abt.iloc[0]
    absolute_treasury = abs(_decimal(abt_row["treasury_cash_vnd"]) or Decimal(0))
    lines = [
        "# Sprint 8A-3B Treasury Upper Bound",
        "",
        "ESTIMATE: This is a ONE-SIDED UPPER BOUND on the treasury-share fraction of issued shares, valid only when the repurchase price was at least par. The below-par test uses calendar-year traded prices as a PROXY and cannot see the actual repurchase date.",
        "",
        "## N1 — Reason counts",
        "",
    ]
    lines.extend(f"- {reason}: {counts[reason]}" for reason in REASONS)
    lines.extend(
        [
            f"- selected_total: {len(bounds)}",
            f"- reason_count_sum: {sum(counts.values())}",
            "",
            "## N2 — Tickers with at least one BELOW_PAR_EXCLUDED year",
            "",
            ", ".join(below_par_tickers),
            "",
            "## N3 — BOUND_OK distribution",
            "",
            f"- min: {statistics['min']}",
            f"- median: {statistics['median']}",
            f"- p90: {statistics['p90']}",
            f"- max: {statistics['max']}",
            f"- share_below_1pct: {statistics['share_below_1pct']}",
            "",
            "## N4 — ABT 2018 worked line",
            "",
            "| ticker | year | paid_in_capital_vnd | absolute_treasury_cash_vnd | upper_bound_fraction | below_par_excluded |",
            "|---|---:|---:|---:|---:|---|",
            f"| ABT | 2018 | {abt_row['paid_in_capital_vnd']} | {absolute_treasury} | "
            f"{abt_row['upper_bound_fraction']} | {abt_row['below_par_excluded']} |",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build cached treasury upper bounds.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    share_dir = repo_root / "data" / "share_count" / RUN_DATE
    capital = pd.read_csv(
        share_dir / "annual_share_capital.csv",
        dtype=str,
        keep_default_na=False,
    )
    prices = pd.read_csv(
        repo_root / "data" / "price_history" / RUN_DATE / "daily_close.csv.gz",
        usecols=["ticker", "date", "close_adjusted", "close_adjusted_unit", "volume"],
    )
    units = sorted(
        str(value)
        for value in prices["close_adjusted_unit"].dropna().unique()
        if str(value).strip()
    )
    if units != ["THOUSAND_VND"]:
        raise ValueError(f"expected THOUSAND_VND adjusted closes, found {units}")

    bounds = build_treasury_bounds(capital, prices)
    output_path = share_dir / "treasury_upper_bound.csv"
    bounds.to_csv(output_path, index=False, lineterminator="\n")
    report_path = repo_root / "docs" / "REPORT_SPRINT_8A3B_TREASURY_BOUND.md"
    report_path.write_text(render_report(bounds), encoding="utf-8", newline="\n")

    counts = reason_counts(bounds)
    statistics = bound_statistics(bounds)
    print(f"SELECTED_TOTAL={len(bounds)}")
    for reason in REASONS:
        print(f"REASON {reason}={counts[reason]}")
    print(f"REASON_COUNT_SUM={sum(counts.values())}")
    print(f"BOUND_OK_MIN={statistics['min']}")
    print(f"BOUND_OK_MEDIAN={statistics['median']}")
    print(f"BOUND_OK_P90={statistics['p90']}")
    print(f"BOUND_OK_MAX={statistics['max']}")
    print(f"BOUND_OK_SHARE_BELOW_1PCT={statistics['share_below_1pct']}")
    print(f"OUTPUT={output_path}")
    print(f"REPORT={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
