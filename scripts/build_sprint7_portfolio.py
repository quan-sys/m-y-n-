"""Build the two owner-approved Sprint 7 snapshot portfolios from local CSVs."""

from __future__ import annotations

from collections import Counter
import math
from pathlib import Path
import sys
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.screener.step1_pipeline import load_simple_config  # noqa: E402


AS_OF = "2026-07-20"
HOLDING_COUNT = 20
SECTOR_CAP = 0.25
CONFIG_PATH = ROOT / "config" / "screener.yaml"
QUALITY_PATH = ROOT / "data" / "screener" / "sprint6_franchise_quality.csv"
SURVIVORS_PATH = ROOT / "data" / "screener" / "step1_survivors.csv"
FSCORE_PATH = ROOT / "data" / "screener" / "sprint6_fscore.csv"
REPORT_ROOT = ROOT / "reports" / AS_OF
CANDIDATE_CONTRACTS = {
    "EBIT_TEV": {
        "path": ROOT / "data" / "screener" / "step2_candidates_ebit_tev.csv",
        "value_column": "ebit_tev",
        "value_rank_column": "ebit_tev_rank",
        "quality_rank_column": "ebit_tev_quality_rank",
        "csv_path": REPORT_ROOT / "portfolio_ebit_tev.csv",
        "md_path": REPORT_ROOT / "PORTFOLIO_EBIT_TEV.md",
    },
    "EP": {
        "path": ROOT / "data" / "screener" / "step2_candidates_ep.csv",
        "value_column": "ep",
        "value_rank_column": "ep_rank",
        "quality_rank_column": "ep_quality_rank",
        "csv_path": REPORT_ROOT / "portfolio_ep.csv",
        "md_path": REPORT_ROOT / "PORTFOLIO_EP.md",
    },
}
QUALITY_COMPONENT_COLUMNS = (
    "fscore_completion_ratio_percentile",
    "roc_arithmetic_mean_percentile",
    "margin_stability_percentile",
)


