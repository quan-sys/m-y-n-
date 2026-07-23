from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.finance_client import LAG_ANNUAL  # noqa: E402


RUN_DATE = "2026-07-22"
PIT_STATUSES = ("PIT_ISSUED_OK", "PIT_TREASURY_PRESENT", "NO_AVAILABLE_ANNUAL")
PIT_COLUMNS = (
    "ticker",
    "quarter",
    "measurement_date",
    "source_fiscal_year",
    "available_from",
    "shares_issued_derived",
    "staleness_days",
    "status",
)


@dataclass(frozen=True)
class TreasuryUpperBound:
    value: Decimal | None
    below_par_excluded: bool


def attach_availability(annual: pd.DataFrame) -> pd.DataFrame:
    output = annual.copy()

    def available_from(year: object) -> str:
        text = str(year).strip()
        if not text.isdigit():
            return ""
        fiscal_year_end = date(int(text), 12, 31)
        return (fiscal_year_end + timedelta(days=LAG_ANNUAL)).isoformat()

    output["available_from"] = output["year"].map(available_from)
    return output


def quarter_measurements() -> list[tuple[str, date]]:
    measurements: list[tuple[str, date]] = []
    for year in range(2018, 2026):
        for quarter, month_day in enumerate(((3, 31), (6, 30), (9, 30), (12, 31)), start=1):
            month, day = month_day
            measurements.append((f"{year}Q{quarter}", date(year, month, day)))
    return measurements


