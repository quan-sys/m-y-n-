from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Iterable

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

from scripts.build_sprint9_4c_gates_as_of import write_deterministic_gzip_csv  # noqa: E402


RUN_DATE = "2026-07-28"
VALUE_SERIES_PATH = ROOT / "data" / "backtest" / "walk_forward" / RUN_DATE / "value_series.csv.gz"
BENCHMARK_PATH = ROOT / "data" / "price_history" / RUN_DATE / "benchmark_daily_close.csv.gz"
OUTPUT_DIR = ROOT / "data" / "backtest" / "walk_forward" / RUN_DATE
COMPARISON_PATH = OUTPUT_DIR / "benchmark_comparison.csv.gz"
SUMMARY_PATH = OUTPUT_DIR / "benchmark_comparison_summary.csv"
REPORT_PATH = ROOT / "docs" / "REPORT_BENCHMARK_COMPARISON.md"

DIAGNOSTIC_LABEL = "DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS"
VALUE_REQUIRED_COLUMNS = {
    "config_id",
    "evaluation_date",
    "execution_date",
    "portfolio_value",
    "cash",
    "status",
    "missing_tickers",
    "in_window",
}
BENCHMARK_REQUIRED_COLUMNS = {
    "ticker",
    "date",
    "close_adjusted",
    "close_adjusted_unit",
    "volume",
    "source",
    "as_of",
    "data_status",
}
COMPARISON_COLUMNS = (
    "config_id",
    "previous_evaluation_date",
    "evaluation_date",
    "previous_execution_date",
    "execution_date",
    "previous_portfolio_value",
    "portfolio_value",
    "portfolio_return",
    "previous_benchmark_index_level",
    "benchmark_index_level",
    "benchmark_return",
    "diagnostic_label",
    "previous_nominal_date_resolved",
    "nominal_date_resolved",
    "previous_diagnostic_index_level",
    "diagnostic_index_level",
    "benchmark_return_diag",
    "excess_return",
    "excess_return_diag",
    "source",
    "as_of",
    "data_status",
)
SUMMARY_COLUMNS = (
    "config_id",
    "period_count",
    "cumulative_portfolio_growth",
    "cumulative_benchmark_growth",
    "cumulative_excess",
    "cumulative_benchmark_growth_diag",
    "cumulative_excess_diag",
    "diagnostic_label",
    "source",
    "as_of",
    "data_status",
)


class BenchmarkComparisonError(ValueError):
    """Raised when the two committed inputs cannot support a faithful comparison."""


@dataclass(frozen=True)
class ComparisonArtifacts:
    comparison: pd.DataFrame
    summary: pd.DataFrame


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"required input does not exist: {path}")
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def _require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise BenchmarkComparisonError(f"{label} is missing required columns: {', '.join(missing)}")


def _parse_dates(frame: pd.DataFrame, column: str, label: str) -> pd.Series:
    values = pd.to_datetime(frame[column], format="%Y-%m-%d", errors="coerce")
    if values.isna().any():
        bad = frame.loc[values.isna(), column].iloc[0]
        raise BenchmarkComparisonError(f"{label} has invalid {column}: {bad!r}")
    return values.dt.normalize()


