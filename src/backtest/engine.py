from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from math import ceil
from pathlib import Path
from typing import Any

import pandas as pd


PRICE_UNAVAILABLE = "PRICE_UNAVAILABLE"
KNOWN_BIASES = (
    "The universe contains only companies listed today, so companies delisted before today are absent "
    "and those are disproportionately the worst performers.",
    "All fundamentals from Sprint 3-7 are restated data and are not point-in-time.",
    "Results are usable only for RELATIVE comparison between configurations sharing the same bias, "
    "never as an expected return.",
)


@dataclass(frozen=True)
class EngineConfig:
    min_traded_sessions_12m: int
    ticker_identity_gap_days: int
    brokerage_fee_pct_per_side: float
    sell_tax_pct: float
    settlement_lag_days: int
    min_candidate_pool_multiple: float | None = None
    selection_ratio_report_threshold: float | None = None


@dataclass(frozen=True)
class EngineResult:
    value_series: pd.DataFrame
    rebalance_log: pd.DataFrame
    trade_log: pd.DataFrame
    ending_value: float | None
    known_biases: tuple[str, ...]
    assumptions: dict[str, float | int | str]


def load_engine_config(path: str | Path) -> EngineConfig:
    values: dict[str, str] = {}
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    required = (
        "MIN_TRADED_SESSIONS_12M",
        "TICKER_IDENTITY_GAP_DAYS",
        "BROKERAGE_FEE_PCT_PER_SIDE",
        "SELL_TAX_PCT",
        "SETTLEMENT_LAG_DAYS",
        "MIN_CANDIDATE_POOL_MULTIPLE",
        "SELECTION_RATIO_REPORT_THRESHOLD",
    )
    missing = [key for key in required if key not in values]
    if missing:
        raise ValueError("engine config missing values: " + ", ".join(missing))
    config = EngineConfig(
        min_traded_sessions_12m=int(values["MIN_TRADED_SESSIONS_12M"]),
        ticker_identity_gap_days=int(values["TICKER_IDENTITY_GAP_DAYS"]),
        brokerage_fee_pct_per_side=float(values["BROKERAGE_FEE_PCT_PER_SIDE"]),
        sell_tax_pct=float(values["SELL_TAX_PCT"]),
        settlement_lag_days=int(values["SETTLEMENT_LAG_DAYS"]),
        min_candidate_pool_multiple=float(values["MIN_CANDIDATE_POOL_MULTIPLE"]),
        selection_ratio_report_threshold=float(values["SELECTION_RATIO_REPORT_THRESHOLD"]),
    )
    if config.brokerage_fee_pct_per_side < 0 or config.sell_tax_pct < 0:
        raise ValueError("cost assumptions cannot be negative")
    if config.settlement_lag_days < 0:
        raise ValueError("settlement lag cannot be negative")
    if config.min_candidate_pool_multiple is None or config.min_candidate_pool_multiple <= 0:
        raise ValueError("candidate pool multiple must be positive")
    if config.selection_ratio_report_threshold is None or not (
        0 <= config.selection_ratio_report_threshold <= 1
    ):
        raise ValueError("selection ratio threshold must be between zero and one")
    return config


def _normalise_targets(targets: Mapping[str, float] | Sequence[str]) -> dict[str, float]:
    if isinstance(targets, Mapping):
        weights = {str(ticker).strip().upper(): float(weight) for ticker, weight in targets.items()}
    else:
        tickers = list(dict.fromkeys(str(ticker).strip().upper() for ticker in targets))
        weights = {ticker: 1.0 / len(tickers) for ticker in tickers} if tickers else {}
    if any(weight < 0 for weight in weights.values()):
        raise ValueError("long-only engine refuses negative target weights")
    if sum(weights.values()) > 1.0 + 1e-12:
        raise ValueError("target weights exceed 100%; leverage is forbidden")
    return weights


def _settlement_date(trade_date: pd.Timestamp, lag_days: int) -> str:
    return (trade_date + pd.offsets.BDay(lag_days)).date().isoformat()


def _exact_price(price_rows: pd.DataFrame, ticker: str, day: pd.Timestamp) -> float | None:
    matches = price_rows[
        (price_rows["ticker"] == ticker)
        & (price_rows["_date"] == day)
        & price_rows["_close"].notna()
        & price_rows["_volume"].notna()
        & (price_rows["_volume"] > 0)
    ]
    if matches.empty:
        return None
    return float(matches.iloc[-1]["_close"])


