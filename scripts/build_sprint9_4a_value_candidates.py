from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation, getcontext
import gzip
import hashlib
import io
from pathlib import Path
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
INPUT_PATH = (
    ROOT
    / "data"
    / "valuation"
    / "2026-07-26"
    / "historical_valuation_point_in_time.csv.gz"
)
CONFIG_PATH = ROOT / "config" / "screener.yaml"
OUTPUT_ROOT = ROOT / "data" / "screener" / "candidates_pit"
REPORT_PATH = ROOT / "docs" / "REPORT_SPRINT_9_4A_VALUE_CANDIDATES.md"
TIME_ZONE = ZoneInfo("Asia/Ho_Chi_Minh")
EARLIEST_DATE = "2019-03-31"
TARGET_SIZES = (20, 25)
THIN_POOL_TARGET = 20
BASKET_LABEL = (
    "VALUE-ONLY BASKET — no fraud, distress or quality gate has been applied; "
    "this is NOT the final screener basket."
)
OUTPUT_COLUMNS = (
    "evaluation_date",
    "quarter",
    "ticker",
    "metric",
    "population_id",
    "metric_value",
    "rank_in_population",
    "population_size",
    "percentile",
    "in_cheap_set",
    "price_confidence",
    "market_cap_status",
    "basket_label",
    "source",
    "as_of",
    "data_status",
)
METRICS = {
    "ebit_tev": "ebit_tev_eligible",
    "e_p": "e_p_eligible",
}
POPULATIONS = (
    "ALL",
    "ALL_EX_UPPER_BOUND",
    "PRICE_OK",
    "PRICE_OK_EX_UPPER_BOUND",
)


@dataclass(frozen=True)
class ValueConfig:
    value_cheapest_pct: Decimal
    min_candidate_pool_multiple: Decimal
    selection_ratio_report_threshold: Decimal


def load_config(path: Path = CONFIG_PATH) -> ValueConfig:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    required = (
        "VALUE_CHEAPEST_PCT",
        "MIN_CANDIDATE_POOL_MULTIPLE",
        "SELECTION_RATIO_REPORT_THRESHOLD",
    )
    missing = [key for key in required if key not in values]
    if missing:
        raise ValueError("config missing values: " + ", ".join(missing))
    config = ValueConfig(
        value_cheapest_pct=Decimal(values["VALUE_CHEAPEST_PCT"]),
        min_candidate_pool_multiple=Decimal(
            values["MIN_CANDIDATE_POOL_MULTIPLE"]
        ),
        selection_ratio_report_threshold=Decimal(
            values["SELECTION_RATIO_REPORT_THRESHOLD"]
        ),
    )
    if not Decimal("0") < config.value_cheapest_pct <= Decimal("1"):
        raise ValueError("VALUE_CHEAPEST_PCT must be in (0, 1]")
    if config.min_candidate_pool_multiple <= 0:
        raise ValueError("MIN_CANDIDATE_POOL_MULTIPLE must be positive")
    if not Decimal("0") <= config.selection_ratio_report_threshold <= Decimal("1"):
        raise ValueError(
            "SELECTION_RATIO_REPORT_THRESHOLD must be between zero and one"
        )
    return config


def to_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError(f"invalid metric value: {value}") from exc


def decimal_text(value: Decimal | None) -> str:
    if value is None:
        return ""
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def bool_value(value: Any) -> bool:
    normalized = str(value).strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"invalid boolean value: {value}")


def population_mask(frame: pd.DataFrame, population_id: str) -> pd.Series:
    mask = pd.Series(True, index=frame.index)
    if population_id in {"ALL_EX_UPPER_BOUND", "PRICE_OK_EX_UPPER_BOUND"}:
        mask &= frame["market_cap_status"].ne("UPPER_BOUND")
    if population_id in {"PRICE_OK", "PRICE_OK_EX_UPPER_BOUND"}:
        mask &= frame["price_confidence"].eq("OK")
    return mask


