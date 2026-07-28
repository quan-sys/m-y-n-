from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping

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

from scripts.build_sprint7_portfolio import HOLDING_COUNT  # noqa: E402
from scripts.build_sprint9_4c_gates_as_of import write_deterministic_gzip_csv  # noqa: E402
from src.backtest.eligibility import compute_eligibility  # noqa: E402
from src.backtest.engine import KNOWN_BIASES, EngineConfig, load_engine_config, run_engine  # noqa: E402
from src.backtest.metrics import MetricsResult, metrics_from_value_series  # noqa: E402
from src.backtest.window import compute_backtest_window  # noqa: E402


RUN_DATE = "2026-07-28"
TARGET_PATH = (
    ROOT
    / "data"
    / "screener"
    / "targets_pit"
    / "2026-07-28"
    / "rebalance_targets_point_in_time.csv.gz"
)
PRICE_PATH = (
    ROOT
    / "data"
    / "price_history"
    / "2026-07-22"
    / "daily_close.csv.gz"
)
CONFIG_PATH = ROOT / "config" / "screener.yaml"
OUTPUT_ROOT = ROOT / "data" / "backtest" / "walk_forward"
REPORT_PATH = ROOT / "docs" / "REPORT_SPRINT_9_5B_WALK_FORWARD.md"
VALUE_OUTPUT_COLUMNS = (
    "config_id",
    "evaluation_date",
    "execution_date",
    "portfolio_value",
    "cash",
    "status",
    "missing_tickers",
    "in_window",
)
METRICS_COLUMNS = (
    "config_id",
    "scope",
    "window_start_date",
    "n_periods",
    "cagr",
    "annualised_volatility",
    "sharpe",
    "sortino",
    "max_drawdown",
    "max_drawdown_magnitude",
    "periods_per_year",
    "rf_annual",
    "diagnostic_only",
    "sample_flag",
    "statuses",
)
TARGET_REQUIRED_COLUMNS = {
    "config_id",
    "rebalance_date",
    "ticker",
    "weight",
    "selected_count",
    "candidate_pool_size",
}
PRICE_REQUIRED_COLUMNS = {"ticker", "date", "close_adjusted", "volume"}
PERIODS_PER_YEAR = 4
RF_ANNUAL = 0.0
SAMPLE_TOO_SMALL = "SAMPLE_TOO_SMALL_FOR_INFERENCE"
ALL_DATES = "ALL_DATES"
IN_WINDOW = "IN_WINDOW"
MAX_EXECUTION_SESSION_ADVANCES = 8


@dataclass(frozen=True)
class ExecutionDateResolution:
    evaluation_date: str
    first_session: str
    execution_date: str
    sessions_delayed: int
    blocking_tickers: tuple[str, ...]


@dataclass(frozen=True)
class ExecutionPriceCalendar:
    sessions: pd.DatetimeIndex
    traded_tickers_by_session: Mapping[pd.Timestamp, frozenset[str]]


def _read_csv(path: Path, *, usecols: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False, usecols=usecols)