def build_point_in_time(available: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    by_ticker = {
        ticker: group.copy()
        for ticker, group in available.groupby("ticker", sort=False)
    }
    rows: list[dict[str, str]] = []
    for ticker in tickers:
        annual = by_ticker.get(ticker, pd.DataFrame(columns=available.columns))
        annual = annual[annual["available_from"] != ""].copy()
        annual["_available_date"] = pd.to_datetime(
            annual["available_from"], errors="coerce"
        ).dt.date
        annual = annual[annual["_available_date"].notna()]
        for quarter, measurement_date in quarter_measurements():
            eligible = annual[annual["_available_date"] <= measurement_date]
            if eligible.empty:
                selected = None
            else:
                selected = eligible.sort_values(
                    ["_available_date", "year"], kind="stable"
                ).iloc[-1]

            if (
                selected is None
                or not str(selected["shares_issued_derived"]).strip()
                or selected["derivation_status"]
                not in ("ISSUED_OK", "OUTSTANDING_UNKNOWN_TREASURY_PRESENT")
            ):
                source_fiscal_year = ""
                selected_available_from = ""
                shares_issued = ""
                staleness_days = ""
                status = "NO_AVAILABLE_ANNUAL"
            else:
                source_fiscal_year = str(selected["year"])
                selected_available_from = str(selected["available_from"])
                shares_issued = str(selected["shares_issued_derived"])
                staleness_days = str(
                    (measurement_date - selected["_available_date"]).days
                )
                status = (
                    "PIT_TREASURY_PRESENT"
                    if selected["derivation_status"]
                    == "OUTSTANDING_UNKNOWN_TREASURY_PRESENT"
                    else "PIT_ISSUED_OK"
                )
            rows.append(
                {
                    "ticker": ticker,
                    "quarter": quarter,
                    "measurement_date": measurement_date.isoformat(),
                    "source_fiscal_year": source_fiscal_year,
                    "available_from": selected_available_from,
                    "shares_issued_derived": shares_issued,
                    "staleness_days": staleness_days,
                    "status": status,
                }
            )
    output = pd.DataFrame(rows, columns=PIT_COLUMNS)
    unknown = sorted(set(output["status"]).difference(PIT_STATUSES))
    if unknown:
        raise ValueError("point-in-time table has invalid status: " + ", ".join(unknown))
    return output


def treasury_fraction_upper_bound(
    paid_in_capital_vnd: object,
    treasury_cash_vnd: object,
    fiscal_year_prices: pd.DataFrame,
) -> TreasuryUpperBound:
    paid = _decimal(paid_in_capital_vnd)
    treasury = _decimal(treasury_cash_vnd)
    if paid is None or paid <= 0 or treasury is None:
        return TreasuryUpperBound(None, False)
    traded = fiscal_year_prices[
        pd.to_numeric(fiscal_year_prices["volume"], errors="coerce").fillna(0) > 0
    ]
    closes = pd.to_numeric(traded["close"], errors="coerce").dropna()
    if closes.empty or bool((closes < 10.0).any()):
        return TreasuryUpperBound(None, True)
    return TreasuryUpperBound(abs(treasury) / paid, False)


def _decimal(value: object) -> Decimal | None:
    text = str(value).strip()
    if not text:
        return None
    try:
        number = Decimal(text)
    except Exception:
        return None
    return number if number.is_finite() else None


def status_counts(point_in_time: pd.DataFrame) -> dict[str, int]:
    return {
        status: int((point_in_time["status"] == status).sum())
        for status in PIT_STATUSES
    }


def append_build_report(report: str, point_in_time: pd.DataFrame) -> str:
    marker = "## Fallback build outputs"
    base = report.split(marker, maxsplit=1)[0].rstrip()
    counts = status_counts(point_in_time)
    vnm = point_in_time[point_in_time["ticker"] == "VNM"]
    lines = [
        base,
        "",
        marker,
        "",
        "### LAG_ANNUAL",
        "",
        f"- value: {LAG_ANNUAL}",
        "- source: `src.data.finance_client.LAG_ANNUAL`",
        "",
        "### Point-in-time status counts",
        "",
    ]
    lines.extend(f"- {status}: {counts[status]}" for status in PIT_STATUSES)
    lines.extend(
        [
            f"- VNM_NO_AVAILABLE_ANNUAL_quarters: {int((vnm['status'] == 'NO_AVAILABLE_ANNUAL').sum())}",
            "",
            "### VNM — all 32 quarters",
            "",
            "| quarter | measurement_date | source_fiscal_year | available_from | shares_issued_derived | staleness_days | status |",
            "|---|---|---:|---|---:|---:|---|",
        ]
    )
    for row in vnm.itertuples(index=False):
        lines.append(
            f"| {row.quarter} | {row.measurement_date} | {row.source_fiscal_year} | "
            f"{row.available_from} | {row.shares_issued_derived} | "
            f"{row.staleness_days} | {row.status} |"
        )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Sprint 8A-3 availability tables.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    share_dir = repo_root / "data" / "share_count" / RUN_DATE
    issued_path = share_dir / "annual_shares_issued.csv"
    available_path = share_dir / "annual_shares_available.csv"
    point_in_time_path = share_dir / "share_count_point_in_time.csv"
    universe_path = repo_root / "data" / "universe.csv"
    report_path = repo_root / "docs" / "REPORT_SPRINT_8A3_PUBLICATION_DATE.md"

    issued = pd.read_csv(issued_path, dtype=str, keep_default_na=False)
    available = attach_availability(issued)
    available.to_csv(available_path, index=False, lineterminator="\n")
    tickers = (
        pd.read_csv(universe_path, dtype=str)["ticker"].str.strip().str.upper().tolist()
    )
    if len(tickers) != 378 or len(set(tickers)) != 378:
        raise ValueError("universe must contain exactly 378 distinct tickers")
    point_in_time = build_point_in_time(available, tickers)
    point_in_time.to_csv(point_in_time_path, index=False, lineterminator="\n")
    report = report_path.read_text(encoding="utf-8")
    report_path.write_text(
        append_build_report(report, point_in_time),
        encoding="utf-8",
        newline="\n",
    )

    counts = status_counts(point_in_time)
    print(f"LAG_ANNUAL={LAG_ANNUAL}")
    print("LAG_ANNUAL_SOURCE=src.data.finance_client.LAG_ANNUAL")
    print(f"ANNUAL_ROWS={len(available)}")
    print(f"POINT_IN_TIME_ROWS={len(point_in_time)}")
    for status in PIT_STATUSES:
        print(f"STATUS {status}={counts[status]}")
    vnm = point_in_time[point_in_time["ticker"] == "VNM"]
    print(
        "VNM_NO_AVAILABLE_ANNUAL="
        f"{int((vnm['status'] == 'NO_AVAILABLE_ANNUAL').sum())}"
    )
    print(f"ANNUAL_OUTPUT={available_path}")
    print(f"POINT_IN_TIME_OUTPUT={point_in_time_path}")
    print(f"REPORT={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
