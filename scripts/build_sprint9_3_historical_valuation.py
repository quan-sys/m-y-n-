from __future__ import annotations

import argparse
from datetime import datetime
from decimal import Decimal, InvalidOperation, getcontext
import gzip
import hashlib
import io
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
getcontext().prec = 50

ROOT = Path(__file__).resolve().parents[1]
FUNDAMENTALS_PATH = (
    ROOT
    / "data"
    / "fundamentals"
    / "quarterly_pit"
    / "2026-07-26"
    / "quarterly_items_point_in_time.csv.gz"
)
MARKET_CAP_PATH = (
    ROOT
    / "data"
    / "market_cap"
    / "2026-07-24"
    / "market_cap_point_in_time.csv"
)
REPORT_PATH = ROOT / "docs" / "REPORT_SPRINT_9_3_HISTORICAL_VALUATION.md"
OUTPUT_ROOT = ROOT / "data" / "valuation"
OVERRIDES_PATH = ROOT / "manual_inputs" / "interest_sign_overrides.csv"
TIME_ZONE = ZoneInfo("Asia/Ho_Chi_Minh")
UNIT_BRIDGE_RATIO = Decimal("1000")
MAX_OUTPUT_ROWS = 7_776

OUTPUT_COLUMNS = (
    "ticker",
    "quarter",
    "evaluation_date",
    "ttm_quarters",
    "stock_quarter",
    "ttm_pbt",
    "ttm_interest_magnitude",
    "interest_override_applied",
    "ebit_proxy_vas",
    "ttm_attributable_to_parent_company",
    "market_cap_thousand_vnd",
    "market_cap_vnd",
    "short_term_borrowings",
    "long_term_borrowings",
    "cash_and_cash_equivalents",
    "minority_interests",
    "minority_interest_status",
    "tev",
    "ebit_tev",
    "e_p",
    "ebit_tev_eligible",
    "e_p_eligible",
    "price_confidence",
    "market_cap_status",
    "valuation_status",
    "source",
    "as_of",
    "data_status",
)
FLOW_ITEMS = (
    "net_accounting_profit_loss_before_tax",
    "interest_expenses",
    "attributable_to_parent_company",
)
STOCK_ITEMS = (
    "short_term_borrowings",
    "long_term_borrowings",
    "cash_and_cash_equivalents",
    "minority_interests",
)
DIAGNOSTIC_LABEL = (
    "DIAGNOSTIC ONLY — quasi point-in-time, restated fundamentals, "
    "survivorship-affected universe; valid for RELATIVE walk-forward comparison, "
    "not as an absolute return expectation or a recommendation."
)
SOURCE_LABEL = (
    DIAGNOSTIC_LABEL
    + " | fundamentals=quarterly_pit/2026-07-26; "
    "market_cap=market_cap/2026-07-24"
)
VALID_STATUSES = {
    "OK",
    "INSUFFICIENT_TTM",
    "NO_MARKET_CAP",
    "NON_POSITIVE_TEV",
}
OVERRIDE_COLUMNS = (
    "ticker",
    "quarter",
    "raw_interest_expenses",
    "override_action",
    "status",
    "evidence_url",
    "published_date",
    "recorded_at",
    "note",
)
VALID_OVERRIDE_ACTIONS = {"ABS", "SUBTRACT"}
VALID_OVERRIDE_STATUSES = {
    "VERIFIED_INCOME",
    "SUSPECTED_SIGN_ERROR",
    "UNVERIFIED",
}


def _missing(value: Any) -> bool:
    return value is None or str(value).strip().lower() in {"", "nan", "none", "<na>"}


def to_decimal(value: Any) -> Decimal | None:
    if _missing(value):
        return None
    try:
        return Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError(f"non-decimal financial value: {value}") from exc