def _prepare_value_series(value_series: pd.DataFrame) -> pd.DataFrame:
    _require_columns(value_series, VALUE_REQUIRED_COLUMNS, "value series")
    values = value_series.copy()
    allowed_in_window = {"True", "False"}
    unexpected = sorted(set(values["in_window"]) - allowed_in_window)
    if unexpected:
        raise BenchmarkComparisonError(
            "value series has unsupported in_window values: " + ", ".join(unexpected)
        )
    values = values.loc[values["in_window"].eq("True")].copy()
    if values.empty:
        raise BenchmarkComparisonError("value series has no in-window observations")

    values["evaluation_timestamp"] = _parse_dates(values, "evaluation_date", "value series")
    values["execution_timestamp"] = _parse_dates(values, "execution_date", "value series")
    values["portfolio_value_numeric"] = pd.to_numeric(values["portfolio_value"], errors="coerce")
    if values["portfolio_value_numeric"].isna().any():
        row = values.loc[values["portfolio_value_numeric"].isna()].iloc[0]
        raise BenchmarkComparisonError(
            f"value series has non-numeric portfolio_value for {row['config_id']} "
            f"at {row['evaluation_date']}: {row['portfolio_value']!r}"
        )
    if (values["portfolio_value_numeric"] <= 0).any():
        row = values.loc[values["portfolio_value_numeric"] <= 0].iloc[0]
        raise BenchmarkComparisonError(
            f"value series has non-positive portfolio_value for {row['config_id']} "
            f"at {row['evaluation_date']}: {row['portfolio_value']!r}"
        )
    if values.duplicated(["config_id", "evaluation_date"]).any():
        row = values.loc[values.duplicated(["config_id", "evaluation_date"], keep=False)].iloc[0]
        raise BenchmarkComparisonError(
            f"value series has duplicate in-window observation for {row['config_id']} "
            f"at {row['evaluation_date']}"
        )
    return values.sort_values(["config_id", "evaluation_timestamp"], kind="stable").reset_index(drop=True)


def _prepare_benchmark(benchmark: pd.DataFrame) -> pd.DataFrame:
    _require_columns(benchmark, BENCHMARK_REQUIRED_COLUMNS, "benchmark history")
    values = benchmark.copy()
    if set(values["ticker"]) != {"VNINDEX"}:
        raise BenchmarkComparisonError("benchmark history must contain VNINDEX only")
    if set(values["close_adjusted_unit"]) != {"INDEX_POINTS"}:
        raise BenchmarkComparisonError("benchmark history must use close_adjusted_unit=INDEX_POINTS")
    non_ok = values.loc[~values["data_status"].eq("OK")]
    if not non_ok.empty:
        raise BenchmarkComparisonError(
            f"benchmark history has non-OK data_status at {non_ok.iloc[0]['date']}: "
            f"{non_ok.iloc[0]['data_status']}"
        )
    values["session_timestamp"] = _parse_dates(values, "date", "benchmark history")
    values["index_level"] = pd.to_numeric(values["close_adjusted"], errors="coerce")
    if values["index_level"].isna().any() or (values["index_level"] <= 0).any():
        row = values.loc[values["index_level"].isna() | values["index_level"].le(0)].iloc[0]
        raise BenchmarkComparisonError(
            f"benchmark history has invalid close_adjusted at {row['date']}: "
            f"{row['close_adjusted']!r}"
        )
    if values.duplicated("date").any():
        date = values.loc[values.duplicated("date", keep=False), "date"].iloc[0]
        raise BenchmarkComparisonError(f"benchmark history has duplicate VNINDEX session: {date}")
    return values.sort_values("session_timestamp", kind="stable").reset_index(drop=True)


def resolve_nominal_session(
    nominal_date: str | pd.Timestamp,
    benchmark_sessions: pd.DatetimeIndex,
) -> pd.Timestamp:
    """Resolve a nominal date to the final observed VNINDEX session on or before it."""

    target = pd.Timestamp(nominal_date).normalize()
    position = benchmark_sessions.searchsorted(target, side="right") - 1
    if position < 0:
        raise BenchmarkComparisonError(
            f"VNINDEX has no observed session on or before nominal evaluation date {target.date().isoformat()}"
        )
    return benchmark_sessions[position]


def _require_execution_level(
    index_by_session: dict[pd.Timestamp, float],
    config_id: str,
    execution_timestamp: pd.Timestamp,
) -> float:
    level = index_by_session.get(execution_timestamp)
    if level is None:
        raise BenchmarkComparisonError(
            f"{config_id}: VNINDEX is missing observed execution session "
            f"{execution_timestamp.date().isoformat()}"
        )
    return level