def select_portfolio(
    pool: pd.DataFrame,
    *,
    holding_count: int,
    sector_cap: float,
    liquidity_adtv_days: float,
    portfolio_capital_vnd: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply the settled selection sequence and return holdings plus complete skips."""
    working = pool.copy()
    working["ticker"] = working["ticker"].astype(str).str.strip().str.upper()
    working["composite_quality_numeric"] = pd.to_numeric(
        working["composite_quality"], errors="coerce"
    )
    working["adtv_20d_numeric"] = pd.to_numeric(working["adtv_20d"], errors="coerce")
    if working["ticker"].duplicated().any():
        raise ValueError("candidate pool contains duplicate tickers")
    skips: list[dict[str, Any]] = []
    remaining_rows: list[dict[str, Any]] = []
    for row in working.to_dict("records"):
        if str(row.get("franchise_history_status", "")) != "READY":
            skips.append(
                {
                    "quality_rank": row.get("quality_rank"),
                    "ticker": row["ticker"],
                    "icb2": row.get("icb2", ""),
                    "composite_quality": row.get("composite_quality"),
                    "reason": "INSUFFICIENT_HISTORY_BLOCKED",
                }
            )
            continue
        adtv = row.get("adtv_20d_numeric")
        if adtv is None or pd.isna(adtv) or float(adtv) <= 0:
            skips.append(
                {
                    "quality_rank": row.get("quality_rank"),
                    "ticker": row["ticker"],
                    "icb2": row.get("icb2", ""),
                    "composite_quality": row.get("composite_quality"),
                    "reason": "MISSING_OR_ZERO_ADTV_20D",
                }
            )
            continue
        if pd.isna(row.get("composite_quality_numeric")):
            raise ValueError(f"{row['ticker']} has no usable composite_quality")
        remaining_rows.append(row)
    ranked = pd.DataFrame(remaining_rows)
    if not ranked.empty:
        ranked = ranked.sort_values(
            ["composite_quality_numeric", "ticker"],
            ascending=[False, True],
            kind="mergesort",
        ).reset_index(drop=True)
    position_value = portfolio_capital_vnd / holding_count
    maximum_sector_count = math.floor(sector_cap * holding_count)
    selected: list[dict[str, Any]] = []
    sector_counts: Counter[str] = Counter()
    for consideration_index, row in enumerate(ranked.to_dict("records"), start=1):
        if len(selected) == holding_count:
            break
        sector = str(row.get("icb2", ""))
        if sector_counts[sector] + 1 > maximum_sector_count:
            skips.append(
                {
                    "quality_rank": row.get("quality_rank"),
                    "consideration_rank": consideration_index,
                    "ticker": row["ticker"],
                    "icb2": sector,
                    "composite_quality": row.get("composite_quality"),
                    "reason": "SECTOR_CAP_SKIPPED",
                }
            )
            continue
        liquidity_limit = liquidity_adtv_days * float(row["adtv_20d_numeric"])
        if position_value > liquidity_limit:
            skips.append(
                {
                    "quality_rank": row.get("quality_rank"),
                    "consideration_rank": consideration_index,
                    "ticker": row["ticker"],
                    "icb2": sector,
                    "composite_quality": row.get("composite_quality"),
                    "reason": "LIQUIDITY_CAP_SKIPPED",
                }
            )
            continue
        chosen = dict(row)
        chosen["consideration_rank"] = consideration_index
        chosen["portfolio_rank"] = len(selected) + 1
        selected.append(chosen)
        sector_counts[sector] += 1
    if len(selected) != holding_count:
        raise RuntimeError(
            f"portfolio shortfall: selected={len(selected)} target={holding_count} "
            f"shortfall={holding_count - len(selected)}"
        )
    holdings = pd.DataFrame(selected)
    skips_frame = pd.DataFrame(skips)
    return holdings, skips_frame


def _latest_sector_cycle() -> tuple[dict[str, str], str]:
    candidates = sorted((ROOT / "reports").glob("*/sector_cycle_signals.csv"))
    if not candidates:
        return {}, ""
    path = candidates[-1]
    frame = pd.read_csv(path)
    if not {"sector", "candidate_cycle_stage"}.issubset(frame.columns):
        return {}, path.relative_to(ROOT).as_posix()
    mapping = dict(
        zip(frame["sector"].astype(str), frame["candidate_cycle_stage"].astype(str))
    )
    return mapping, path.relative_to(ROOT).as_posix()


def _prepare_pool(
    portfolio_name: str,
    contract: dict[str, Any],
    quality: pd.DataFrame,
    survivors: pd.DataFrame,
    fscore: pd.DataFrame,
) -> pd.DataFrame:
    candidates = pd.read_csv(contract["path"])
    value_column = str(contract["value_column"])
    value_rank_column = str(contract["value_rank_column"])
    quality_rank_column = str(contract["quality_rank_column"])
    candidate_fields = candidates[
        ["ticker", "exchange", "icb2", value_column, value_rank_column]
    ].rename(
        columns={
            value_column: "value_metric_value",
            value_rank_column: "value_rank",
        }
    )
    quality_fields = quality[
        [
            "ticker",
            "composite_quality",
            *QUALITY_COMPONENT_COLUMNS,
            "franchise_history_status",
            "franchise_history_flag",
            "composite_confidence_flag",
            quality_rank_column,
        ]
    ].rename(columns={quality_rank_column: "quality_rank"})
    survivor_fields = survivors[["ticker", "adtv_20d", "source", "as_of"]].rename(
        columns={"source": "survivor_source", "as_of": "survivor_as_of"}
    )
    fscore_fields = fscore[
        [
            "ticker",
            "cross_step_flag",
            "fscore_confidence_flag",
            "criterion_7_flag",
            "non_positive_revenue_n_minus_1",
        ]
    ]
    pool = candidate_fields.merge(
        quality_fields, on="ticker", how="left", validate="one_to_one"
    ).merge(survivor_fields, on="ticker", how="left", validate="one_to_one").merge(
        fscore_fields, on="ticker", how="left", validate="one_to_one"
    )
    pool["portfolio_name"] = portfolio_name
    pool["candidate_list_membership"] = portfolio_name
    pool["value_metric_name"] = str(contract["value_column"])
    pool["candidate_source_path"] = contract["path"].relative_to(ROOT).as_posix()
    pool["quality_source_path"] = QUALITY_PATH.relative_to(ROOT).as_posix()
    pool["survivor_source_path"] = SURVIVORS_PATH.relative_to(ROOT).as_posix()
    return pool


def _finalize_holdings(
    holdings: pd.DataFrame,
    *,
    portfolio_name: str,
    liquidity_adtv_days: float,
    portfolio_capital_vnd: float,
    sector_cycle: dict[str, str],
    sector_cycle_source: str,
) -> pd.DataFrame:
    output = holdings.copy()
    sector_counts = output["icb2"].astype(str).value_counts()
    position_value = portfolio_capital_vnd / HOLDING_COUNT
    output["portfolio_id"] = f"SPRINT7_{portfolio_name}_{AS_OF}"
    output["as_of"] = AS_OF
    output["target_weight"] = 1 / HOLDING_COUNT
    output["sector_count"] = output["icb2"].astype(str).map(sector_counts)
    output["sector_share"] = output["sector_count"] / HOLDING_COUNT
    output["sector_cap_status"] = "WITHIN_CAP"
    output["position_value_vnd"] = position_value
    output["liquidity_limit_vnd"] = (
        liquidity_adtv_days * output["adtv_20d_numeric"].astype(float)
    )
    output["liquidity_headroom_vnd"] = (
        output["liquidity_limit_vnd"] - position_value
    )
    output["liquidity_headroom_ratio"] = (
        output["liquidity_limit_vnd"] / position_value
    )
    output["liquidity_status"] = "WITHIN_CAP"
    output["momentum_enabled"] = False
    output["momentum_veto_status"] = "NOT_EVALUATED"
    output["sector_cycle_reporting_label"] = output["icb2"].astype(str).map(
        sector_cycle
    ).fillna("SECTOR_CYCLE_UNAVAILABLE")
    output["sector_cycle_source_path"] = sector_cycle_source
    output["membership_change"] = "ENTER"
    output["change_reason"] = "INITIAL_SNAPSHOT"
    columns = [
        "portfolio_id",
        "as_of",
        "portfolio_rank",
        "ticker",
        "exchange",
        "icb2",
        "candidate_list_membership",
        "value_metric_name",
        "value_metric_value",
        "value_rank",
        "composite_quality",
        *QUALITY_COMPONENT_COLUMNS,
        "franchise_history_status",
        "quality_rank",
        "target_weight",
        "sector_count",
        "sector_share",
        "sector_cap_status",
        "adtv_20d",
        "position_value_vnd",
        "liquidity_limit_vnd",
        "liquidity_headroom_vnd",
        "liquidity_headroom_ratio",
        "liquidity_status",
        "momentum_enabled",
        "momentum_veto_status",
        "sector_cycle_reporting_label",
        "cross_step_flag",
        "franchise_history_flag",
        "composite_confidence_flag",
        "fscore_confidence_flag",
        "criterion_7_flag",
        "non_positive_revenue_n_minus_1",
        "candidate_source_path",
        "quality_source_path",
        "survivor_source_path",
        "survivor_source",
        "survivor_as_of",
        "sector_cycle_source_path",
        "membership_change",
        "change_reason",
    ]
    return output[columns]


def liquidity_sensitivity(
    holdings: pd.DataFrame,
    *,
    portfolio_name: str,
    liquidity_adtv_days: float,
    base_capital_vnd: float,
) -> pd.DataFrame:
    lowest = holdings.sort_values(["adtv_20d", "ticker"], kind="mergesort").iloc[0]
    rows: list[dict[str, Any]] = []
    for multiple in (1, 10, 50):
        capital = base_capital_vnd * multiple
        position_value = capital / HOLDING_COUNT
        limits = liquidity_adtv_days * pd.to_numeric(holdings["adtv_20d"])
        rows.append(
            {
                "portfolio_id": portfolio_name,
                "portfolio_capital_vnd": int(capital),
                "breach_count": int((position_value > limits).sum()),
                "lowest_adtv_ticker": lowest["ticker"],
                "lowest_adtv_20d": lowest["adtv_20d"],
                "lowest_adtv_headroom_ratio": (
                    liquidity_adtv_days * float(lowest["adtv_20d"]) / position_value
                ),
            }
        )
    return pd.DataFrame(rows)


def sector_summary(holdings: pd.DataFrame, portfolio_name: str) -> pd.DataFrame:
    counts = holdings["icb2"].astype(str).value_counts().sort_index()
    deepest = int(counts.max())
    return pd.DataFrame(
        [
            {
                "portfolio_id": portfolio_name,
                "icb2": sector,
                "holding_count": int(count),
                "holding_share_pct": int(count) / HOLDING_COUNT * 100,
                "is_deepest_sector": bool(int(count) == deepest),
                "portfolio_deepest_sector_share_pct": deepest
                / HOLDING_COUNT
                * 100,
            }
            for sector, count in counts.items()
        ]
    )


def _display(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else format(value, ".17g")
    return str(value).replace("|", "\\|")


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "|" + "|".join("---" for _ in columns) + "|",
    ]
    for row in frame[columns].to_dict("records"):
        lines.append("| " + " | ".join(_display(row[column]) for column in columns) + " |")
    if frame.empty:
        lines.append("| " + " | ".join("" for _ in columns) + " |")
    return lines


def render_report(
    portfolio_name: str,
    holdings: pd.DataFrame,
    skips: pd.DataFrame,
    sensitivity: pd.DataFrame,
    sectors: pd.DataFrame,
    liquidity_adtv_days: float,
    portfolio_capital_vnd: float,
) -> str:
    holding_columns = [
        "portfolio_rank",
        "ticker",
        "icb2",
        "composite_quality",
        *QUALITY_COMPONENT_COLUMNS,
        "value_metric_value",
        "value_rank",
        "adtv_20d",
        "target_weight",
    ]
    skip_columns = [
        "quality_rank",
        "consideration_rank",
        "ticker",
        "icb2",
        "composite_quality",
        "reason",
    ]
    for column in skip_columns:
        if column not in skips:
            skips[column] = None
    lines = [
        f"# Sprint 7 {portfolio_name} initial snapshot",
        "",
        f"- As of: `{AS_OF}` (off-cycle initial snapshot).",
        f"- Holdings: `{len(holdings)}`; target weight sum: `{format(float(holdings['target_weight'].sum()), '.17g')}`.",
        f"- Portfolio capital: `{int(portfolio_capital_vnd)}` VND; liquidity allowance: `{_display(liquidity_adtv_days)}` ADTV days.",
        "- Momentum is disabled and no momentum value was computed.",
        "",
        "## Holdings",
        "",
        *markdown_table(holdings, holding_columns),
        "",
        "## Complete skip log",
        "",
        *markdown_table(skips, skip_columns),
        "",
        "## Liquidity sensitivity",
        "",
        *markdown_table(sensitivity, list(sensitivity.columns)),
        "",
        "## Sector counts",
        "",
        *markdown_table(sectors, list(sectors.columns)),
    ]
    return "\n".join(lines) + "\n"


def build() -> dict[str, dict[str, pd.DataFrame]]:
    config = load_simple_config(CONFIG_PATH)
    liquidity_adtv_days = float(config["LIQUIDITY_ADTV_DAYS"])
    portfolio_capital_vnd = float(config["PORTFOLIO_CAPITAL_VND"])
    quality = pd.read_csv(QUALITY_PATH)
    survivors = pd.read_csv(SURVIVORS_PATH)
    fscore = pd.read_csv(FSCORE_PATH)
    sector_cycle, sector_cycle_source = _latest_sector_cycle()
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, pd.DataFrame]] = {}
    for portfolio_name, contract in CANDIDATE_CONTRACTS.items():
        pool = _prepare_pool(
            portfolio_name, contract, quality, survivors, fscore
        )
        selected, skips = select_portfolio(
            pool,
            holding_count=HOLDING_COUNT,
            sector_cap=SECTOR_CAP,
            liquidity_adtv_days=liquidity_adtv_days,
            portfolio_capital_vnd=portfolio_capital_vnd,
        )
        holdings = _finalize_holdings(
            selected,
            portfolio_name=portfolio_name,
            liquidity_adtv_days=liquidity_adtv_days,
            portfolio_capital_vnd=portfolio_capital_vnd,
            sector_cycle=sector_cycle,
            sector_cycle_source=sector_cycle_source,
        )
        sensitivity = liquidity_sensitivity(
            holdings,
            portfolio_name=portfolio_name,
            liquidity_adtv_days=liquidity_adtv_days,
            base_capital_vnd=portfolio_capital_vnd,
        )
        sectors = sector_summary(holdings, portfolio_name)
        holdings.to_csv(contract["csv_path"], index=False, lineterminator="\n")
        contract["md_path"].write_text(
            render_report(
                portfolio_name,
                holdings,
                skips,
                sensitivity,
                sectors,
                liquidity_adtv_days,
                portfolio_capital_vnd,
            ),
            encoding="utf-8",
        )
        results[portfolio_name] = {
            "holdings": holdings,
            "skips": skips,
            "sensitivity": sensitivity,
            "sectors": sectors,
        }
    return results


def _stdout_table(label: str, frame: pd.DataFrame, columns: list[str]) -> None:
    print(label)
    sys.stdout.write(frame[columns].to_csv(index=False, lineterminator="\n"))


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    results = build()
    holding_columns = [
        "portfolio_rank",
        "ticker",
        "icb2",
        "composite_quality",
        *QUALITY_COMPONENT_COLUMNS,
        "value_metric_value",
        "value_rank",
        "adtv_20d",
        "target_weight",
    ]
    skip_columns = [
        "quality_rank",
        "consideration_rank",
        "ticker",
        "icb2",
        "composite_quality",
        "reason",
    ]
    for portfolio_name, tables in results.items():
        skips = tables["skips"].copy()
        for column in skip_columns:
            if column not in skips:
                skips[column] = None
        _stdout_table(f"HOLDINGS_{portfolio_name}", tables["holdings"], holding_columns)
        _stdout_table(f"SKIP_LOG_{portfolio_name}", skips, skip_columns)
        _stdout_table(
            f"LIQUIDITY_SENSITIVITY_{portfolio_name}",
            tables["sensitivity"],
            list(tables["sensitivity"].columns),
        )
        _stdout_table(
            f"SECTOR_COUNTS_{portfolio_name}",
            tables["sectors"],
            list(tables["sectors"].columns),
        )
    print("momentum_values_computed=0")
    print("network_calls=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
