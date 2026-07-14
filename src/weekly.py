from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
import hashlib
import importlib.metadata
import json
import math
import platform
import subprocess
from typing import Any

import pandas as pd

from src.data.vnstock_client import FetchResult, VnstockClient
from src.universe import _extract_market_cap_with_source


MISSING = "N/A (MISSING_DATA)"
API_ERROR = "API_ERROR"
STALE_DATA = "STALE_DATA"
LIMITED_HISTORY = "LIMITED_HISTORY"
SOURCE = "vnstock_vci_quote_history"
MARKET_CAP_SOURCE = "vnstock_vci_company_overview"
VNINDEX_SYMBOLS = ("VNINDEX", "VN30")
INDEX_SOURCE_PROXY = "UNIVERSE_EQUAL_WEIGHT_PROXY"
CACHE_STATE_CACHED = "CACHED"
CACHE_STATE_FETCHED = "FETCHED"
MARKET_CAP_SOURCE_REPORTED = "SOURCE_REPORTED_MARKET_CAP"
MARKET_CAP_SOURCE_PROXY = "SHARES_X_LAST_CLOSE_X1000_PROXY"
MARKET_CAP_SOURCE_MISSING = "N/A"
MARKET_CAP_STATUS_OK = "OK"
MARKET_CAP_STATUS_MISSING = "MISSING_DATA"
CAP_WEIGHT_STATUS_OK = "OK"
CAP_WEIGHT_STATUS_SKIPPED = "SKIPPED_MISSING_MARKET_CAP"

INDICATOR_COLUMNS = [
    "as_of",
    "icb2",
    "ticker_count",
    "valid_price_count",
    "sector_return_1w_equal_weight",
    "sector_return_1m_equal_weight",
    "sector_return_3m_equal_weight",
    "sector_return_1w_cap_weight",
    "sector_return_1m_cap_weight",
    "relative_strength_1m_vs_vnindex",
    "breadth_ma50_pct",
    "breadth_ma200_pct",
    "drawdown_from_52w_high",
    "distance_from_52w_low",
    "liquidity_trend_4w",
    "volatility_20d",
    "data_quality_status",
    "missing_fields",
    "source",
]

SUMMARY_COLUMNS = [
    "as_of",
    "icb2",
    "ticker_count",
    "main_signal",
    "supporting_evidence",
    "contradicting_evidence",
    "data_quality_status",
    "confidence_lite",
    "source",
]

QUALITY_COLUMNS = [
    "as_of",
    "icb2",
    "accepted_ticker_count",
    "valid_price_count",
    "cached_price_count",
    "stale_price_count",
    "valid_ma50_count",
    "valid_ma200_count",
    "valid_market_cap_count",
    "market_cap_available_count",
    "market_cap_missing_count",
    "market_cap_coverage_pct",
    "market_cap_source",
    "market_cap_status",
    "missing_price_count",
    "api_error_count",
    "api_error_tickers",
    "missing_indicator_count",
    "coverage_status",
    "coverage_warning",
    "index_source",
    "cap_weight_available",
    "cap_weight_status",
    "cap_weight_reason",
    "source",
]

CYCLE_SIGNAL_COLUMNS = [
    "sector",
    "ticker_count",
    "valid_price_count",
    "data_quality_status",
    "coverage_status",
    "relative_strength_1m_vs_vnindex",
    "sector_return_1w_equal_weight",
    "sector_return_1m_equal_weight",
    "price_trend_signal",
    "relative_strength_signal",
    "momentum_signal",
    "breadth_signal",
    "liquidity_signal",
    "data_confidence_signal",
    "candidate_cycle_stage",
    "cycle_signal_confidence",
    "evidence_summary",
    "warning_flags",
]

DRIVER_MAP_COLUMNS = [
    "sector",
    "driver_name",
    "why_it_matters",
    "driver_type",
    "source_strategy",
    "public_web_search_available",
    "codex_pipeline_required",
    "priority",
    "interpretation_note",
    "data_status",
]

CORE_INDICATORS = [
    "sector_return_1w_equal_weight",
    "sector_return_1m_equal_weight",
    "sector_return_3m_equal_weight",
    "relative_strength_1m_vs_vnindex",
    "breadth_ma50_pct",
    "drawdown_from_52w_high",
    "distance_from_52w_low",
    "volatility_20d",
    "liquidity_trend_4w",
]

OPTIONAL_INDICATORS = [
    "sector_return_1w_cap_weight",
    "sector_return_1m_cap_weight",
    "breadth_ma200_pct",
]

BANNED_REPORT_PHRASES = [
    "đã tạo đáy",
    "đã tạo đỉnh",
    "nên mua",
    "nên bán",
    "mã x hấp dẫn",
    "target price",
    "mục tiêu giá",
    "khuyến nghị mua",
    "khuyến nghị bán",
]


@dataclass(frozen=True)
class WeeklyMvpResult:
    output_dir: Path
    indicators: pd.DataFrame
    summary: pd.DataFrame
    data_quality: pd.DataFrame
    metadata: dict[str, Any]


@dataclass(frozen=True)
class IndexContext:
    return_1m: float | None
    source: str
    missing: bool