def rank_population(
    frame: pd.DataFrame,
    *,
    metric: str,
    population_id: str,
    config: ValueConfig,
    run_date: str,
) -> pd.DataFrame:
    eligibility_column = METRICS[metric]
    eligible = frame.loc[
        frame["valuation_status"].eq("OK")
        & frame[eligibility_column].map(bool_value)
        & frame[metric].ne("")
    ].copy()
    eligible = eligible.loc[population_mask(eligible, population_id)].copy()
    if eligible.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    eligible["_metric_decimal"] = eligible[metric].map(to_decimal)
    eligible["rank_in_population"] = eligible["_metric_decimal"].rank(
        method="average", ascending=False
    )
    population_size = len(eligible)
    if population_size == 1:
        eligible["percentile"] = Decimal("1")
    else:
        denominator = Decimal(population_size - 1)
        eligible["percentile"] = eligible["rank_in_population"].map(
            lambda rank: (
                Decimal(population_size) - Decimal(str(rank))
            )
            / denominator
        )
    cheap_cut = Decimal("1") - config.value_cheapest_pct
    eligible["in_cheap_set"] = eligible["percentile"].map(
        lambda value: value >= cheap_cut
    )
    eligible["metric_value"] = eligible[metric]
    eligible["metric"] = metric
    eligible["population_id"] = population_id
    eligible["population_size"] = population_size
    eligible["basket_label"] = BASKET_LABEL
    eligible["source"] = (
        "Sprint 9-3 historical valuation point-in-time; "
        "config/screener.yaml value thresholds"
    )
    eligible["as_of"] = run_date
    eligible["data_status"] = "OK"
    return eligible.loc[:, OUTPUT_COLUMNS]


def load_input() -> pd.DataFrame:
    frame = pd.read_csv(INPUT_PATH, dtype=str, keep_default_na=False)
    required = {
        "evaluation_date",
        "quarter",
        "ticker",
        "ebit_tev",
        "e_p",
        "ebit_tev_eligible",
        "e_p_eligible",
        "price_confidence",
        "market_cap_status",
        "valuation_status",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"input missing columns: {missing}")
    return frame


