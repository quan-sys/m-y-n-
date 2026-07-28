from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
from pathlib import Path
import sys
from typing import Any, Iterable

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
from scripts.build_sprint9_4c_gates_as_of import (  # noqa: E402
    _all_six_pass,
    write_deterministic_gzip_csv,
)
from src.backtest.eligibility import compute_eligibility  # noqa: E402
from src.backtest.engine import KNOWN_BIASES, EngineConfig, load_engine_config  # noqa: E402
from src.backtest.window import compute_backtest_window  # noqa: E402


RUN_DATE = "2026-07-28"
CANDIDATE_PATH = (
    ROOT
    / "data"
    / "screener"
    / "candidates_pit"
    / "2026-07-26"
    / "value_candidates_point_in_time.csv.gz"
)
GATE_PATH = (
    ROOT
    / "data"
    / "screener"
    / "gates_pit"
    / "2026-07-27"
    / "gate_values_point_in_time.csv.gz"
)
SESSION_PATH = (
    ROOT
    / "data"
    / "price_history"
    / "2026-07-22"
    / "daily_close.csv.gz"
)
CONFIG_PATH = ROOT / "config" / "screener.yaml"
OUTPUT_ROOT = ROOT / "data" / "screener" / "targets_pit"
REPORT_PATH = ROOT / "docs" / "REPORT_SPRINT_9_5A_REBALANCE_TARGETS.md"
SOURCE_LABEL = (
    "Sprint 9-5A | candidates_pit/2026-07-26; gates_pit/2026-07-27; "
    "daily_close/2026-07-22 volume eligibility"
)
WALK_FORWARD_ROLE = "WALK_FORWARD"
VALUE_ONLY = "VALUE_ONLY"
VALUE_PLUS_GATES = "VALUE_PLUS_GATES"
POPULATIONS = ("ALL", "PRICE_OK")
METRICS = ("ebit_tev", "e_p")
GATE_SETTINGS = (VALUE_ONLY, VALUE_PLUS_GATES)
EVALUATION_DATES = tuple(
    value.date().isoformat()
    for value in pd.date_range("2019-03-31", "2025-12-31", freq="QE-DEC")
)
GATED_OUTPUT_DATES = tuple(
    value.date().isoformat()
    for value in pd.date_range("2024-03-31", "2025-12-31", freq="QE-DEC")
)
OUTPUT_COLUMNS = (
    "config_id",
    "population_id",
    "metric",
    "gate_setting",
    "rebalance_date",
    "ticker",
    "rank_in_population",
    "weight",
    "selected_count",
    "candidate_pool_size",
    "pool_threshold",
    "meets_pool_threshold",
    "THIN_CANDIDATE_POOL",
    "SHORT_BASKET",
    "dropped_ineligible_count",
    "source",
    "as_of",
    "data_status",
)
CANDIDATE_REQUIRED_COLUMNS = {
    "evaluation_date",
    "ticker",
    "metric",
    "population_id",
    "rank_in_population",
    "in_cheap_set",
    "source",
    "as_of",
    "data_status",
}
GATE_REQUIRED_COLUMNS = {
    "evaluation_date",
    "grid_role",
    "ticker",
    "sta_status",
    "snoa_status",
    "high_accrual_flag",
    "m_score_status",
    "m_score_flag",
    "distress_status",
    "distress_high_risk",
    "fscore_status",
    "franchise_status",
}
SESSION_REQUIRED_COLUMNS = {"ticker", "date", "volume"}
GATE_BOOLEAN_COLUMNS = (
    "high_accrual_flag",
    "m_score_flag",
    "distress_high_risk",
)
CONFIG_GRID = tuple(
    (population_id, metric, gate_setting)
    for population_id in POPULATIONS
    for metric in METRICS
    for gate_setting in GATE_SETTINGS
)