def _compound_growth(returns: Iterable[float]) -> float:
    factor = 1.0
    for value in returns:
        factor *= 1.0 + float(value)
    return factor - 1.0


def build_benchmark_comparison(
    value_series: pd.DataFrame,
    benchmark_history: pd.DataFrame,
    *,
    run_date: str,
    source: str,
) -> ComparisonArtifacts:
    """Build the primary execution-date and diagnostic nominal-date comparison."""

    values = _prepare_value_series(value_series)
    benchmark = _prepare_benchmark(benchmark_history)
    sessions = pd.DatetimeIndex(benchmark["session_timestamp"])
    index_by_session = {
        timestamp: float(level)
        for timestamp, level in zip(benchmark["session_timestamp"], benchmark["index_level"], strict=True)
    }

    comparison_rows: list[dict[str, object]] = []
    for config_id, config_rows in values.groupby("config_id", sort=True):
        ordered = config_rows.sort_values("evaluation_timestamp", kind="stable").reset_index(drop=True)
        if len(ordered) < 2:
            raise BenchmarkComparisonError(f"{config_id}: fewer than two in-window observations")
        if not ordered["evaluation_timestamp"].is_monotonic_increasing:
            raise BenchmarkComparisonError(f"{config_id}: evaluation dates are not ordered")
        for previous, current in zip(
            ordered.iloc[:-1].itertuples(index=False),
            ordered.iloc[1:].itertuples(index=False),
            strict=True,
        ):
            if current.evaluation_timestamp <= previous.evaluation_timestamp:
                raise BenchmarkComparisonError(
                    f"{config_id}: evaluation dates are not strictly increasing at "
                    f"{current.evaluation_date}"
                )
            previous_level = _require_execution_level(
                index_by_session, config_id, previous.execution_timestamp
            )
            current_level = _require_execution_level(
                index_by_session, config_id, current.execution_timestamp
            )
            previous_nominal = resolve_nominal_session(previous.evaluation_timestamp, sessions)
            current_nominal = resolve_nominal_session(current.evaluation_timestamp, sessions)
            previous_diagnostic_level = index_by_session[previous_nominal]
            current_diagnostic_level = index_by_session[current_nominal]
            portfolio_return = (
                float(current.portfolio_value_numeric) / float(previous.portfolio_value_numeric) - 1.0
            )
            benchmark_return = current_level / previous_level - 1.0
            benchmark_return_diag = current_diagnostic_level / previous_diagnostic_level - 1.0
            comparison_rows.append(
                {
                    "config_id": config_id,
                    "previous_evaluation_date": previous.evaluation_timestamp.date().isoformat(),
                    "evaluation_date": current.evaluation_timestamp.date().isoformat(),
                    "previous_execution_date": previous.execution_timestamp.date().isoformat(),
                    "execution_date": current.execution_timestamp.date().isoformat(),
                    "previous_portfolio_value": float(previous.portfolio_value_numeric),
                    "portfolio_value": float(current.portfolio_value_numeric),
                    "portfolio_return": portfolio_return,
                    "previous_benchmark_index_level": previous_level,
                    "benchmark_index_level": current_level,
                    "benchmark_return": benchmark_return,
                    "diagnostic_label": DIAGNOSTIC_LABEL,
                    "previous_nominal_date_resolved": previous_nominal.date().isoformat(),
                    "nominal_date_resolved": current_nominal.date().isoformat(),
                    "previous_diagnostic_index_level": previous_diagnostic_level,
                    "diagnostic_index_level": current_diagnostic_level,
                    "benchmark_return_diag": benchmark_return_diag,
                    "excess_return": portfolio_return - benchmark_return,
                    "excess_return_diag": portfolio_return - benchmark_return_diag,
                    "source": source,
                    "as_of": run_date,
                    "data_status": "OK",
                }
            )

    comparison = pd.DataFrame(comparison_rows, columns=COMPARISON_COLUMNS)
    summary_rows: list[dict[str, object]] = []
    for config_id, periods in comparison.groupby("config_id", sort=True):
        portfolio_growth = _compound_growth(periods["portfolio_return"])
        benchmark_growth = _compound_growth(periods["benchmark_return"])
        benchmark_growth_diag = _compound_growth(periods["benchmark_return_diag"])
        summary_rows.append(
            {
                "config_id": config_id,
                "period_count": int(len(periods)),
                "cumulative_portfolio_growth": portfolio_growth,
                "cumulative_benchmark_growth": benchmark_growth,
                "cumulative_excess": (1.0 + portfolio_growth) / (1.0 + benchmark_growth) - 1.0,
                "cumulative_benchmark_growth_diag": benchmark_growth_diag,
                "cumulative_excess_diag": (1.0 + portfolio_growth)
                / (1.0 + benchmark_growth_diag)
                - 1.0,
                "diagnostic_label": DIAGNOSTIC_LABEL,
                "source": source,
                "as_of": run_date,
                "data_status": "OK",
            }
        )
    summary = pd.DataFrame(summary_rows, columns=SUMMARY_COLUMNS)
    return ComparisonArtifacts(comparison=comparison, summary=summary)