def build_output(
    frame: pd.DataFrame,
    *,
    config: ValueConfig,
    run_date: str,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for evaluation_date, date_frame in frame.groupby(
        "evaluation_date", sort=True
    ):
        for metric in METRICS:
            for population_id in POPULATIONS:
                ranked = rank_population(
                    date_frame,
                    metric=metric,
                    population_id=population_id,
                    config=config,
                    run_date=run_date,
                )
                if not ranked.empty:
                    frames.append(ranked)
    if not frames:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    output = pd.concat(frames, ignore_index=True)
    return output.sort_values(
        [
            "evaluation_date",
            "metric",
            "population_id",
            "rank_in_population",
            "ticker",
        ],
        kind="stable",
    ).reset_index(drop=True)


def pool_diagnostics(output: pd.DataFrame, config: ValueConfig) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    grouped = output.groupby(
        ["evaluation_date", "metric", "population_id"], sort=True
    )
    for (evaluation_date, metric, population_id), frame in grouped:
        cheap_set_size = int(frame["in_cheap_set"].sum())
        row: dict[str, Any] = {
            "evaluation_date": evaluation_date,
            "metric": metric,
            "population_id": population_id,
            "population_size": len(frame),
            "cheap_set_size": cheap_set_size,
            "thin_candidate_pool": (
                Decimal(cheap_set_size)
                < Decimal(THIN_POOL_TARGET)
                * config.min_candidate_pool_multiple
            ),
        }
        for target_size in TARGET_SIZES:
            ratio = (
                Decimal(target_size) / Decimal(cheap_set_size)
                if cheap_set_size
                else None
            )
            row[f"selection_ratio_{target_size}"] = ratio
            row[f"low_selectivity_{target_size}"] = (
                ratio is None
                or ratio > config.selection_ratio_report_threshold
            )
        rows.append(row)
    return pd.DataFrame(rows)


def validate_stop_gates(output: pd.DataFrame, config: ValueConfig) -> None:
    violations: list[dict[str, Any]] = []
    grouped = output.groupby(
        ["evaluation_date", "metric", "population_id"], sort=False
    )
    for keys, frame in grouped:
        maximum = max(frame["metric_value"].map(to_decimal))
        maximum_rows = frame.loc[
            frame["metric_value"].map(to_decimal).eq(maximum)
        ]
        if not (
            maximum_rows["rank_in_population"].eq(1).all()
            and maximum_rows["percentile"].map(to_decimal).eq(Decimal("1")).all()
            and maximum_rows["in_cheap_set"].all()
        ):
            violations.append({"gate": "DIRECTION", "group": keys})
    early = output.loc[output["evaluation_date"].lt(EARLIEST_DATE)]
    if not early.empty:
        violations.append(
            {
                "gate": "EARLIEST_DATE",
                "rows": early.loc[
                    :, ["evaluation_date", "metric", "population_id", "ticker"]
                ].to_dict(orient="records"),
            }
        )
    duplicate = output.duplicated(
        ["evaluation_date", "metric", "population_id", "ticker"], keep=False
    )
    if bool(duplicate.any()):
        violations.append(
            {
                "gate": "DUPLICATE",
                "rows": output.loc[
                    duplicate,
                    ["evaluation_date", "metric", "population_id", "ticker"],
                ].to_dict(orient="records"),
            }
        )
    cheap_cut = Decimal("1") - config.value_cheapest_pct
    invalid_cut = output["in_cheap_set"] & output["percentile"].map(
        to_decimal
    ).lt(cheap_cut)
    if bool(invalid_cut.any()):
        violations.append(
            {
                "gate": "CHEAP_CUT",
                "rows": output.loc[
                    invalid_cut,
                    [
                        "evaluation_date",
                        "metric",
                        "population_id",
                        "ticker",
                        "percentile",
                    ],
                ].to_dict(orient="records"),
            }
        )
    if violations:
        raise RuntimeError(f"STOP gate violations: {violations}")
    if output.empty or output["evaluation_date"].min() != EARLIEST_DATE:
        raise RuntimeError(
            "STOP: first evaluation_date is not exactly " + EARLIEST_DATE
        )


def output_for_csv(output: pd.DataFrame) -> pd.DataFrame:
    serializable = output.copy()
    serializable["rank_in_population"] = serializable[
        "rank_in_population"
    ].map(lambda value: decimal_text(Decimal(str(value))))
    serializable["percentile"] = serializable["percentile"].map(decimal_text)
    serializable["in_cheap_set"] = serializable["in_cheap_set"].map(
        lambda value: "True" if value else "False"
    )
    return serializable.loc[:, OUTPUT_COLUMNS]


def write_deterministic_gzip(output: pd.DataFrame, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = output_for_csv(output)
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


def _markdown_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                str(value).replace("|", "\\|").replace("\n", " ")
                for value in row
            )
            + " |"
        )
    return "\n".join(lines)


def _stat_text(series: pd.Series) -> str:
    return (
        f"{int(series.min())} / {decimal_text(Decimal(str(series.median())))}"
        f" / {int(series.max())}"
    )


def _date_list(frame: pd.DataFrame, column: str) -> str:
    values = frame.loc[frame[column], "evaluation_date"].tolist()
    return ", ".join(values) if values else "NONE"


def cheap_sets(output: pd.DataFrame) -> dict[tuple[str, str, str], set[str]]:
    sets: dict[tuple[str, str, str], set[str]] = {}
    cheap = output.loc[output["in_cheap_set"]]
    for keys, frame in cheap.groupby(
        ["evaluation_date", "metric", "population_id"], sort=True
    ):
        sets[keys] = set(frame["ticker"])
    return sets


def report_c4(output: pd.DataFrame) -> list[list[Any]]:
    sets = cheap_sets(output)
    rows: list[dict[str, Any]] = []
    dates = sorted(output["evaluation_date"].unique())
    for population_id in ("ALL", "PRICE_OK"):
        for evaluation_date in dates:
            ebit = sets.get(
                (evaluation_date, "ebit_tev", population_id), set()
            )
            ep = sets.get((evaluation_date, "e_p", population_id), set())
            if ebit:
                rows.append(
                    {
                        "population_id": population_id,
                        "calendar_year": evaluation_date[:4],
                        "fraction": Decimal(len(ebit & ep))
                        / Decimal(len(ebit)),
                    }
                )
    frame = pd.DataFrame(rows)
    result: list[list[Any]] = []
    for keys, group in frame.groupby(
        ["population_id", "calendar_year"], sort=True
    ):
        mean = sum(group["fraction"], Decimal("0")) / Decimal(len(group))
        result.append([keys[0], keys[1], len(group), decimal_text(mean)])
    return result


