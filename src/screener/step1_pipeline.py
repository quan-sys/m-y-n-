"""Sprint 4 Step-1 cleaning orchestration over the reviewed annual cache."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import pandas as pd

from src.screener.step1_cleaning import DistressResult, FormulaResult
from src.screener.step1_data import PreparedTicker, prepare_ticker_from_cache


FILTER_ORDER = (
    "FINANCIAL_SECTOR_EXCLUDED",
    "UPCOM_EXCLUDED_V1",
    "HIGH_ACCRUAL",
    "M_SCORE_FLAG",
    "PFD_HIGH_RISK",
)
FINANCIAL_ICB2 = {"NGÂN HÀNG", "BẢO HIỂM", "DỊCH VỤ TÀI CHÍNH"}
FORMULA_NAMES = (
    "STA", "SNOA", "DSRI", "GMI", "AQI", "SGI", "DEPI", "SGAI", "LVGI", "TATA", "M_SCORE"
)
AUDIT_COLUMNS = (
    "filter_stage", "reason_label", "trigger_metric", "trigger_value", "threshold_or_cutoff"
)
REJECT_COLUMNS = (
    "ticker", "filter_stage", "reason_label", "trigger_metric", "trigger_value",
    "threshold_or_cutoff", "exchange", "icb2", "source", "as_of", "data_status",
)


@dataclass(frozen=True)
class TailCutoff:
    valid_count: int
    cut_count: int
    cutoff: float | None
    flags: pd.Series


@dataclass(frozen=True)
class PipelineResult:
    evaluated: pd.DataFrame
    survivors: pd.DataFrame
    rejects: pd.DataFrame
    sector_a: pd.DataFrame
    sector_b: pd.DataFrame
    filter_stats: pd.DataFrame
    cutoffs: Mapping[str, TailCutoff]
    guard_triggered: bool
    guard_details: pd.DataFrame


def load_simple_config(path: str | Path) -> dict[str, Any]:
    """Read the flat reviewed YAML config without adding a YAML dependency."""

    values: dict[str, Any] = {}
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        key, raw_value = line.split(":", 1)
        value = raw_value.strip()
        try:
            parsed: Any = float(value)
        except ValueError:
            parsed = value
        values[key.strip()] = parsed
    return values


def finite_number(value: Any) -> bool:
    try:
        return value is not None and not isinstance(value, (bool, str, bytes)) and math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def known_boolean_true(value: Any) -> bool:
    """Return true only for an available Python or NumPy boolean true value."""

    if value is None or value is pd.NA:
        return False
    return pd.api.types.is_bool(value) and bool(value)


def higher_tail_flags(values: pd.Series, worst_pct: float) -> TailCutoff:
    """Flag the observed higher tail, including every tie at the boundary."""

    numeric = pd.to_numeric(values, errors="coerce")
    valid = numeric[numeric.map(finite_number)]
    flags = pd.Series(False, index=values.index, dtype=bool)
    if valid.empty:
        return TailCutoff(0, 0, None, flags)
    k = max(1, math.ceil(len(valid) * float(worst_pct)))
    cutoff = float(valid.sort_values(ascending=False).iloc[k - 1])
    flags.loc[valid.index] = valid.ge(cutoff)
    return TailCutoff(len(valid), k, cutoff, flags)


def higher_worse_percentile(values: pd.Series, groups: pd.Series | None = None) -> pd.Series:
    """Return ascending max-rank percentile; the largest (worst) value is 1."""

    numeric = pd.to_numeric(values, errors="coerce").where(lambda s: s.map(finite_number))
    if groups is None:
        return numeric.rank(method="max", pct=True, ascending=True)
    return numeric.groupby(groups, dropna=False).rank(method="max", pct=True, ascending=True)


def _joined(values: Iterable[Any]) -> str:
    cleaned = sorted({str(value) for value in values if pd.notna(value) and str(value)})
    return "|".join(cleaned)


def _prepared_row(prepared: PreparedTicker, universe_row: Mapping[str, Any]) -> dict[str, Any]:
    pair = prepared.pair or (None, None)
    eligible = prepared.eligible_rows
    row: dict[str, Any] = {
        "ticker": prepared.ticker,
        "exchange": prepared.exchange,
        "icb2": prepared.icb2,
        "annual_n": pair[0],
        "annual_n_minus_1": pair[1],
        "source": _joined(eligible.get("source", pd.Series(dtype=object))),
        "as_of": _joined(eligible.get("as_of", pd.Series(dtype=object))),
        "available_from": _joined(eligible.get("available_from", pd.Series(dtype=object))),
        "data_status": _joined(eligible.get("data_status", pd.Series(dtype=object))),
    }
    for column in ("icb3", "icb4", "market_cap", "adtv_20d"):
        row[column] = universe_row.get(column)
    for name in FORMULA_NAMES:
        result = prepared.results[name]
        assert isinstance(result, FormulaResult)
        row[name.lower()] = result.value
        row[f"{name.lower()}_reason"] = result.reason
        row[f"{name.lower()}_invalid_inputs"] = "|".join(result.invalid_inputs)
    distress = prepared.results["DISTRESS"]
    assert isinstance(distress, DistressResult)
    inputs = prepared.formula_inputs["DISTRESS"]
    for key, value in inputs.items():
        row[f"distress_input_{key}"] = value
    row.update(
        distress_accumulated_loss=distress.accumulated_loss,
        distress_negative_equity=distress.negative_equity,
        distress_hose_warning=distress.hose_warning,
        distress_high_risk=distress.high_risk,
        distress_reason=distress.reason,
        distress_invalid_inputs="|".join(distress.invalid_inputs),
    )
    row["raw_formula_inputs"] = repr(prepared.formula_inputs)
    return row


def evaluate_formula_stage(
    universe: pd.DataFrame,
    cache_root: str | Path,
    evaluation_date: str,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for universe_row in universe.to_dict("records"):
        prepared = prepare_ticker_from_cache(
            universe_row, cache_root, evaluation_date, hose_warning=None
        )
        rows.append(_prepared_row(prepared, universe_row))
    return pd.DataFrame(rows)


def add_formula_flags(frame: pd.DataFrame, worst_pct: float, mscore_threshold: float) -> tuple[pd.DataFrame, dict[str, TailCutoff]]:
    result = frame.copy()
    sta = higher_tail_flags(result["sta"], worst_pct)
    snoa = higher_tail_flags(result["snoa"], worst_pct)
    result["sta_percentile"] = higher_worse_percentile(result["sta"])
    result["snoa_percentile"] = higher_worse_percentile(result["snoa"])
    result["m_score_percentile"] = higher_worse_percentile(result["m_score"])
    result["sta_within_icb2_percentile"] = higher_worse_percentile(result["sta"], result["icb2"])
    result["snoa_within_icb2_percentile"] = higher_worse_percentile(result["snoa"], result["icb2"])
    result["m_score_within_icb2_percentile"] = higher_worse_percentile(result["m_score"], result["icb2"])
    result["sta_flag"] = sta.flags
    result["snoa_flag"] = snoa.flags
    result["high_accrual_flag"] = result["sta_flag"] | result["snoa_flag"]
    result["m_score_flag"] = pd.to_numeric(result["m_score"], errors="coerce").gt(float(mscore_threshold))
    result["pfd_high_risk_flag"] = result["distress_high_risk"].map(known_boolean_true)
    return result, {"STA": sta, "SNOA": snoa}


def assign_primary_rejections(full_universe: pd.DataFrame, evaluated: pd.DataFrame, cutoffs: Mapping[str, TailCutoff], mscore_threshold: float) -> pd.DataFrame:
    metrics = evaluated.set_index("ticker", drop=False)
    rows: list[dict[str, Any]] = []
    for source in full_universe.to_dict("records"):
        ticker = str(source["ticker"])
        reason = metric = value = threshold = ""
        if str(source["icb2"]) in FINANCIAL_ICB2:
            reason, metric = FILTER_ORDER[0], "icb2"
            value, threshold = source["icb2"], "financial ICB2 exclusion"
            details = source
        elif str(source["exchange"]).upper() == "UPCOM":
            reason, metric = FILTER_ORDER[1], "exchange"
            value, threshold = source["exchange"], "UPCOM"
            details = source
        else:
            details = metrics.loc[ticker]
            if bool(details["high_accrual_flag"]):
                reason = FILTER_ORDER[2]
                triggered = [name for name in ("sta", "snoa") if bool(details[f"{name}_flag"])]
                metric = "+".join(name.upper() for name in triggered)
                value = ";".join(f"{name.upper()}={details[name]}" for name in triggered)
                threshold = ";".join(f"{name.upper()}>={cutoffs[name.upper()].cutoff}" for name in triggered)
            elif bool(details["m_score_flag"]):
                reason, metric = FILTER_ORDER[3], "M_SCORE"
                value, threshold = details["m_score"], f">{mscore_threshold}"
            elif bool(details["pfd_high_risk_flag"]):
                reason, metric = FILTER_ORDER[4], "DISTRESS"
                signals = [
                    name for name in ("accumulated_loss", "negative_equity", "hose_warning")
                    if known_boolean_true(details[f"distress_{name}"])
                ]
                value, threshold = "|".join(signals), "high_risk is True"
        if reason:
            rows.append({
                "ticker": ticker, "filter_stage": FILTER_ORDER.index(reason) + 1,
                "reason_label": reason, "trigger_metric": metric,
                "trigger_value": value, "threshold_or_cutoff": threshold,
                "exchange": source["exchange"], "icb2": source["icb2"],
                "source": details.get("source", source.get("source", "")),
                "as_of": details.get("as_of", source.get("as_of", "")),
                "data_status": details.get("data_status", source.get("data_status", "")),
            })
    return pd.DataFrame(rows, columns=REJECT_COLUMNS)


def calculate_filter_stats(full_universe: pd.DataFrame, rejects: pd.DataFrame) -> pd.DataFrame:
    entering = len(full_universe)
    rows = []
    for stage, reason in enumerate(FILTER_ORDER, start=1):
        removed = int((rejects["reason_label"] == reason).sum())
        pct = removed / entering if entering else 0.0
        rows.append({"filter_stage": stage, "filter": reason, "entering": entering, "removed": removed, "removal_pct": pct})
        entering -= removed
    return pd.DataFrame(rows)


def build_sector_a(evaluated: pd.DataFrame, rejects: pd.DataFrame) -> pd.DataFrame:
    operative = rejects[rejects["reason_label"].isin(("HIGH_ACCRUAL", "M_SCORE_FLAG"))]
    total = len(evaluated)
    reject_total = len(operative)
    rows = []
    for icb2, group in evaluated.groupby("icb2", sort=True):
        affected = operative[operative["icb2"] == icb2]
        universe_weight = len(group) / total if total else 0.0
        reject_weight = len(affected) / reject_total if reject_total else 0.0
        ratio = reject_weight / universe_weight if universe_weight else 0.0
        rows.append({
            "icb2": icb2, "formula_stage_universe_count": len(group),
            "universe_weight": universe_weight,
            "high_accrual_reject_count": int((affected["reason_label"] == "HIGH_ACCRUAL").sum()),
            "m_score_flag_reject_count": int((affected["reason_label"] == "M_SCORE_FLAG").sum()),
            "reject_count": len(affected), "reject_set_weight": reject_weight,
            "reject_weight_divided_by_universe_weight": ratio,
            "review_flag": ratio > 2.0,
        })
    return pd.DataFrame(rows)


def build_sector_b(evaluated: pd.DataFrame, worst_pct: float) -> pd.DataFrame:
    rows = []
    for icb2, group in evaluated.groupby("icb2", sort=True):
        sta = higher_tail_flags(group["sta"], worst_pct)
        snoa = higher_tail_flags(group["snoa"], worst_pct)
        sta_names = set(group.loc[sta.flags, "ticker"])
        snoa_names = set(group.loc[snoa.flags, "ticker"])
        union = sta_names | snoa_names
        operative = set(group.loc[group["high_accrual_flag"], "ticker"])
        planned = max(1, math.ceil(len(group) * worst_pct)) if len(group) else 0
        rows.append({
            "icb2": icb2, "group_size": len(group), "per_sector_worst_pct": worst_pct,
            "per_sector_cut_count": planned, "effective_cut_percentage": len(union) / len(group) if len(group) else 0.0,
            "sta_affected_tickers": "|".join(sorted(sta_names)),
            "snoa_affected_tickers": "|".join(sorted(snoa_names)),
            "union_affected_tickers": "|".join(sorted(union)),
            "difference_from_operative_whole_universe": "|".join(sorted(union.symmetric_difference(operative))),
        })
    return pd.DataFrame(rows)


def guardrail(filter_stats: pd.DataFrame, rejects: pd.DataFrame, evaluated: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
    triggered = filter_stats[filter_stats["removal_pct"] > 0.30]
    details = []
    indexed = evaluated.set_index("ticker", drop=False)
    for stat in triggered.to_dict("records"):
        affected = rejects.loc[rejects["reason_label"] == stat["filter"], "ticker"].head(5)
        for ticker in affected:
            row = indexed.loc[ticker] if ticker in indexed.index else None
            details.append({
                **stat, "ticker": ticker,
                "raw_inputs": "" if row is None else row["raw_formula_inputs"],
                "intermediate_calculations": "" if row is None else repr({name: row.get(name) for name in ("sta", "snoa", "m_score", "distress_high_risk")}),
                "final_triggering_value": rejects.loc[rejects["ticker"] == ticker, "trigger_value"].iloc[0],
                "threshold_or_cutoff": rejects.loc[rejects["ticker"] == ticker, "threshold_or_cutoff"].iloc[0],
            })
    return not triggered.empty, pd.DataFrame(details)


def run_cleaning_pipeline(full_universe: pd.DataFrame, cache_root: str | Path, evaluation_date: str, worst_pct: float, mscore_threshold: float) -> PipelineResult:
    upstream_keep = ~full_universe["icb2"].isin(FINANCIAL_ICB2) & ~full_universe["exchange"].astype(str).str.upper().eq("UPCOM")
    formula_universe = full_universe.loc[upstream_keep].reset_index(drop=True)
    evaluated = evaluate_formula_stage(formula_universe, cache_root, evaluation_date)
    evaluated, cutoffs = add_formula_flags(evaluated, worst_pct, mscore_threshold)
    rejects = assign_primary_rejections(full_universe, evaluated, cutoffs, mscore_threshold)
    rejected = set(rejects["ticker"])
    survivors = evaluated.loc[~evaluated["ticker"].isin(rejected)].copy().reset_index(drop=True)
    stats = calculate_filter_stats(full_universe, rejects)
    sector_a = build_sector_a(evaluated, rejects)
    sector_b = build_sector_b(evaluated, worst_pct)
    triggered, guard_details = guardrail(stats, rejects, evaluated)
    return PipelineResult(evaluated, survivors, rejects, sector_a, sector_b, stats, cutoffs, triggered, guard_details)


def normalized_history_hash(frame: pd.DataFrame, original_columns: Iterable[str]) -> str:
    payload = frame.loc[:, list(original_columns)].to_csv(index=False, lineterminator="\n").encode("utf-8")
    return sha256(payload).hexdigest()


def extend_reject_history(history: pd.DataFrame, new_rejects: pd.DataFrame, universe: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    original_columns = list(history.columns)
    before_hash = normalized_history_hash(history, original_columns)
    historical = history.copy()
    for column in AUDIT_COLUMNS:
        historical[column] = ""
    universe_by_ticker = universe.set_index("ticker", drop=False)
    appended = []
    for rejection in new_rejects.to_dict("records"):
        source = universe_by_ticker.loc[rejection["ticker"]]
        row = {column: source.get(column, "") for column in original_columns}
        row.update(
            status="REJECTED", reject_reason=rejection["reason_label"],
            source=rejection["source"], as_of=rejection["as_of"], data_status=rejection["data_status"],
        )
        row.update({column: rejection[column] for column in AUDIT_COLUMNS})
        appended.append(row)
    final = pd.concat([historical, pd.DataFrame(appended)], ignore_index=True)
    preserved = final.iloc[: len(history)].loc[:, original_columns]
    pd.testing.assert_frame_equal(history.reset_index(drop=True), preserved.reset_index(drop=True), check_dtype=False)
    after_hash = normalized_history_hash(preserved, original_columns)
    return final, {
        "historical_row_count": len(history), "appended_sprint4_row_count": len(appended),
        "final_row_count": len(final), "historical_hash_before": before_hash,
        "historical_hash_after": after_hash, "historical_rows_preserved": before_hash == after_hash,
    }