def _require_columns(frame: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = sorted(columns.difference(frame.columns))
    if missing:
        raise ValueError(f"{label} missing columns: " + ", ".join(missing))


def _normalise_tickers(values: pd.Series, label: str) -> pd.Series:
    tickers = values.astype(str).str.strip().str.upper()
    if tickers.eq("").any():
        raise ValueError(f"{label} contains a blank ticker")
    return tickers


def _number(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be numeric") from error
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def load_targets() -> pd.DataFrame:
    targets = _read_csv(TARGET_PATH)
    _require_columns(targets, TARGET_REQUIRED_COLUMNS, "target input")
    targets = targets.copy()
    targets["config_id"] = targets["config_id"].astype(str).str.strip()
    targets["rebalance_date"] = targets["rebalance_date"].astype(str).str.strip()
    targets["ticker"] = _normalise_tickers(targets["ticker"], "target input")
    targets["_weight"] = [
        _number(value, "target weight") for value in targets["weight"].tolist()
    ]
    targets["_selected_count"] = [
        int(_number(value, "selected_count"))
        for value in targets["selected_count"].tolist()
    ]
    targets["_candidate_pool_size"] = [
        int(_number(value, "candidate_pool_size"))
        for value in targets["candidate_pool_size"].tolist()
    ]
    if targets.duplicated(["config_id", "rebalance_date", "ticker"], keep=False).any():
        raise ValueError("target input has duplicate config_id/rebalance_date/ticker keys")
    for _, frame in targets.groupby(["config_id", "rebalance_date"], sort=False):
        if frame["_selected_count"].nunique() != 1:
            raise ValueError("target group has inconsistent selected_count")
        if frame["_candidate_pool_size"].nunique() != 1:
            raise ValueError("target group has inconsistent candidate_pool_size")
        if len(frame) != int(frame["_selected_count"].iloc[0]):
            raise ValueError("target group row count differs from selected_count")
        if not math.isclose(float(frame["_weight"].sum()), 1.0, abs_tol=1e-9):
            raise ValueError("target group weights do not sum to one")
    return targets


def load_price_rows() -> pd.DataFrame:
    prices = _read_csv(PRICE_PATH, usecols=sorted(PRICE_REQUIRED_COLUMNS))
    _require_columns(prices, PRICE_REQUIRED_COLUMNS, "price input")
    prices = prices.copy()
    prices["ticker"] = _normalise_tickers(prices["ticker"], "price input")
    prices["_date"] = pd.to_datetime(prices["date"], errors="raise").dt.normalize()
    if prices.duplicated(["ticker", "date"], keep=False).any():
        raise ValueError("price input has duplicate ticker/date keys")
    return prices


def _load_portfolio_capital(path: Path) -> float:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    if "PORTFOLIO_CAPITAL_VND" not in values:
        raise ValueError("config missing PORTFOLIO_CAPITAL_VND")
    capital = _number(values["PORTFOLIO_CAPITAL_VND"], "PORTFOLIO_CAPITAL_VND")
    if capital <= 0:
        raise ValueError("PORTFOLIO_CAPITAL_VND must be positive")
    return capital


def _market_sessions(price_rows: pd.DataFrame) -> pd.DatetimeIndex:
    _require_columns(price_rows, {"date", "volume"}, "execution-date input")
    dates = pd.to_datetime(price_rows["date"], errors="raise").dt.normalize()
    volumes = pd.to_numeric(price_rows["volume"], errors="coerce")
    sessions = pd.DatetimeIndex(sorted(dates.loc[volumes.gt(0)].unique()))
    if sessions.empty:
        raise ValueError("execution-date input has no market session")
    return sessions


def _traded_tickers_on_date(price_rows: pd.DataFrame, session: pd.Timestamp) -> set[str]:
    _require_columns(
        price_rows,
        {"ticker", "date", "close_adjusted", "volume"},
        "held-price input",
    )
    rows = price_rows.copy()
    dates = pd.to_datetime(rows["date"], errors="raise").dt.normalize()
    close = pd.to_numeric(rows["close_adjusted"], errors="coerce")
    volume = pd.to_numeric(rows["volume"], errors="coerce")
    valid = dates.eq(session) & volume.gt(0) & close.gt(0) & close.notna()
    return set(_normalise_tickers(rows.loc[valid, "ticker"], "held-price input"))


def _execution_price_calendar(price_rows: pd.DataFrame) -> ExecutionPriceCalendar:
    _require_columns(
        price_rows,
        {"ticker", "date", "close_adjusted", "volume"},
        "execution-date input",
    )
    sessions = _market_sessions(price_rows)
    dates = pd.to_datetime(price_rows["date"], errors="raise").dt.normalize()
    close = pd.to_numeric(price_rows["close_adjusted"], errors="coerce")
    volume = pd.to_numeric(price_rows["volume"], errors="coerce")
    valid = volume.gt(0) & close.gt(0) & close.notna()
    traded = pd.DataFrame(
        {
            "date": dates.loc[valid],
            "ticker": _normalise_tickers(
                price_rows.loc[valid, "ticker"],
                "execution-date input",
            ),
        }
    )
    by_session = {
        pd.Timestamp(session).normalize(): frozenset(group["ticker"])
        for session, group in traded.groupby("date", sort=False)
    }
    return ExecutionPriceCalendar(sessions=sessions, traded_tickers_by_session=by_session)


def resolve_execution_date(
    evaluation_date: str,
    price_rows: pd.DataFrame,
    held_tickers: Iterable[str] = (),
    execution_calendar: ExecutionPriceCalendar | None = None,
) -> ExecutionDateResolution:
    sessions = execution_calendar.sessions if execution_calendar is not None else _market_sessions(price_rows)
    evaluation = pd.Timestamp(evaluation_date).normalize()
    position = int(sessions.searchsorted(evaluation, side="left"))
    if position >= len(sessions):
        raise ValueError(f"no execution session on or after {evaluation_date}")
    held = tuple(sorted({str(ticker).strip().upper() for ticker in held_tickers}))
    if "" in held:
        raise ValueError("held ticker set contains a blank ticker")
    first_session = sessions[position]
    initial_blockers: tuple[str, ...] = ()
    blockers_seen: set[str] = set()
    for delayed in range(MAX_EXECUTION_SESSION_ADVANCES + 1):
        session_position = position + delayed
        if session_position >= len(sessions):
            break
        session = sessions[session_position]
        if not held:
            traded_tickers: set[str] = set()
        elif execution_calendar is not None:
            traded_tickers = set(execution_calendar.traded_tickers_by_session.get(session, frozenset()))
        else:
            traded_tickers = _traded_tickers_on_date(price_rows, session)
        missing = sorted(set(held).difference(traded_tickers))
        if not missing:
            return ExecutionDateResolution(
                evaluation_date=evaluation.date().isoformat(),
                first_session=first_session.date().isoformat(),
                execution_date=session.date().isoformat(),
                sessions_delayed=delayed,
                blocking_tickers=initial_blockers,
            )
        if not initial_blockers:
            initial_blockers = tuple(missing)
        blockers_seen.update(missing)
    raise RuntimeError(
        "STOP: no session within 8 advances prices every held ticker for "
        f"{evaluation.date().isoformat()}; blocking_tickers={','.join(sorted(blockers_seen))}"
    )


def resolve_execution_dates(
    evaluation_dates: Iterable[str],
    price_rows: pd.DataFrame,
) -> dict[str, str]:
    resolved: dict[str, str] = {}
    for evaluation_date in sorted(dict.fromkeys(str(value) for value in evaluation_dates)):
        resolved[evaluation_date] = resolve_execution_date(
            evaluation_date,
            price_rows,
        ).execution_date
    return resolved


def build_eligibility_frame(
    price_rows: pd.DataFrame,
    evaluation_date: str,
    tickers: Iterable[str],
    config: EngineConfig,
) -> pd.DataFrame:
    _require_columns(price_rows, {"ticker", "date", "volume"}, "eligibility input")
    normalized = price_rows.copy()
    if "_date" not in normalized.columns:
        normalized["_date"] = pd.to_datetime(normalized["date"], errors="raise").dt.normalize()
    evaluation = pd.Timestamp(evaluation_date).normalize()
    prior_rows = normalized.loc[
        normalized["_date"].lt(evaluation),
        ["ticker", "date", "volume"],
    ]
    return compute_eligibility(
        prior_rows,
        evaluation_date,
        min_traded_sessions_12m=config.min_traded_sessions_12m,
        ticker_identity_gap_days=config.ticker_identity_gap_days,
        universe_tickers=tickers,
    )


def window_details(
    periods: list[tuple[str, int]],
    config: EngineConfig,
) -> tuple[str, dict[str, bool]]:
    if config.min_candidate_pool_multiple is None:
        raise ValueError("engine config missing min_candidate_pool_multiple")
    start_date, _ = compute_backtest_window(
        periods,
        HOLDING_COUNT,
        config.min_candidate_pool_multiple,
    )
    if start_date is None:
        raise RuntimeError("backtest window did not start")
    start = start_date.date().isoformat()
    return start, {evaluation_date: evaluation_date >= start for evaluation_date, _ in periods}


def _target_groups(targets: pd.DataFrame) -> dict[str, list[tuple[str, pd.DataFrame]]]:
    groups: dict[str, list[tuple[str, pd.DataFrame]]] = {}
    for config_id, config_frame in targets.groupby("config_id", sort=False):
        rows: list[tuple[str, pd.DataFrame]] = []
        for evaluation_date, frame in config_frame.groupby("rebalance_date", sort=True):
            rows.append((str(evaluation_date), frame.copy().reset_index(drop=True)))
        groups[str(config_id)] = rows
    return groups


def _traded_price_rows(price_rows: pd.DataFrame) -> pd.DataFrame:
    _require_columns(price_rows, PRICE_REQUIRED_COLUMNS, "engine price input")
    close = pd.to_numeric(price_rows["close_adjusted"], errors="coerce")
    volume = pd.to_numeric(price_rows["volume"], errors="coerce")
    return price_rows.loc[volume.gt(0) & close.gt(0) & close.notna()].copy()


def _configuration_execution_dates(
    periods_with_targets: list[tuple[str, pd.DataFrame]],
    price_rows: pd.DataFrame,
    eligibility_by_evaluation: Mapping[str, pd.DataFrame],
    execution_calendar: ExecutionPriceCalendar,
) -> dict[str, ExecutionDateResolution]:
    held_tickers: set[str] = set()
    resolutions: dict[str, ExecutionDateResolution] = {}
    for evaluation_date, frame in periods_with_targets:
        resolution = resolve_execution_date(
            evaluation_date,
            price_rows,
            held_tickers,
            execution_calendar,
        )
        selected_tickers = set(frame["ticker"].astype(str))
        eligibility = eligibility_by_evaluation[evaluation_date].set_index("ticker")
        ineligible = sorted(
            ticker
            for ticker in selected_tickers
            if ticker not in eligibility.index or not bool(eligibility.loc[ticker, "eligible"])
        )
        if ineligible:
            raise RuntimeError(
                "STOP: Sprint 9-5A selected tickers are ineligible at evaluation date "
                f"{evaluation_date}: {','.join(ineligible)}"
            )
        traded_selected = set(
            execution_calendar.traded_tickers_by_session.get(
                pd.Timestamp(resolution.execution_date),
                frozenset(),
            )
        )
        # The engine will hold exactly the selected names that have an exact traded price here.
        # A newly selected unavailable name remains unowned and its intended weight stays in cash.
        held_tickers = selected_tickers.intersection(traded_selected)
        resolutions[evaluation_date] = resolution
    return resolutions


def _preflight_missing_prices(
    targets: pd.DataFrame,
    price_rows: pd.DataFrame,
    execution_dates: Mapping[str, Mapping[str, ExecutionDateResolution]],
) -> pd.DataFrame:
    requested = targets.loc[:, ["config_id", "rebalance_date", "ticker"]].copy()
    requested["execution_date"] = [
        execution_dates[str(config_id)][str(evaluation_date)].execution_date
        for config_id, evaluation_date in zip(
            requested["config_id"],
            requested["rebalance_date"],
        )
    ]
    prices = price_rows.loc[:, ["ticker", "date", "close_adjusted", "volume"]].copy()
    prices = prices.rename(columns={"date": "execution_date"})
    merged = requested.merge(
        prices,
        on=["ticker", "execution_date"],
        how="left",
        validate="many_to_one",
    )
    valid = (
        pd.to_numeric(merged["close_adjusted"], errors="coerce").notna()
        & pd.to_numeric(merged["volume"], errors="coerce").gt(0)
    )
    return merged.loc[
        ~valid,
        ["config_id", "rebalance_date", "execution_date", "ticker"],
    ].sort_values(
        ["config_id", "rebalance_date", "ticker"], kind="mergesort"
    ).reset_index(drop=True)


def _engine_frames(
    *,
    config_id: str,
    result: Any,
    execution_to_evaluation: Mapping[str, str],
    in_window: Mapping[str, bool],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    values = result.value_series.copy()
    numeric_value = pd.to_numeric(values["portfolio_value"], errors="coerce")
    # Engine status describes the rebalance as a whole.  A newly selected but unpriced name
    # makes that status PRICE_UNAVAILABLE even when every carried holding was priced and the
    # portfolio value is numeric.  The value-series status is specifically the valuation status;
    # the unchanged engine status remains in rebalance_log and trade_log.
    values.loc[numeric_value.notna(), "status"] = "OK"
    values["execution_date"] = values["date"].astype(str)
    values["evaluation_date"] = values["execution_date"].map(execution_to_evaluation)
    if values["evaluation_date"].isna().any():
        raise RuntimeError("engine value series has an unmapped execution date")
    values["config_id"] = config_id
    values["in_window"] = values["evaluation_date"].map(in_window).astype(bool)
    values = values.loc[:, VALUE_OUTPUT_COLUMNS].sort_values(
        ["evaluation_date"], kind="mergesort"
    ).reset_index(drop=True)

    rebalance = result.rebalance_log.copy()
    rebalance["execution_date"] = rebalance["date"].astype(str)
    rebalance["evaluation_date"] = rebalance["execution_date"].map(execution_to_evaluation)
    if rebalance["evaluation_date"].isna().any():
        raise RuntimeError("engine rebalance log has an unmapped execution date")
    rebalance["config_id"] = config_id
    rebalance["in_window"] = rebalance["evaluation_date"].map(in_window).astype(bool)
    rebalance_columns = (
        "config_id",
        "evaluation_date",
        "execution_date",
        *tuple(result.rebalance_log.columns),
        "in_window",
    )
    rebalance = rebalance.loc[:, rebalance_columns].sort_values(
        ["evaluation_date"], kind="mergesort"
    ).reset_index(drop=True)

    trades = result.trade_log.copy()
    trades["execution_date"] = trades["rebalance_date"].astype(str)
    trades["evaluation_date"] = trades["execution_date"].map(execution_to_evaluation)
    if trades["evaluation_date"].isna().any():
        raise RuntimeError("engine trade log has an unmapped execution date")
    trades["config_id"] = config_id
    trade_columns = (
        "config_id",
        "evaluation_date",
        "execution_date",
        *tuple(result.trade_log.columns),
    )
    trades = trades.loc[:, trade_columns].sort_values(
        ["evaluation_date", "ticker", "side"], kind="mergesort"
    ).reset_index(drop=True)
    return values, rebalance, trades


def _metrics_row(
    *,
    config_id: str,
    scope: str,
    window_start_date: str,
    values: pd.DataFrame,
) -> dict[str, Any]:
    metrics: MetricsResult = metrics_from_value_series(
        values.loc[:, ["execution_date", "portfolio_value"]].rename(
            columns={"execution_date": "date"}
        ),
        periods_per_year=PERIODS_PER_YEAR,
        rf_annual=RF_ANNUAL,
    )
    return {
        "config_id": config_id,
        "scope": scope,
        "window_start_date": window_start_date,
        "n_periods": metrics.n_periods,
        "cagr": metrics.cagr if metrics.cagr is not None else "",
        "annualised_volatility": (
            metrics.annualised_volatility
            if metrics.annualised_volatility is not None
            else ""
        ),
        "sharpe": metrics.sharpe if metrics.sharpe is not None else "",
        "sortino": metrics.sortino if metrics.sortino is not None else "",
        "max_drawdown": metrics.max_drawdown if metrics.max_drawdown is not None else "",
        "max_drawdown_magnitude": (
            metrics.max_drawdown_magnitude
            if metrics.max_drawdown_magnitude is not None
            else ""
        ),
        "periods_per_year": metrics.periods_per_year,
        "rf_annual": metrics.rf_annual,
        "diagnostic_only": True,
        "sample_flag": SAMPLE_TOO_SMALL if metrics.n_periods < 12 else "",
        "statuses": json.dumps(metrics.statuses, sort_keys=True),
    }


def _cumulative_return_from_imported_metrics(values: pd.DataFrame) -> tuple[float | None, int]:
    metrics = metrics_from_value_series(
        values.loc[:, ["execution_date", "portfolio_value"]].rename(
            columns={"execution_date": "date"}
        ),
        periods_per_year=PERIODS_PER_YEAR,
        rf_annual=RF_ANNUAL,
    )
    if metrics.n_periods != 7:
        return None, metrics.n_periods
    return math.prod(1.0 + value for value in metrics.periodic_returns) - 1.0, metrics.n_periods


def _validate_value_coverage(targets: pd.DataFrame, values: pd.DataFrame) -> None:
    expected = targets.loc[:, ["config_id", "rebalance_date"]].drop_duplicates().rename(
        columns={"rebalance_date": "evaluation_date"}
    )
    actual = values.loc[:, ["config_id", "evaluation_date"]]
    if actual.duplicated(["config_id", "evaluation_date"], keep=False).any():
        raise RuntimeError("STOP: value series has duplicate configuration/evaluation pairs")
    missing = expected.merge(
        actual,
        on=["config_id", "evaluation_date"],
        how="left",
        indicator=True,
    ).loc[lambda rows: rows["_merge"].eq("left_only")]
    if not missing.empty:
        raise RuntimeError(
            "STOP: value series lost target pairs: "
            + missing.loc[:, ["config_id", "evaluation_date"]].to_json(orient="records")
        )
    if len(values) != len(expected):
        raise RuntimeError("STOP: value series contains an unexpected configuration/evaluation pair")
    numeric_values = [_number(value, "portfolio_value") for value in values["portfolio_value"]]
    if any(value <= 0 for value in numeric_values):
        raise RuntimeError("STOP: value series contains a non-positive portfolio value")
    unavailable = values.loc[values["status"].eq("PRICE_UNAVAILABLE")]
    if not unavailable.empty:
        raise RuntimeError(
            "STOP: value series retains PRICE_UNAVAILABLE status: "
            + unavailable.loc[:, ["config_id", "evaluation_date"]].to_json(orient="records")
        )


def _validate_metric_lengths(metrics: pd.DataFrame) -> None:
    all_dates = metrics.loc[metrics["scope"].eq(ALL_DATES)].copy()
    expected_periods = all_dates["config_id"].map(
        lambda config_id: 27 if str(config_id).endswith("__VALUE_ONLY") else 7
    )
    actual_periods = pd.to_numeric(all_dates["n_periods"], errors="raise")
    mismatches = all_dates.loc[
        actual_periods.ne(expected_periods),
        ["config_id", "scope", "n_periods"],
    ]
    if not mismatches.empty:
        raise RuntimeError(
            "STOP: metrics n_periods does not match the required configuration length: "
            + mismatches.to_json(orient="records")
        )


def build_walk_forward(
    targets: pd.DataFrame,
    price_rows: pd.DataFrame,
    config: EngineConfig,
    initial_value: float,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    dict[str, dict[str, ExecutionDateResolution]],
    pd.DataFrame,
]:
    groups = _target_groups(targets)
    target_tickers = set(targets["ticker"].astype(str))
    eligibility_prices = price_rows.loc[price_rows["ticker"].isin(target_tickers)].copy()
    engine_prices = _traded_price_rows(
        eligibility_prices
    )
    target_tickers_by_evaluation: dict[str, set[str]] = {}
    for periods_with_targets in groups.values():
        for evaluation_date, frame in periods_with_targets:
            target_tickers_by_evaluation.setdefault(evaluation_date, set()).update(
                frame["ticker"].astype(str)
            )
    eligibility_by_evaluation = {
        evaluation_date: build_eligibility_frame(
            eligibility_prices,
            evaluation_date,
            sorted(tickers),
            config,
        )
        for evaluation_date, tickers in sorted(target_tickers_by_evaluation.items())
    }
    execution_calendar = _execution_price_calendar(price_rows)
    execution_dates_by_config = {
        config_id: _configuration_execution_dates(
            periods_with_targets,
            price_rows,
            eligibility_by_evaluation,
            execution_calendar,
        )
        for config_id, periods_with_targets in groups.items()
    }
    missing_prices = _preflight_missing_prices(
        targets,
        price_rows,
        execution_dates_by_config,
    )
    value_frames: list[pd.DataFrame] = []
    rebalance_frames: list[pd.DataFrame] = []
    trade_frames: list[pd.DataFrame] = []
    metric_rows: list[dict[str, Any]] = []

    for config_id, periods_with_targets in groups.items():
        periods = [
            (evaluation_date, int(frame["_candidate_pool_size"].iloc[0]))
            for evaluation_date, frame in periods_with_targets
        ]
        window_start_date, in_window = window_details(periods, config)
        targets_by_execution: dict[str, dict[str, float]] = {}
        eligibility_by_execution: dict[str, pd.DataFrame] = {}
        candidate_pool_by_execution: dict[str, int] = {}
        for evaluation_date, frame in periods_with_targets:
            execution_date = execution_dates_by_config[config_id][evaluation_date].execution_date
            targets_by_execution[execution_date] = dict(
                zip(
                    frame["ticker"].astype(str),
                    frame["_weight"].astype(float),
                )
            )
            selected_tickers = set(frame["ticker"].astype(str))
            eligibility_by_execution[execution_date] = (
                eligibility_by_evaluation[evaluation_date]
                .loc[lambda values: values["ticker"].isin(selected_tickers)]
                .reset_index(drop=True)
            )
            candidate_pool_by_execution[execution_date] = int(
                frame["_candidate_pool_size"].iloc[0]
            )
        config_tickers = set(
            pd.concat([frame["ticker"] for _, frame in periods_with_targets], ignore_index=True)
        )
        execution_days = pd.DatetimeIndex(
            pd.to_datetime(list(targets_by_execution), errors="raise")
        ).normalize()
        config_engine_prices = engine_prices.loc[
            engine_prices["ticker"].isin(config_tickers)
            & engine_prices["_date"].isin(execution_days),
            ["ticker", "date", "close_adjusted", "volume"],
        ].copy()
        result = run_engine(
            config_engine_prices,
            targets_by_execution,
            eligibility_by_execution,
            config=config,
            initial_value=initial_value,
            candidate_pool_sizes_by_rebalance=candidate_pool_by_execution,
            portfolio_size=HOLDING_COUNT,
        )
        values, rebalances, trades = _engine_frames(
            config_id=config_id,
            result=result,
            execution_to_evaluation={
                resolution.execution_date: evaluation_date
                for evaluation_date, resolution in execution_dates_by_config[config_id].items()
            },
            in_window=in_window,
        )
        failures = rebalances.loc[rebalances["selected_count"].ne(HOLDING_COUNT)]
        if not failures.empty:
            raise RuntimeError(
                "STOP: engine selected_count differs from HOLDING_COUNT: "
                + failures.loc[:, ["config_id", "evaluation_date", "selected_count"]]
                .to_json(orient="records")
            )
        value_frames.append(values)
        rebalance_frames.append(rebalances)
        trade_frames.append(trades)
        metric_rows.extend(
            [
                _metrics_row(
                    config_id=config_id,
                    scope=ALL_DATES,
                    window_start_date=window_start_date,
                    values=values,
                ),
                _metrics_row(
                    config_id=config_id,
                    scope=IN_WINDOW,
                    window_start_date=window_start_date,
                    values=values.loc[values["in_window"]].reset_index(drop=True),
                ),
            ]
        )

    value_output = pd.concat(value_frames, ignore_index=True).sort_values(
        ["config_id", "evaluation_date"], kind="mergesort"
    ).reset_index(drop=True)
    rebalance_output = pd.concat(rebalance_frames, ignore_index=True).sort_values(
        ["config_id", "evaluation_date"], kind="mergesort"
    ).reset_index(drop=True)
    trade_output = pd.concat(trade_frames, ignore_index=True).sort_values(
        ["config_id", "evaluation_date", "ticker", "side"], kind="mergesort"
    ).reset_index(drop=True)
    metrics_output = pd.DataFrame(metric_rows, columns=METRICS_COLUMNS).sort_values(
        ["config_id", "scope"], kind="mergesort"
    ).reset_index(drop=True)
    if len(metrics_output) != len(groups) * 2:
        raise RuntimeError("metrics summary does not contain two scopes per configuration")
    if not metrics_output["diagnostic_only"].astype(bool).all():
        raise RuntimeError("metrics summary must be diagnostic only")
    _validate_value_coverage(targets, value_output)
    _validate_metric_lengths(metrics_output)
    return (
        value_output,
        rebalance_output,
        trade_output,
        metrics_output,
        execution_dates_by_config,
        missing_prices,
    )


def _markdown_table(headers: Iterable[Any], rows: Iterable[Iterable[Any]]) -> str:
    rendered_headers = [str(value) for value in headers]
    lines = [
        "| " + " | ".join(rendered_headers) + " |",
        "| " + " | ".join("---" for _ in rendered_headers) + " |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(str(value).replace("|", "\\|") for value in row)
            + " |"
        )
    return "\n".join(lines)


def _format_value(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, float):
        return repr(value)
    return str(value)


def _window_start_lookup(metrics: pd.DataFrame) -> dict[str, str]:
    starts = metrics.groupby("config_id", sort=False)["window_start_date"].unique()
    result: dict[str, str] = {}
    for config_id, values in starts.items():
        if len(values) != 1:
            raise RuntimeError("metrics rows disagree on window_start_date")
        result[str(config_id)] = str(values[0])
    return result


def _gate_comparison_rows(value_output: pd.DataFrame) -> list[list[Any]]:
    live_dates = ("2024-03-31", "2024-06-30", "2024-09-30", "2024-12-31", "2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31")
    rows: list[list[Any]] = []
    pairs = ("ALL__ebit_tev", "ALL__e_p", "PRICE_OK__ebit_tev", "PRICE_OK__e_p")
    for prefix in pairs:
        value_config = prefix + "__VALUE_ONLY"
        gated_config = prefix + "__VALUE_PLUS_GATES"
        value_rows = value_output.loc[
            value_output["config_id"].eq(value_config)
            & value_output["evaluation_date"].isin(live_dates)
        ].sort_values("evaluation_date", kind="mergesort")
        gated_rows = value_output.loc[
            value_output["config_id"].eq(gated_config)
            & value_output["evaluation_date"].isin(live_dates)
        ].sort_values("evaluation_date", kind="mergesort")
        if tuple(value_rows["evaluation_date"]) != live_dates:
            missing = sorted(set(live_dates).difference(value_rows["evaluation_date"]))
            raise RuntimeError(
                "STOP: VALUE_ONLY gate comparison lost value rows at "
                + ",".join(missing)
            )
        if tuple(gated_rows["evaluation_date"]) != live_dates:
            missing = sorted(set(live_dates).difference(gated_rows["evaluation_date"]))
            raise RuntimeError(
                "STOP: VALUE_PLUS_GATES comparison lost value rows at "
                + ",".join(missing)
            )
        population_id, metric = prefix.split("__", 1)
        value_return, value_n_periods = _cumulative_return_from_imported_metrics(value_rows)
        gated_return, gated_n_periods = _cumulative_return_from_imported_metrics(gated_rows)
        rows.append(
            [
                population_id,
                metric,
                _format_value(value_return) if value_return is not None else "UNAVAILABLE_PRICE_UNAVAILABLE",
                _format_value(gated_return) if gated_return is not None else "UNAVAILABLE_PRICE_UNAVAILABLE",
                value_n_periods,
                gated_n_periods,
                SAMPLE_TOO_SMALL if value_n_periods < 12 or gated_n_periods < 12 else "",
            ]
        )
    return rows


def _artifact_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_report(
    *,
    targets: pd.DataFrame,
    value_output: pd.DataFrame,
    rebalance_output: pd.DataFrame,
    metrics_output: pd.DataFrame,
    execution_dates: Mapping[str, Mapping[str, ExecutionDateResolution]],
    missing_prices: pd.DataFrame,
    initial_value: float,
    hashes: Mapping[str, str],
) -> None:
    w1_rows = [
        [
            config_id,
            evaluation_date,
            resolution.first_session,
            resolution.execution_date,
            resolution.sessions_delayed,
            "|".join(resolution.blocking_tickers),
        ]
        for config_id, resolutions in sorted(execution_dates.items())
        for evaluation_date, resolution in sorted(resolutions.items())
    ]
    starts = _window_start_lookup(metrics_output)
    w2_rows = []
    for config_id, frame in targets.groupby("config_id", sort=True):
        emitted_dates = frame["rebalance_date"].nunique()
        in_window_dates = int(
            sum(
                evaluation_date >= starts[str(config_id)]
                for evaluation_date in sorted(frame["rebalance_date"].unique())
            )
        )
        all_metrics = metrics_output.loc[
            metrics_output["config_id"].eq(config_id)
            & metrics_output["scope"].eq(ALL_DATES)
        ].iloc[0]
        in_metrics = metrics_output.loc[
            metrics_output["config_id"].eq(config_id)
            & metrics_output["scope"].eq(IN_WINDOW)
        ].iloc[0]
        w2_rows.append(
            [
                config_id,
                starts[str(config_id)],
                emitted_dates,
                in_window_dates,
                int(all_metrics.n_periods),
                int(in_metrics.n_periods),
            ]
        )
    w3_rows = [
        [_format_value(row[column]) for column in METRICS_COLUMNS]
        for _, row in metrics_output.iterrows()
    ]
    w4 = rebalance_output.loc[
        ~rebalance_output["status"].eq("OK"),
        [
            "config_id",
            "evaluation_date",
            "execution_date",
            "status",
            "excluded_tickers",
            "selected_count",
            "cash_after",
        ],
    ].copy()
    unavailable_count = w4["excluded_tickers"].astype(str).str.count("PRICE_UNAVAILABLE")
    w4["held_name_count"] = pd.to_numeric(w4["selected_count"], errors="raise") - unavailable_count
    w4 = w4.loc[
        :,
        [
            "config_id",
            "evaluation_date",
            "execution_date",
            "status",
            "excluded_tickers",
            "held_name_count",
            "cash_after",
        ],
    ]
    w4_rows = w4.values.tolist() if not w4.empty else [["NONE", "", "", "", "", "", ""]]
    w5_rows = []
    for config_id, frame in rebalance_output.groupby("config_id", sort=True):
        total_cost = float(pd.to_numeric(frame["cost_paid"], errors="coerce").fillna(0.0).sum())
        w5_rows.append([config_id, _format_value(total_cost), _format_value(total_cost / initial_value)])
    w6 = rebalance_output.loc[
        rebalance_output["period_flags"].astype(str).str.contains(
            "THIN_CANDIDATE_POOL|LOW_SELECTIVITY", regex=True
        ),
        ["config_id", "evaluation_date", "execution_date", "period_flags"],
    ]
    w6_rows = w6.values.tolist() if not w6.empty else [["NONE", "", "", ""]]
    lines = [
        "# Sprint 9-5B Walk-Forward",
        "",
        "## W1. Evaluation-date to execution-date map",
        "",
        _markdown_table(
            [
                "config_id",
                "evaluation_date",
                "first_market_session",
                "execution_date",
                "sessions_delayed",
                "blocking_tickers",
            ],
            w1_rows,
        ),
        "",
        "## W2. Configuration window and sample sizes",
        "",
        _markdown_table(
            [
                "config_id",
                "window_start_date",
                "emitted_dates",
                "in_window_dates",
                "ALL_DATES n_periods",
                "IN_WINDOW n_periods",
            ],
            w2_rows,
        ),
        "",
        "## W3. Imported metrics summary",
        "",
        _markdown_table(METRICS_COLUMNS, w3_rows),
        "",
        "A Sharpe ratio computed from fewer than 12 quarterly returns cannot distinguish skill from noise.",
        "",
        "## W4. Rebalances with a non-OK status",
        "",
        _markdown_table(
            [
                "config_id",
                "evaluation_date",
                "execution_date",
                "status",
                "missing_tickers",
                "held_name_count",
                "cash_after",
            ],
            w4_rows,
        ),
        "",
        "### Target rows with no traded price on the execution date",
        "",
        _markdown_table(
            ["config_id", "evaluation_date", "execution_date", "ticker"],
            missing_prices.values.tolist() if not missing_prices.empty else [["NONE", "", "", ""]],
        ),
        "",
        "## W5. Trading costs",
        "",
        _markdown_table(
            ["config_id", "total_cost_paid", "cost_as_fraction_of_initial_capital"],
            w5_rows,
        ),
        "",
        "## W6. Engine thin-pool or low-selectivity flags",
        "",
        _markdown_table(
            ["config_id", "evaluation_date", "execution_date", "period_flags"],
            w6_rows,
        ),
        "",
        "## W7. Gate comparison on shared live dates only",
        "",
        _markdown_table(
            [
                "population_id",
                "metric",
                "VALUE_ONLY cumulative return",
                "VALUE_PLUS_GATES cumulative return",
                "VALUE_ONLY n_periods",
                "VALUE_PLUS_GATES n_periods",
                "sample_flag",
            ],
            _gate_comparison_rows(value_output),
        ),
        "",
        "On 2024-09-30 the VALUE_ONLY configurations execute at 2024-10-02 while the VALUE_PLUS_GATES configurations execute at 2024-09-30: a disclosed two-session mismatch that is not corrected.",
        "",
        "## W8. Known biases and limits",
        "",
    ]
    lines.extend(f"- {bias}" for bias in KNOWN_BIASES)
    lines.extend(
        [
            "- No VN-Index or any benchmark series exists in this repository, so no figure here can be compared against buying the market.",
            "- `rf=0`, `BROKERAGE_FEE_PCT_PER_SIDE`, `SELL_TAX_PCT` and `SETTLEMENT_LAG_DAYS` are all ESTIMATE_UNVERIFIED.",
            "- Seven quarters is far too short to support any statement about a strategy and proves only that the pipeline runs end to end.",
            "",
            "## Artifact SHA-256",
            "",
        ]
    )
    lines.extend(f"- `{name}`: `{hash_value}`." for name, hash_value in hashes.items())
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Sprint 9-5B walk-forward artifacts.")
    parser.add_argument("--run-date", default=RUN_DATE, help="Required run date (YYYY-MM-DD).")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_date = str(args.run_date)
    if run_date != RUN_DATE:
        raise ValueError(f"Sprint 9-5B run date must be {RUN_DATE}")
    print(f"RUN_DATE={run_date}", flush=True)
    config = load_engine_config(CONFIG_PATH)
    initial_value = _load_portfolio_capital(CONFIG_PATH)
    targets = load_targets()
    prices = load_price_rows()
    value_output, rebalance_output, trade_output, metrics_output, execution_dates, missing_prices = build_walk_forward(
        targets,
        prices,
        config,
        initial_value,
    )
    output_dir = OUTPUT_ROOT / run_date
    value_path = output_dir / "value_series.csv.gz"
    rebalance_path = output_dir / "rebalance_log.csv.gz"
    trade_path = output_dir / "trade_log.csv.gz"
    metrics_path = output_dir / "metrics_summary.csv"
    hashes = {
        "value_series.csv.gz": write_deterministic_gzip_csv(value_output, value_path),
        "rebalance_log.csv.gz": write_deterministic_gzip_csv(rebalance_output, rebalance_path),
        "trade_log.csv.gz": write_deterministic_gzip_csv(trade_output, trade_path),
    }
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_output.to_csv(metrics_path, index=False, lineterminator="\n")
    hashes["metrics_summary.csv"] = _artifact_hash(metrics_path)
    write_report(
        targets=targets,
        value_output=value_output,
        rebalance_output=rebalance_output,
        metrics_output=metrics_output,
        execution_dates=execution_dates,
        missing_prices=missing_prices,
        initial_value=initial_value,
        hashes=hashes,
    )
    print(f"VALUE_SERIES={value_path}")
    print(f"REBALANCE_LOG={rebalance_path}")
    print(f"TRADE_LOG={trade_path}")
    print(f"METRICS_SUMMARY={metrics_path}")
    print(f"MISSING_PRICE_ROWS={len(missing_prices)}")
    for name, hash_value in hashes.items():
        print(f"SHA256_{name.upper()}={hash_value}")
    print(f"REPORT={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