def report_c5(output: pd.DataFrame) -> list[list[Any]]:
    sets = cheap_sets(output)
    rows: list[list[Any]] = []
    dates = sorted(output["evaluation_date"].unique())
    for metric in METRICS:
        for year in sorted({date[:4] for date in dates}):
            fractions: list[Decimal] = []
            entered: set[str] = set()
            left: set[str] = set()
            used_dates = 0
            for evaluation_date in [
                value for value in dates if value.startswith(year)
            ]:
                all_set = sets.get((evaluation_date, metric, "ALL"), set())
                excluded_set = sets.get(
                    (evaluation_date, metric, "ALL_EX_UPPER_BOUND"), set()
                )
                if not all_set:
                    continue
                used_dates += 1
                fractions.append(
                    Decimal(len(all_set & excluded_set))
                    / Decimal(len(all_set))
                )
                entered.update(excluded_set - all_set)
                left.update(all_set - excluded_set)
            if used_dates:
                rows.append(
                    [
                        metric,
                        year,
                        used_dates,
                        decimal_text(
                            sum(fractions, Decimal("0"))
                            / Decimal(len(fractions))
                        ),
                        len(entered),
                        len(left),
                    ]
                )
    return rows


def write_report(
    *,
    output: pd.DataFrame,
    diagnostics: pd.DataFrame,
    config: ValueConfig,
    run_date: str,
    output_path: Path,
    sha256: str,
) -> None:
    c2_rows: list[list[Any]] = []
    for (metric, population_id), frame in diagnostics.groupby(
        ["metric", "population_id"], sort=True
    ):
        c2_rows.append(
            [
                metric,
                population_id,
                _stat_text(frame["population_size"]),
                _stat_text(frame["cheap_set_size"]),
                int(frame["low_selectivity_20"].sum()),
                int(frame["low_selectivity_25"].sum()),
                int(frame["thin_candidate_pool"].sum()),
                _date_list(frame, "low_selectivity_20"),
                _date_list(frame, "low_selectivity_25"),
                _date_list(frame, "thin_candidate_pool"),
            ]
        )

    c3_rows: list[list[Any]] = []
    thin_floor = (
        Decimal(THIN_POOL_TARGET) * config.min_candidate_pool_multiple
    )
    for metric in METRICS:
        metric_frame = diagnostics.loc[diagnostics["metric"].eq(metric)]
        earliest = "NONE"
        for evaluation_date, frame in metric_frame.groupby(
            "evaluation_date", sort=True
        ):
            sizes = dict(
                zip(frame["population_id"], frame["cheap_set_size"], strict=True)
            )
            if all(
                population_id in sizes
                and Decimal(int(sizes[population_id])) >= thin_floor
                for population_id in POPULATIONS
            ):
                earliest = evaluation_date
                break
        c3_rows.append([metric, decimal_text(thin_floor), earliest])

    worked = output.loc[
        output["evaluation_date"].eq("2024-12-31")
        & output["population_id"].eq("ALL")
        & output["metric"].eq("ebit_tev")
    ].sort_values(["rank_in_population", "ticker"], kind="stable")
    top_ten = worked.head(10)
    cheap_count = int(worked["in_cheap_set"].sum())
    threshold_count = int(
        worked["percentile"].map(to_decimal).ge(
            Decimal("1") - config.value_cheapest_pct
        ).sum()
    )
    c6_rows = [
        [
            row.ticker,
            row.metric_value,
            decimal_text(Decimal(str(row.rank_in_population))),
            decimal_text(row.percentile),
            row.in_cheap_set,
            row.market_cap_status,
            row.population_size,
        ]
        for row in top_ten.itertuples(index=False)
    ]

    lines = [
        "# Sprint 9-4A Value Candidates",
        "",
        f"> {BASKET_LABEL}",
        "",
        "Sprint 9-3 measured that 32.9 percent of OK rows carry an UPPER_BOUND market cap, whose EBIT/TEV and E/P are therefore LOWER bounds, so those names are pushed down the cheapness ordering by a data limitation rather than by valuation. The two EX_UPPER_BOUND populations measure how much that limitation moves the basket.",
        "",
        "## C1 — Rebalance grid",
        "",
        f"- Rebalance dates: `{output['evaluation_date'].nunique()}`.",
        f"- First date: `{output['evaluation_date'].min()}`.",
        f"- Last date: `{output['evaluation_date'].max()}`.",
        f"- Total output rows: `{len(output)}`.",
        "",
        "## C2 — Population and pool-depth diagnostics",
        "",
        f"- VALUE_CHEAPEST_PCT: `{decimal_text(config.value_cheapest_pct)}`.",
        f"- MIN_CANDIDATE_POOL_MULTIPLE: `{decimal_text(config.min_candidate_pool_multiple)}`.",
        f"- SELECTION_RATIO_REPORT_THRESHOLD: `{decimal_text(config.selection_ratio_report_threshold)}`.",
        "",
        _markdown_table(
            [
                "metric",
                "population_id",
                "population_size min / median / max",
                "cheap_set_size min / median / max",
                "LOW_SELECTIVITY target 20 dates",
                "LOW_SELECTIVITY target 25 dates",
                "THIN_CANDIDATE_POOL dates",
                "target 20 flagged date list",
                "target 25 flagged date list",
                "thin-pool flagged date list",
            ],
            c2_rows,
        ),
        "",
        "## C3 — Earliest adequately deep date",
        "",
        _markdown_table(
            ["metric", "required cheap_set_size", "earliest evaluation_date"],
            c3_rows,
        ),
        "",
        "Dates before the stated date produce baskets whose result reflects pool scarcity more than strategy.",
        "",
        "## C4 — EBIT/TEV versus E/P cheap-set overlap",
        "",
        _markdown_table(
            [
                "population_id",
                "calendar_year",
                "rebalance_dates",
                "mean fraction of EBIT/TEV cheap set also in E/P cheap set",
            ],
            report_c4(output),
        ),
        "",
        "## C5 — Effect of excluding upper-bound market caps",
        "",
        _markdown_table(
            [
                "metric",
                "calendar_year",
                "rebalance_dates",
                "mean fraction of ALL cheap set also in ALL_EX_UPPER_BOUND",
                "distinct tickers entering",
                "distinct tickers leaving",
            ],
            report_c5(output),
        ),
        "",
        "The enter/leave counts show how many distinct tickers change cheap-set membership because of the upper-bound treatment.",
        "",
        "## C6 — Worked check: 2024-12-31 / ALL / ebit_tev",
        "",
        _markdown_table(
            [
                "ticker",
                "metric_value",
                "rank_in_population",
                "percentile",
                "in_cheap_set",
                "market_cap_status",
                "population_size",
            ],
            c6_rows,
        ),
        "",
        f"- cheap_set_size: `{cheap_count}`.",
        f"- Count with percentile >= 1 - VALUE_CHEAPEST_PCT: `{threshold_count}`.",
        f"- Equality check: `{cheap_count == threshold_count}`.",
        "",
        "## C7 — Output identity",
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
        description="Build Sprint 9-4A value-only candidate rankings."
    )
    parser.add_argument("--run-date", help="Asia/Ho_Chi_Minh date (YYYY-MM-DD).")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_date = args.run_date or datetime.now(TIME_ZONE).date().isoformat()
    output_path = (
        OUTPUT_ROOT
        / run_date
        / "value_candidates_point_in_time.csv.gz"
    )
    print(f"RUN_DATE={run_date}")
    config = load_config()
    frame = load_input()
    output = build_output(frame, config=config, run_date=run_date)
    validate_stop_gates(output, config)
    diagnostics = pool_diagnostics(output, config)
    sha256 = write_deterministic_gzip(output, output_path)
    write_report(
        output=output,
        diagnostics=diagnostics,
        config=config,
        run_date=run_date,
        output_path=output_path,
        sha256=sha256,
    )
    print(f"OUTPUT={output_path}")
    print(f"ROW_COUNT={len(output)}")
    print(f"SHA256={sha256}")
    print(f"REPORT={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
