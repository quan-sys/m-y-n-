"""Cache-only Sprint 5 data-readiness audit; no valuation arithmetic or ranking."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SURVIVORS_PATH = ROOT / "data" / "screener" / "step1_survivors.csv"
FUNDAMENTALS_ROOT = ROOT / "data" / "fundamentals"
MARKET_CACHE_ROOT = ROOT / "src" / "data" / "cache"
OUTPUT_PATH = ROOT / "data" / "screener" / "sprint5_readiness_audit.csv"
EVALUATION_DATE = "2026-07-18"
EBIT_PRODUCTION_ITEM_IDS = (
    "net_accounting_profit_loss_before_tax",
    "interest_expenses",
)
EP_PRODUCTION_ITEM_ID = "attributable_to_parent_company"
EP_DIAGNOSTIC_ITEM_ID = "net_profit_loss_after_tax"
INTEREST_RULE_NEGATE_RAW = "NEGATE_RAW"
INTEREST_RULE_RAW_POSITIVE = "RAW_POSITIVE"
INTEREST_RULE_BLOCKED = "BLOCKED_SIGN_AMBIGUOUS"

EBIT_CANDIDATE_ITEM_IDS = (
    "operating_profit_loss",
    "net_accounting_profit_loss_before_tax",
    "interest_expenses",
    "financial_income",
    "financial_expenses",
    "other_incomes",
    "other_expenses",
    "net_other_income_expenses",
)
EARNINGS_CANDIDATE_ITEM_IDS = (
    "net_profit_loss_after_tax",
    "attributable_to_parent_company",
)
TEV_COMPONENT_ITEM_IDS = (
    "short_term_borrowings",
    "long_term_borrowings",
    "cash_and_cash_equivalents",
    "minority_interests",
)
NORMALIZED_REQUIRED_COLUMNS = (
    "ticker",
    "statement_type",
    "period_type",
    "report_period",
    "period_end",
    "available_from",
    "item_id",
    "value",
    "currency",
    "source",
    "as_of",
    "data_status",
)
SHARE_COLUMNS = (
    "issue_share",
    "issueShare",
    "outstanding_share",
    "outstandingShare",
    "listed_share",
    "listedShare",
    "shares_outstanding",
    "sharesOutstanding",
)
PRICE_COLUMNS = ("last_close", "lastClose", "current_price", "currentPrice", "close")
DIRECT_MARKET_CAP_COLUMNS = (
    "market_cap",
    "marketCap",
    "market_capitalization",
    "marketCapitalization",
    "listedValue",
)


@dataclass(frozen=True)
class QuarterSelection:
    selected_quarters: tuple[str, ...]
    selected_available_from: tuple[str, ...]
    eligible_quarter_count: int
    missing_quarter_count: int
    duplicate_period_case: bool
    future_period_exclusion_count: int
    future_row_exclusion_count: int

    @property
    def four_consecutive(self) -> bool:
        return len(self.selected_quarters) == 4 and self.missing_quarter_count == 0


@dataclass(frozen=True)
class InterestExpenseSignEvidence:
    nonzero_count: int
    positive_count: int
    negative_count: int
    zero_count: int
    missing_quarter_count: int
    duplicate_value_case: bool
    sign_pattern: str


def quarter_ordinal(value: Any) -> int:
    match = re.fullmatch(r"(\d{4})-?Q([1-4])", str(value).strip().upper())
    if not match:
        raise ValueError(f"invalid quarter: {value}")
    return int(match.group(1)) * 4 + int(match.group(2)) - 1


def select_latest_four_quarters(rows: pd.DataFrame, evaluation_date: str) -> QuarterSelection:
    """Select four latest eligible quarter labels and expose gaps/future rows."""

    required = {"period_type", "report_period", "available_from"}
    missing = sorted(required - set(rows.columns))
    if missing:
        raise ValueError(f"quarter rows missing columns: {missing}")
    quarter_rows = rows.loc[rows["period_type"].astype(str).str.upper().eq("QUARTER")].copy()
    available = pd.to_datetime(quarter_rows["available_from"], errors="coerce")
    cutoff = pd.Timestamp(evaluation_date)
    future_labels = set(quarter_rows.loc[available.gt(cutoff), "report_period"].astype(str))
    future_row_count = int(available.gt(cutoff).sum())
    eligible = quarter_rows.loc[available.notna() & available.le(cutoff)].copy()

    metadata_columns = ["report_period", "available_from"]
    if "period_end" in eligible.columns:
        metadata_columns.append("period_end")
    metadata = eligible.loc[:, metadata_columns].drop_duplicates()
    metadata_conflict = metadata["report_period"].astype(str).duplicated(keep=False).any()
    duplicate_tidy = False
    if "item_id" in eligible.columns:
        duplicate_tidy = eligible.duplicated(["report_period", "item_id"], keep=False).any()
    duplicate_case = bool(metadata_conflict or duplicate_tidy)

    period_availability = (
        eligible.assign(_available=pd.to_datetime(eligible["available_from"], errors="coerce"))
        .sort_values(["_available", "report_period"])
        .drop_duplicates("report_period", keep="last")
    )
    labels = sorted(
        period_availability["report_period"].astype(str).tolist(),
        key=quarter_ordinal,
        reverse=True,
    )
    selected = tuple(labels[:4])
    availability_map = {
        str(row.report_period): str(row.available_from)
        for row in period_availability.itertuples(index=False)
    }
    selected_available = tuple(availability_map[label] for label in selected)
    if selected:
        latest = quarter_ordinal(selected[0])
        expected = {latest - offset for offset in range(4)}
        present = {quarter_ordinal(label) for label in labels}
        missing_count = len(expected - present)
    else:
        missing_count = 4
    return QuarterSelection(
        selected_quarters=selected,
        selected_available_from=selected_available,
        eligible_quarter_count=len(labels),
        missing_quarter_count=missing_count,
        duplicate_period_case=duplicate_case,
        future_period_exclusion_count=len(future_labels),
        future_row_exclusion_count=future_row_count,
    )


def item_present_for_quarters(rows: pd.DataFrame, item_id: str, quarters: tuple[str, ...]) -> bool:
    if len(quarters) != 4 or rows.empty:
        return False
    matches = rows.loc[
        rows["item_id"].astype(str).eq(item_id)
        & rows["report_period"].astype(str).isin(quarters)
    ].copy()
    if matches.duplicated(["report_period", "item_id"], keep=False).any():
        return False
    values = pd.to_numeric(matches["value"], errors="coerce")
    return bool(matches["report_period"].astype(str).nunique() == 4 and values.notna().all())


def component_present_at_quarter(rows: pd.DataFrame, item_id: str, quarter: str | None) -> bool:
    if not quarter or rows.empty:
        return False
    matches = rows.loc[
        rows["item_id"].astype(str).eq(item_id)
        & rows["report_period"].astype(str).eq(quarter)
    ]
    if len(matches) != 1:
        return False
    return bool(pd.to_numeric(matches["value"], errors="coerce").notna().all())


def rows_available_by(rows: pd.DataFrame, evaluation_date: str) -> pd.DataFrame:
    if rows.empty:
        return rows.copy()
    if "available_from" not in rows.columns:
        raise ValueError("normalized rows missing available_from")
    available = pd.to_datetime(rows["available_from"], errors="coerce")
    return rows.loc[available.notna() & available.le(pd.Timestamp(evaluation_date))].copy()


def interest_expense_sign_evidence(
    rows: pd.DataFrame, quarters: tuple[str, ...]
) -> InterestExpenseSignEvidence:
    """Classify cached interest-expense signs without normalizing the values."""

    if rows.empty:
        matches = pd.DataFrame(columns=["report_period", "item_id", "value"])
    else:
        matches = rows.loc[
            rows["item_id"].astype(str).eq("interest_expenses")
            & rows["report_period"].astype(str).isin(quarters)
        ].copy()
    duplicate_case = bool(
        not matches.empty
        and matches.duplicated(["report_period", "item_id"], keep=False).any()
    )
    values = pd.to_numeric(matches.get("value", pd.Series(dtype=float)), errors="coerce")
    numeric_periods = set(matches.loc[values.notna(), "report_period"].astype(str))
    expected_periods = set(quarters) if len(quarters) == 4 else set(quarters)
    missing_count = max(4 - len(expected_periods), 0) + len(expected_periods - numeric_periods)
    positive_count = int(values.gt(0).sum())
    negative_count = int(values.lt(0).sum())
    zero_count = int(values.eq(0).sum())

    complete = len(quarters) == 4 and missing_count == 0 and not duplicate_case
    if not complete:
        pattern = "MISSING_OR_INCOMPLETE"
    elif positive_count and negative_count:
        pattern = "MIXED_NONZERO_SIGNS"
    elif negative_count == 4:
        pattern = "ALL_NEGATIVE"
    elif positive_count == 4:
        pattern = "ALL_POSITIVE"
    elif zero_count == 4:
        pattern = "ALL_ZERO"
    elif negative_count and not positive_count:
        pattern = "NEGATIVE_AND_ZERO"
    elif positive_count and not negative_count:
        pattern = "POSITIVE_AND_ZERO"
    else:
        pattern = "MISSING_OR_INCOMPLETE"
    return InterestExpenseSignEvidence(
        nonzero_count=positive_count + negative_count,
        positive_count=positive_count,
        negative_count=negative_count,
        zero_count=zero_count,
        missing_quarter_count=missing_count,
        duplicate_value_case=duplicate_case,
        sign_pattern=pattern,
    )


def determine_interest_expense_magnitude_rule(
    positive_count: int, negative_count: int
) -> str:
    if negative_count > 0 and positive_count == 0:
        return INTEREST_RULE_NEGATE_RAW
    if positive_count > 0 and negative_count == 0:
        return INTEREST_RULE_RAW_POSITIVE
    return INTEREST_RULE_BLOCKED


def normalize_interest_expense_magnitude(values: pd.Series, rule: str) -> pd.Series:
    """Apply only an explicit sign rule; mixed signs are never hidden."""

    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.isna().any():
        raise ValueError("interest_expenses contains missing or non-numeric values")
    if rule == INTEREST_RULE_NEGATE_RAW:
        if numeric.gt(0).any():
            raise ValueError("positive interest_expenses conflicts with NEGATE_RAW")
        return -numeric
    if rule == INTEREST_RULE_RAW_POSITIVE:
        if numeric.lt(0).any():
            raise ValueError("negative interest_expenses conflicts with RAW_POSITIVE")
        return numeric.copy()
    raise ValueError("interest-expense magnitude rule is blocked")


def interest_expense_pattern_is_ready(pattern: str, rule: str) -> bool:
    compatible_patterns = {
        INTEREST_RULE_NEGATE_RAW: {"ALL_NEGATIVE", "NEGATIVE_AND_ZERO", "ALL_ZERO"},
        INTEREST_RULE_RAW_POSITIVE: {"ALL_POSITIVE", "POSITIVE_AND_ZERO", "ALL_ZERO"},
    }.get(rule, set())
    return pattern in compatible_patterns


def classify_price_adjustment(metadata: dict[str, Any] | None, source_exists: bool) -> str:
    """Require an explicit raw/adjusted flag; absence is a proxy blocker."""

    if not source_exists:
        return "NO_CACHED_PRICE_SOURCE"
    value = str((metadata or {}).get("price_adjustment_status", "")).strip().upper()
    if value in {"RAW", "UNADJUSTED", "RAW_UNADJUSTED"}:
        return "RAW_UNADJUSTED"
    if value in {"ADJUSTED", "ADJUSTED_OBSERVED"}:
        return "ADJUSTED"
    return "UNKNOWN_BLOCKED"


def _read_frame(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def _latest_normalized(ticker: str, statement_dir: str) -> tuple[pd.DataFrame, str, int]:
    root = FUNDAMENTALS_ROOT / ticker / statement_dir / "quarter"
    paths = sorted((*root.rglob("normalized.parquet"), *root.rglob("normalized.csv")))
    if not paths:
        return pd.DataFrame(), "", 0
    latest_as_of = max(path.parent.parent.name for path in paths)
    latest = sorted(path for path in paths if path.parent.parent.name == latest_as_of)
    selected = latest[-1]
    frame = _read_frame(selected)
    missing = sorted(set(NORMALIZED_REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"{selected} missing normalized columns: {missing}")
    return frame, selected.relative_to(ROOT).as_posix(), len(latest)


def _first_column(frame: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    exact = {str(column): str(column) for column in frame.columns}
    lower = {str(column).lower(): str(column) for column in frame.columns}
    for candidate in candidates:
        if candidate in exact:
            return exact[candidate]
        if candidate.lower() in lower:
            return lower[candidate.lower()]
    return None


def _positive_value(frame: pd.DataFrame, candidates: tuple[str, ...]) -> float | None:
    column = _first_column(frame, candidates)
    if column is None:
        return None
    values = pd.to_numeric(frame[column], errors="coerce").dropna()
    if values.empty or float(values.iloc[-1]) <= 0:
        return None
    return float(values.iloc[-1])


def _cached_market_inputs(ticker: str) -> dict[str, Any]:
    market_paths = [
        MARKET_CACHE_ROOT / "market_cap" / f"{ticker}.parquet",
        MARKET_CACHE_ROOT / "market_cap" / f"{ticker}.csv",
    ]
    price_paths = [
        MARKET_CACHE_ROOT / "prices" / f"{ticker}.parquet",
        MARKET_CACHE_ROOT / "prices" / f"{ticker}.csv",
    ]
    market_path = next((path for path in market_paths if path.exists()), None)
    price_path = next((path for path in price_paths if path.exists()), None)
    market = _read_frame(market_path) if market_path else pd.DataFrame()
    price = _read_frame(price_path) if price_path else pd.DataFrame()
    metadata_path = price_path.with_suffix(".metadata.json") if price_path else None
    metadata: dict[str, Any] = {}
    if metadata_path and metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    shares = _positive_value(market, SHARE_COLUMNS)
    price_value = _positive_value(price, ("close",))
    if price_value is None:
        price_value = _positive_value(market, PRICE_COLUMNS)
    adjustment = classify_price_adjustment(metadata, price_path is not None or market_path is not None)
    raw_price_available = price_value is not None and adjustment == "RAW_UNADJUSTED"
    direct_value = _positive_value(market, DIRECT_MARKET_CAP_COLUMNS)
    return {
        "overview_cache_path": "" if market_path is None else market_path.relative_to(ROOT).as_posix(),
        "price_cache_path": "" if price_path is None else price_path.relative_to(ROOT).as_posix(),
        "cached_direct_market_cap_value": direct_value,
        "shares_outstanding_available": shares is not None,
        "raw_price_available": raw_price_available,
        "price_adjustment_status": adjustment,
        "proxy_market_cap_eligible": bool(shares is not None and raw_price_available),
    }


def audit_survivor(row: dict[str, Any]) -> dict[str, Any]:
    ticker = str(row["ticker"]).strip().upper()
    income, income_path, income_observations = _latest_normalized(ticker, "income_statement")
    balance, balance_path, balance_observations = _latest_normalized(ticker, "balance_sheet")
    selection = select_latest_four_quarters(income, EVALUATION_DATE) if not income.empty else QuarterSelection((), (), 0, 4, False, 0, 0)
    latest_quarter = selection.selected_quarters[0] if selection.selected_quarters else None
    eligible_income = rows_available_by(income, EVALUATION_DATE)
    eligible_balance = rows_available_by(balance, EVALUATION_DATE)
    market = _cached_market_inputs(ticker)
    sign_evidence = interest_expense_sign_evidence(
        eligible_income, selection.selected_quarters
    )

    survivor_market_cap = pd.to_numeric(pd.Series([row.get("market_cap")]), errors="coerce").iloc[0]
    source_text = str(row.get("source", ""))
    direct_documented = (
        pd.notna(survivor_market_cap)
        and float(survivor_market_cap) > 0
        and "SOURCE_REPORTED_MARKET_CAP" in source_text
    )
    # The current cache contract has no documented unit/as-of metadata for a
    # cached direct value. Presence alone therefore cannot make it usable.
    cached_direct_documented = False
    direct_available = bool(direct_documented or cached_direct_documented)
    market_cap_blocker = ""
    if not direct_available and not market["proxy_market_cap_eligible"]:
        if market["price_adjustment_status"] in {"ADJUSTED", "UNKNOWN_BLOCKED"}:
            market_cap_blocker = "RAW_PRICE_NOT_VERIFIED"
        elif market["price_adjustment_status"] == "NO_CACHED_PRICE_SOURCE":
            market_cap_blocker = "NO_CACHED_PRICE_SOURCE"
        elif not market["shares_outstanding_available"]:
            market_cap_blocker = "NO_CACHED_SHARE_COUNT"
        else:
            market_cap_blocker = "NO_USABLE_MARKET_CAP"

    result: dict[str, Any] = {
        "ticker": ticker,
        "exchange": row.get("exchange", ""),
        "icb2": row.get("icb2", ""),
        "evaluation_date": EVALUATION_DATE,
        "income_quarter_cache_path": income_path,
        "income_latest_as_of_observation_count": income_observations,
        "balance_quarter_cache_path": balance_path,
        "balance_latest_as_of_observation_count": balance_observations,
        "eligible_quarter_count": selection.eligible_quarter_count,
        "selected_ttm_quarters": "|".join(selection.selected_quarters),
        "selected_quarter_available_from": "|".join(selection.selected_available_from),
        "four_consecutive_eligible_quarters": selection.four_consecutive,
        "missing_one_quarter": selection.missing_quarter_count == 1,
        "missing_two_or_more_quarters": selection.missing_quarter_count >= 2,
        "missing_quarter_count": selection.missing_quarter_count,
        "duplicate_period_case": selection.duplicate_period_case,
        "future_period_exclusion_count": selection.future_period_exclusion_count,
        "future_row_exclusion_count": selection.future_row_exclusion_count,
        "interest_expenses_nonzero_quarter_count": sign_evidence.nonzero_count,
        "interest_expenses_positive_quarter_count": sign_evidence.positive_count,
        "interest_expenses_negative_quarter_count": sign_evidence.negative_count,
        "interest_expenses_zero_quarter_count": sign_evidence.zero_count,
        "interest_expenses_missing_quarter_count": sign_evidence.missing_quarter_count,
        "interest_expenses_duplicate_value_case": sign_evidence.duplicate_value_case,
        "interest_expenses_sign_pattern": sign_evidence.sign_pattern,
        "direct_market_cap_available": direct_available,
        "direct_market_cap_value": float(survivor_market_cap) if direct_documented else market["cached_direct_market_cap_value"],
        "direct_market_cap_method": "SOURCE_REPORTED_MARKET_CAP" if direct_available else "UNAVAILABLE",
        "market_cap_blocker": market_cap_blocker,
        **market,
    }
    for item_id in TEV_COMPONENT_ITEM_IDS:
        result[f"{item_id}_available"] = component_present_at_quarter(
            eligible_balance, item_id, latest_quarter
        )
    for item_id in EBIT_CANDIDATE_ITEM_IDS:
        result[f"ebit_candidate_{item_id}_4q_available"] = selection.four_consecutive and item_present_for_quarters(eligible_income, item_id, selection.selected_quarters)
    for item_id in EARNINGS_CANDIDATE_ITEM_IDS:
        result[f"earnings_candidate_{item_id}_4q_available"] = selection.four_consecutive and item_present_for_quarters(eligible_income, item_id, selection.selected_quarters)

    required_tev = (
        result["short_term_borrowings_available"],
        result["long_term_borrowings_available"],
        result["cash_and_cash_equivalents_available"],
    )
    market_cap_ready = direct_available or bool(result["proxy_market_cap_eligible"])
    result["complete_tev_input_available"] = bool(market_cap_ready and all(required_tev))
    result["ebit_candidate_operating_line_inputs_available"] = bool(
        result["ebit_candidate_operating_profit_loss_4q_available"]
    )
    result["ebit_candidate_pretax_interest_inputs_available"] = bool(
        result["ebit_candidate_net_accounting_profit_loss_before_tax_4q_available"]
        and result["ebit_candidate_interest_expenses_4q_available"]
    )
    result["ebit_production_item_ids"] = "|".join(EBIT_PRODUCTION_ITEM_IDS)
    result["ep_production_item_id"] = EP_PRODUCTION_ITEM_ID
    result["ep_diagnostic_item_id"] = EP_DIAGNOSTIC_ITEM_ID
    result["complete_ep_total_data_ready"] = bool(
        market_cap_ready and result["earnings_candidate_net_profit_loss_after_tax_4q_available"]
    )
    result["complete_ep_parent_data_ready"] = bool(
        market_cap_ready and result["earnings_candidate_attributable_to_parent_company_4q_available"]
    )
    result["source"] = "merged Sprint 4 survivors + existing immutable quarterly fundamentals cache"
    result["as_of"] = max(
        [str(value) for value in (*income.get("as_of", pd.Series(dtype=str)).dropna().unique(), *balance.get("as_of", pd.Series(dtype=str)).dropna().unique())],
        default="",
    )
    result["data_status"] = "READINESS_AUDIT_ONLY"
    return result


def run_audit() -> pd.DataFrame:
    survivors = pd.read_csv(SURVIVORS_PATH)
    if survivors["ticker"].duplicated().any():
        raise ValueError("duplicate ticker in Sprint 4 survivor input")
    audited = pd.DataFrame(audit_survivor(row) for row in survivors.to_dict("records"))
    if len(audited) != len(survivors):
        raise AssertionError("readiness audit row count does not match survivors")
    positive_count = int(audited["interest_expenses_positive_quarter_count"].sum())
    negative_count = int(audited["interest_expenses_negative_quarter_count"].sum())
    magnitude_rule = determine_interest_expense_magnitude_rule(
        positive_count, negative_count
    )
    audited["interest_expense_magnitude_rule"] = magnitude_rule
    audited["interest_expense_magnitude_rule_ready"] = (
        audited["interest_expenses_sign_pattern"].map(
            lambda pattern: interest_expense_pattern_is_ready(pattern, magnitude_rule)
        )
        & audited["ebit_candidate_pretax_interest_inputs_available"]
    )
    audited["complete_ebit_tev_data_ready"] = (
        audited["complete_tev_input_available"]
        & audited["ebit_candidate_pretax_interest_inputs_available"]
        & audited["interest_expense_magnitude_rule_ready"]
    )
    audited["complete_ep_production_data_ready"] = audited[
        "complete_ep_parent_data_ready"
    ]
    return audited


def main() -> int:
    audited = run_audit()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    audited.to_csv(OUTPUT_PATH, index=False)
    print(f"input={SURVIVORS_PATH.relative_to(ROOT).as_posix()}; rows={len(audited)}")
    print(f"output={OUTPUT_PATH.relative_to(ROOT).as_posix()}; rows={len(audited)}")
    print(f"four_consecutive={int(audited['four_consecutive_eligible_quarters'].sum())}")
    print(f"direct_market_cap={int(audited['direct_market_cap_available'].sum())}")
    print(f"proxy_eligible={int(audited['proxy_market_cap_eligible'].sum())}")
    print(
        "interest_sign="
        f"positive={int(audited['interest_expenses_positive_quarter_count'].sum())}; "
        f"negative={int(audited['interest_expenses_negative_quarter_count'].sum())}; "
        f"zero={int(audited['interest_expenses_zero_quarter_count'].sum())}; "
        f"mixed_tickers={int(audited['interest_expenses_sign_pattern'].eq('MIXED_NONZERO_SIGNS').sum())}; "
        f"rule={audited['interest_expense_magnitude_rule'].iloc[0]}"
    )
    print("network_calls=0; valuation_values=0; rankings=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
