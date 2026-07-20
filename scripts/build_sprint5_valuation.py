"""Build Sprint 5 EBIT/TEV and E/P candidates from reviewed local evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.screener.step1_pipeline import load_simple_config


EVALUATION_DATE = "2026-07-20"
EXPECTED_SURVIVORS = 156
SURVIVORS_PATH = ROOT / "data" / "screener" / "step1_survivors.csv"
MARKET_CAP_PATH = ROOT / "data" / "market_cap" / "2026-07-19" / "universe_market_cap.csv"
QUARTERLY_CACHE_ROOT = ROOT / "data" / "fundamentals" / "run_state" / "2026-07-17" / "normalized"
CONFIG_PATH = ROOT / "config" / "screener.yaml"
ALL_OUTPUT_PATH = ROOT / "data" / "screener" / "step2_valuation_all.csv"
EBIT_TEV_OUTPUT_PATH = ROOT / "data" / "screener" / "step2_candidates_ebit_tev.csv"
EP_OUTPUT_PATH = ROOT / "data" / "screener" / "step2_candidates_ep.csv"

PBT_ITEM = "net_accounting_profit_loss_before_tax"
INTEREST_ITEM = "interest_expenses"
FINANCIAL_EXPENSES_ITEM = "financial_expenses"
EARNINGS_ITEM = "attributable_to_parent_company"
SHORT_DEBT_ITEM = "short_term_borrowings"
LONG_DEBT_ITEM = "long_term_borrowings"
CASH_ITEM = "cash_and_cash_equivalents"
MINORITY_ITEM = "minority_interests"


@dataclass(frozen=True)
class TTMWindow:
    periods: tuple[str, ...]
    missing_periods: tuple[str, ...]
    duplicate_entries: tuple[str, ...]
    future_row_exclusion_count: int

    @property
    def complete(self) -> bool:
        return (
            len(self.periods) == 4
            and not self.missing_periods
            and not self.duplicate_entries
        )


@dataclass(frozen=True)
class ItemSeries:
    values: tuple[int | None, ...]
    missing_periods: tuple[str, ...]
    duplicate_periods: tuple[str, ...]
    non_numeric_periods: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return (
            len(self.values) == 4
            and not self.missing_periods
            and not self.duplicate_periods
            and not self.non_numeric_periods
            and all(value is not None for value in self.values)
        )


@dataclass(frozen=True)
class TevResult:
    value: int | None
    status: str
    minority_treatment: str


@dataclass(frozen=True)
class CheapSetResult:
    eligible_count: int
    target_count: int
    actual_count: int
    cutoff: float | None
    ranks: pd.Series
    flags: pd.Series


@dataclass(frozen=True)
class BuildResult:
    all_rows: pd.DataFrame
    ebit_tev_candidates: pd.DataFrame
    ep_candidates: pd.DataFrame
    anomalies: pd.DataFrame
    hand_checks: pd.DataFrame
    summary: dict[str, Any]


def finite_number(value: Any) -> bool:
    if value is None or value is pd.NA or isinstance(value, (bool, str, bytes)):
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def integer_value(value: Any) -> int | None:
    if not finite_number(value):
        return None
    return int(round(float(value)))


def quarter_ordinal(value: Any) -> int:
    text = str(value).strip().upper().replace("-", "")
    if len(text) != 6 or text[4] != "Q" or not text[:4].isdigit() or text[5] not in "1234":
        raise ValueError(f"invalid quarter: {value}")
    return int(text[:4]) * 4 + int(text[5]) - 1


def quarter_from_ordinal(value: int) -> str:
    return f"{value // 4}Q{value % 4 + 1}"


def _eligible_quarter_rows(rows: pd.DataFrame, evaluation_date: str) -> tuple[pd.DataFrame, int]:
    required = {"period_type", "report_period", "available_from", "item_id", "value"}
    missing = sorted(required - set(rows.columns))
    if missing:
        raise ValueError(f"normalized rows missing columns: {missing}")
    quarters = rows.loc[rows["period_type"].astype(str).str.upper().eq("QUARTER")].copy()
    available = pd.to_datetime(quarters["available_from"], errors="coerce")
    cutoff = pd.Timestamp(evaluation_date)
    future_count = int(available.gt(cutoff).sum())
    eligible = quarters.loc[available.notna() & available.le(cutoff)].copy()
    return eligible, future_count


def select_ttm_window(
    rows: pd.DataFrame,
    evaluation_date: str,
    required_item_ids: Iterable[str],
) -> TTMWindow:
    eligible, future_count = _eligible_quarter_rows(rows, evaluation_date)
    if eligible.empty:
        return TTMWindow((), ("NO_ELIGIBLE_QUARTER",), (), future_count)
    labels: list[str] = []
    for value in eligible["report_period"].dropna().astype(str).unique():
        quarter_ordinal(value)
        labels.append(value.replace("-", "").upper())
    latest = max(quarter_ordinal(value) for value in labels)
    expected = tuple(quarter_from_ordinal(latest - offset) for offset in range(4))
    present = set(labels)
    missing_periods = tuple(period for period in expected if period not in present)

    required = eligible.loc[eligible["item_id"].astype(str).isin(tuple(required_item_ids))].copy()
    duplicated = required.loc[
        required.duplicated(["report_period", "item_id"], keep=False),
        ["report_period", "item_id"],
    ].drop_duplicates()
    duplicate_entries = sorted(
        f"{str(row.report_period).replace('-', '').upper()}:{row.item_id}"
        for row in duplicated.itertuples(index=False)
    )
    metadata_conflicts = (
        eligible.assign(_available=eligible["available_from"].astype(str))
        .groupby("report_period", dropna=False)["_available"]
        .nunique(dropna=False)
    )
    duplicate_entries.extend(
        f"{str(period).replace('-', '').upper()}:AVAILABLE_FROM_CONFLICT"
        for period in metadata_conflicts[metadata_conflicts.gt(1)].index
    )
    return TTMWindow(
        periods=expected,
        missing_periods=missing_periods,
        duplicate_entries=tuple(sorted(set(duplicate_entries))),
        future_row_exclusion_count=future_count,
    )


def item_series(rows: pd.DataFrame, item_id: str, periods: tuple[str, ...]) -> ItemSeries:
    if len(periods) != 4:
        return ItemSeries(tuple(None for _ in periods), ("NO_TTM_WINDOW",), (), ())
    normalized_periods = rows["report_period"].astype(str).str.replace("-", "", regex=False).str.upper()
    values: list[int | None] = []
    missing: list[str] = []
    duplicate: list[str] = []
    non_numeric: list[str] = []
    for period in periods:
        matches = rows.loc[
            rows["item_id"].astype(str).eq(item_id) & normalized_periods.eq(period), "value"
        ]
        if matches.empty:
            values.append(None)
            missing.append(period)
        elif len(matches) > 1:
            values.append(None)
            duplicate.append(period)
        else:
            value = integer_value(matches.iloc[0])
            values.append(value)
            if value is None:
                non_numeric.append(period)
    return ItemSeries(tuple(values), tuple(missing), tuple(duplicate), tuple(non_numeric))


def latest_eligible_quarter(rows: pd.DataFrame, evaluation_date: str) -> str | None:
    eligible, _ = _eligible_quarter_rows(rows, evaluation_date)
    if eligible.empty:
        return None
    labels = {
        str(value).replace("-", "").upper()
        for value in eligible["report_period"].dropna().unique()
    }
    return max(labels, key=quarter_ordinal) if labels else None


def component_value(rows: pd.DataFrame, item_id: str, period: str | None) -> tuple[int | None, str]:
    if period is None:
        return None, "NO_ELIGIBLE_BALANCE_PERIOD"
    normalized_periods = rows["report_period"].astype(str).str.replace("-", "", regex=False).str.upper()
    matches = rows.loc[
        rows["item_id"].astype(str).eq(item_id) & normalized_periods.eq(period), "value"
    ]
    if matches.empty:
        return None, "MISSING"
    if len(matches) > 1:
        return None, "DUPLICATE"
    value = integer_value(matches.iloc[0])
    return (value, "OK") if value is not None else (None, "NON_NUMERIC")


def calculate_tev(
    market_cap_vnd: int | None,
    short_term_borrowings_vnd: int | None,
    long_term_borrowings_vnd: int | None,
    cash_and_cash_equivalents_vnd: int | None,
    minority_interests_vnd: int | None,
) -> TevResult:
    mandatory = {
        "market_cap_vnd": market_cap_vnd,
        "short_term_borrowings_vnd": short_term_borrowings_vnd,
        "long_term_borrowings_vnd": long_term_borrowings_vnd,
        "cash_and_cash_equivalents_vnd": cash_and_cash_equivalents_vnd,
    }
    missing = [name for name, value in mandatory.items() if value is None]
    minority_treatment = (
        "INCLUDED_EXPLICIT_VALUE"
        if minority_interests_vnd is not None
        else "OMITTED_EXPLICITLY_UNAVAILABLE"
    )
    if missing:
        return TevResult(None, "MISSING:" + "|".join(missing), minority_treatment)
    assert market_cap_vnd is not None
    assert short_term_borrowings_vnd is not None
    assert long_term_borrowings_vnd is not None
    assert cash_and_cash_equivalents_vnd is not None
    value = (
        market_cap_vnd
        + short_term_borrowings_vnd
        + long_term_borrowings_vnd
        - cash_and_cash_equivalents_vnd
    )
    if minority_interests_vnd is not None:
        value += minority_interests_vnd
    return TevResult(value, "OK", minority_treatment)


def calculate_ebit_proxy_vas(
    pbt_values: Iterable[int | None],
    raw_interest_expense_values: Iterable[int | None],
) -> tuple[int | None, int | None, int | None]:
    pbt = tuple(pbt_values)
    interest = tuple(raw_interest_expense_values)
    if len(pbt) != 4 or len(interest) != 4:
        raise ValueError("EBIT_PROXY_VAS requires exactly four quarterly values")
    if any(value is None for value in pbt) or any(value is None for value in interest):
        return None, None, None
    ttm_pbt = sum(value for value in pbt if value is not None)
    ttm_interest_magnitude = sum(abs(value) for value in interest if value is not None)
    return ttm_pbt, ttm_interest_magnitude, ttm_pbt + ttm_interest_magnitude


def ebit_tev_exclusion_reason(ebit_vnd: int | None, tev_vnd: int | None) -> str:
    reasons: list[str] = []
    if ebit_vnd is None:
        reasons.append("MISSING_EBIT")
    if tev_vnd is None:
        reasons.append("MISSING_TEV")
    if ebit_vnd is not None and ebit_vnd < 0:
        reasons.append("NEGATIVE_EBIT")
    if tev_vnd is not None and tev_vnd <= 0:
        reasons.append("NON_POSITIVE_TEV")
    return "|".join(reasons)


def ep_exclusion_reason(earnings_vnd: int | None, market_cap_vnd: int | None) -> str:
    reasons: list[str] = []
    if earnings_vnd is None:
        reasons.append("MISSING_EARNINGS")
    if market_cap_vnd is None:
        reasons.append("MISSING_MARKET_CAP")
    if earnings_vnd is not None and earnings_vnd < 0:
        reasons.append("NEGATIVE_EARNINGS")
    return "|".join(reasons)


def select_cheapest(values: pd.Series, eligible: pd.Series, cheapest_pct: float) -> CheapSetResult:
    if not 0 < cheapest_pct <= 1:
        raise ValueError("VALUE_CHEAPEST_PCT must be in (0, 1]")
    numeric = pd.to_numeric(values, errors="coerce")
    valid_mask = eligible.astype(bool) & numeric.notna() & numeric.map(finite_number)
    valid = numeric.loc[valid_mask]
    ranks = pd.Series(pd.NA, index=values.index, dtype="Float64")
    flags = pd.Series(False, index=values.index, dtype=bool)
    if valid.empty:
        return CheapSetResult(0, 0, 0, None, ranks, flags)
    target = max(1, math.ceil(len(valid) * cheapest_pct))
    cutoff = float(valid.sort_values(ascending=False).iloc[target - 1])
    flags.loc[valid.index] = valid.ge(cutoff)
    ranks.loc[valid.index] = valid.rank(method="min", ascending=False)
    return CheapSetResult(len(valid), target, int(flags.sum()), cutoff, ranks, flags)


def _read_statement(ticker: str, statement: str) -> tuple[pd.DataFrame, str]:
    path = QUARTERLY_CACHE_ROOT / ticker / f"{statement}.parquet"
    if not path.exists():
        return pd.DataFrame(columns=["period_type", "report_period", "available_from", "item_id", "value"]), ""
    return pd.read_parquet(path), path.relative_to(ROOT).as_posix()


def _series_status(series: ItemSeries) -> str:
    parts: list[str] = []
    if series.missing_periods:
        parts.append("MISSING:" + "|".join(series.missing_periods))
    if series.duplicate_periods:
        parts.append("DUPLICATE:" + "|".join(series.duplicate_periods))
    if series.non_numeric_periods:
        parts.append("NON_NUMERIC:" + "|".join(series.non_numeric_periods))
    return "OK" if not parts else ";".join(parts)


def _safe_ratio(numerator: int | None, denominator: int | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def _joined(values: Iterable[str]) -> str:
    return "|".join(value for value in values if value)


def _market_cap_record(market_row: pd.Series | None) -> tuple[int | None, str]:
    if market_row is None:
        return None, "MISSING_MARKET_CAP_ROW"
    flags = "" if pd.isna(market_row.get("guard_flags")) else str(market_row.get("guard_flags", "")).strip()
    value = integer_value(market_row.get("market_cap_vnd"))
    if flags:
        return None, flags
    if value is None or value <= 0:
        return None, "MISSING_OR_NON_POSITIVE_MARKET_CAP"
    return value, "OK"


def _spearman(left: pd.Series, right: pd.Series) -> tuple[float | None, int]:
    frame = pd.DataFrame({"left": pd.to_numeric(left, errors="coerce"), "right": pd.to_numeric(right, errors="coerce")}).dropna()
    frame = frame.loc[frame.left.map(finite_number) & frame.right.map(finite_number)]
    if len(frame) < 2:
        return None, len(frame)
    left_rank = frame.left.rank(method="average", ascending=True)
    right_rank = frame.right.rank(method="average", ascending=True)
    return float(left_rank.corr(right_rank)), len(frame)


def build_valuation() -> BuildResult:
    config = load_simple_config(CONFIG_PATH)
    cheapest_pct = float(config.get("VALUE_CHEAPEST_PCT", -1))
    if cheapest_pct != 0.30:
        raise ValueError(f"VALUE_CHEAPEST_PCT must equal 0.30; found {cheapest_pct}")

    survivors = pd.read_csv(SURVIVORS_PATH)
    tickers = survivors["ticker"].astype(str).str.strip().str.upper()
    if len(survivors) != EXPECTED_SURVIVORS or tickers.nunique() != EXPECTED_SURVIVORS:
        raise ValueError(
            f"survivors must contain exactly {EXPECTED_SURVIVORS} unique tickers; "
            f"rows={len(survivors)} unique={tickers.nunique()}"
        )
    survivors = survivors.copy()
    survivors["ticker"] = tickers

    market = pd.read_csv(MARKET_CAP_PATH)
    if market["ticker"].astype(str).str.upper().duplicated().any():
        raise ValueError("market-cap input has duplicate tickers")
    market["ticker"] = market["ticker"].astype(str).str.upper()
    market_map = {row.ticker: row for _, row in market.iterrows()}

    records: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []
    for survivor in survivors.to_dict("records"):
        ticker = survivor["ticker"]
        income, income_path = _read_statement(ticker, "income_statement")
        balance, balance_path = _read_statement(ticker, "balance_sheet")
        income_eligible, _ = _eligible_quarter_rows(income, EVALUATION_DATE)
        balance_eligible, _ = _eligible_quarter_rows(balance, EVALUATION_DATE)
        window = select_ttm_window(
            income,
            EVALUATION_DATE,
            (PBT_ITEM, INTEREST_ITEM, FINANCIAL_EXPENSES_ITEM, EARNINGS_ITEM),
        )
        pbt = item_series(income_eligible, PBT_ITEM, window.periods)
        interest_raw = item_series(income_eligible, INTEREST_ITEM, window.periods)
        financial_expenses = item_series(income_eligible, FINANCIAL_EXPENSES_ITEM, window.periods)
        earnings = item_series(income_eligible, EARNINGS_ITEM, window.periods)

        interest_magnitudes = tuple(abs(value) if value is not None else None for value in interest_raw.values)
        if window.complete and pbt.complete and interest_raw.complete:
            ttm_pbt, ttm_interest, ebit = calculate_ebit_proxy_vas(
                pbt.values, interest_raw.values
            )
        else:
            ttm_pbt, ttm_interest, ebit = None, None, None
        ttm_earnings = sum(value for value in earnings.values if value is not None) if window.complete and earnings.complete else None

        for period, interest_value, financial_value in zip(
            window.periods, interest_raw.values, financial_expenses.values, strict=True
        ):
            if (
                interest_value is not None
                and financial_value is not None
                and abs(interest_value) > abs(financial_value)
            ):
                anomalies.append(
                    {
                        "ticker": ticker,
                        "report_period": period,
                        "interest_expenses_raw_vnd": interest_value,
                        "interest_expense_magnitude_vnd": abs(interest_value),
                        "financial_expenses_raw_vnd": financial_value,
                        "financial_expenses_magnitude_vnd": abs(financial_value),
                        "reason": "ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES",
                    }
                )

        market_row = market_map.get(ticker)
        market_cap, market_status = _market_cap_record(market_row)
        price_as_of = "" if market_row is None or pd.isna(market_row.get("price_as_of")) else str(market_row.get("price_as_of"))
        shares_as_of = "" if market_row is None or pd.isna(market_row.get("shares_as_of")) else str(market_row.get("shares_as_of"))

        balance_period = latest_eligible_quarter(balance, EVALUATION_DATE)
        short_debt, short_debt_status = component_value(balance_eligible, SHORT_DEBT_ITEM, balance_period)
        long_debt, long_debt_status = component_value(balance_eligible, LONG_DEBT_ITEM, balance_period)
        cash, cash_status = component_value(balance_eligible, CASH_ITEM, balance_period)
        minority, minority_status = component_value(balance_eligible, MINORITY_ITEM, balance_period)
        tev = calculate_tev(market_cap, short_debt, long_debt, cash, minority)
        ebit_tev = _safe_ratio(ebit, tev.value)
        ep = _safe_ratio(ttm_earnings, market_cap)
        ebit_exclusion = ebit_tev_exclusion_reason(ebit, tev.value)
        ep_exclusion = ep_exclusion_reason(ttm_earnings, market_cap)

        row: dict[str, Any] = {
            "ticker": ticker,
            "exchange": survivor.get("exchange", ""),
            "icb2": survivor.get("icb2", ""),
            "evaluation_date": EVALUATION_DATE,
            "market_cap_vnd": market_cap,
            "market_cap_status": market_status,
            "price_as_of": price_as_of,
            "shares_as_of": shares_as_of,
            "ttm_window_status": "OK" if window.complete else "INCOMPLETE",
            "ttm_missing_periods": _joined(window.missing_periods),
            "ttm_duplicate_entries": _joined(window.duplicate_entries),
            "future_income_rows_excluded": window.future_row_exclusion_count,
            "pbt_status": _series_status(pbt),
            "interest_expenses_status": _series_status(interest_raw),
            "financial_expenses_status": _series_status(financial_expenses),
            "earnings_status": _series_status(earnings),
            "ttm_pbt_vnd": ttm_pbt,
            "ttm_interest_expense_magnitude_vnd": ttm_interest,
            "ebit_proxy_vas_vnd": ebit,
            "ttm_attributable_to_parent_company_vnd": ttm_earnings,
            "balance_period_used": balance_period,
            "short_term_borrowings_vnd": short_debt,
            "short_term_borrowings_status": short_debt_status,
            "long_term_borrowings_vnd": long_debt,
            "long_term_borrowings_status": long_debt_status,
            "cash_and_cash_equivalents_vnd": cash,
            "cash_and_cash_equivalents_status": cash_status,
            "minority_interests_vnd": minority,
            "minority_interests_status": minority_status,
            "minority_interest_treatment": tev.minority_treatment,
            "tev_vnd": tev.value,
            "tev_status": tev.status,
            "ebit_tev": ebit_tev,
            "ep": ep,
            "ebit_tev_exclusion_reason": ebit_exclusion,
            "ep_exclusion_reason": ep_exclusion,
            "ebit_tev_eligible": ebit_exclusion == "" and ebit_tev is not None,
            "ep_eligible": ep_exclusion == "" and ep is not None,
            "interest_financial_expense_anomaly_count": 0,
            "interest_financial_expense_anomaly_quarters": "",
            "income_source_path": income_path,
            "balance_source_path": balance_path,
            "market_cap_source_path": MARKET_CAP_PATH.relative_to(ROOT).as_posix(),
            "source": "Sprint 4 survivors + Sprint 3 normalized quarterly cache + calibrated KBS market cap",
            "as_of": max(filter(None, [price_as_of, shares_as_of, "2026-07-17"]), default=""),
            "data_status": "MISSING_DATA" if any(value is None for value in (market_cap, ebit, ttm_earnings, tev.value)) else "OK",
        }
        for index in range(4):
            suffix = index + 1
            row[f"ttm_q{suffix}_period"] = window.periods[index] if index < len(window.periods) else ""
            row[f"pbt_q{suffix}_vnd"] = pbt.values[index] if index < len(pbt.values) else None
            row[f"interest_expenses_raw_q{suffix}_vnd"] = interest_raw.values[index] if index < len(interest_raw.values) else None
            row[f"interest_expense_magnitude_q{suffix}_vnd"] = interest_magnitudes[index] if index < len(interest_magnitudes) else None
            row[f"financial_expenses_raw_q{suffix}_vnd"] = financial_expenses.values[index] if index < len(financial_expenses.values) else None
            row[f"earnings_parent_q{suffix}_vnd"] = earnings.values[index] if index < len(earnings.values) else None
        records.append(row)

    frame = pd.DataFrame(records, dtype=object)
    anomaly_frame = pd.DataFrame(anomalies, dtype=object)
    if not anomaly_frame.empty:
        anomaly_group = anomaly_frame.groupby("ticker")["report_period"].agg(list)
        for ticker, periods in anomaly_group.items():
            mask = frame.ticker.eq(ticker)
            frame.loc[mask, "interest_financial_expense_anomaly_count"] = len(periods)
            frame.loc[mask, "interest_financial_expense_anomaly_quarters"] = "|".join(periods)

    ebit_cut = select_cheapest(frame["ebit_tev"], frame["ebit_tev_eligible"], cheapest_pct)
    ep_cut = select_cheapest(frame["ep"], frame["ep_eligible"], cheapest_pct)
    frame["ebit_tev_rank"] = ebit_cut.ranks
    frame["ep_rank"] = ep_cut.ranks
    frame["ebit_tev_in_cheap_set"] = ebit_cut.flags
    frame["ep_in_cheap_set"] = ep_cut.flags

    ebit_candidates = frame.loc[frame.ebit_tev_in_cheap_set].sort_values(
        ["ebit_tev", "ticker"], ascending=[False, True]
    ).copy()
    ep_candidates = frame.loc[frame.ep_in_cheap_set].sort_values(
        ["ep", "ticker"], ascending=[False, True]
    ).copy()
    both = frame.loc[frame.ebit_tev_eligible & frame.ep_eligible]
    spearman, spearman_count = _spearman(both["ebit_tev"], both["ep"])

    evidence_tickers = ("VNM", "FPT", "HPG")
    evidence = frame.loc[frame.ticker.isin(evidence_tickers)].copy()
    evidence["_order"] = evidence.ticker.map({ticker: index for index, ticker in enumerate(evidence_tickers)})
    evidence = evidence.sort_values("_order").drop(columns="_order")
    if evidence.ticker.tolist() != list(evidence_tickers):
        raise ValueError("mandatory VNM/FPT/HPG hand-check rows are missing")
    if evidence.icb2.nunique() != 3:
        raise ValueError("hand-check tickers must come from three different ICB2 sectors")
    required_evidence = [
        "market_cap_vnd", "ttm_pbt_vnd", "ttm_interest_expense_magnitude_vnd",
        "ebit_proxy_vas_vnd", "ttm_attributable_to_parent_company_vnd",
        "short_term_borrowings_vnd", "long_term_borrowings_vnd",
        "cash_and_cash_equivalents_vnd", "tev_vnd", "ebit_tev", "ep",
    ]
    if evidence[required_evidence].isna().any().any():
        raise ValueError("mandatory VNM/FPT/HPG hand-check rows are not complete")

    summary = {
        "evaluation_date": EVALUATION_DATE,
        "survivor_rows": len(frame),
        "unique_survivors": int(frame.ticker.nunique()),
        "market_cap_valid": int(frame.market_cap_status.eq("OK").sum()),
        "market_cap_missing": int(frame.market_cap_status.ne("OK").sum()),
        "ttm_window_complete": int(frame.ttm_window_status.eq("OK").sum()),
        "ebit_tev_eligible": ebit_cut.eligible_count,
        "ebit_tev_target_30pct": ebit_cut.target_count,
        "ebit_tev_candidates_with_ties": ebit_cut.actual_count,
        "ebit_tev_cutoff": ebit_cut.cutoff,
        "ep_eligible": ep_cut.eligible_count,
        "ep_target_30pct": ep_cut.target_count,
        "ep_candidates_with_ties": ep_cut.actual_count,
        "ep_cutoff": ep_cut.cutoff,
        "spearman_common_eligible": spearman_count,
        "spearman_rank_correlation": spearman,
        "anomaly_rows": len(anomaly_frame),
    }
    return BuildResult(frame, ebit_candidates, ep_candidates, anomaly_frame, evidence, summary)


def _markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    def shown(value: Any) -> str:
        if value is None or value is pd.NA or (isinstance(value, float) and pd.isna(value)):
            return ""
        return str(value).replace("|", "\\|")

    lines = [
        "| " + " | ".join(columns) + " |",
        "|" + "|".join("---" for _ in columns) + "|",
    ]
    for row in frame.loc[:, columns].itertuples(index=False, name=None):
        lines.append("| " + " | ".join(shown(value) for value in row) + " |")
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    result = build_valuation()
    ALL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    csv_options = {
        "index": False,
        "lineterminator": "\n",
        "float_format": "%.17g",
    }
    result.all_rows.to_csv(ALL_OUTPUT_PATH, **csv_options)
    result.ebit_tev_candidates.to_csv(EBIT_TEV_OUTPUT_PATH, **csv_options)
    result.ep_candidates.to_csv(EP_OUTPUT_PATH, **csv_options)
    print(json.dumps(result.summary, ensure_ascii=False, sort_keys=True))
    hand_columns = [
        "ticker", "icb2",
        "ttm_q1_period", "pbt_q1_vnd", "interest_expense_magnitude_q1_vnd",
        "ttm_q2_period", "pbt_q2_vnd", "interest_expense_magnitude_q2_vnd",
        "ttm_q3_period", "pbt_q3_vnd", "interest_expense_magnitude_q3_vnd",
        "ttm_q4_period", "pbt_q4_vnd", "interest_expense_magnitude_q4_vnd",
        "ttm_pbt_vnd", "ttm_interest_expense_magnitude_vnd", "ebit_proxy_vas_vnd",
        "ttm_attributable_to_parent_company_vnd", "market_cap_vnd",
        "short_term_borrowings_vnd", "long_term_borrowings_vnd",
        "cash_and_cash_equivalents_vnd", "minority_interests_vnd",
        "minority_interest_treatment", "tev_vnd", "ebit_tev", "ep",
    ]
    print("HAND_CHECK_TABLE_BEGIN")
    print(_markdown_table(result.hand_checks, hand_columns))
    print("HAND_CHECK_TABLE_END")
    print("ANOMALY_TABLE_BEGIN")
    if result.anomalies.empty:
        print("NONE")
    else:
        print(_markdown_table(result.anomalies, list(result.anomalies.columns)))
    print("ANOMALY_TABLE_END")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