def _format_number(value: object) -> str:
    return format(float(value), ".15g")


def _trace_lines(comparison: pd.DataFrame) -> list[str]:
    trace = comparison.loc[
        comparison["config_id"].eq("ALL__ebit_tev__VALUE_ONLY")
    ].head(3)
    lines = [
        "## Required trace: ALL__ebit_tev__VALUE_ONLY",
        "",
        "| Period | Field | Value |",
        "| ---: | --- | --- |",
    ]
    fields = (
        "previous_evaluation_date",
        "evaluation_date",
        "previous_execution_date",
        "execution_date",
        "previous_portfolio_value",
        "portfolio_value",
        "portfolio_return",
        "previous_benchmark_index_level",
        "benchmark_index_level",
        "benchmark_return",
        "previous_nominal_date_resolved",
        "nominal_date_resolved",
        "previous_diagnostic_index_level",
        "diagnostic_index_level",
        "benchmark_return_diag",
        "excess_return",
        "excess_return_diag",
        "diagnostic_label",
    )
    for period, row in enumerate(trace.itertuples(index=False), start=1):
        values = row._asdict()
        for field in fields:
            value = values[field]
            text = _format_number(value) if isinstance(value, float) else str(value)
            lines.append(f"| {period} | {field} | {text} |")
    return lines