def run_engine(
    price_rows: pd.DataFrame,
    targets_by_rebalance: Mapping[str | date | pd.Timestamp, Mapping[str, float] | Sequence[str]],
    eligibility_by_rebalance: Mapping[str | date | pd.Timestamp, pd.DataFrame],
    *,
    config: EngineConfig,
    initial_value: float,
    candidate_pool_sizes_by_rebalance: Mapping[str | date | pd.Timestamp, int] | None = None,
    portfolio_size: int | None = None,
    valuation_date: str | date | pd.Timestamp | None = None,
) -> EngineResult:
    """Run mechanical long-only rebalances without computing performance metrics."""
    if initial_value <= 0:
        raise ValueError("initial_value must be positive")
    if portfolio_size is not None and portfolio_size < 1:
        raise ValueError("portfolio_size must be positive")
    window_rules_configured = (
        config.min_candidate_pool_multiple is not None
        and config.selection_ratio_report_threshold is not None
    )
    if (candidate_pool_sizes_by_rebalance is not None or portfolio_size is not None) and not (
        window_rules_configured
    ):
        raise ValueError("candidate pool rules require configured thresholds")
    required = {"ticker", "date", "close_adjusted", "volume"}
    missing = sorted(required.difference(price_rows.columns))
    if missing:
        raise ValueError("price rows missing columns: " + ", ".join(missing))
    if not KNOWN_BIASES or any(not text.strip() for text in KNOWN_BIASES):
        raise RuntimeError("Known biases section cannot be empty")

    prices = price_rows.copy()
    prices["ticker"] = prices["ticker"].astype(str).str.strip().str.upper()
    prices["_date"] = pd.to_datetime(prices["date"], errors="raise").dt.normalize()
    prices["_close"] = pd.to_numeric(prices["close_adjusted"], errors="coerce")
    prices["_volume"] = pd.to_numeric(prices["volume"], errors="coerce")

    eligibility_lookup = {
        pd.Timestamp(day).normalize(): frame.copy() for day, frame in eligibility_by_rebalance.items()
    }
    candidate_pool_lookup = (
        {
            pd.Timestamp(day).normalize(): int(pool_size)
            for day, pool_size in candidate_pool_sizes_by_rebalance.items()
        }
        if candidate_pool_sizes_by_rebalance is not None
        else None
    )
    rebalances = sorted(
        (pd.Timestamp(day).normalize(), targets) for day, targets in targets_by_rebalance.items()
    )
    holdings: dict[str, float] = {}
    cash = float(initial_value)
    trade_rows: list[dict[str, Any]] = []
    rebalance_rows: list[dict[str, Any]] = []
    value_rows: list[dict[str, Any]] = []
    window_started = False

    for rebalance_day, raw_targets in rebalances:
        cash_before = cash
        if rebalance_day not in eligibility_lookup:
            raise ValueError(f"missing eligibility frame for {rebalance_day.date().isoformat()}")
        eligibility = eligibility_lookup[rebalance_day].copy()
        eligibility["ticker"] = eligibility["ticker"].astype(str).str.strip().str.upper()
        eligibility_index = eligibility.set_index("ticker")
        weights = _normalise_targets(raw_targets)
        excluded: list[str] = []
        eligible_weights: dict[str, float] = {}
        for ticker, weight in weights.items():
            if ticker not in eligibility_index.index or not bool(eligibility_index.loc[ticker, "eligible"]):
                reason = (
                    str(eligibility_index.loc[ticker, "reason"])
                    if ticker in eligibility_index.index
                    else "INSUFFICIENT_TRADED_SESSIONS"
                )
                excluded.append(f"{ticker}:{reason}")
            else:
                eligible_weights[ticker] = weight

        if candidate_pool_lookup is not None:
            if rebalance_day not in candidate_pool_lookup:
                raise ValueError(
                    f"missing candidate pool size for {rebalance_day.date().isoformat()}"
                )
            candidate_pool_size = candidate_pool_lookup[rebalance_day]
        else:
            candidate_pool_size = len(weights)
        if candidate_pool_size < 0:
            raise ValueError("candidate_pool_size cannot be negative")
        if candidate_pool_size < len(eligible_weights):
            raise ValueError("candidate_pool_size cannot be smaller than selected_count")
        effective_portfolio_size = portfolio_size if portfolio_size is not None else len(weights)
        threshold = (
            ceil(config.min_candidate_pool_multiple * effective_portfolio_size)
            if config.min_candidate_pool_multiple is not None
            else 0
        )
        meets_threshold = candidate_pool_size >= threshold
        if not window_started and meets_threshold:
            window_started = True
        selection_ratio = (
            len(eligible_weights) / candidate_pool_size if candidate_pool_size else 0.0
        )
        period_flags: list[str] = []
        if window_started and not meets_threshold:
            period_flags.append("THIN_CANDIDATE_POOL")
        if (
            config.selection_ratio_report_threshold is not None
            and selection_ratio > config.selection_ratio_report_threshold
        ):
            period_flags.append("LOW_SELECTIVITY")

        price_map: dict[str, float] = {}
        unavailable: list[str] = []
        for ticker in sorted(set(holdings).union(eligible_weights)):
            price = _exact_price(prices, ticker, rebalance_day)
            if price is None:
                unavailable.append(ticker)
                excluded.append(f"{ticker}:{PRICE_UNAVAILABLE}")
                trade_rows.append(
                    {
                        "rebalance_date": rebalance_day.date().isoformat(),
                        "ticker": ticker,
                        "side": "",
                        "entry_price": "",
                        "gross_value": "",
                        "cost_paid": "",
                        "shares": "",
                        "settlement_date": "",
                        "status": PRICE_UNAVAILABLE,
                    }
                )
            else:
                price_map[ticker] = price

        missing_current = sorted(set(holdings).intersection(unavailable))
        cost_paid = 0.0
        status = PRICE_UNAVAILABLE if unavailable else "OK"
        if missing_current:
            portfolio_before: float | None = None
            portfolio_after: float | None = None
        else:
            portfolio_before = cash + sum(
                shares * price_map[ticker] for ticker, shares in holdings.items()
            )
            desired_values = {
                ticker: portfolio_before * weight
                for ticker, weight in eligible_weights.items()
                if ticker in price_map
            }

            for ticker in sorted(list(holdings)):
                current_value = holdings[ticker] * price_map[ticker]
                desired_value = desired_values.get(ticker, 0.0)
                if current_value <= desired_value + 1e-12:
                    continue
                gross = current_value - desired_value
                shares_sold = gross / price_map[ticker]
                cost = gross * (config.brokerage_fee_pct_per_side + config.sell_tax_pct)
                holdings[ticker] -= shares_sold
                if holdings[ticker] <= 1e-12:
                    del holdings[ticker]
                cash += gross - cost
                cost_paid += cost
                trade_rows.append(
                    {
                        "rebalance_date": rebalance_day.date().isoformat(),
                        "ticker": ticker,
                        "side": "SELL",
                        "entry_price": price_map[ticker],
                        "gross_value": gross,
                        "cost_paid": cost,
                        "shares": shares_sold,
                        "settlement_date": _settlement_date(rebalance_day, config.settlement_lag_days),
                        "status": "OK",
                    }
                )

            buy_needs: dict[str, float] = {}
            for ticker, desired_value in desired_values.items():
                current_value = holdings.get(ticker, 0.0) * price_map[ticker]
                if desired_value > current_value + 1e-12:
                    buy_needs[ticker] = desired_value - current_value
            required_cash = sum(
                gross * (1.0 + config.brokerage_fee_pct_per_side)
                for gross in buy_needs.values()
            )
            scale = min(1.0, cash / required_cash) if required_cash > 0 else 1.0
            for ticker in sorted(buy_needs):
                gross = buy_needs[ticker] * scale
                cost = gross * config.brokerage_fee_pct_per_side
                shares_bought = gross / price_map[ticker]
                holdings[ticker] = holdings.get(ticker, 0.0) + shares_bought
                cash -= gross + cost
                cost_paid += cost
                trade_rows.append(
                    {
                        "rebalance_date": rebalance_day.date().isoformat(),
                        "ticker": ticker,
                        "side": "BUY",
                        "entry_price": price_map[ticker],
                        "gross_value": gross,
                        "cost_paid": cost,
                        "shares": shares_bought,
                        "settlement_date": _settlement_date(rebalance_day, config.settlement_lag_days),
                        "status": "OK",
                    }
                )
            if abs(cash) <= 1e-9:
                cash = 0.0

            portfolio_after = cash + sum(
                shares * price_map[ticker] for ticker, shares in holdings.items()
            )
            value_rows.append(
                {
                    "date": rebalance_day.date().isoformat(),
                    "portfolio_value": portfolio_after,
                    "cash": cash,
                    "status": status,
                    "missing_tickers": "|".join(unavailable),
                }
            )

        rebalance_rows.append(
            {
                "date": rebalance_day.date().isoformat(),
                "eligible_count": int(eligibility["eligible"].astype(bool).sum()),
                "selected_count": len(eligible_weights),
                "candidate_pool_size": candidate_pool_size,
                "selection_ratio": selection_ratio,
                "period_flags": "|".join(period_flags),
                "excluded_tickers": "|".join(sorted(set(excluded))),
                "cost_paid": cost_paid,
                "status": status,
                "portfolio_value_before": portfolio_before if portfolio_before is not None else "",
                "cash_before": cash_before,
                "portfolio_value_after": portfolio_after if portfolio_after is not None else "",
                "cash_after": cash,
            }
        )

    ending_value: float | None = value_rows[-1]["portfolio_value"] if value_rows else initial_value
    if valuation_date is not None:
        final_day = pd.Timestamp(valuation_date).normalize()
        missing_final: list[str] = []
        final_prices: dict[str, float] = {}
        for ticker in holdings:
            price = _exact_price(prices, ticker, final_day)
            if price is None:
                missing_final.append(ticker)
            else:
                final_prices[ticker] = price
        if missing_final:
            ending_value = None
            value_rows.append(
                {
                    "date": final_day.date().isoformat(),
                    "portfolio_value": "",
                    "cash": cash,
                    "status": PRICE_UNAVAILABLE,
                    "missing_tickers": "|".join(sorted(missing_final)),
                }
            )
        else:
            ending_value = cash + sum(
                shares * final_prices[ticker] for ticker, shares in holdings.items()
            )
            value_rows.append(
                {
                    "date": final_day.date().isoformat(),
                    "portfolio_value": ending_value,
                    "cash": cash,
                    "status": "OK",
                    "missing_tickers": "",
                }
            )

    assumptions: dict[str, float | int | str] = {
        "BROKERAGE_FEE_PCT_PER_SIDE": config.brokerage_fee_pct_per_side,
        "SELL_TAX_PCT": config.sell_tax_pct,
        "SETTLEMENT_LAG_DAYS": config.settlement_lag_days,
        "MIN_CANDIDATE_POOL_MULTIPLE": (
            config.min_candidate_pool_multiple
            if config.min_candidate_pool_multiple is not None
            else "UNCONFIGURED"
        ),
        "SELECTION_RATIO_REPORT_THRESHOLD": (
            config.selection_ratio_report_threshold
            if config.selection_ratio_report_threshold is not None
            else "UNCONFIGURED"
        ),
        "assumption_status": "ESTIMATE_UNVERIFIED_PUBLISHED_FEE_SCHEDULE",
    }
    return EngineResult(
        value_series=pd.DataFrame(
            value_rows,
            columns=("date", "portfolio_value", "cash", "status", "missing_tickers"),
        ),
        rebalance_log=pd.DataFrame(
            rebalance_rows,
            columns=(
                "date",
                "eligible_count",
                "selected_count",
                "candidate_pool_size",
                "selection_ratio",
                "period_flags",
                "excluded_tickers",
                "cost_paid",
                "status",
                "portfolio_value_before",
                "cash_before",
                "portfolio_value_after",
                "cash_after",
            ),
        ),
        trade_log=pd.DataFrame(
            trade_rows,
            columns=(
                "rebalance_date",
                "ticker",
                "side",
                "entry_price",
                "gross_value",
                "cost_paid",
                "shares",
                "settlement_date",
                "status",
            ),
        ),
        ending_value=ending_value,
        known_biases=KNOWN_BIASES,
        assumptions=assumptions,
    )