@dataclass(frozen=True)
class SelectionResult:
    selected: pd.DataFrame
    candidate_pool_size: int
    dropped_ineligible_count: int
    dropped_tickers: tuple[str, ...]
    selected_count: int
    short_basket: bool


@dataclass(frozen=True)
class BuildResult:
    targets: pd.DataFrame
    diagnostics: pd.DataFrame
    drop_events: pd.DataFrame
    gate_passes_by_date: dict[str, set[str]]


def _read_csv(path: Path, *, usecols: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        usecols=usecols,
    )


def _require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"{label} missing columns: " + ", ".join(missing))


def _normalise_ticker_series(values: pd.Series, label: str) -> pd.Series:
    normalized = values.astype(str).str.strip().str.upper()
    if normalized.eq("").any():
        raise ValueError(f"{label} contains a blank ticker")
    return normalized


def _parse_nullable_bool(value: Any) -> bool | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().casefold()
    if text == "":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValueError(f"invalid boolean value: {value!r}")


def _parse_required_bool(value: Any, label: str) -> bool:
    parsed = _parse_nullable_bool(value)
    if parsed is None:
        raise ValueError(f"{label} must be true or false")
    return parsed


def _numeric_rank(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.isna().any() or not pd.Series(numeric).map(math.isfinite).all():
        raise ValueError("rank_in_population must contain finite numeric values")
    return numeric


def _config_id(population_id: str, metric: str, gate_setting: str) -> str:
    return "__".join((population_id, metric, gate_setting))


def _config_order(config_id: str) -> int:
    expected = [_config_id(*parts) for parts in CONFIG_GRID]
    return expected.index(config_id)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    candidates = _read_csv(CANDIDATE_PATH)
    gates = _read_csv(GATE_PATH)
    _require_columns(candidates, CANDIDATE_REQUIRED_COLUMNS, "candidate input")
    _require_columns(gates, GATE_REQUIRED_COLUMNS, "gate input")

    candidates = candidates.copy()
    candidates["ticker"] = _normalise_ticker_series(candidates["ticker"], "candidate input")
    candidates["evaluation_date"] = candidates["evaluation_date"].astype(str).str.strip()
    candidates["metric"] = candidates["metric"].astype(str).str.strip()
    candidates["population_id"] = candidates["population_id"].astype(str).str.strip()
    candidates["_in_cheap_set"] = [
        _parse_required_bool(value, "in_cheap_set")
        for value in candidates["in_cheap_set"].tolist()
    ]
    candidates["_rank_numeric"] = _numeric_rank(candidates["rank_in_population"])
    candidate_key = ["evaluation_date", "metric", "population_id", "ticker"]
    if candidates.duplicated(candidate_key, keep=False).any():
        raise ValueError("candidate input has duplicate evaluation_date/metric/population_id/ticker keys")
    if set(candidates["evaluation_date"]) != set(EVALUATION_DATES):
        raise ValueError("candidate input dates do not match the required WALK_FORWARD grid")
    if not set(POPULATIONS).issubset(set(candidates["population_id"])):
        raise ValueError("candidate input does not contain every required population")
    if set(candidates["metric"]) != set(METRICS):
        raise ValueError("candidate input metrics do not match the required grid")

    gates = gates.copy()
    gates["ticker"] = _normalise_ticker_series(gates["ticker"], "gate input")
    gates["evaluation_date"] = gates["evaluation_date"].astype(str).str.strip()
    gates["grid_role"] = gates["grid_role"].astype(str).str.strip()
    if gates.duplicated(["evaluation_date", "ticker"], keep=False).any():
        raise ValueError("gate input has duplicate evaluation_date/ticker keys")
    for column in GATE_BOOLEAN_COLUMNS:
        gates[column] = pd.Series(
            [_parse_nullable_bool(value) for value in gates[column].tolist()],
            index=gates.index,
            dtype=object,
        )
    walk_dates = set(gates.loc[gates["grid_role"].eq(WALK_FORWARD_ROLE), "evaluation_date"])
    if walk_dates != set(EVALUATION_DATES):
        raise ValueError("gate WALK_FORWARD dates do not match the required grid")
    return candidates, gates


def load_session_rows(candidate_tickers: Iterable[str]) -> pd.DataFrame:
    session_rows = _read_csv(SESSION_PATH, usecols=sorted(SESSION_REQUIRED_COLUMNS))
    _require_columns(session_rows, SESSION_REQUIRED_COLUMNS, "session input")
    session_rows = session_rows.copy()
    session_rows["ticker"] = _normalise_ticker_series(session_rows["ticker"], "session input")
    session_rows["_date"] = pd.to_datetime(session_rows["date"], errors="raise").dt.normalize()
    needed_tickers = {
        str(ticker).strip().upper()
        for ticker in candidate_tickers
        if str(ticker).strip()
    }
    return session_rows.loc[session_rows["ticker"].isin(needed_tickers)].reset_index(drop=True)


def build_gate_pass_sets(gates: pd.DataFrame) -> dict[str, set[str]]:
    walk = gates.loc[gates["grid_role"].eq(WALK_FORWARD_ROLE)].copy()
    result: dict[str, set[str]] = {}
    for evaluation_date, frame in walk.groupby("evaluation_date", sort=True):
        result[str(evaluation_date)] = {
            str(row.ticker)
            for row in frame.itertuples(index=False)
            if _all_six_pass(row)
        }
    if tuple(sorted(result)) != EVALUATION_DATES:
        raise ValueError("gate pass sets do not cover the required WALK_FORWARD grid")
    return result


def build_eligibility_by_date(
    session_rows: pd.DataFrame,
    candidate_tickers: Iterable[str],
    config: EngineConfig,
) -> dict[str, pd.DataFrame]:
    candidate_universe = tuple(
        dict.fromkeys(str(ticker).strip().upper() for ticker in candidate_tickers)
    )
    output: dict[str, pd.DataFrame] = {}
    for evaluation_date in EVALUATION_DATES:
        rebalance_timestamp = pd.Timestamp(evaluation_date)
        prior_rows = session_rows.loc[
            session_rows["_date"].lt(rebalance_timestamp),
            ["ticker", "date", "volume"],
        ]
        output[evaluation_date] = compute_eligibility(
            prior_rows,
            evaluation_date,
            min_traded_sessions_12m=config.min_traded_sessions_12m,
            ticker_identity_gap_days=config.ticker_identity_gap_days,
            universe_tickers=candidate_universe,
        )
    return output


def select_eligible_targets(
    candidates: pd.DataFrame,
    eligibility: pd.DataFrame,
) -> SelectionResult:
    required = {"ticker", "rank_in_population", "_rank_numeric"}
    _require_columns(candidates, required, "candidate selection frame")
    _require_columns(eligibility, {"ticker", "eligible", "reason"}, "eligibility frame")
    if eligibility.duplicated("ticker", keep=False).any():
        raise ValueError("eligibility frame has duplicate ticker values")

    working = candidates.copy()
    eligibility_lookup = eligibility.set_index("ticker")["eligible"]
    working["_eligible"] = working["ticker"].map(eligibility_lookup).fillna(False).astype(bool)
    dropped = working.loc[~working["_eligible"], "ticker"].astype(str).tolist()
    selected = working.loc[working["_eligible"]].sort_values(
        ["_rank_numeric", "ticker"],
        kind="mergesort",
    ).head(HOLDING_COUNT).copy()
    selected_count = len(selected)
    selected["weight"] = 1.0 / selected_count if selected_count else float("nan")
    return SelectionResult(
        selected=selected.reset_index(drop=True),
        candidate_pool_size=int(working["_eligible"].sum()),
        dropped_ineligible_count=len(dropped),
        dropped_tickers=tuple(sorted(dropped)),
        selected_count=selected_count,
        short_basket=selected_count < HOLDING_COUNT,
    )


def _sorted_diagnostics(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    output["_config_order"] = output["config_id"].map(_config_order)
    return output.sort_values(
        ["_config_order", "rebalance_date"],
        kind="mergesort",
    ).drop(columns="_config_order").reset_index(drop=True)


def build_targets(
    candidates: pd.DataFrame,
    gates: pd.DataFrame,
    session_rows: pd.DataFrame,
    config: EngineConfig,
    *,
    run_date: str = RUN_DATE,
) -> BuildResult:
    gate_passes_by_date = build_gate_pass_sets(gates)
    cheap_tickers = candidates.loc[candidates["_in_cheap_set"], "ticker"].astype(str).unique()
    eligibility_by_date = build_eligibility_by_date(session_rows, cheap_tickers, config)
    selections: dict[tuple[str, str], SelectionResult] = {}
    diagnostic_rows: list[dict[str, Any]] = []
    drop_rows: list[dict[str, str]] = []

    for population_id, metric, gate_setting in CONFIG_GRID:
        config_id = _config_id(population_id, metric, gate_setting)
        for evaluation_date in EVALUATION_DATES:
            candidate_set = candidates.loc[
                candidates["evaluation_date"].eq(evaluation_date)
                & candidates["population_id"].eq(population_id)
                & candidates["metric"].eq(metric)
                & candidates["_in_cheap_set"],
            ].copy()
            if gate_setting == VALUE_PLUS_GATES:
                candidate_set = candidate_set.loc[
                    candidate_set["ticker"].isin(gate_passes_by_date[evaluation_date])
                ].copy()
            selection = select_eligible_targets(
                candidate_set,
                eligibility_by_date[evaluation_date],
            )
            selections[(config_id, evaluation_date)] = selection
            diagnostic_rows.append(
                {
                    "config_id": config_id,
                    "population_id": population_id,
                    "metric": metric,
                    "gate_setting": gate_setting,
                    "rebalance_date": evaluation_date,
                    "candidate_pool_before_eligibility": len(candidate_set),
                    "candidate_pool_size": selection.candidate_pool_size,
                    "selected_count": selection.selected_count,
                    "SHORT_BASKET": selection.short_basket,
                    "dropped_ineligible_count": selection.dropped_ineligible_count,
                }
            )
            drop_rows.extend(
                {
                    "config_id": config_id,
                    "rebalance_date": evaluation_date,
                    "ticker": ticker,
                    "reason": "INSUFFICIENT_TRADED_SESSIONS",
                }
                for ticker in selection.dropped_tickers
            )

    diagnostics = _sorted_diagnostics(pd.DataFrame(diagnostic_rows))
    diagnostics["pool_threshold"] = pd.Series(0, index=diagnostics.index, dtype=int)
    diagnostics["meets_pool_threshold"] = pd.Series(False, index=diagnostics.index, dtype=bool)
    diagnostics["THIN_CANDIDATE_POOL"] = pd.Series(False, index=diagnostics.index, dtype=bool)
    for config_id, frame in diagnostics.groupby("config_id", sort=False):
        periods = [
            (str(row.rebalance_date), int(row.candidate_pool_size))
            for row in frame.itertuples(index=False)
        ]
        _, window = compute_backtest_window(
            periods,
            HOLDING_COUNT,
            float(config.min_candidate_pool_multiple),
        )
        if len(window) != len(EVALUATION_DATES):
            raise RuntimeError("window calculation did not retain every required date")
        window = window.copy()
        window["rebalance_date"] = window["rebalance_date"].dt.date.astype(str)
        indexer = diagnostics["config_id"].eq(config_id)
        diagnostics.loc[indexer, "pool_threshold"] = window["threshold"].tolist()
        diagnostics.loc[indexer, "meets_pool_threshold"] = window["meets_threshold"].tolist()
        diagnostics.loc[indexer, "THIN_CANDIDATE_POOL"] = window[
            "THIN_CANDIDATE_POOL"
        ].tolist()

    for column in ("pool_threshold", "candidate_pool_size", "selected_count", "dropped_ineligible_count"):
        diagnostics[column] = diagnostics[column].astype(int)
    for column in ("meets_pool_threshold", "THIN_CANDIDATE_POOL", "SHORT_BASKET"):
        diagnostics[column] = diagnostics[column].astype(bool)

    diagnostics_lookup = {
        (str(row.config_id), str(row.rebalance_date)): row._asdict()
        for row in diagnostics.itertuples(index=False)
    }
    target_rows: list[dict[str, Any]] = []
    for population_id, metric, gate_setting in CONFIG_GRID:
        config_id = _config_id(population_id, metric, gate_setting)
        for evaluation_date in EVALUATION_DATES:
            selection = selections[(config_id, evaluation_date)]
            diagnostic = diagnostics_lookup[(config_id, evaluation_date)]
            for candidate in selection.selected.itertuples(index=False):
                target_rows.append(
                    {
                        "config_id": config_id,
                        "population_id": population_id,
                        "metric": metric,
                        "gate_setting": gate_setting,
                        "rebalance_date": evaluation_date,
                        "ticker": str(candidate.ticker),
                        "rank_in_population": candidate.rank_in_population,
                        "weight": candidate.weight,
                        "selected_count": diagnostic["selected_count"],
                        "candidate_pool_size": diagnostic["candidate_pool_size"],
                        "pool_threshold": diagnostic["pool_threshold"],
                        "meets_pool_threshold": diagnostic["meets_pool_threshold"],
                        "THIN_CANDIDATE_POOL": diagnostic["THIN_CANDIDATE_POOL"],
                        "SHORT_BASKET": diagnostic["SHORT_BASKET"],
                        "dropped_ineligible_count": diagnostic["dropped_ineligible_count"],
                        "source": SOURCE_LABEL,
                        "as_of": run_date,
                        "data_status": "OK",
                    }
                )
    targets = pd.DataFrame(target_rows, columns=OUTPUT_COLUMNS)
    if not targets.empty:
        targets["_config_order"] = targets["config_id"].map(_config_order)
        targets["_rank_numeric"] = pd.to_numeric(targets["rank_in_population"], errors="raise")
        targets = targets.sort_values(
            ["_config_order", "rebalance_date", "_rank_numeric", "ticker"],
            kind="mergesort",
        ).drop(columns=["_config_order", "_rank_numeric"]).reset_index(drop=True)
    validate_targets(targets, diagnostics)
    return BuildResult(
        targets=targets,
        diagnostics=diagnostics,
        drop_events=pd.DataFrame(drop_rows, columns=("config_id", "rebalance_date", "ticker", "reason")),
        gate_passes_by_date=gate_passes_by_date,
    )


def validate_targets(targets: pd.DataFrame, diagnostics: pd.DataFrame) -> None:
    if tuple(targets.columns) != OUTPUT_COLUMNS:
        raise RuntimeError("target output column order differs from the contract")
    if targets.duplicated(["config_id", "rebalance_date", "ticker"], keep=False).any():
        raise RuntimeError("target output has duplicate config_id/rebalance_date/ticker keys")
    config_ids = {_config_id(*parts) for parts in CONFIG_GRID}
    if set(targets["config_id"]) != config_ids:
        raise RuntimeError("target output does not contain every required configuration")
    if len(diagnostics) != len(CONFIG_GRID) * len(EVALUATION_DATES):
        raise RuntimeError("diagnostics do not contain every configuration/date")
    for population_id, metric, gate_setting in CONFIG_GRID:
        config_id = _config_id(population_id, metric, gate_setting)
        actual_dates = tuple(
            sorted(targets.loc[targets["config_id"].eq(config_id), "rebalance_date"].unique())
        )
        expected_dates = EVALUATION_DATES if gate_setting == VALUE_ONLY else GATED_OUTPUT_DATES
        if actual_dates != expected_dates:
            raise RuntimeError(f"unexpected populated dates for {config_id}: {actual_dates}")


def _markdown_table(headers: Iterable[Any], rows: Iterable[Iterable[Any]]) -> str:
    header_values = [str(value) for value in headers]
    lines = [
        "| " + " | ".join(header_values) + " |",
        "| " + " | ".join("---" for _ in header_values) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def _nonempty_date_range(frame: pd.DataFrame) -> tuple[str, str]:
    dates = frame.loc[frame["selected_count"].gt(0), "rebalance_date"].astype(str).tolist()
    return (min(dates), max(dates)) if dates else ("", "")


def _overlap_rows(targets: pd.DataFrame) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for population_id in POPULATIONS:
        for metric in METRICS:
            value_config = _config_id(population_id, metric, VALUE_ONLY)
            gated_config = _config_id(population_id, metric, VALUE_PLUS_GATES)
            for rebalance_date in GATED_OUTPUT_DATES:
                value_names = set(
                    targets.loc[
                        targets["config_id"].eq(value_config)
                        & targets["rebalance_date"].eq(rebalance_date),
                        "ticker",
                    ]
                )
                gated_names = set(
                    targets.loc[
                        targets["config_id"].eq(gated_config)
                        & targets["rebalance_date"].eq(rebalance_date),
                        "ticker",
                    ]
                )
                rows.append(
                    [
                        population_id,
                        metric,
                        rebalance_date,
                        len(value_names),
                        len(gated_names),
                        len(value_names & gated_names),
                        f"{len(value_names & gated_names)} / {HOLDING_COUNT}",
                    ]
                )
    return rows


def write_report(
    *,
    output_path: Path,
    targets: pd.DataFrame,
    diagnostics: pd.DataFrame,
    drop_events: pd.DataFrame,
    sha256: str,
) -> None:
    config_date_rows = []
    r2_rows = []
    r3_rows = []
    r3_thin_rows = []
    r4_total_rows = []
    for population_id, metric, gate_setting in CONFIG_GRID:
        config_id = _config_id(population_id, metric, gate_setting)
        frame = diagnostics.loc[diagnostics["config_id"].eq(config_id)].copy()
        emitted_dates = targets.loc[targets["config_id"].eq(config_id), "rebalance_date"].nunique()
        config_date_rows.append([config_id, emitted_dates])
        first_date, last_date = _nonempty_date_range(frame)
        r2_rows.append(
            [
                config_id,
                int(frame["selected_count"].eq(HOLDING_COUNT).sum()),
                int(frame["SHORT_BASKET"].sum()),
                first_date,
                last_date,
            ]
        )
        r3_rows.extend(
            [
                config_id,
                row.rebalance_date,
                int(row.candidate_pool_size),
                int(row.pool_threshold),
                bool(row.meets_pool_threshold),
                bool(row.THIN_CANDIDATE_POOL),
            ]
            for row in frame.itertuples(index=False)
        )
        r3_thin_rows.append([config_id, int(frame["THIN_CANDIDATE_POOL"].sum())])
        r4_total_rows.append([config_id, int(frame["dropped_ineligible_count"].sum())])

    top_dropped = (
        drop_events.groupby("ticker", sort=True).size().reset_index(name="drop_count")
        if not drop_events.empty
        else pd.DataFrame(columns=("ticker", "drop_count"))
    )
    if not top_dropped.empty:
        top_dropped = top_dropped.sort_values(
            ["drop_count", "ticker"],
            ascending=[False, True],
            kind="mergesort",
        ).head(5)
        top_dropped_rows = top_dropped.loc[:, ["ticker", "drop_count"]].values.tolist()
    else:
        top_dropped_rows = [["NONE", 0]]

    lines = [
        "# Sprint 9-5A Rebalance Targets",
        "",
        "## R1. Output identity and coverage",
        "",
        _markdown_table(
            ["measure", "value"],
            [
                ["row_count", len(targets)],
                ["distinct config_id", targets["config_id"].nunique()],
                ["SHA-256", sha256],
            ],
        ),
        "",
        _markdown_table(
            ["config_id", "distinct rebalance_date count"],
            config_date_rows,
        ),
        "",
        "## R2. Basket coverage",
        "",
        _markdown_table(
            [
                "config_id",
                f"full {HOLDING_COUNT}-name basket dates",
                "SHORT_BASKET dates",
                "first date carrying names",
                "last date carrying names",
            ],
            r2_rows,
        ),
        "",
        "## R3. Candidate pools after eligibility",
        "",
        _markdown_table(
            [
                "config_id",
                "rebalance_date",
                "candidate_pool_size",
                "pool_threshold",
                "meets_pool_threshold",
                "THIN_CANDIDATE_POOL",
            ],
            r3_rows,
        ),
        "",
        "### R3 thin-pool date counts",
        "",
        _markdown_table(["config_id", "THIN_CANDIDATE_POOL dates"], r3_thin_rows),
        "",
        "## R4. Eligibility drops",
        "",
        "Every recorded drop has reason `INSUFFICIENT_TRADED_SESSIONS`.",
        "",
        _markdown_table(
            ["config_id", "total candidates dropped by eligibility"],
            r4_total_rows,
        ),
        "",
        _markdown_table(
            ["ticker", "drop count across all configurations and dates"],
            top_dropped_rows,
        ),
        "",
        "## R5. VALUE_ONLY / VALUE_PLUS_GATES basket overlap",
        "",
        _markdown_table(
            [
                "population_id",
                "metric",
                "rebalance_date",
                "VALUE_ONLY selected",
                "VALUE_PLUS_GATES selected",
                "common names",
                f"common names out of {HOLDING_COUNT}",
            ],
            _overlap_rows(targets),
        ),
        "",
        "## R6. Known biases",
        "",
    ]
    lines.extend(f"- {bias}" for bias in KNOWN_BIASES)
    lines.extend(
        [
            "- No price, return or performance figure appears anywhere in this sprint; basket composition alone proves nothing about profitability.",
            "",
            "The selection rank is copied from Sprint 9-4A and is not recomputed. The sector cap remains an open question for a later sprint because the historical candidate inputs do not provide the required point-in-time sector fields.",
            "",
            f"- Output path: `{output_path.relative_to(ROOT).as_posix()}`.",
            f"- SHA-256: `{sha256}`.",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Sprint 9-5A point-in-time rebalance targets.")
    parser.add_argument("--run-date", default=RUN_DATE, help="Required run date (YYYY-MM-DD).")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_date = str(args.run_date)
    if run_date != RUN_DATE:
        raise ValueError(f"Sprint 9-5A run date must be {RUN_DATE}")
    print(f"RUN_DATE={run_date}", flush=True)
    config = load_engine_config(CONFIG_PATH)
    candidates, gates = load_inputs()
    candidate_tickers = candidates.loc[candidates["_in_cheap_set"], "ticker"].astype(str).unique()
    session_rows = load_session_rows(candidate_tickers)
    result = build_targets(candidates, gates, session_rows, config, run_date=run_date)
    output_path = OUTPUT_ROOT / run_date / "rebalance_targets_point_in_time.csv.gz"
    sha256 = write_deterministic_gzip_csv(result.targets, output_path)
    write_report(
        output_path=output_path,
        targets=result.targets,
        diagnostics=result.diagnostics,
        drop_events=result.drop_events,
        sha256=sha256,
    )
    print(f"OUTPUT={output_path}")
    print(f"ROW_COUNT={len(result.targets)}")
    print(f"SHA256={sha256}")
    print(f"REPORT={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