def _summary_lines(summary: pd.DataFrame) -> list[str]:
    lines = [
        "## Per-configuration geometric summaries",
        "",
        "These are separate diagnostics by configuration, not a ranking, selection, recommendation, or conclusion.",
        "",
        "| config_id | period_count | cumulative_portfolio_growth | cumulative_benchmark_growth | cumulative_excess | cumulative_benchmark_growth_diag | cumulative_excess_diag | diagnostic_label |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in summary.itertuples(index=False):
        lines.append(
            "| {config_id} | {period_count} | {portfolio} | {benchmark} | {excess} | {diag_benchmark} | {diag_excess} | {label} |".format(
                config_id=row.config_id,
                period_count=row.period_count,
                portfolio=_format_number(row.cumulative_portfolio_growth),
                benchmark=_format_number(row.cumulative_benchmark_growth),
                excess=_format_number(row.cumulative_excess),
                diag_benchmark=_format_number(row.cumulative_benchmark_growth_diag),
                diag_excess=_format_number(row.cumulative_excess_diag),
                label=row.diagnostic_label,
            )
        )
    return lines


def write_report(
    *,
    comparison: pd.DataFrame,
    summary: pd.DataFrame,
    run_date: str,
    comparison_hash: str,
) -> None:
    lines = [
        "# Benchmark Comparison Report",
        "",
        "## Scope",
        "",
        f"This report uses only the committed {VALUE_SERIES_PATH.relative_to(ROOT).as_posix()} and {BENCHMARK_PATH.relative_to(ROOT).as_posix()} inputs as read on {run_date}.",
        "The primary comparison uses consecutive execution dates. The nominal-date comparison is labelled DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS throughout and is not used for a conclusion, ranking, configuration selection, or recommendation.",
        "",
        "## Output verification",
        "",
        f"- Comparison rows: {len(comparison)}.",
        f"- Period count by configuration: {comparison.groupby('config_id', sort=True).size().to_dict()}.",
        f"- Deterministic SHA-256 of benchmark_comparison.csv.gz: {comparison_hash}.",
        "",
        *_trace_lines(comparison),
        "",
        *_summary_lines(summary),
        "",
        "## Known biases of this comparison",
        "",
        "1. VNINDEX is a PRICE index and excludes dividends, while the portfolio price series is ADJUSTED_OBSERVED according to data_contract.md; if the portfolio series is dividend-adjusted, the comparison is systematically favourable to the strategy by roughly the market dividend yield each period, compounding over time, so even smaller apparent outperformance may contain no skill, and a total-return index is unavailable here.",
        "2. Portfolio values are net of the configured transaction costs, while the VNINDEX price index carries no equivalent trading cost.",
        "3. The portfolio history remains contaminated by survivorship and financial-statement restatement bias; this comparison does not repair either contamination.",
        "",
        "## Boundaries",
        "",
        "No CAGR, Sharpe, Sortino, drawdown, alpha, beta, regression, information ratio, tracking error, t-statistic, or risk-adjusted statistic is calculated. No index session is filled, interpolated, or fabricated.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(artifacts: ComparisonArtifacts, *, run_date: str) -> tuple[str, Path, Path]:
    if run_date != RUN_DATE:
        raise ValueError(f"benchmark comparison run date must be {RUN_DATE}")
    for path in (COMPARISON_PATH, SUMMARY_PATH):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite existing output: {path}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    comparison_hash = write_deterministic_gzip_csv(artifacts.comparison, COMPARISON_PATH)
    artifacts.summary.to_csv(SUMMARY_PATH, index=False, lineterminator="\n")
    return comparison_hash, COMPARISON_PATH, SUMMARY_PATH


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build observed VNINDEX benchmark-comparison diagnostics."
    )
    parser.add_argument("--run-date", default=RUN_DATE, help="Required run date (YYYY-MM-DD).")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_date = str(args.run_date)
    if run_date != RUN_DATE:
        raise ValueError(f"benchmark comparison run date must be {RUN_DATE}")
    value_series = _read_csv(VALUE_SERIES_PATH)
    benchmark_history = _read_csv(BENCHMARK_PATH)
    source = (
        f"{VALUE_SERIES_PATH.relative_to(ROOT).as_posix()}|"
        f"{BENCHMARK_PATH.relative_to(ROOT).as_posix()}"
    )
    artifacts = build_benchmark_comparison(
        value_series,
        benchmark_history,
        run_date=run_date,
        source=source,
    )
    comparison_hash, comparison_path, summary_path = write_outputs(artifacts, run_date=run_date)
    write_report(
        comparison=artifacts.comparison,
        summary=artifacts.summary,
        run_date=run_date,
        comparison_hash=comparison_hash,
    )
    print(f"RUN_DATE={run_date}")
    print(f"COMPARISON_ROWS={len(artifacts.comparison)}")
    print(
        "PERIOD_COUNTS="
        + str(artifacts.comparison.groupby("config_id", sort=True).size().to_dict())
    )
    print(f"COMPARISON_SHA256={comparison_hash}")
    print(f"COMPARISON_PATH={comparison_path.relative_to(ROOT).as_posix()}")
    print(f"SUMMARY_PATH={summary_path.relative_to(ROOT).as_posix()}")
    print(f"REPORT_PATH={REPORT_PATH.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