def run_weekly_mvp(
    universe_path: str | Path = "data/universe.csv",
    reports_root: str | Path = "reports",
    client: Any | None = None,
    limit_sectors: int | None = None,
    market_cap_limit: int = 0,
    progress: bool = True,
) -> WeeklyMvpResult:
    if market_cap_limit < 0:
        raise ValueError("market_cap_limit must be zero or greater")
    universe_path = Path(universe_path)
    reports_root = Path(reports_root)
    universe = _accepted_universe(_read_universe(universe_path))
    if universe.empty:
        raise ValueError("data/universe.csv has no accepted rows")

    if limit_sectors is not None:
        sectors = sorted(universe["icb2"].dropna().astype(str).unique())[: max(limit_sectors, 0)]
        universe = universe[universe["icb2"].astype(str).isin(sectors)].copy()
        if universe.empty:
            raise ValueError("--limit-sectors produced an empty universe slice")

    client = client or VnstockClient(
        cache_dir=Path(__file__).resolve().parent / "data" / "cache" / "weekly_mvp",
        min_sleep_seconds=0.5,
        max_sleep_seconds=1.0,
    )

    price_results = _fetch_ticker_prices(universe, client=client, progress=progress)
    market_cap_results = _fetch_market_caps(
        universe,
        client=client,
        progress=progress,
        market_cap_limit=market_cap_limit,
    )
    universe = enrich_universe_market_caps(universe, market_cap_results)
    index_result = _fetch_index_prices(client)
    outputs = build_weekly_outputs(universe, price_results, index_result=index_result, source=SOURCE)

    report_date = date.today().isoformat()
    output_dir = reports_root / report_date
    output_dir.mkdir(parents=True, exist_ok=True)

    indicators = outputs.indicators
    summary = outputs.summary
    data_quality = outputs.data_quality
    cycle_signals = build_sector_cycle_signals(indicators, summary, data_quality)
    driver_map = build_sector_driver_map(indicators)
    as_of = _latest_as_of(indicators, fallback=report_date)
    metadata_extra = run_quality_metadata(data_quality)
    metadata_extra.update(ai_package_metadata(cycle_signals, driver_map))
    metadata = build_run_metadata(
        universe_path=universe_path,
        universe=universe,
        as_of=as_of,
        source=SOURCE,
        output_dir=output_dir,
        extra=metadata_extra,
    )

    indicators.to_csv(output_dir / "sector_indicators_tier1.csv", index=False)
    summary.to_csv(output_dir / "sector_summary.csv", index=False)
    data_quality.to_csv(output_dir / "data_quality.csv", index=False)
    cycle_signals.to_csv(output_dir / "sector_cycle_signals.csv", index=False)
    driver_map.to_csv(output_dir / "sector_driver_map.csv", index=False)
    ai_summary_text = render_ai_input_summary(indicators, data_quality, cycle_signals, metadata)
    readme_text = render_readme_for_ai()
    _assert_report_is_safe(ai_summary_text)
    _assert_report_is_safe(readme_text)
    (output_dir / "AI_INPUT_SUMMARY.md").write_text(ai_summary_text, encoding="utf-8")
    (output_dir / "README_FOR_AI.md").write_text(readme_text, encoding="utf-8")
    (output_dir / "run_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    report_text = render_weekly_report(indicators, summary, data_quality, metadata)
    _assert_report_is_safe(report_text)
    (output_dir / "WEEKLY_REPORT.md").write_text(report_text, encoding="utf-8")

    return WeeklyMvpResult(
        output_dir=output_dir,
        indicators=indicators,
        summary=summary,
        data_quality=data_quality,
        metadata=metadata,
    )


def build_weekly_outputs(
    universe: pd.DataFrame,
    price_results: dict[str, Any],
    index_result: Any | None = None,
    source: str = SOURCE,
) -> WeeklyMvpResult:
    universe = _accepted_universe(universe)
    if universe.empty:
        raise ValueError("universe has no accepted rows")

    index_context = build_index_context(price_results, index_result=index_result, source=source)

    indicator_rows: list[dict[str, Any]] = []
    quality_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for icb2, group in universe.groupby("icb2", dropna=False):
        sector_name = str(icb2).strip() or MISSING
        histories: dict[str, pd.DataFrame] = {}
        statuses: dict[str, str] = {}
        cache_states: dict[str, str] = {}
        sources: dict[str, str] = {}

        for _, universe_row in group.iterrows():
            ticker = str(universe_row["ticker"]).strip().upper()
            result = _as_fetch_result(price_results.get(ticker), source=source)
            histories[ticker] = _normalize_prices(result.data)
            statuses[ticker] = result.status
            cache_states[ticker] = price_cache_state(result)
            sources[ticker] = result.source or source

        indicator_row = calculate_sector_indicators(
            icb2=sector_name,
            universe_rows=group,
            price_histories=histories,
            price_statuses=statuses,
            index_return_1m=index_context.return_1m,
            index_missing=index_context.missing,
            source=_combine_sources(source, index_context.source),
        )
        quality_row = build_data_quality_row(
            icb2=sector_name,
            universe_rows=group,
            price_histories=histories,
            price_statuses=statuses,
            price_cache_states=cache_states,
            indicator_row=indicator_row,
            index_source=index_context.source,
            source=_combine_sources(source, *sources.values()),
        )
        indicator_row["data_quality_status"] = quality_row["coverage_status"]
        summary_row = build_summary_row(
            indicator_row,
            quality_row,
            index_missing=index_context.missing,
            source=_combine_sources(source, index_context.source),
        )

        indicator_rows.append(indicator_row)
        quality_rows.append(quality_row)
        summary_rows.append(summary_row)

    return WeeklyMvpResult(
        output_dir=Path(),
        indicators=pd.DataFrame(indicator_rows, columns=INDICATOR_COLUMNS),
        summary=pd.DataFrame(summary_rows, columns=SUMMARY_COLUMNS),
        data_quality=pd.DataFrame(quality_rows, columns=QUALITY_COLUMNS),
        metadata={},
    )


def build_sector_cycle_signals(
    indicators: pd.DataFrame,
    summary: pd.DataFrame,
    data_quality: pd.DataFrame,
) -> pd.DataFrame:
    if indicators.empty:
        return pd.DataFrame(columns=CYCLE_SIGNAL_COLUMNS)

    rows: list[dict[str, Any]] = []
    for _, indicator_row in indicators.sort_values("icb2").iterrows():
        sector = str(indicator_row.get("icb2", "")).strip()
        quality_row = find_row(data_quality, "icb2", indicator_row.get("icb2"))
        summary_row = find_row(summary, "icb2", indicator_row.get("icb2"))
        ticker_count = int_or_zero(indicator_row.get("ticker_count"))
        valid_price_count = int_or_zero(indicator_row.get("valid_price_count"))
        coverage_status = str(quality_row.get("coverage_status", indicator_row.get("data_quality_status", MISSING)))
        data_quality_status = str(indicator_row.get("data_quality_status", coverage_status))
        one_week = signal_number(indicator_row.get("sector_return_1w_equal_weight"))
        one_month = signal_number(indicator_row.get("sector_return_1m_equal_weight"))
        relative = signal_number(indicator_row.get("relative_strength_1m_vs_vnindex"))
        breadth = signal_number(indicator_row.get("breadth_ma50_pct"))
        liquidity = signal_number(indicator_row.get("liquidity_trend_4w"))
        stage = candidate_cycle_stage_for(
            coverage_status=coverage_status,
            one_week=one_week,
            one_month=one_month,
            relative=relative,
            breadth=breadth,
        )
        confidence = cycle_signal_confidence_for(
            coverage_status=coverage_status,
            ticker_count=ticker_count,
            valid_price_count=valid_price_count,
            one_week=one_week,
            one_month=one_month,
            relative=relative,
            breadth=breadth,
            liquidity=liquidity,
            candidate_cycle_stage=stage,
        )
        warnings = warning_flags_for(indicator_row, quality_row, relative=relative, breadth=breadth)

        rows.append(
            {
                "sector": sector,
                "ticker_count": ticker_count,
                "valid_price_count": valid_price_count,
                "data_quality_status": data_quality_status,
                "coverage_status": coverage_status,
                "relative_strength_1m_vs_vnindex": indicator_row.get("relative_strength_1m_vs_vnindex", MISSING),
                "sector_return_1w_equal_weight": indicator_row.get("sector_return_1w_equal_weight", MISSING),
                "sector_return_1m_equal_weight": indicator_row.get("sector_return_1m_equal_weight", MISSING),
                "price_trend_signal": price_trend_signal(one_month),
                "relative_strength_signal": relative_strength_signal(relative),
                "momentum_signal": momentum_signal(one_week, one_month),
                "breadth_signal": breadth_signal(breadth),
                "liquidity_signal": liquidity_signal(liquidity),
                "data_confidence_signal": data_confidence_signal(
                    coverage_status=coverage_status,
                    ticker_count=ticker_count,
                    valid_price_count=valid_price_count,
                ),
                "candidate_cycle_stage": stage,
                "cycle_signal_confidence": confidence,
                "evidence_summary": cycle_evidence_summary(
                    one_week=one_week,
                    one_month=one_month,
                    relative=relative,
                    breadth=breadth,
                    liquidity=liquidity,
                    main_signal=summary_row.get("main_signal", MISSING),
                ),
                "warning_flags": warnings,
            }
        )
    return pd.DataFrame(rows, columns=CYCLE_SIGNAL_COLUMNS)


def build_sector_driver_map(indicators: pd.DataFrame) -> pd.DataFrame:
    if indicators.empty or "icb2" not in indicators:
        return pd.DataFrame(columns=DRIVER_MAP_COLUMNS)

    templates = sector_driver_templates()
    rows: list[dict[str, Any]] = []
    sectors = sorted(str(value).strip() for value in indicators["icb2"].dropna().astype(str).unique() if str(value).strip())
    for sector in sectors:
        drivers = templates.get(sector, generic_sector_drivers())
        for driver in drivers:
            row = {"sector": sector}
            row.update(driver)
            rows.append(row)
    return pd.DataFrame(rows, columns=DRIVER_MAP_COLUMNS)


def ai_package_metadata(cycle_signals: pd.DataFrame, driver_map: pd.DataFrame) -> dict[str, Any]:
    return {
        "ai_ready_package_created": bool(not cycle_signals.empty and not driver_map.empty),
        "cycle_signals_created": bool(not cycle_signals.empty),
        "driver_map_created": bool(not driver_map.empty),
        "cycle_signal_sector_count": int(cycle_signals["sector"].nunique()) if "sector" in cycle_signals else 0,
        "driver_map_sector_count": int(driver_map["sector"].nunique()) if "sector" in driver_map else 0,
        "driver_map_row_count": int(len(driver_map)),
    }


def render_ai_input_summary(
    indicators: pd.DataFrame,
    data_quality: pd.DataFrame,
    cycle_signals: pd.DataFrame,
    metadata: dict[str, Any],
) -> str:
    generated_at = metadata.get("generated_at", MISSING)
    as_of = metadata.get("as_of", MISSING)
    universe_count = metadata.get("universe_row_count", 0)
    sector_count = int(cycle_signals["sector"].nunique()) if "sector" in cycle_signals else 0
    quality_counts = quality_status_counts(data_quality)
    valid_price_total = quality_total(data_quality, "valid_price_count")
    api_error_total = quality_total(data_quality, "api_error_count")
    index_source = quality_unique_values(data_quality, "index_source")
    relative_strength_available = "yes" if indicator_has_any_value(indicators, "relative_strength_1m_vs_vnindex") else "no"
    cap_weight_status = quality_unique_values(data_quality, "cap_weight_status")
    cap_weight_reason = unique_quality_text(data_quality, "cap_weight_reason")

    lines = [
        "# AI Input Summary",
        "",
        "This is an input package for AI analysis, not a buy/sell recommendation report.",
        "",
        "## Run Context",
        "",
        f"- report date: {as_of}",
        f"- generated_at: {generated_at}",
        f"- universe ticker count: {universe_count}",
        f"- sector count: {sector_count}",
        f"- valid_price total: {valid_price_total}",
        f"- API_ERROR total: {api_error_total}",
        f"- index_source: {index_source}",
        f"- relative_strength availability: {relative_strength_available}",
        f"- cap_weight_status: {cap_weight_status}",
        f"- cap_weight_reason: {cap_weight_reason}",
        f"- OK sectors: {quality_counts.get('OK', 0)}",
        f"- WATCH sectors: {quality_counts.get('WATCH', 0)}",
        f"- LOW_COVERAGE sectors: {quality_counts.get('LOW_COVERAGE', 0)}",
        f"- DATA_WEAK sectors: {quality_counts.get('DATA_WEAK', 0)}",
        "",
        "## Sector Snapshot",
        "",
        "| sector | ticker_count | valid_price_count | coverage/data_quality | relative_strength_1m_vs_vnindex | return_1w_equal_weight | return_1m_equal_weight | warning_flags |",
        "| --- | ---: | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for _, row in cycle_signals.sort_values("sector").iterrows():
        quality_text = f"{row['coverage_status']}/{row['data_quality_status']}"
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["sector"]),
                    str(row["ticker_count"]),
                    str(row["valid_price_count"]),
                    quality_text,
                    format_value(row["relative_strength_1m_vs_vnindex"]),
                    format_value(row["sector_return_1w_equal_weight"]),
                    format_value(row["sector_return_1m_equal_weight"]),
                    str(row["warning_flags"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Reading Notes",
            "",
            "- Candidate cycle labels are deterministic input labels, not final interpretation.",
            "- Missing values must stay missing and must not be treated as zero.",
            "- Cap-weight fields remain unavailable unless cap_weight_status is OK.",
            "- Public web research is still required for current sector drivers and news context.",
            "",
        ]
    )
    return "\n".join(lines)


def render_readme_for_ai() -> str:
    lines = [
        "# README For AI",
        "",
        "Use this package as structured input for sector-level cycle analysis only.",
        "",
        "## Rules",
        "",
        "- Analyze only at sector level.",
        "- Do not recommend buying or selling.",
        "- Do not rank individual stocks.",
        "- Do not provide price targets.",
        "- Do not treat missing data as zero.",
        "- Cap-weight indicators are unavailable unless cap_weight_status says OK.",
        "- If a sector has LOW_COVERAGE or DATA_WEAK, conclusions must be cautious.",
        "- Relative strength is compared against index_source.",
        "- Web search should be used later for public sector drivers, news, commodity prices, macro policy, and recent context.",
        "- Non-public or unavailable data must be marked as N/A, not invented.",
        "",
        "## Files",
        "",
        "- AI_INPUT_SUMMARY.md: compact run summary for AI consumption.",
        "- sector_cycle_signals.csv: deterministic candidate sector-cycle labels and warnings.",
        "- sector_driver_map.csv: sector-level driver checklist for later public web research.",
        "- sector_indicators_tier1.csv: raw tier-1 sector indicators.",
        "- data_quality.csv: data coverage, source, and missing-data warnings.",
        "- WEEKLY_REPORT.md: automated data summary, not a final analytical report.",
        "",
    ]
    return "\n".join(lines)


def signal_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    text = str(value).strip()
    if text == "" or text == MISSING:
        return None
    try:
        number = float(text.replace(",", ""))
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def int_or_zero(value: Any) -> int:
    number = signal_number(value)
    return int(number) if number is not None else 0


def price_trend_signal(one_month: float | None) -> str:
    if one_month is None:
        return "MISSING"
    if one_month > 0.03:
        return "STRONG_UP"
    if one_month > 0:
        return "UP"
    if one_month < -0.03:
        return "STRONG_DOWN"
    if one_month < 0:
        return "DOWN"
    return "FLAT"


def relative_strength_signal(relative: float | None) -> str:
    if relative is None:
        return "MISSING"
    if relative > 0.02:
        return "OUTPERFORMING"
    if relative > 0:
        return "SLIGHTLY_OUTPERFORMING"
    if relative < -0.02:
        return "UNDERPERFORMING"
    if relative < 0:
        return "SLIGHTLY_UNDERPERFORMING"
    return "INLINE"


def momentum_signal(one_week: float | None, one_month: float | None) -> str:
    if one_week is None or one_month is None:
        return "MISSING"
    if one_week > 0 and one_month > 0:
        return "POSITIVE"
    if one_week < 0 and one_month < 0:
        return "NEGATIVE"
    if one_week > 0 and one_month < 0:
        return "RECOVERING"
    if one_week < 0 and one_month > 0:
        return "COOLING"
    return "MIXED"


def breadth_signal(breadth: float | None) -> str:
    if breadth is None:
        return "MISSING"
    if breadth >= 0.65:
        return "BROAD_POSITIVE"
    if breadth >= 0.5:
        return "POSITIVE"
    if breadth >= 0.35:
        return "MIXED"
    return "WEAK"


def liquidity_signal(liquidity: float | None) -> str:
    if liquidity is None:
        return "MISSING"
    if liquidity > 0.1:
        return "EXPANDING"
    if liquidity >= 0:
        return "STABLE_TO_UP"
    if liquidity > -0.1:
        return "STABLE_TO_DOWN"
    return "CONTRACTING"


def data_confidence_signal(coverage_status: str, ticker_count: int, valid_price_count: int) -> str:
    if coverage_status in {"LOW_COVERAGE", "DATA_WEAK"}:
        return "LOW"
    if coverage_status == "WATCH" or valid_price_count < ticker_count:
        return "MEDIUM"
    return "HIGH"


def candidate_cycle_stage_for(
    coverage_status: str,
    one_week: float | None,
    one_month: float | None,
    relative: float | None,
    breadth: float | None,
) -> str:
    if coverage_status in {"LOW_COVERAGE", "DATA_WEAK"} or one_month is None or relative is None:
        return "UNCLEAR_DATA"
    if one_month > 0 and relative > 0 and breadth is not None and breadth >= 0.5:
        return "LEADERSHIP" if one_week is not None and one_week > 0 else "IMPROVING"
    if (one_month > 0 and relative >= 0) or (relative > 0 and breadth is not None and breadth >= 0.4):
        return "IMPROVING"
    if one_month < 0 and relative < 0 and breadth is not None and breadth <= 0.4:
        return "LAGGING"
    if one_month < 0 or relative < 0:
        return "WEAKENING"
    return "NEUTRAL"


def cycle_signal_confidence_for(
    coverage_status: str,
    ticker_count: int,
    valid_price_count: int,
    one_week: float | None,
    one_month: float | None,
    relative: float | None,
    breadth: float | None,
    liquidity: float | None,
    candidate_cycle_stage: str,
) -> str:
    required_missing = any(value is None for value in (one_month, relative))
    if candidate_cycle_stage == "UNCLEAR_DATA" or coverage_status in {"LOW_COVERAGE", "DATA_WEAK"} or required_missing:
        return "LOW"
    optional_missing = any(value is None for value in (one_week, breadth, liquidity))
    if coverage_status == "OK" and valid_price_count == ticker_count and not optional_missing:
        return "HIGH"
    return "MEDIUM"


def cycle_evidence_summary(
    one_week: float | None,
    one_month: float | None,
    relative: float | None,
    breadth: float | None,
    liquidity: float | None,
    main_signal: Any,
) -> str:
    parts = [
        f"1w={format_value(one_week)}",
        f"1m={format_value(one_month)}",
        f"relative_1m={format_value(relative)}",
        f"breadth_ma50={format_value(breadth)}",
        f"liquidity_4w={format_value(liquidity)}",
        f"summary={main_signal}",
    ]
    return "; ".join(parts)


def warning_flags_for(
    indicator_row: pd.Series,
    quality_row: dict[str, Any],
    relative: float | None,
    breadth: float | None,
) -> str:
    flags: list[str] = []
    coverage = str(quality_row.get("coverage_status", indicator_row.get("data_quality_status", "")))
    if coverage and coverage != "OK":
        flags.append(coverage)
    cap_weight_status = str(quality_row.get("cap_weight_status", ""))
    if cap_weight_status and cap_weight_status != CAP_WEIGHT_STATUS_OK:
        flags.append("CAP_WEIGHT_SKIPPED")
    missing_fields = str(indicator_row.get("missing_fields", "NONE"))
    if missing_fields and missing_fields != "NONE":
        flags.append(f"MISSING_FIELDS={missing_fields}")
    api_error_count = int_or_zero(quality_row.get("api_error_count"))
    if api_error_count:
        flags.append(f"API_ERROR={api_error_count}")
    if relative is None:
        flags.append("MISSING_RELATIVE_STRENGTH")
    elif relative < 0:
        flags.append("NEGATIVE_RELATIVE_STRENGTH")
    if breadth is None:
        flags.append("MISSING_BREADTH")
    elif breadth < 0.4:
        flags.append("LOW_BREADTH")
    return "|".join(dict.fromkeys(flags)) if flags else "NONE"


def indicator_has_any_value(indicators: pd.DataFrame, column: str) -> bool:
    if indicators.empty or column not in indicators:
        return False
    return any(signal_number(value) is not None for value in indicators[column])


def unique_quality_text(data_quality: pd.DataFrame, column: str) -> str:
    if data_quality.empty or column not in data_quality:
        return MISSING
    values = []
    for value in data_quality[column].dropna().astype(str):
        text = value.strip()
        if text and text not in values:
            values.append(text)
    return "; ".join(values) if values else MISSING


def sector_driver_templates() -> dict[str, list[dict[str, str]]]:
    return {
        "BÁN LẺ": [
            driver("consumer spending", "Tracks household demand and discretionary purchase cycles.", "demand", "high"),
            driver("same-store sales", "Shows whether retail growth is broad or store-opening driven.", "operating", "high"),
            driver("inventory cycle", "High inventory can pressure margins and cash conversion.", "operating", "medium"),
        ],
        "BẢO HIỂM": [
            driver("bond yields", "Investment income and reserve discount rates are sensitive to yields.", "macro", "high"),
            driver("premium growth", "Shows insurance demand and distribution momentum.", "demand", "high"),
            driver("claim ratio", "Rising claims can pressure underwriting profitability.", "operating", "medium"),
        ],
        "BẤT ĐỘNG SẢN": [
            driver("interest rate and credit policy", "Affects buyer affordability, financing access, and project progress.", "macro", "high"),
            driver("legal approvals", "Approval pace affects launch timing, presales, and revenue recognition.", "policy", "high"),
            driver("housing presales", "Shows demand strength before accounting revenue appears.", "demand", "high"),
        ],
        "CÔNG NGHỆ THÔNG TIN": [
            driver("global IT spending", "Affects outsourcing demand and project budgets.", "demand", "high"),
            driver("USD/VND exchange rate", "Revenue and margin can be sensitive to export billing currency.", "macro", "medium"),
            driver("digital transformation budgets", "Domestic enterprise and public-sector budgets support demand.", "demand", "medium"),
        ],
        "DU LỊCH VÀ GIẢI TRÍ": [
            driver("tourist arrivals", "Visitor flow drives hotel, airport service, and leisure demand.", "demand", "high"),
            driver("hotel occupancy", "Occupancy shows pricing power and service utilization.", "operating", "high"),
            driver("airline capacity", "Seat supply and routes affect travel volume and costs.", "supply", "medium"),
        ],
        "DẦU KHÍ": [
            driver("Brent crude price", "Oil price affects upstream revenue, sentiment, and project economics.", "commodity", "high"),
            driver("gas demand", "Industrial and power-sector demand affects gas volume cycles.", "demand", "medium"),
            driver("refining margin", "Crack spreads influence refinery earnings sensitivity.", "commodity", "high"),
        ],
        "DỊCH VỤ TÀI CHÍNH": [
            driver("market turnover", "Brokerage revenue and sentiment follow market liquidity.", "market", "high"),
            driver("margin lending", "Affects securities-company interest income and risk appetite.", "credit", "high"),
            driver("IPO and issuance pipeline", "Capital-market activity supports fee income cycles.", "market", "medium"),
        ],
        "HÀNG & DỊCH VỤ CÔNG NGHIỆP": [
            driver("manufacturing PMI", "Shows industrial demand and order momentum.", "macro", "high"),
            driver("export orders", "Industrial service demand often follows external orders.", "demand", "high"),
            driver("logistics cost", "Freight and fuel costs can pressure margins.", "cost", "medium"),
        ],
        "HÀNG CÁ NHÂN & GIA DỤNG": [
            driver("consumer discretionary demand", "Demand cycle affects volume and pricing power.", "demand", "high"),
            driver("export orders", "Many manufacturers depend on external consumer demand.", "demand", "medium"),
            driver("input costs", "Materials and labor shifts affect gross margin.", "cost", "medium"),
        ],
        "HÓA CHẤT": [
            driver("rubber price", "Affects revenue and margin for rubber producers and cost pressure for downstream users.", "commodity", "high"),
            driver("fertilizer and chemical input cost", "Feedstock costs influence spread and profitability.", "commodity", "high"),
            driver("export demand", "External demand affects volume and pricing cycle.", "demand", "medium"),
        ],
        "NGÂN HÀNG": [
            driver("credit growth", "Affects loan growth and banking revenue cycle.", "credit", "high"),
            driver("net interest margin", "Interest-rate cycle affects spread income.", "macro", "high"),
            driver("asset quality and NPLs", "Credit costs can lag the loan cycle and affect earnings quality.", "risk", "high"),
        ],
        "THỰC PHẨM VÀ ĐỒ UỐNG": [
            driver("input commodity prices", "Sugar, grain, milk, and packaging costs affect margins.", "commodity", "high"),
            driver("consumer demand", "Volume growth follows staples and discretionary spending trends.", "demand", "high"),
            driver("export markets", "Seafood and food exporters depend on overseas demand and trade rules.", "demand", "medium"),
        ],
        "TRUYỀN THÔNG": [
            driver("advertising spend", "Ad budgets drive revenue sensitivity for media businesses.", "demand", "high"),
            driver("platform regulation", "Policy changes can affect distribution and monetization.", "policy", "medium"),
            driver("event and content cycle", "Major events and content releases can shift traffic and ad demand.", "operating", "medium"),
        ],
        "TÀI NGUYÊN CƠ BẢN": [
            driver("steel price", "Price cycle affects revenue and inventory gains or losses.", "commodity", "high"),
            driver("iron ore and coking coal", "Input costs affect steel producer margins.", "commodity", "high"),
            driver("China demand", "Regional commodity demand often follows China construction and manufacturing.", "macro", "medium"),
        ],
        "VIỄN THÔNG": [
            driver("subscriber and ARPU trend", "User growth and revenue per user drive telecom revenue cycle.", "operating", "high"),
            driver("5G capex", "Network investment affects cost cycle and future service capacity.", "capex", "medium"),
            driver("data usage", "Traffic growth supports monetization if pricing holds.", "demand", "medium"),
        ],
        "XÂY DỰNG VÀ VẬT LIỆU": [
            driver("public investment", "Infrastructure spending drives construction and materials demand.", "policy", "high"),
            driver("cement and steel prices", "Material price cycles affect margins and demand timing.", "commodity", "high"),
            driver("construction permits", "Permit activity signals private construction demand.", "demand", "medium"),
        ],
        "Y TẾ": [
            driver("hospital and pharma demand", "Patient volume and medicine demand drive revenue cycles.", "demand", "high"),
            driver("drug tender policy", "Tender rules affect pricing, volume, and timing.", "policy", "high"),
            driver("insurance reimbursement", "Payment policy can change affordability and provider cash flow.", "policy", "medium"),
        ],
        "Ô TÔ VÀ PHỤ TÙNG": [
            driver("vehicle sales", "Unit sales show demand cycle for assemblers and parts suppliers.", "demand", "high"),
            driver("registration fee and tax policy", "Policy incentives can pull demand forward.", "policy", "high"),
            driver("auto loan rates", "Financing cost affects consumer purchase affordability.", "macro", "medium"),
        ],
        "ĐIỆN, NƯỚC & XĂNG DẦU KHÍ ĐỐT": [
            driver("power demand", "Electricity load tracks industrial and household consumption.", "demand", "high"),
            driver("hydrology and water inflow", "Water availability affects hydropower output mix and margins.", "weather", "high"),
            driver("regulated tariff policy", "Tariff changes affect revenue and cost pass-through.", "policy", "high"),
        ],
    }


def generic_sector_drivers() -> list[dict[str, str]]:
    return [
        driver("sector demand", "Checks whether end-market demand is expanding or contracting.", "demand", "high"),
        driver("input cost cycle", "Tracks whether cost pressure is rising or easing.", "cost", "medium"),
        driver("policy and macro context", "Sector cycles can be affected by interest rates, regulation, and fiscal policy.", "macro", "medium"),
    ]


def driver(
    driver_name: str,
    why_it_matters: str,
    driver_type: str,
    priority: str,
    source_strategy: str = "CHATGPT_WEB_SEARCH_PUBLIC",
    public_web_search_available: str = "yes",
    codex_pipeline_required: str = "no",
    data_status: str = "NEEDS_WEB_RESEARCH",
) -> dict[str, str]:
    return {
        "driver_name": driver_name,
        "why_it_matters": why_it_matters,
        "driver_type": driver_type,
        "source_strategy": source_strategy,
        "public_web_search_available": public_web_search_available,
        "codex_pipeline_required": codex_pipeline_required,
        "priority": priority,
        "interpretation_note": "Use public current context later; do not invent live values in this package.",
        "data_status": data_status,
    }


def build_index_context(
    price_results: dict[str, Any],
    index_result: Any | None = None,
    source: str = SOURCE,
) -> IndexContext:
    index_fetch = _as_fetch_result(index_result, source=source)
    index_prices = _normalize_prices(index_fetch.data)
    index_return_1m = calc_return(index_prices, 21)
    index_source = index_source_from_fetch(index_fetch)
    if index_return_1m is not None:
        return IndexContext(return_1m=index_return_1m, source=index_source, missing=False)

    proxy_prices = build_universe_equal_weight_proxy_index(price_results)
    proxy_return_1m = calc_return(proxy_prices, 21)
    if proxy_return_1m is not None:
        return IndexContext(return_1m=proxy_return_1m, source=INDEX_SOURCE_PROXY, missing=False)

    return IndexContext(return_1m=None, source=index_source, missing=True)


def build_universe_equal_weight_proxy_index(price_results: dict[str, Any]) -> pd.DataFrame:
    histories: dict[str, pd.DataFrame] = {}
    for ticker, value in price_results.items():
        result = _as_fetch_result(value, source=SOURCE)
        price = _normalize_prices(result.data)
        if _has_valid_close(price, min_rows=22):
            histories[str(ticker).upper()] = price
    proxy_returns = build_sector_daily_returns(histories)
    proxy_index = build_sector_index(proxy_returns)
    if proxy_index.empty:
        return pd.DataFrame(columns=["date", "close", "volume", "value"])
    return pd.DataFrame(
        {
            "date": pd.to_datetime(proxy_index.index),
            "close": proxy_index.to_numpy(dtype=float),
            "volume": pd.NA,
            "value": pd.NA,
        }
    )


def index_source_from_fetch(index_fetch: FetchResult) -> str:
    metadata = index_fetch.metadata or {}
    metadata_source = str(metadata.get("index_source", "")).strip()
    if metadata_source:
        return metadata_source
    source_text = str(index_fetch.source or "").upper()
    for symbol in VNINDEX_SYMBOLS:
        if symbol in source_text:
            return symbol
    return "MISSING_INDEX"


def price_cache_state(result: FetchResult) -> str:
    metadata = result.metadata or {}
    state = str(metadata.get("cache_state", "")).strip().upper()
    if state:
        return state
    if result.status == STALE_DATA:
        return STALE_DATA
    if result.status == API_ERROR:
        return API_ERROR
    return "UNKNOWN"


def enrich_universe_market_caps(universe: pd.DataFrame, market_cap_results: dict[str, Any]) -> pd.DataFrame:
    frame = _accepted_universe(universe)
    for column, default in (
        ("market_cap_source", MARKET_CAP_SOURCE_MISSING),
        ("market_cap_status", MARKET_CAP_STATUS_MISSING),
    ):
        if column not in frame.columns:
            frame[column] = default

    for index, row in frame.iterrows():
        ticker = str(row["ticker"]).strip().upper()
        existing_cap = _single_positive_number(row.get("market_cap"))
        if existing_cap is not None:
            frame.at[index, "market_cap"] = existing_cap
            if str(row.get("market_cap_source", "")).strip() in {"", MARKET_CAP_SOURCE_MISSING}:
                frame.at[index, "market_cap_source"] = MARKET_CAP_SOURCE_REPORTED
            if str(row.get("market_cap_status", "")).strip() in {"", MARKET_CAP_STATUS_MISSING}:
                frame.at[index, "market_cap_status"] = MARKET_CAP_STATUS_OK
            continue

        result = _as_fetch_result(market_cap_results.get(ticker), source=MARKET_CAP_SOURCE)
        value, source = extract_market_cap_from_result(result)
        if value is not None and source is not None:
            frame.at[index, "market_cap"] = value
            frame.at[index, "market_cap_source"] = source
            frame.at[index, "market_cap_status"] = result.status if result.status == STALE_DATA else MARKET_CAP_STATUS_OK
        else:
            frame.at[index, "market_cap"] = ""
            frame.at[index, "market_cap_source"] = MARKET_CAP_SOURCE_MISSING
            frame.at[index, "market_cap_status"] = market_cap_missing_status(result)
    return frame


def extract_market_cap_from_result(result: FetchResult) -> tuple[float | None, str | None]:
    if not result.ok:
        return None, None
    value, source = _extract_market_cap_with_source(result.data)
    if value is None or source is None:
        return None, None
    return float(value), source


def market_cap_missing_status(result: FetchResult) -> str:
    if result.status in {API_ERROR, STALE_DATA}:
        return result.status
    return MARKET_CAP_STATUS_MISSING


def calculate_sector_indicators(
    icb2: str,
    universe_rows: pd.DataFrame,
    price_histories: dict[str, pd.DataFrame],
    price_statuses: dict[str, str] | None = None,
    index_return_1m: float | None = None,
    index_missing: bool = False,
    source: str = SOURCE,
) -> dict[str, Any]:
    price_statuses = price_statuses or {}
    accepted_count = len(universe_rows)
    valid_histories = {
        ticker: _normalize_prices(frame)
        for ticker, frame in price_histories.items()
        if _has_valid_close(_normalize_prices(frame), min_rows=6)
    }
    valid_price_count = len(valid_histories)
    sector_returns = build_sector_daily_returns(valid_histories)
    sector_index = build_sector_index(sector_returns)

    returns_1w = ticker_returns(valid_histories, 5)
    returns_1m = ticker_returns(valid_histories, 21)
    returns_3m = ticker_returns(valid_histories, 63)
    sector_return_1m = mean_or_none(list(returns_1m.values()))

    row: dict[str, Any] = {
        "as_of": latest_price_date(valid_histories) or date.today().isoformat(),
        "icb2": icb2,
        "ticker_count": accepted_count,
        "valid_price_count": valid_price_count,
        "sector_return_1w_equal_weight": mean_or_missing(list(returns_1w.values())),
        "sector_return_1m_equal_weight": mean_or_missing(list(returns_1m.values())),
        "sector_return_3m_equal_weight": mean_or_missing(list(returns_3m.values())),
        "sector_return_1w_cap_weight": cap_weighted_return_or_missing(universe_rows, returns_1w),
        "sector_return_1m_cap_weight": cap_weighted_return_or_missing(universe_rows, returns_1m),
        "relative_strength_1m_vs_vnindex": relative_strength_or_missing(sector_return_1m, index_return_1m),
        "breadth_ma50_pct": breadth_ma_pct_or_missing(valid_histories, 50),
        "breadth_ma200_pct": breadth_ma_pct_or_missing(valid_histories, 200),
        "drawdown_from_52w_high": drawdown_from_52w_high_or_missing(sector_index),
        "distance_from_52w_low": distance_from_52w_low_or_missing(sector_index),
        "liquidity_trend_4w": liquidity_trend_4w_or_missing(valid_histories),
        "volatility_20d": volatility_20d_or_missing(sector_returns),
        "data_quality_status": "OK",
        "missing_fields": "NONE",
        "source": source,
    }

    missing_fields = [name for name in CORE_INDICATORS + OPTIONAL_INDICATORS if row.get(name) == MISSING]
    if index_missing and row["relative_strength_1m_vs_vnindex"] == MISSING:
        missing_fields.append("vnindex_price_history")
    if 0 < len(sector_index) < 252:
        missing_fields.append(LIMITED_HISTORY)
    stale_count = sum(1 for status in price_statuses.values() if status == STALE_DATA)
    if stale_count:
        missing_fields.append("stale_price_data")

    row["missing_fields"] = "|".join(dict.fromkeys(missing_fields)) if missing_fields else "NONE"
    return row


def build_data_quality_row(
    icb2: str,
    universe_rows: pd.DataFrame,
    price_histories: dict[str, pd.DataFrame],
    price_statuses: dict[str, str],
    price_cache_states: dict[str, str] | None,
    indicator_row: dict[str, Any],
    index_source: str,
    source: str = SOURCE,
) -> dict[str, Any]:
    accepted_count = len(universe_rows)
    valid_price_count = int(indicator_row["valid_price_count"])
    price_cache_states = price_cache_states or {}
    cached_price_count = sum(1 for state in price_cache_states.values() if state == CACHE_STATE_CACHED)
    stale_price_count = sum(1 for status in price_statuses.values() if status == STALE_DATA)
    valid_ma50_count = sum(1 for frame in price_histories.values() if _has_valid_close(frame, min_rows=50))
    valid_ma200_count = sum(1 for frame in price_histories.values() if _has_valid_close(frame, min_rows=200))
    market_caps = _market_caps(universe_rows)
    valid_market_cap_count = int((market_caps > 0).sum())
    market_cap_available_count = valid_market_cap_count
    market_cap_missing_count = max(accepted_count - market_cap_available_count, 0)
    market_cap_coverage_pct = (
        market_cap_available_count / accepted_count if accepted_count else 0.0
    )
    market_cap_source = _combine_unique_values(universe_rows, "market_cap_source")
    market_cap_status = _combine_unique_values(universe_rows, "market_cap_status")
    api_error_count = sum(1 for status in price_statuses.values() if status == API_ERROR)
    api_error_tickers = sorted(ticker for ticker, status in price_statuses.items() if status == API_ERROR)
    missing_price_count = max(accepted_count - valid_price_count, 0)
    missing_indicator_count = count_missing_indicators(indicator_row)
    coverage_status = coverage_status_for(accepted_count, valid_price_count)
    coverage_warning = coverage_warning_for(coverage_status, accepted_count, valid_price_count)
    cap_weight_available = (
        indicator_row["sector_return_1w_cap_weight"] != MISSING
        and indicator_row["sector_return_1m_cap_weight"] != MISSING
    )
    cap_weight_status = CAP_WEIGHT_STATUS_OK if cap_weight_available else CAP_WEIGHT_STATUS_SKIPPED
    cap_weight_reason = cap_weight_reason_for(
        cap_weight_available=cap_weight_available,
        market_cap_available_count=market_cap_available_count,
        accepted_count=accepted_count,
        valid_price_count=valid_price_count,
        market_cap_status=market_cap_status,
    )

    return {
        "as_of": indicator_row["as_of"],
        "icb2": icb2,
        "accepted_ticker_count": accepted_count,
        "valid_price_count": valid_price_count,
        "cached_price_count": cached_price_count,
        "stale_price_count": stale_price_count,
        "valid_ma50_count": valid_ma50_count,
        "valid_ma200_count": valid_ma200_count,
        "valid_market_cap_count": valid_market_cap_count,
        "market_cap_available_count": market_cap_available_count,
        "market_cap_missing_count": market_cap_missing_count,
        "market_cap_coverage_pct": market_cap_coverage_pct,
        "market_cap_source": market_cap_source,
        "market_cap_status": market_cap_status,
        "missing_price_count": missing_price_count,
        "api_error_count": api_error_count,
        "api_error_tickers": "|".join(api_error_tickers) if api_error_tickers else "NONE",
        "missing_indicator_count": missing_indicator_count,
        "coverage_status": coverage_status,
        "coverage_warning": coverage_warning,
        "index_source": index_source,
        "cap_weight_available": "yes" if cap_weight_available else "no",
        "cap_weight_status": cap_weight_status,
        "cap_weight_reason": cap_weight_reason,
        "source": source,
    }


def build_summary_row(
    indicator_row: dict[str, Any],
    quality_row: dict[str, Any],
    index_missing: bool,
    source: str = SOURCE,
) -> dict[str, Any]:
    confidence = compute_confidence_lite(
        accepted_ticker_count=int(quality_row["accepted_ticker_count"]),
        valid_price_count=int(quality_row["valid_price_count"]),
        cap_weight_missing=(
            indicator_row["sector_return_1w_cap_weight"] == MISSING
            or indicator_row["sector_return_1m_cap_weight"] == MISSING
        ),
        core_missing_count=sum(1 for field in CORE_INDICATORS if indicator_row.get(field) == MISSING),
        vnindex_missing=index_missing and indicator_row["relative_strength_1m_vs_vnindex"] == MISSING,
        stale_price_data=_is_positive(quality_row.get("stale_price_count", 0)) or is_stale_as_of(indicator_row["as_of"]),
    )
    return {
        "as_of": indicator_row["as_of"],
        "icb2": indicator_row["icb2"],
        "ticker_count": indicator_row["ticker_count"],
        "main_signal": main_signal(indicator_row, quality_row),
        "supporting_evidence": supporting_evidence(indicator_row),
        "contradicting_evidence": contradicting_evidence(indicator_row, quality_row),
        "data_quality_status": quality_row["coverage_status"],
        "confidence_lite": confidence,
        "source": source,
    }


def calc_return(price: pd.DataFrame, lookback: int) -> float | None:
    price = _normalize_prices(price).dropna(subset=["close"])
    if len(price) <= lookback:
        return None
    latest = float(price.iloc[-1]["close"])
    base = float(price.iloc[-lookback - 1]["close"])
    if base <= 0 or not math.isfinite(base):
        return None
    return latest / base - 1


def ticker_returns(price_histories: dict[str, pd.DataFrame], lookback: int) -> dict[str, float]:
    returns: dict[str, float] = {}
    for ticker, frame in price_histories.items():
        value = calc_return(frame, lookback)
        if value is not None:
            returns[ticker] = value
    return returns


def cap_weighted_return_or_missing(universe_rows: pd.DataFrame, returns: dict[str, float]) -> float | str:
    if not returns:
        return MISSING
    work = universe_rows[universe_rows["ticker"].astype(str).str.upper().isin(returns.keys())].copy()
    if len(work) != len(returns):
        return MISSING
    caps = _market_caps(work)
    if caps.isna().any() or (caps <= 0).any():
        return MISSING
    total = float(caps.sum())
    if total <= 0:
        return MISSING
    weighted_sum = 0.0
    for (_, row), cap in zip(work.iterrows(), caps, strict=True):
        weighted_sum += returns[str(row["ticker"]).upper()] * float(cap)
    return weighted_sum / total


def relative_strength_or_missing(sector_return_1m: float | None, index_return_1m: float | None) -> float | str:
    if sector_return_1m is None or index_return_1m is None:
        return MISSING
    return float(sector_return_1m - index_return_1m)


def breadth_ma_pct(price_histories: dict[str, pd.DataFrame], window: int) -> float | None:
    values: list[bool] = []
    for frame in price_histories.values():
        price = _normalize_prices(frame).dropna(subset=["close"])
        if len(price) < window:
            continue
        latest = float(price.iloc[-1]["close"])
        ma = float(price["close"].tail(window).mean())
        values.append(latest > ma)
    if not values:
        return None
    return sum(values) / len(values)


def breadth_ma_pct_or_missing(price_histories: dict[str, pd.DataFrame], window: int) -> float | str:
    value = breadth_ma_pct(price_histories, window)
    return MISSING if value is None else float(value)


def build_sector_daily_returns(price_histories: dict[str, pd.DataFrame]) -> pd.Series:
    series_by_ticker = []
    for ticker, frame in price_histories.items():
        price = _normalize_prices(frame).dropna(subset=["date", "close"])
        if len(price) < 2:
            continue
        close = price.set_index("date")["close"].astype(float).sort_index()
        daily_return = close.pct_change().dropna()
        daily_return.name = ticker
        series_by_ticker.append(daily_return)
    if not series_by_ticker:
        return pd.Series(dtype="float64")
    combined = pd.concat(series_by_ticker, axis=1).sort_index()
    return combined.mean(axis=1, skipna=True).dropna()


def build_sector_index(sector_daily_returns: pd.Series) -> pd.Series:
    if sector_daily_returns.empty:
        return pd.Series(dtype="float64")
    return (1 + sector_daily_returns.astype(float)).cumprod()


def drawdown_from_52w_high_or_missing(sector_index: pd.Series) -> float | str:
    value = calc_drawdown_from_52w_high(sector_index)
    return MISSING if value is None else value


def calc_drawdown_from_52w_high(sector_index: pd.Series) -> float | None:
    sector_index = sector_index.dropna().astype(float)
    if sector_index.empty:
        return None
    window = sector_index.tail(252)
    high = float(window.max())
    latest = float(window.iloc[-1])
    if high <= 0:
        return None
    return latest / high - 1


def distance_from_52w_low_or_missing(sector_index: pd.Series) -> float | str:
    value = calc_distance_from_52w_low(sector_index)
    return MISSING if value is None else value


def calc_distance_from_52w_low(sector_index: pd.Series) -> float | None:
    sector_index = sector_index.dropna().astype(float)
    if sector_index.empty:
        return None
    window = sector_index.tail(252)
    low = float(window.min())
    latest = float(window.iloc[-1])
    if low <= 0:
        return None
    return latest / low - 1


def volatility_20d_or_missing(sector_daily_returns: pd.Series) -> float | str:
    value = calc_volatility_20d(sector_daily_returns)
    return MISSING if value is None else value


def calc_volatility_20d(sector_daily_returns: pd.Series) -> float | None:
    returns = sector_daily_returns.dropna().astype(float)
    if len(returns) < 20:
        return None
    return float(returns.tail(20).std(ddof=0))


def liquidity_trend_4w_or_missing(price_histories: dict[str, pd.DataFrame]) -> float | str:
    trends = []
    for frame in price_histories.values():
        value = calc_liquidity_trend_4w(frame)
        if value is not None:
            trends.append(value)
    return mean_or_missing(trends)


def calc_liquidity_trend_4w(price: pd.DataFrame) -> float | None:
    price = with_trading_value(price)
    valid = price.dropna(subset=["trading_value"])
    if len(valid) < 40:
        return None
    recent = float(valid.tail(20)["trading_value"].mean())
    previous = float(valid.iloc[-40:-20]["trading_value"].mean())
    if previous <= 0:
        return None
    return recent / previous - 1


def with_trading_value(price: pd.DataFrame) -> pd.DataFrame:
    result = _normalize_prices(price)
    if result.empty:
        result["trading_value"] = pd.Series(dtype="float64")
        return result
    result["trading_value"] = result["value"]
    missing = result["trading_value"].isna()
    proxy_ready = missing & result["close"].notna() & result["volume"].notna()
    result.loc[proxy_ready, "trading_value"] = result.loc[proxy_ready, "close"] * result.loc[proxy_ready, "volume"]
    return result


def compute_confidence_lite(
    accepted_ticker_count: int,
    valid_price_count: int,
    cap_weight_missing: bool,
    core_missing_count: int,
    vnindex_missing: bool,
    stale_price_data: bool,
) -> int:
    score = 100
    price_ratio = valid_price_count / accepted_ticker_count if accepted_ticker_count else 0
    if accepted_ticker_count < 3:
        score -= 30
    elif accepted_ticker_count <= 5:
        score -= 15
    if price_ratio < 0.7:
        score -= 20
    if cap_weight_missing:
        score -= 10
    score -= max(core_missing_count, 0) * 5
    if vnindex_missing:
        score -= 20
    if stale_price_data:
        score -= 15
    return max(0, min(100, int(score)))


def coverage_status_for(accepted_ticker_count: int, valid_price_count: int) -> str:
    price_ratio = valid_price_count / accepted_ticker_count if accepted_ticker_count else 0
    if accepted_ticker_count < 3:
        return "LOW_COVERAGE"
    if price_ratio < 0.7:
        return "DATA_WEAK"
    if accepted_ticker_count <= 5:
        return "WATCH"
    return "OK"


def coverage_warning_for(status: str, accepted_ticker_count: int, valid_price_count: int) -> str:
    if status == "LOW_COVERAGE":
        return "Cảnh báo: ngành này có ít mã hợp lệ, chỉ báo có thể bị méo bởi một vài cổ phiếu lớn."
    if status == "DATA_WEAK":
        return "Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc."
    if status == "WATCH":
        return "Cảnh báo: số mã hợp lệ còn mỏng, nên đọc cùng phần dữ liệu thiếu."
    return f"OK: {valid_price_count}/{accepted_ticker_count} mã có dữ liệu giá hợp lệ."


def count_missing_indicators(indicator_row: dict[str, Any]) -> int:
    return sum(1 for field in CORE_INDICATORS + OPTIONAL_INDICATORS if indicator_row.get(field) == MISSING)


def main_signal(indicator_row: dict[str, Any], quality_row: dict[str, Any]) -> str:
    if quality_row["coverage_status"] in {"LOW_COVERAGE", "DATA_WEAK"}:
        return "Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm."
    one_month = indicator_row["sector_return_1m_equal_weight"]
    relative = indicator_row["relative_strength_1m_vs_vnindex"]
    breadth = indicator_row["breadth_ma50_pct"]
    if one_month == MISSING:
        return "Dữ liệu chưa đủ để kết luận xu hướng ngành."
    if _is_positive(one_month) and _is_positive(relative) and _is_at_least(breadth, 0.5):
        return "Tín hiệu cải thiện khi lợi suất 1 tháng vượt VN-Index và breadth MA50 khá."
    if _is_negative(one_month) and _is_negative(relative):
        return "Tín hiệu suy yếu khi lợi suất 1 tháng kém hơn VN-Index."
    return "Tín hiệu còn pha trộn, ngành đáng theo dõi thêm."


def supporting_evidence(indicator_row: dict[str, Any]) -> str:
    fields = [
        "sector_return_1w_equal_weight",
        "sector_return_1m_equal_weight",
        "relative_strength_1m_vs_vnindex",
        "breadth_ma50_pct",
    ]
    return "; ".join(f"{field}={format_value(indicator_row[field])}" for field in fields)


def contradicting_evidence(indicator_row: dict[str, Any], quality_row: dict[str, Any]) -> str:
    fields = [
        "drawdown_from_52w_high",
        "volatility_20d",
        "liquidity_trend_4w",
    ]
    pieces = [f"{field}={format_value(indicator_row[field])}" for field in fields]
    if indicator_row["missing_fields"] != "NONE":
        pieces.append(f"missing_fields={indicator_row['missing_fields']}")
    if quality_row["coverage_status"] != "OK":
        pieces.append(f"coverage_warning={quality_row['coverage_warning']}")
    return "; ".join(pieces)


def render_weekly_report(
    indicators: pd.DataFrame,
    summary: pd.DataFrame,
    data_quality: pd.DataFrame,
    metadata: dict[str, Any],
) -> str:
    generated_at = metadata.get("generated_at", MISSING)
    as_of = metadata.get("as_of", MISSING)
    universe_count = metadata.get("universe_row_count", 0)
    sector_count = int(indicators["icb2"].nunique()) if not indicators.empty else 0
    quality_warning = general_quality_warning(data_quality, indicators)
    quality_counts = quality_status_counts(data_quality)
    api_error_total = quality_total(data_quality, "api_error_count")
    index_sources = quality_unique_values(data_quality, "index_source")
    cap_weight_available_count = int(
        (data_quality.get("cap_weight_available", pd.Series(dtype=str)).astype(str) == "yes").sum()
    )
    market_cap_available_total = quality_total(data_quality, "market_cap_available_count")
    market_cap_missing_total = quality_total(data_quality, "market_cap_missing_count")
    market_cap_sources = quality_unique_values(data_quality, "market_cap_source")
    cap_weight_statuses = quality_unique_values(data_quality, "cap_weight_status")
    market_cap_min_coverage = quality_min(data_quality, "market_cap_coverage_pct")
    cap_weight_note = (
        "Cap-weight indicators are unavailable because reliable market_cap/share-count data is missing. "
        "The report does not substitute equal-weight data as cap-weight."
        if cap_weight_available_count == 0
        else (
            "Cap-weight indicators are shown only for sectors with complete market_cap coverage for the return window; "
            "sectors without complete coverage remain SKIPPED_MISSING_MARKET_CAP and equal-weight data is not substituted."
        )
    )

    lines = [
        "# Báo cáo tuần Sector Cycle Monitor",
        "",
        f"- Ngày chạy: {generated_at}",
        f"- As of: {as_of}",
        f"- Số mã trong universe: {universe_count}",
        f"- Số ngành ICB2: {sector_count}",
        f"- Cảnh báo dữ liệu chung: {quality_warning}",
        f"- Số ngành OK: {quality_counts.get('OK', 0)}",
        f"- Số ngành DATA_WEAK: {quality_counts.get('DATA_WEAK', 0)}",
        f"- Tổng ticker API_ERROR: {api_error_total}",
        f"- Index source đang dùng: {index_sources}",
        f"- Cap-weight available: {'yes' if cap_weight_available_count else 'no'} ({cap_weight_available_count}/{sector_count} sectors)",
        f"- Cap-weight status: {cap_weight_statuses}",
        f"- Market-cap source: {market_cap_sources}",
        f"- Market-cap available/missing: {market_cap_available_total}/{market_cap_missing_total}",
        f"- Market-cap min sector coverage: {format_value(market_cap_min_coverage)}",
        "- AI-ready outputs: AI_INPUT_SUMMARY.md exists; README_FOR_AI.md exists; sector_cycle_signals.csv exists; sector_driver_map.csv exists.",
        "This report is not a buy/sell recommendation.",
        "",
        "Báo cáo này chỉ tổng hợp chỉ báo cấp ngành. Đây không phải chỉ dẫn giao dịch.",
        "",
        "## Tổng Quan Nhanh",
        "",
        f"- Top ngành return 1w: {sector_extreme(indicators, 'sector_return_1w_equal_weight', largest=True)}",
        f"- Top ngành return 1m: {sector_extreme(indicators, 'sector_return_1m_equal_weight', largest=True)}",
        f"- Ngành relative strength tốt nhất: {sector_extreme(indicators, 'relative_strength_1m_vs_vnindex', largest=True)}",
        f"- Ngành breadth MA50 cao nhất: {sector_extreme(indicators, 'breadth_ma50_pct', largest=True)}",
        f"- Ngành drawdown sâu nhất: {sector_extreme(indicators, 'drawdown_from_52w_high', largest=False)}",
        f"- Ngành coverage yếu nhất: {weakest_coverage(data_quality)}",
        "",
        "## Bảng 19 Ngành",
        "",
        "| ICB2 | Return 1w | Return 1m | Relative strength | Breadth MA50 | Drawdown 52w | Liquidity 4w | confidence_lite | data_quality_status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]

    for _, row in indicators.sort_values("icb2").iterrows():
        summary_row = find_row(summary, "icb2", row["icb2"])
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["icb2"]),
                    format_value(row["sector_return_1w_equal_weight"]),
                    format_value(row["sector_return_1m_equal_weight"]),
                    format_value(row["relative_strength_1m_vs_vnindex"]),
                    format_value(row["breadth_ma50_pct"]),
                    format_value(row["drawdown_from_52w_high"]),
                    format_value(row["liquidity_trend_4w"]),
                    str(summary_row.get("confidence_lite", 0)),
                    str(row["data_quality_status"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Ghi Chú Theo Ngành", ""])
    for _, row in summary.sort_values("icb2").iterrows():
        indicator_row = find_row(indicators, "icb2", row["icb2"])
        quality_row = find_row(data_quality, "icb2", row["icb2"])
        lines.extend(
            [
                f"### {row['icb2']}",
                "",
                f"- Tín hiệu chính: {row['main_signal']}",
                f"- Bằng chứng ủng hộ: {row['supporting_evidence']}",
                f"- Bằng chứng mâu thuẫn: {row['contradicting_evidence']}",
                f"- Dữ liệu thiếu: {indicator_row.get('missing_fields', MISSING)}",
                f"- Cảnh báo coverage: {quality_row.get('coverage_warning', MISSING)}",
                "",
            ]
        )

    lines.extend(
        [
            "## Phụ Lục",
            "",
            "### Data Quality",
            "",
        ]
    )
    for _, row in data_quality.sort_values("icb2").iterrows():
        lines.append(
            f"- {row['icb2']}: {row['coverage_status']}; "
            f"valid_price={row['valid_price_count']}/{row['accepted_ticker_count']}; "
            f"cached_price={row.get('cached_price_count', 0)}; stale_price={row.get('stale_price_count', 0)}; "
            f"api_error={row.get('api_error_count', 0)}; "
            f"valid_ma50={row['valid_ma50_count']}; valid_ma200={row['valid_ma200_count']}; "
            f"market_cap_available={row.get('market_cap_available_count', 0)}; "
            f"market_cap_coverage={format_value(row.get('market_cap_coverage_pct', MISSING))}; "
            f"market_cap_source={row.get('market_cap_source', MISSING)}; "
            f"market_cap_status={row.get('market_cap_status', MISSING)}; "
            f"index_source={row.get('index_source', MISSING)}; "
            f"cap_weight_available={row.get('cap_weight_available', 'no')}; "
            f"cap_weight_status={row.get('cap_weight_status', MISSING)}; "
            f"missing_indicator_count={row['missing_indicator_count']}."
        )

    lines.extend(
        [
            "",
            "### Missing Data",
            "",
            f"- `{MISSING}` nghĩa là nguồn dữ liệu chưa đủ để tính chỉ báo.",
            "- Cap-weight return cần market_cap từ universe; nếu market_cap trống thì chỉ báo cap-weight được để thiếu dữ liệu.",
            f"- {cap_weight_note}",
            "- AI-ready package files: `AI_INPUT_SUMMARY.md`, `README_FOR_AI.md`, `sector_cycle_signals.csv`, and `sector_driver_map.csv`.",
            "- Relative strength dùng `index_source` trong `data_quality.csv`: VNINDEX, VN30, hoặc UNIVERSE_EQUAL_WEIGHT_PROXY khi index thật không lấy được.",
            "- M0 mặc định không bật `--fetch-market-cap`, vì vậy cap-weight không dùng equal-weight thay thế khi market_cap trống.",
            "- Volatility 20d là độ lệch chuẩn 20 phiên của daily sector returns, không annualize.",
            "- Liquidity trend 4w dùng trading value nếu có, nếu thiếu thì dùng proxy close * volume và ghi rõ trong source.",
            "",
            "### Cách Đọc Báo Cáo",
            "",
            "- `confidence_lite` đo độ tin cậy dữ liệu, không đo mức hấp dẫn đầu tư.",
            "- Các tín hiệu ngành nên được đọc cùng coverage warning và missing_fields.",
            "- Báo cáo này không đưa chỉ dẫn giao dịch.",
            "",
        ]
    )
    return "\n".join(lines)


def build_run_metadata(
    universe_path: Path,
    universe: pd.DataFrame,
    as_of: str,
    source: str,
    output_dir: Path,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    metadata = {
        "run_id": f"weekly-mvp-{generated_at}",
        "generated_at": generated_at,
        "as_of": as_of,
        "git_commit_if_available": git_commit(),
        "python_version": platform.python_version(),
        "package_versions": package_versions(["pandas", "pyarrow", "pytest", "tenacity", "pydantic", "vnstock"]),
        "universe_row_count": int(len(universe)),
        "universe_hash": file_hash(universe_path),
        "source": source,
        "output_dir": str(output_dir),
    }
    if extra:
        metadata.update(extra)
    return metadata


def run_quality_metadata(data_quality: pd.DataFrame) -> dict[str, Any]:
    if data_quality.empty:
        return {}
    return {
        "valid_price_total": int(pd.to_numeric(data_quality["valid_price_count"], errors="coerce").fillna(0).sum()),
        "api_error_total": int(pd.to_numeric(data_quality["api_error_count"], errors="coerce").fillna(0).sum()),
        "cached_price_total": int(pd.to_numeric(data_quality["cached_price_count"], errors="coerce").fillna(0).sum()),
        "stale_price_total": int(pd.to_numeric(data_quality["stale_price_count"], errors="coerce").fillna(0).sum()),
        "index_source": ";".join(sorted(data_quality["index_source"].dropna().astype(str).unique())),
        "cap_weight_available_sectors": int((data_quality["cap_weight_available"].astype(str) == "yes").sum()),
        "market_cap_available_total": int(
            pd.to_numeric(data_quality["market_cap_available_count"], errors="coerce").fillna(0).sum()
        ),
        "market_cap_coverage_min": float(
            pd.to_numeric(data_quality["market_cap_coverage_pct"], errors="coerce").fillna(0).min()
        ),
        "cap_weight_status": ";".join(sorted(data_quality["cap_weight_status"].dropna().astype(str).unique())),
    }


def _fetch_ticker_prices(universe: pd.DataFrame, client: Any, progress: bool) -> dict[str, FetchResult]:
    tickers = universe["ticker"].dropna().astype(str).str.upper().drop_duplicates().tolist()
    results: dict[str, FetchResult] = {}
    total = len(tickers)
    for index, ticker in enumerate(tickers, start=1):
        results[ticker] = _fetch_price_history_with_source_fallbacks(client, ticker, months=14)
        if results[ticker].status == API_ERROR:
            _clear_terminal_api_error(client)
        if progress and (index % 25 == 0 or index == total):
            ok_count = sum(1 for item in results.values() if item.ok)
            fetched_count = sum(1 for item in results.values() if price_cache_state(item) == CACHE_STATE_FETCHED)
            cached_count = sum(1 for item in results.values() if price_cache_state(item) == CACHE_STATE_CACHED)
            stale_count = sum(1 for item in results.values() if item.status == STALE_DATA)
            error_count = sum(1 for item in results.values() if item.status == API_ERROR)
            print(
                "weekly price progress: "
                f"{index}/{total}; ok={ok_count}; fetched={fetched_count}; "
                f"cached={cached_count}; stale={stale_count}; api_error={error_count}",
                flush=True,
            )
    return results


def _fetch_market_caps(
    universe: pd.DataFrame,
    client: Any,
    progress: bool,
    market_cap_limit: int,
) -> dict[str, FetchResult]:
    tickers = universe["ticker"].dropna().astype(str).str.upper().drop_duplicates().tolist()
    results: dict[str, FetchResult] = {}
    total = len(tickers)
    live_fetch_count = 0
    for index, ticker in enumerate(tickers, start=1):
        existing_rows = universe[universe["ticker"].astype(str).str.upper() == ticker]
        existing_cap = None
        if not existing_rows.empty:
            existing_cap = _single_positive_number(existing_rows.iloc[0].get("market_cap"))
        if existing_cap is not None:
            results[ticker] = FetchResult(
                True,
                pd.DataFrame([{"market_cap": existing_cap}]),
                source=MARKET_CAP_SOURCE,
                metadata={"cache_state": "EXISTING_UNIVERSE"},
            )
        elif live_fetch_count < market_cap_limit:
            live_fetch_count += 1
            results[ticker] = _as_fetch_result(client.get_market_cap(ticker), source=MARKET_CAP_SOURCE)
        else:
            results[ticker] = FetchResult(
                True,
                pd.DataFrame(),
                status=MARKET_CAP_STATUS_MISSING,
                source=MARKET_CAP_SOURCE,
                metadata={"cache_state": "CONTROLLED_SKIP", "reason": "market_cap_batch_limit"},
            )
        if results[ticker].status == API_ERROR:
            _clear_terminal_api_error(client)
        if progress and (index % 25 == 0 or index == total):
            ok_count = sum(1 for item in results.values() if item.ok)
            fetched_count = sum(1 for item in results.values() if price_cache_state(item) == CACHE_STATE_FETCHED)
            cached_count = sum(1 for item in results.values() if price_cache_state(item) == CACHE_STATE_CACHED)
            stale_count = sum(1 for item in results.values() if item.status == STALE_DATA)
            error_count = sum(1 for item in results.values() if item.status == API_ERROR)
            print(
                "market cap progress: "
                f"{index}/{total}; ok={ok_count}; fetched={fetched_count}; "
                f"cached={cached_count}; stale={stale_count}; api_error={error_count}",
                flush=True,
            )
    return results


def _fetch_index_prices(client: Any) -> FetchResult:
    last_error: FetchResult | None = None
    for symbol in VNINDEX_SYMBOLS:
        result = _fetch_price_history_with_source_fallbacks(client, symbol, months=14, source=f"{SOURCE}_{symbol}")
        if result.ok and not _normalize_prices(result.data).empty:
            metadata = dict(result.metadata or {})
            metadata["index_source"] = symbol
            return FetchResult(
                result.ok,
                result.data,
                status=result.status,
                error=result.error,
                source=f"{SOURCE}_{symbol}",
                as_of=result.as_of,
                metadata=metadata,
            )
        if result.status == API_ERROR:
            _clear_terminal_api_error(client)
        last_error = result
    return last_error or FetchResult(False, pd.DataFrame(), status=API_ERROR, source=SOURCE)


def _fetch_price_history_with_source_fallbacks(
    client: Any,
    ticker: str,
    months: int,
    source: str = SOURCE,
) -> FetchResult:
    result = _as_fetch_result(client.get_price_history(ticker, months=months), source=source)
    if result.ok or not hasattr(client, "quote_source"):
        return result

    primary_quote_source = getattr(client, "quote_source")
    fallback_sources = ["TCBS", "VCI"]
    for quote_source in fallback_sources:
        if quote_source == primary_quote_source:
            continue
        _clear_terminal_api_error(client)
        try:
            setattr(client, "quote_source", quote_source)
            fallback = _as_fetch_result(client.get_price_history(ticker, months=months), source=f"{source}_{quote_source}")
        finally:
            setattr(client, "quote_source", primary_quote_source)
        if fallback.ok:
            metadata = dict(fallback.metadata or {})
            metadata["fallback_quote_source"] = quote_source
            return FetchResult(
                True,
                fallback.data,
                status=fallback.status,
                error=fallback.error,
                source=f"{source}_{quote_source}",
                as_of=fallback.as_of,
                metadata=metadata,
            )
        result = fallback

    return result


def _clear_terminal_api_error(client: Any) -> None:
    if hasattr(client, "_terminal_api_error"):
        try:
            client._terminal_api_error = None
        except Exception:
            pass


def _read_universe(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"universe file not found: {path}")
    return pd.read_csv(path, keep_default_na=False)


def _accepted_universe(universe: pd.DataFrame) -> pd.DataFrame:
    frame = universe.copy()
    if "status" in frame.columns:
        frame = frame[frame["status"].astype(str).str.upper() == "ACCEPTED"].copy()
    for column in ("ticker", "icb2", "market_cap", "market_cap_source", "market_cap_status"):
        if column not in frame.columns:
            frame[column] = ""
    frame["ticker"] = frame["ticker"].astype(str).str.strip().str.upper()
    frame["icb2"] = frame["icb2"].astype(str).str.strip()
    frame["market_cap_source"] = frame["market_cap_source"].replace("", MARKET_CAP_SOURCE_MISSING)
    frame["market_cap_status"] = frame["market_cap_status"].replace("", MARKET_CAP_STATUS_MISSING)
    caps = _market_caps(frame)
    valid_cap = caps > 0
    frame.loc[
        valid_cap & frame["market_cap_source"].isin(["", MARKET_CAP_SOURCE_MISSING]),
        "market_cap_source",
    ] = MARKET_CAP_SOURCE_REPORTED
    frame.loc[
        valid_cap & frame["market_cap_status"].isin(["", MARKET_CAP_STATUS_MISSING]),
        "market_cap_status",
    ] = MARKET_CAP_STATUS_OK
    return frame[frame["ticker"] != ""].reset_index(drop=True)


def _normalize_prices(data: Any) -> pd.DataFrame:
    if isinstance(data, FetchResult):
        return _normalize_prices(data.data)
    if isinstance(data, pd.DataFrame):
        frame = data.copy()
    elif data is None:
        frame = pd.DataFrame()
    else:
        frame = pd.DataFrame(data)
    if frame.empty:
        return pd.DataFrame(columns=["date", "close", "volume", "value"])

    date_col = first_existing(frame, ["date", "time", "trading_date", "tradingDate", "datetime"])
    close_col = first_existing(frame, ["close", "close_price", "closePrice", "adj_close", "match_price"])
    volume_col = first_existing(frame, ["volume", "trading_volume", "tradingVolume", "total_volume", "nmVolume"])
    value_col = first_existing(
        frame,
        ["value", "trading_value", "tradingValue", "total_value", "totalTradingValue", "nmValue"],
    )

    result = pd.DataFrame()
    result["date"] = pd.to_datetime(frame[date_col], errors="coerce") if date_col else pd.NaT
    result["close"] = numeric(frame[close_col]) if close_col else pd.NA
    result["volume"] = numeric(frame[volume_col]) if volume_col else pd.NA
    result["value"] = numeric(frame[value_col]) if value_col else pd.NA
    return result.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)


def _as_fetch_result(value: Any, source: str) -> FetchResult:
    if isinstance(value, FetchResult):
        return value
    if value is None:
        return FetchResult(False, pd.DataFrame(), status=API_ERROR, source=source)
    return FetchResult(True, value, source=source)


def _has_valid_close(price: pd.DataFrame, min_rows: int) -> bool:
    return len(_normalize_prices(price).dropna(subset=["close"])) >= min_rows


def _market_caps(universe_rows: pd.DataFrame) -> pd.Series:
    if "market_cap" not in universe_rows.columns:
        return pd.Series([pd.NA] * len(universe_rows), index=universe_rows.index)
    return numeric(universe_rows["market_cap"])


def _single_positive_number(value: Any) -> float | None:
    if isinstance(value, pd.Series):
        values = numeric(value).dropna()
    else:
        values = numeric(pd.Series([value])).dropna()
    if values.empty:
        return None
    number = float(values.iloc[-1])
    return number if math.isfinite(number) and number > 0 else None


def _combine_unique_values(frame: pd.DataFrame, column: str) -> str:
    if column not in frame:
        return MARKET_CAP_SOURCE_MISSING
    values = []
    for value in frame[column].dropna().astype(str):
        text = value.strip()
        if text and text not in values:
            values.append(text)
    return "|".join(values) if values else MARKET_CAP_SOURCE_MISSING


def cap_weight_reason_for(
    cap_weight_available: bool,
    market_cap_available_count: int,
    accepted_count: int,
    valid_price_count: int,
    market_cap_status: str,
) -> str:
    if cap_weight_available:
        return "OK: cap-weight uses market_cap for every ticker included in the sector return window."
    if market_cap_available_count <= 0:
        return (
            "SKIPPED_MISSING_MARKET_CAP: reliable market_cap/share-count data is missing; "
            "equal-weight data is not substituted as cap-weight."
        )
    return (
        "SKIPPED_MISSING_MARKET_CAP: market_cap coverage "
        f"{market_cap_available_count}/{accepted_count} is not complete for cap-weight returns "
        f"with {valid_price_count} valid price series; market_cap_status={market_cap_status}; "
        "equal-weight data is not substituted as cap-weight."
    )


def latest_price_date(histories: dict[str, pd.DataFrame]) -> str | None:
    dates = []
    for frame in histories.values():
        price = _normalize_prices(frame)
        if not price.empty:
            dates.append(price["date"].max())
    if not dates:
        return None
    return max(dates).date().isoformat()


def _latest_as_of(indicators: pd.DataFrame, fallback: str) -> str:
    if indicators.empty or "as_of" not in indicators:
        return fallback
    if "valid_price_count" in indicators.columns:
        indicators = indicators[pd.to_numeric(indicators["valid_price_count"], errors="coerce").fillna(0) > 0]
    dates = pd.to_datetime(indicators["as_of"], errors="coerce").dropna()
    return dates.max().date().isoformat() if not dates.empty else fallback


def mean_or_none(values: list[float]) -> float | None:
    clean = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    if not clean:
        return None
    return float(sum(clean) / len(clean))


def mean_or_missing(values: list[float]) -> float | str:
    value = mean_or_none(values)
    return MISSING if value is None else value


def is_stale_as_of(as_of: Any, max_days: int = 5) -> bool:
    parsed = pd.to_datetime(as_of, errors="coerce")
    if pd.isna(parsed):
        return True
    return (pd.Timestamp(date.today()) - parsed.normalize()) > pd.Timedelta(days=max_days)


def sector_extreme(indicators: pd.DataFrame, column: str, largest: bool) -> str:
    if indicators.empty or column not in indicators.columns:
        return MISSING
    numeric_values = pd.to_numeric(indicators[column], errors="coerce")
    if numeric_values.dropna().empty:
        return MISSING
    idx = numeric_values.idxmax() if largest else numeric_values.idxmin()
    return f"{indicators.loc[idx, 'icb2']} ({format_value(numeric_values.loc[idx])})"


def weakest_coverage(data_quality: pd.DataFrame) -> str:
    if data_quality.empty:
        return MISSING
    priority = {"LOW_COVERAGE": 0, "DATA_WEAK": 1, "WATCH": 2, "OK": 3}
    ranked = data_quality.copy()
    ranked["_priority"] = ranked["coverage_status"].map(priority).fillna(9)
    ranked = ranked.sort_values(["_priority", "valid_price_count", "accepted_ticker_count"])
    row = ranked.iloc[0]
    return f"{row['icb2']} ({row['coverage_status']})"


def general_quality_warning(data_quality: pd.DataFrame, indicators: pd.DataFrame) -> str:
    if data_quality.empty:
        return MISSING
    counts = data_quality["coverage_status"].value_counts().to_dict()
    missing_cap = int(
        (indicators["sector_return_1w_cap_weight"] == MISSING).sum()
        if "sector_return_1w_cap_weight" in indicators
        else 0
    )
    parts = [f"{status}={count}" for status, count in sorted(counts.items())]
    if missing_cap:
        parts.append(f"cap_weight_missing={missing_cap}")
    api_errors = quality_total(data_quality, "api_error_count")
    if api_errors:
        parts.append(f"api_error={api_errors}")
    if "index_source" in data_quality:
        parts.append(f"index_source={quality_unique_values(data_quality, 'index_source')}")
    return "; ".join(parts)


def quality_status_counts(data_quality: pd.DataFrame) -> dict[str, int]:
    if data_quality.empty or "coverage_status" not in data_quality:
        return {}
    return {str(key): int(value) for key, value in data_quality["coverage_status"].value_counts().to_dict().items()}


def quality_total(data_quality: pd.DataFrame, column: str) -> int:
    if data_quality.empty or column not in data_quality:
        return 0
    return int(pd.to_numeric(data_quality[column], errors="coerce").fillna(0).sum())


def quality_min(data_quality: pd.DataFrame, column: str) -> float | str:
    if data_quality.empty or column not in data_quality:
        return MISSING
    values = pd.to_numeric(data_quality[column], errors="coerce").dropna()
    if values.empty:
        return MISSING
    return float(values.min())


def quality_unique_values(data_quality: pd.DataFrame, column: str) -> str:
    if data_quality.empty or column not in data_quality:
        return MISSING
    values = sorted(value for value in data_quality[column].dropna().astype(str).unique() if value)
    return "|".join(values) if values else MISSING


def find_row(frame: pd.DataFrame, column: str, value: Any) -> dict[str, Any]:
    if frame.empty or column not in frame.columns:
        return {}
    match = frame[frame[column] == value]
    return match.iloc[0].to_dict() if not match.empty else {}


def format_value(value: Any) -> str:
    if value == MISSING or value is None:
        return MISSING
    try:
        if pd.isna(value):
            return MISSING
    except TypeError:
        pass
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return f"{float(value):.4f}"
    return str(value)


def first_existing(frame: pd.DataFrame, candidates: list[str]) -> str | None:
    exact = {str(column): str(column) for column in frame.columns}
    lower = {str(column).lower(): str(column) for column in frame.columns}
    for candidate in candidates:
        if candidate in exact:
            return exact[candidate]
        if candidate.lower() in lower:
            return lower[candidate.lower()]
    return None


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False).replace("", pd.NA), errors="coerce")


def package_versions(packages: list[str]) -> dict[str, str]:
    versions = {}
    for package in packages:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "not installed"
    return versions


def file_hash(path: Path) -> str:
    if not path.exists():
        return MISSING
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return MISSING
    return result.stdout.strip() or MISSING


def _combine_sources(*sources: Any) -> str:
    cleaned: list[str] = []
    for source in sources:
        text = str(source).strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return "+".join(cleaned) if cleaned else SOURCE


def _is_positive(value: Any) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def _is_negative(value: Any) -> bool:
    try:
        return float(value) < 0
    except (TypeError, ValueError):
        return False


def _is_at_least(value: Any, threshold: float) -> bool:
    try:
        return float(value) >= threshold
    except (TypeError, ValueError):
        return False


def _assert_report_is_safe(report_text: str) -> None:
    lower = report_text.lower()
    found = [phrase for phrase in BANNED_REPORT_PHRASES if phrase in lower]
    if found:
        raise ValueError(f"report contains banned wording: {found}")