def decimal_text(value: Decimal | None) -> str:
    if value is None:
        return ""
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def decimal_summary(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return format(Decimal(str(value)), ".12g")


def market_cap_to_vnd(market_cap_thousand_vnd: Decimal) -> Decimal:
    """Apply the thousand-VND-to-VND bridge exactly once."""
    return (market_cap_thousand_vnd * UNIT_BRIDGE_RATIO).normalize()


def calculate_tev(
    market_cap_vnd: Decimal,
    short_term_borrowings: Decimal,
    long_term_borrowings: Decimal,
    cash_and_cash_equivalents: Decimal,
    minority_interests: Decimal | None,
) -> Decimal:
    value = (
        market_cap_vnd
        + short_term_borrowings
        + long_term_borrowings
        - cash_and_cash_equivalents
    )
    if minority_interests is not None:
        value += minority_interests
    return value.normalize()


def normalize_quarter(value: str) -> str:
    return str(value).strip().upper().replace("-", "")


def quarter_ordinal(value: str) -> int:
    normalized = normalize_quarter(value)
    match = re.fullmatch(r"(\d{4})Q([1-4])", normalized)
    if not match:
        raise ValueError(f"invalid quarter: {value}")
    return int(match.group(1)) * 4 + int(match.group(2)) - 1


def quarter_from_ordinal(value: int) -> str:
    year, zero_based_quarter = divmod(value, 4)
    return f"{year}Q{zero_based_quarter + 1}"


def select_ttm_quarters(
    ticker_fundamentals: pd.DataFrame,
    evaluation_date: str,
) -> tuple[str, ...]:
    if ticker_fundamentals.empty:
        return ()
    eligible = ticker_fundamentals.loc[
        pd.to_datetime(ticker_fundamentals["available_from"], errors="raise")
        <= pd.Timestamp(evaluation_date)
    ]
    if eligible.empty:
        return ()
    observed = {
        normalize_quarter(value)
        for value in eligible["quarter"].astype(str).unique().tolist()
    }
    latest = max(observed, key=quarter_ordinal)
    latest_ordinal = quarter_ordinal(latest)
    window = tuple(
        quarter_from_ordinal(value)
        for value in range(latest_ordinal - 3, latest_ordinal + 1)
    )
    return window if all(quarter in observed for quarter in window) else ()


def _item_value(
    ticker_fundamentals: pd.DataFrame,
    quarter: str,
    item_id: str,
) -> Decimal | None:
    rows = ticker_fundamentals.loc[
        ticker_fundamentals["quarter"].eq(quarter)
        & ticker_fundamentals["item_id"].eq(item_id),
        "value",
    ]
    if len(rows) > 1:
        raise ValueError(f"duplicate fundamental key: {quarter}/{item_id}")
    return to_decimal(rows.iloc[0]) if len(rows) == 1 else None


def load_interest_overrides(
    path: Path | None = None,
) -> frozenset[tuple[str, str]]:
    """Return committed SUBTRACT keys, or no keys when the manual file is absent.

    SUBTRACT is applied as -abs(value); on an already-negative raw value that would convert a genuine interest expense into a credit, so SUBTRACT is only meaningful on strictly positive raw values.
    """
    source_path = path or OVERRIDES_PATH
    if not source_path.is_file():
        return frozenset()
    overrides = pd.read_csv(source_path, dtype=str, keep_default_na=False)
    if tuple(overrides.columns) != OVERRIDE_COLUMNS:
        raise ValueError(
            "interest overrides must use exactly these columns: "
            + ", ".join(OVERRIDE_COLUMNS)
        )
    overrides = overrides.copy()
    overrides["ticker"] = overrides["ticker"].str.strip().str.upper()
    overrides["quarter"] = overrides["quarter"].map(normalize_quarter)
    overrides["override_action"] = overrides["override_action"].str.strip().str.upper()
    overrides["status"] = overrides["status"].str.strip().str.upper()
    if overrides.duplicated(["ticker", "quarter"]).any():
        raise ValueError("interest overrides contain duplicate ticker/quarter rows")
    invalid_actions = sorted(
        set(overrides["override_action"]) - VALID_OVERRIDE_ACTIONS
    )
    if invalid_actions:
        raise ValueError(f"interest overrides contain invalid actions: {invalid_actions}")
    invalid_statuses = sorted(set(overrides["status"]) - VALID_OVERRIDE_STATUSES)
    if invalid_statuses:
        raise ValueError(f"interest overrides contain invalid statuses: {invalid_statuses}")
    for row in overrides.loc[
        overrides["override_action"].eq("SUBTRACT"),
        ["ticker", "quarter", "raw_interest_expenses"],
    ].itertuples(index=False):
        try:
            raw_interest = to_decimal(row.raw_interest_expenses)
        except ValueError as exc:
            raise ValueError(
                "SUBTRACT raw_interest_expenses must be strictly positive for "
                f"{row.ticker} {row.quarter}"
            ) from exc
        if raw_interest is None or raw_interest <= 0:
            raise ValueError(
                "SUBTRACT raw_interest_expenses must be strictly positive for "
                f"{row.ticker} {row.quarter}"
            )
    return frozenset(
        (row.ticker, row.quarter)
        for row in overrides.loc[
            overrides["override_action"].eq("SUBTRACT"), ["ticker", "quarter"]
        ].itertuples(index=False)
    )


def _interest_override_keys(
    ticker: str,
    quarters: Iterable[str],
    interest_overrides: frozenset[tuple[str, str]],
) -> tuple[str, ...]:
    ticker_key = str(ticker).strip().upper()
    return tuple(
        f"{ticker_key}:{normalize_quarter(quarter)}"
        for quarter in quarters
        if (ticker_key, normalize_quarter(quarter)) in interest_overrides
    )


def _sum_item(
    ticker_fundamentals: pd.DataFrame,
    quarters: Iterable[str],
    item_id: str,
    *,
    absolute: bool = False,
    interest_overrides: frozenset[tuple[str, str]] = frozenset(),
) -> Decimal | None:
    window = tuple(quarters)
    values = [_item_value(ticker_fundamentals, quarter, item_id) for quarter in window]
    if any(value is None for value in values):
        return None
    if absolute and item_id == "interest_expenses":
        tickers = ticker_fundamentals["ticker"].str.strip().str.upper().unique()
        if len(tickers) != 1:
            raise ValueError("interest overrides require exactly one ticker per valuation")
        ticker = str(tickers[0])
        usable = [
            -abs(value)
            if (ticker, normalize_quarter(quarter)) in interest_overrides
            else abs(value)
            for quarter, value in zip(window, values, strict=True)
            if value is not None
        ]
    else:
        usable = [
            abs(value) if absolute else value for value in values if value is not None
        ]
    return sum(usable, Decimal("0")).normalize()


def build_valuation_row(
    market_row: dict[str, Any] | pd.Series,
    ticker_fundamentals: pd.DataFrame,
    *,
    run_date: str,
    interest_overrides: frozenset[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    ticker = str(market_row["ticker"]).strip().upper()
    active_interest_overrides = (
        load_interest_overrides()
        if interest_overrides is None
        else interest_overrides
    )
    quarter = normalize_quarter(str(market_row["quarter"]))
    evaluation_date = str(market_row["measurement_date"])
    market_cap_status = str(market_row["market_cap_status"])
    price_confidence = "" if _missing(market_row.get("price_confidence")) else str(
        market_row["price_confidence"]
    )
    market_cap_thousand = to_decimal(market_row.get("market_cap_thousand_vnd"))
    usable_market_cap = (
        market_cap_status not in {"NO_PRICE", "NO_SHARE_COUNT"}
        and market_cap_thousand is not None
    )
    market_cap_vnd = (
        market_cap_to_vnd(market_cap_thousand)
        if usable_market_cap and market_cap_thousand is not None
        else None
    )

    ttm_quarters = select_ttm_quarters(ticker_fundamentals, evaluation_date)
    stock_quarter = ttm_quarters[-1] if len(ttm_quarters) == 4 else ""
    ttm_pbt = (
        _sum_item(
            ticker_fundamentals,
            ttm_quarters,
            "net_accounting_profit_loss_before_tax",
        )
        if stock_quarter
        else None
    )
    ttm_interest = (
        _sum_item(
            ticker_fundamentals,
            ttm_quarters,
            "interest_expenses",
            absolute=True,
            interest_overrides=active_interest_overrides,
        )
        if stock_quarter
        else None
    )
    ttm_parent = (
        _sum_item(
            ticker_fundamentals,
            ttm_quarters,
            "attributable_to_parent_company",
        )
        if stock_quarter
        else None
    )
    ebit_proxy = (
        (ttm_pbt + ttm_interest).normalize()
        if ttm_pbt is not None and ttm_interest is not None
        else None
    )
    interest_override_applied = "|".join(
        _interest_override_keys(
            ticker,
            ttm_quarters,
            active_interest_overrides,
        )
    )

    short_debt = (
        _item_value(ticker_fundamentals, stock_quarter, "short_term_borrowings")
        if stock_quarter
        else None
    )
    long_debt = (
        _item_value(ticker_fundamentals, stock_quarter, "long_term_borrowings")
        if stock_quarter
        else None
    )
    cash = (
        _item_value(
            ticker_fundamentals, stock_quarter, "cash_and_cash_equivalents"
        )
        if stock_quarter
        else None
    )
    minority = (
        _item_value(ticker_fundamentals, stock_quarter, "minority_interests")
        if stock_quarter
        else None
    )
    minority_status = "AVAILABLE" if minority is not None else "UNAVAILABLE"

    complete_fundamentals = (
        len(ttm_quarters) == 4
        and ebit_proxy is not None
        and ttm_parent is not None
        and short_debt is not None
        and long_debt is not None
        and cash is not None
    )
    tev: Decimal | None = None
    ebit_tev: Decimal | None = None
    e_p: Decimal | None = None
    ebit_tev_eligible = False
    e_p_eligible = False

    if not usable_market_cap:
        valuation_status = "NO_MARKET_CAP"
    elif not complete_fundamentals or market_cap_vnd is None:
        valuation_status = "INSUFFICIENT_TTM"
    else:
        tev = calculate_tev(
            market_cap_vnd,
            short_debt,
            long_debt,
            cash,
            minority,
        )
        if tev != 0:
            ebit_tev = (ebit_proxy / tev).normalize()
        e_p = (ttm_parent / market_cap_vnd).normalize()
        ebit_tev_eligible = ebit_proxy >= 0 and tev > 0
        e_p_eligible = ttm_parent >= 0
        valuation_status = "NON_POSITIVE_TEV" if tev <= 0 else "OK"

    if valuation_status not in VALID_STATUSES:
        raise ValueError(f"invalid valuation_status: {valuation_status}")
    data_status = (
        "OK"
        if valuation_status in {"OK", "NON_POSITIVE_TEV"}
        else "MISSING_DATA"
    )
    return {
        "ticker": ticker,
        "quarter": quarter,
        "evaluation_date": evaluation_date,
        "ttm_quarters": "|".join(ttm_quarters),
        "stock_quarter": stock_quarter,
        "ttm_pbt": ttm_pbt,
        "ttm_interest_magnitude": ttm_interest,
        "interest_override_applied": interest_override_applied,
        "ebit_proxy_vas": ebit_proxy,
        "ttm_attributable_to_parent_company": ttm_parent,
        "market_cap_thousand_vnd": market_cap_thousand,
        "market_cap_vnd": market_cap_vnd,
        "short_term_borrowings": short_debt,
        "long_term_borrowings": long_debt,
        "cash_and_cash_equivalents": cash,
        "minority_interests": minority,
        "minority_interest_status": minority_status,
        "tev": tev,
        "ebit_tev": ebit_tev,
        "e_p": e_p,
        "ebit_tev_eligible": ebit_tev_eligible,
        "e_p_eligible": e_p_eligible,
        "price_confidence": price_confidence,
        "market_cap_status": market_cap_status,
        "valuation_status": valuation_status,
        "source": SOURCE_LABEL,
        "as_of": run_date,
        "data_status": data_status,
    }


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    fundamentals = pd.read_csv(FUNDAMENTALS_PATH, dtype=str, keep_default_na=False)
    market_cap = pd.read_csv(MARKET_CAP_PATH, dtype=str, keep_default_na=False)
    expected_fundamental_columns = {
        "ticker",
        "quarter",
        "available_from",
        "item_id",
        "value",
    }
    expected_market_columns = {
        "ticker",
        "quarter",
        "measurement_date",
        "market_cap_thousand_vnd",
        "price_confidence",
        "market_cap_status",
    }
    if missing := sorted(expected_fundamental_columns - set(fundamentals.columns)):
        raise ValueError(f"fundamentals missing columns: {missing}")
    if missing := sorted(expected_market_columns - set(market_cap.columns)):
        raise ValueError(f"market cap missing columns: {missing}")

    fundamentals["ticker"] = fundamentals["ticker"].str.strip().str.upper()
    fundamentals["quarter"] = fundamentals["quarter"].map(normalize_quarter)
    market_cap["ticker"] = market_cap["ticker"].str.strip().str.upper()
    market_cap["quarter"] = market_cap["quarter"].map(normalize_quarter)
    duplicate_fundamentals = fundamentals.duplicated(
        ["ticker", "quarter", "item_id"], keep=False
    )
    if bool(duplicate_fundamentals.any()):
        raise ValueError("fundamentals contain duplicate ticker/quarter/item_id rows")
    if bool(market_cap.duplicated(["ticker", "quarter"], keep=False).any()):
        raise ValueError("market cap contains duplicate ticker/quarter rows")
    return fundamentals, market_cap


def build_output(
    fundamentals: pd.DataFrame,
    market_cap: pd.DataFrame,
    *,
    run_date: str,
) -> pd.DataFrame:
    interest_overrides = load_interest_overrides()
    fundamental_keys = fundamentals.loc[:, ["ticker", "quarter"]].drop_duplicates()
    grid = market_cap.merge(
        fundamental_keys,
        on=["ticker", "quarter"],
        how="inner",
        validate="one_to_one",
    )
    grouped = {
        ticker: frame.copy()
        for ticker, frame in fundamentals.groupby("ticker", sort=False)
    }
    rows = [
        build_valuation_row(
            market_row,
            grouped[str(market_row["ticker"])],
            run_date=run_date,
            interest_overrides=interest_overrides,
        )
        for market_row in grid.to_dict(orient="records")
    ]
    return (
        pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
        .sort_values(["ticker", "quarter"], kind="stable")
        .reset_index(drop=True)
    )


def _parse_ttm(value: str) -> tuple[str, ...]:
    return tuple(part for part in str(value).split("|") if part)


def validate_stop_gates(output: pd.DataFrame, fundamentals: pd.DataFrame) -> None:
    if len(output) > MAX_OUTPUT_ROWS:
        raise RuntimeError(
            f"STOP: output row count {len(output)} exceeds {MAX_OUTPUT_ROWS}"
        )
    if bool(output.duplicated(["ticker", "quarter"], keep=False).any()):
        raise RuntimeError("STOP: duplicate ticker/quarter output rows")

    fundamentals_index = fundamentals.set_index(["ticker", "quarter", "item_id"])
    lookahead_rows: list[dict[str, str]] = []
    invalid_windows: list[dict[str, str]] = []
    invalid_bridges: list[dict[str, str]] = []
    for row in output.itertuples(index=False):
        ttm_quarters = _parse_ttm(row.ttm_quarters)
        if len(ttm_quarters) != len(set(ttm_quarters)):
            invalid_windows.append(
                {
                    "ticker": row.ticker,
                    "quarter": row.quarter,
                    "reason": "REPEATED_TTM_QUARTER",
                }
            )
        if row.valuation_status == "OK" and len(ttm_quarters) != 4:
            invalid_windows.append(
                {
                    "ticker": row.ticker,
                    "quarter": row.quarter,
                    "reason": "OK_WITHOUT_FOUR_TTM_QUARTERS",
                }
            )
        for ttm_quarter in ttm_quarters:
            key = (
                row.ticker,
                ttm_quarter,
                "net_accounting_profit_loss_before_tax",
            )
            if key in fundamentals_index.index:
                available_from = str(fundamentals_index.loc[key, "available_from"])
                if pd.Timestamp(available_from) > pd.Timestamp(row.evaluation_date):
                    lookahead_rows.append(
                        {
                            "ticker": row.ticker,
                            "quarter": row.quarter,
                            "ttm_quarter": ttm_quarter,
                            "available_from": available_from,
                            "evaluation_date": row.evaluation_date,
                        }
                    )
        thousand = to_decimal(row.market_cap_thousand_vnd)
        vnd = to_decimal(row.market_cap_vnd)
        if thousand is not None or vnd is not None:
            if thousand is None or vnd is None or vnd / thousand != UNIT_BRIDGE_RATIO:
                invalid_bridges.append(
                    {
                        "ticker": row.ticker,
                        "quarter": row.quarter,
                        "market_cap_thousand_vnd": decimal_text(thousand),
                        "market_cap_vnd": decimal_text(vnd),
                    }
                )
    if lookahead_rows:
        raise RuntimeError(f"STOP: look-ahead TTM rows: {lookahead_rows}")
    if invalid_windows:
        raise RuntimeError(f"STOP: invalid TTM windows: {invalid_windows}")
    if invalid_bridges:
        raise RuntimeError(f"STOP: invalid market-cap bridges: {invalid_bridges}")


def _output_for_csv(output: pd.DataFrame) -> pd.DataFrame:
    serializable = output.copy()
    decimal_columns = (
        "ttm_pbt",
        "ttm_interest_magnitude",
        "ebit_proxy_vas",
        "ttm_attributable_to_parent_company",
        "market_cap_thousand_vnd",
        "market_cap_vnd",
        "short_term_borrowings",
        "long_term_borrowings",
        "cash_and_cash_equivalents",
        "minority_interests",
        "tev",
        "ebit_tev",
        "e_p",
    )
    for column in decimal_columns:
        serializable[column] = serializable[column].map(decimal_text)
    return serializable.loc[:, OUTPUT_COLUMNS]


def write_deterministic_gzip(output: pd.DataFrame, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = _output_for_csv(output)
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
                serializable.to_csv(text, index=False, lineterminator="\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def interest_anomalies(fundamentals: pd.DataFrame) -> pd.DataFrame:
    relevant = fundamentals.loc[
        fundamentals["item_id"].isin(["interest_expenses", "financial_expenses"])
    ].copy()
    pivot = relevant.pivot(
        index=["ticker", "quarter"], columns="item_id", values="value"
    ).reset_index()
    pivot["interest_expenses"] = pivot["interest_expenses"].map(to_decimal)
    pivot["financial_expenses"] = pivot["financial_expenses"].map(to_decimal)
    usable = pivot.loc[
        pivot["interest_expenses"].notna() & pivot["financial_expenses"].notna()
    ].copy()
    return usable.loc[
        usable.apply(
            lambda row: abs(row["interest_expenses"])
            > abs(row["financial_expenses"]),
            axis=1,
        )
    ].sort_values(["ticker", "quarter"], kind="stable")


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


def _window_frames(output: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "ALL": output,
        "PRICE_CONFIDENCE_OK": output.loc[output["price_confidence"].eq("OK")],
    }


def _distribution_rows(output: pd.DataFrame) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for window, frame in _window_frames(output).items():
        for metric, eligible_column in (
            ("ebit_tev", "ebit_tev_eligible"),
            ("e_p", "e_p_eligible"),
        ):
            values = [
                float(value)
                for value in frame.loc[frame[eligible_column], metric].tolist()
                if value is not None
            ]
            series = pd.Series(values, dtype="float64")
            rows.append(
                [
                    window,
                    metric,
                    len(series),
                    decimal_summary(series.min()) if not series.empty else "",
                    decimal_summary(series.quantile(0.10)) if not series.empty else "",
                    decimal_summary(series.median()) if not series.empty else "",
                    decimal_summary(series.quantile(0.90)) if not series.empty else "",
                    decimal_summary(series.max()) if not series.empty else "",
                ]
            )
    return rows


def _spearman(left: pd.Series, right: pd.Series) -> float | None:
    if len(left) < 2:
        return None
    left_rank = pd.to_numeric(left, errors="coerce").rank(method="average")
    right_rank = pd.to_numeric(right, errors="coerce").rank(method="average")
    value = left_rank.corr(right_rank, method="pearson")
    return None if pd.isna(value) else float(value)


def worked_vnm_lines(
    output: pd.DataFrame,
    fundamentals: pd.DataFrame,
) -> list[str]:
    row = output.loc[
        output["ticker"].eq("VNM")
        & output["evaluation_date"].eq("2024-12-31")
    ].iloc[0]
    vnm = fundamentals.loc[fundamentals["ticker"].eq("VNM")]
    quarters = _parse_ttm(row["ttm_quarters"])
    lines = [
        f"- evaluation_date = `2024-12-31`.",
        "- 2024Q4 is excluded because `available_from=2025-01-30` is after `evaluation_date=2024-12-31`.",
        f"- ttm_quarters = `{'|'.join(quarters)}`.",
    ]
    pbt_values = [
        _item_value(vnm, quarter, "net_accounting_profit_loss_before_tax")
        for quarter in quarters
    ]
    interest_values = [
        _item_value(vnm, quarter, "interest_expenses") for quarter in quarters
    ]
    parent_values = [
        _item_value(vnm, quarter, "attributable_to_parent_company")
        for quarter in quarters
    ]
    for quarter, value in zip(quarters, pbt_values, strict=True):
        lines.append(
            f"- net_accounting_profit_loss_before_tax[{quarter}] = `{decimal_text(value)}` VND."
        )
    lines.append(f"- ttm_pbt = `{decimal_text(row['ttm_pbt'])}` VND.")
    for quarter, value in zip(quarters, interest_values, strict=True):
        lines.append(
            f"- abs(interest_expenses[{quarter}]) = `{decimal_text(abs(value) if value is not None else None)}` VND."
        )
    lines.extend(
        [
            f"- ttm_interest_magnitude = `{decimal_text(row['ttm_interest_magnitude'])}` VND.",
            f"- ebit_proxy_vas = `{decimal_text(row['ebit_proxy_vas'])}` VND.",
            f"- stock_quarter = `{row['stock_quarter']}`.",
            f"- short_term_borrowings = `{decimal_text(row['short_term_borrowings'])}` VND.",
            f"- long_term_borrowings = `{decimal_text(row['long_term_borrowings'])}` VND.",
            f"- cash_and_cash_equivalents = `{decimal_text(row['cash_and_cash_equivalents'])}` VND.",
            f"- minority_interests = `{decimal_text(row['minority_interests'])}` VND.",
            f"- market_cap_thousand_vnd = `{decimal_text(row['market_cap_thousand_vnd'])}`.",
            f"- market_cap_vnd = `{decimal_text(row['market_cap_vnd'])}`.",
            "- Anchor check: `market_cap_thousand_vnd=133044183264.750106811523`, therefore `market_cap_vnd=133044183264750.106811523`, and it must NOT equal `133044183264.75`.",
            "- tev = market_cap_vnd + short_term_borrowings + long_term_borrowings - cash_and_cash_equivalents + minority_interests.",
            f"- tev = `{decimal_text(row['tev'])}` VND.",
            f"- ebit_tev = `{decimal_text(row['ebit_tev'])}`.",
        ]
    )
    for quarter, value in zip(quarters, parent_values, strict=True):
        lines.append(
            f"- attributable_to_parent_company[{quarter}] = `{decimal_text(value)}` VND."
        )
    lines.extend(
        [
            f"- ttm_attributable_to_parent_company = `{decimal_text(row['ttm_attributable_to_parent_company'])}` VND.",
            f"- e_p = `{decimal_text(row['e_p'])}`.",
        ]
    )
    return lines


def write_report(
    *,
    run_date: str,
    output_path: Path,
    output: pd.DataFrame,
    fundamentals: pd.DataFrame,
    market_cap: pd.DataFrame,
    sha256: str,
) -> None:
    windows = _window_frames(output)
    v1_rows: list[list[Any]] = []
    for window, frame in windows.items():
        for dimension in ("valuation_status", "market_cap_status"):
            for status, count in frame[dimension].value_counts().sort_index().items():
                v1_rows.append([window, dimension, status, int(count)])

    v2_rows: list[list[Any]] = []
    for window, frame in windows.items():
        computable_ebit_tev = int(frame["ebit_tev"].notna().sum())
        computable_ep = int(frame["e_p"].notna().sum())
        negative_ebit = int(
            sum(
                value is not None and value < 0
                for value in frame["ebit_proxy_vas"].tolist()
            )
        )
        non_positive_tev = int(
            sum(value is not None and value <= 0 for value in frame["tev"].tolist())
        )
        negative_earnings = int(
            sum(
                value is not None and value < 0
                for value in frame["ttm_attributable_to_parent_company"].tolist()
            )
        )
        v2_rows.extend(
            [
                [window, "computable_ebit_tev", computable_ebit_tev],
                [window, "computable_e_p", computable_ep],
                [window, "excluded_negative_ebit", negative_ebit],
                [window, "excluded_non_positive_tev", non_positive_tev],
                [window, "excluded_negative_earnings", negative_earnings],
            ]
        )

    v4_rows: list[list[Any]] = []
    for window, frame in windows.items():
        work = frame.copy()
        work["calendar_year"] = work["quarter"].str[:4]
        for year in range(2018, 2026):
            year_frame = work.loc[work["calendar_year"].eq(str(year))]
            v4_rows.append(
                [
                    window,
                    year,
                    int(
                        year_frame.loc[year_frame["ebit_tev"].notna(), "ticker"].nunique()
                    ),
                ]
            )

    v5_rows: list[list[Any]] = []
    for window, frame in windows.items():
        work = frame.loc[frame["ebit_tev"].notna() & frame["e_p"].notna()].copy()
        work["calendar_year"] = work["quarter"].str[:4]
        for year in range(2018, 2026):
            year_frame = work.loc[work["calendar_year"].eq(str(year))]
            correlation = _spearman(
                year_frame["ebit_tev"], year_frame["e_p"]
            )
            v5_rows.append(
                [
                    window,
                    year,
                    len(year_frame),
                    "" if correlation is None else f"{correlation:.12g}",
                ]
            )

    anomalies = interest_anomalies(fundamentals)
    confidence = market_cap.loc[
        :, ["ticker", "quarter", "price_confidence"]
    ].copy()
    anomalies = anomalies.merge(
        confidence, on=["ticker", "quarter"], how="left", validate="one_to_one"
    )
    anomaly_rows = [
        [
            row.ticker,
            row.quarter,
            decimal_text(row.interest_expenses),
            decimal_text(row.financial_expenses),
        ]
        for row in anomalies.head(20).itertuples(index=False)
    ]

    lines = [
        "# Sprint 9-3 Historical Valuation Diagnostics",
        "",
        f"> {DIAGNOSTIC_LABEL}",
        "",
        "Sprint 9-3 supersedes Sprint 5 section 3 only for this historical input: Sprint 5's no-x1000 rule remains correct for the current KBS VND-price proxy, while Sprint 9-3 uses Sprint 9-1b de-adjusted historical prices and Sprint 9-1c market cap explicitly stored in thousand VND, so the single x1000 bridge in 9-3-3 applies here.",
        "",
        "For `market_cap_status=UPPER_BOUND`, market cap is an upper bound, therefore TEV is an upper bound and both EBIT/TEV and E/P are lower bounds; `market_cap_status` and `price_confidence` remain separate.",
        "",
        "## V1 — Status counts",
        "",
        _markdown_table(
            ["window", "dimension", "status", "row_count"],
            v1_rows,
        ),
        "",
        "## V2 — Computable metrics and exclusion reasons",
        "",
        _markdown_table(["window", "measure", "row_count"], v2_rows),
        "",
        "## V3 — Diagnostic metric distributions",
        "",
        _markdown_table(
            ["window", "metric", "n", "min", "p10", "median", "p90", "max"],
            _distribution_rows(output),
        ),
        "",
        "These are diagnostic distributions, not a ranking.",
        "",
        "## V4 — Computable EBIT/TEV coverage by calendar year",
        "",
        _markdown_table(
            ["window", "calendar_year", "tickers_with_computable_ebit_tev"],
            v4_rows,
        ),
        "",
        "## V5 — Annual Spearman correlation",
        "",
        _markdown_table(
            ["window", "calendar_year", "rows_with_both", "spearman"],
            v5_rows,
        ),
        "",
        "A low correlation means EBIT/TEV and E/P would select different portfolios; the choice between them is not cosmetic.",
        "",
        "## V6 — Interest-expense anomalies",
        "",
        f"- ALL anomaly rows: `{len(anomalies)}`.",
        f"- PRICE_CONFIDENCE_OK anomaly rows: `{int(anomalies['price_confidence'].eq('OK').sum())}`.",
        "- First 20 anomaly rows:",
        "",
        _markdown_table(
            [
                "ticker",
                "quarter",
                "interest_expenses",
                "financial_expenses",
            ],
            anomaly_rows,
        ),
        "",
        "## V7 — Unavailable minority interest",
        "",
        f"- ALL rows with minority_interest_status=UNAVAILABLE: `{int(output['minority_interest_status'].eq('UNAVAILABLE').sum())}`.",
        f"- PRICE_CONFIDENCE_OK rows with minority_interest_status=UNAVAILABLE: `{int(windows['PRICE_CONFIDENCE_OK']['minority_interest_status'].eq('UNAVAILABLE').sum())}`.",
        "- None was filled with 0.",
        "",
        "## V8 — VNM worked arithmetic at 2024-12-31",
        "",
        *worked_vnm_lines(output, fundamentals),
        "",
        "## V9 — Output identity",
        "",
        f"- RUN_DATE: `{run_date}`.",
        f"- Output path: `{output_path.relative_to(ROOT).as_posix()}`.",
        f"- Row count: `{len(output)}`.",
        f"- SHA-256: `{sha256}`.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Sprint 9-3 historical valuation diagnostics."
    )
    parser.add_argument("--run-date", help="Asia/Ho_Chi_Minh date (YYYY-MM-DD).")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_date = args.run_date or datetime.now(TIME_ZONE).date().isoformat()
    output_path = (
        OUTPUT_ROOT / run_date / "historical_valuation_point_in_time.csv.gz"
    )
    print(f"RUN_DATE={run_date}")
    fundamentals, market_cap = load_inputs()
    output = build_output(fundamentals, market_cap, run_date=run_date)
    validate_stop_gates(output, fundamentals)
    sha256 = write_deterministic_gzip(output, output_path)
    write_report(
        run_date=run_date,
        output_path=output_path,
        output=output,
        fundamentals=fundamentals,
        market_cap=market_cap,
        sha256=sha256,
    )
    print(f"OUTPUT={output_path}")
    print(f"ROW_COUNT={len(output)}")
    print(f"SHA256={sha256}")
    print(f"REPORT={REPORT_PATH}")
    print("VNM_WORKED_TABLE_START")
    for line in worked_vnm_lines(output, fundamentals):
        print(line)
    print("VNM_WORKED_TABLE_END")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
