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


MISSING = "N/A (MISSING_DATA)"
SOURCE = "vnstock+tier1_market_data"
VNINDEX_SYMBOL = "VNINDEX"

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
    "ticker_count",
    "valid_price_count",
    "missing_price_count",
    "missing_price_pct",
    "missing_fields",
    "data_quality_status",
    "source",
]


@dataclass(frozen=True)
class WeeklyMvpResult:
    output_dir: Path
    indicators: pd.DataFrame
    summary: pd.DataFrame
    data_quality: pd.DataFrame
    metadata: dict[str, Any]


def run_weekly_mvp(
    universe_path: str | Path = "data/universe.csv",
    reports_root: str | Path = "reports",
    client: Any | None = None,
) -> WeeklyMvpResult:
    universe_path = Path(universe_path)
    reports_root = Path(reports_root)
    client = client or VnstockClient()
    universe = _read_universe(universe_path)

    price_results: dict[str, FetchResult] = {}
    for ticker in universe["ticker"].dropna().astype(str).unique():
        price_results[ticker] = _as_fetch_result(client.get_price_history(ticker, months=14), source=SOURCE)

    if universe.empty:
        index_result = FetchResult(False, pd.DataFrame(), status="MISSING_DATA", source=SOURCE)
    else:
        index_result = _as_fetch_result(client.get_price_history(VNINDEX_SYMBOL, months=14), source=SOURCE)
    outputs = build_weekly_outputs(universe, price_results, index_result)

    report_date = date.today().isoformat()
    output_dir = reports_root / report_date
    output_dir.mkdir(parents=True, exist_ok=True)

    indicators = outputs["indicators"]
    summary = outputs["summary"]
    data_quality = outputs["data_quality"]
    as_of = _latest_as_of(indicators, fallback=report_date)

    metadata = build_run_metadata(
        universe_path=universe_path,
        universe=universe,
        as_of=as_of,
        source=SOURCE,
    )

    indicators.to_csv(output_dir / "sector_indicators_tier1.csv", index=False)
    summary.to_csv(output_dir / "sector_summary.csv", index=False)
    data_quality.to_csv(output_dir / "data_quality.csv", index=False)
    (output_dir / "run_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "WEEKLY_REPORT.md").write_text(
        render_weekly_report(
            indicators=indicators,
            summary=summary,
            data_quality=data_quality,
            metadata=metadata,
        ),
        encoding="utf-8",
    )

    return WeeklyMvpResult(output_dir=output_dir, indicators=indicators, summary=summary, data_quality=data_quality, metadata=metadata)


def build_weekly_outputs(
    universe: pd.DataFrame,
    price_results: dict[str, Any],
    index_result: Any | None = None,
    source: str = SOURCE,
) -> dict[str, pd.DataFrame]:
    universe = _accepted_universe(universe)
    index_prices = _normalize_prices(_as_fetch_result(index_result, source=source).data) if index_result is not None else pd.DataFrame()
    index_return_1m = calc_return(index_prices, 21)

    indicator_rows: list[dict[str, Any]] = []
    quality_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    if universe.empty:
        empty_indicators = pd.DataFrame(columns=INDICATOR_COLUMNS)
        today = date.today().isoformat()
        empty_summary = pd.DataFrame(
            [
                {
                    "as_of": today,
                    "icb2": MISSING,
                    "ticker_count": 0,
                    "main_signal": "Data is not sufficient to describe a sector signal.",
                    "supporting_evidence": MISSING,
                    "contradicting_evidence": MISSING,
                    "data_quality_status": "MISSING_DATA",
                    "confidence_lite": 0,
                    "source": source,
                }
            ],
            columns=SUMMARY_COLUMNS,
        )
        empty_quality = pd.DataFrame(
            [
                {
                    "as_of": today,
                    "icb2": MISSING,
                    "ticker_count": 0,
                    "valid_price_count": 0,
                    "missing_price_count": 0,
                    "missing_price_pct": 1,
                    "missing_fields": "universe_accepted_rows",
                    "data_quality_status": "MISSING_DATA",
                    "source": source,
                }
            ],
            columns=QUALITY_COLUMNS,
        )
        return {"indicators": empty_indicators, "summary": empty_summary, "data_quality": empty_quality}

    for icb2, group in universe.groupby("icb2", dropna=False):
        sector = str(icb2).strip() or MISSING
        histories: dict[str, pd.DataFrame] = {}
        price_statuses: dict[str, str] = {}
        for _, row in group.iterrows():
            ticker = str(row["ticker"])
            result = _as_fetch_result(price_results.get(ticker), source=source)
            histories[ticker] = _normalize_prices(result.data)
            price_statuses[ticker] = result.status

        indicator_row = calculate_sector_indicators(
            icb2=sector,
            universe_rows=group,
            price_histories=histories,
            index_return_1m=index_return_1m,
            price_statuses=price_statuses,
            source=source,
        )
        quality_row = _quality_row(sector, group, histories, indicator_row, source)
        summary_row = _summary_row(indicator_row, quality_row, source)

        indicator_rows.append(indicator_row)
        quality_rows.append(quality_row)
        summary_rows.append(summary_row)

    return {
        "indicators": pd.DataFrame(indicator_rows, columns=INDICATOR_COLUMNS),
        "summary": pd.DataFrame(summary_rows, columns=SUMMARY_COLUMNS),
        "data_quality": pd.DataFrame(quality_rows, columns=QUALITY_COLUMNS),
    }


def calculate_sector_indicators(
    icb2: str,
    universe_rows: pd.DataFrame,
    price_histories: dict[str, pd.DataFrame],
    index_return_1m: float | None = None,
    price_statuses: dict[str, str] | None = None,
    source: str = SOURCE,
) -> dict[str, Any]:
    price_statuses = price_statuses or {}
    ticker_count = len(universe_rows)
    valid_histories = {ticker: frame for ticker, frame in price_histories.items() if not _normalize_prices(frame).empty}
    valid_price_count = len(valid_histories)
    as_of = _max_price_date(valid_histories) or date.today().isoformat()

    returns_1w = _ticker_returns(valid_histories, 5)
    returns_1m = _ticker_returns(valid_histories, 21)
    returns_3m = _ticker_returns(valid_histories, 63)

    row: dict[str, Any] = {
        "as_of": as_of,
        "icb2": icb2,
        "ticker_count": ticker_count,
        "valid_price_count": valid_price_count,
        "sector_return_1w_equal_weight": _mean_or_missing(returns_1w),
        "sector_return_1m_equal_weight": _mean_or_missing(returns_1m),
        "sector_return_3m_equal_weight": _mean_or_missing(returns_3m),
        "sector_return_1w_cap_weight": _cap_weighted_or_missing(universe_rows, returns_1w),
        "sector_return_1m_cap_weight": _cap_weighted_or_missing(universe_rows, returns_1m),
        "relative_strength_1m_vs_vnindex": _relative_strength(_mean_or_none(returns_1m), index_return_1m),
        "breadth_ma50_pct": _breadth_ma_pct(valid_histories, 50),
        "breadth_ma200_pct": _breadth_ma_pct(valid_histories, 200),
        "drawdown_from_52w_high": _mean_or_missing(_drawdowns_52w(valid_histories)),
        "distance_from_52w_low": _mean_or_missing(_distances_52w_low(valid_histories)),
        "liquidity_trend_4w": _mean_or_missing(_liquidity_trends_4w(valid_histories)),
        "volatility_20d": _mean_or_missing(_volatilities_20d(valid_histories)),
        "data_quality_status": "OK",
        "missing_fields": "NONE",
        "source": source,
    }

    missing_fields = [column for column in INDICATOR_COLUMNS if column not in {"missing_fields", "source", "data_quality_status"} and row.get(column) == MISSING]
    stale_count = sum(1 for status in price_statuses.values() if status == "STALE_DATA")
    if stale_count:
        missing_fields.append("stale_price_data")

    row["missing_fields"] = "|".join(missing_fields) if missing_fields else "NONE"
    row["data_quality_status"] = _data_quality_status(ticker_count, valid_price_count, missing_fields, stale_count)
    return row


def calc_return(price: pd.DataFrame, lookback: int) -> float | None:
    price = _normalize_prices(price)
    price = price.dropna(subset=["close"])
    if len(price) <= lookback:
        return None
    latest = float(price.iloc[-1]["close"])
    base = float(price.iloc[-lookback - 1]["close"])
    if base <= 0:
        return None
    return latest / base - 1


def calc_volatility_20d(price: pd.DataFrame) -> float | None:
    price = _normalize_prices(price).dropna(subset=["close"])
    returns = price["close"].pct_change().dropna()
    if len(returns) < 20:
        return None
    return float(returns.tail(20).std(ddof=0))


def calc_drawdown_52w(price: pd.DataFrame) -> float | None:
    price = _normalize_prices(price).dropna(subset=["close"])
    if len(price) < 252:
        return None
    recent = price.tail(252)
    high = float(recent["close"].max())
    latest = float(recent.iloc[-1]["close"])
    if high <= 0:
        return None
    return latest / high - 1


def calc_distance_52w_low(price: pd.DataFrame) -> float | None:
    price = _normalize_prices(price).dropna(subset=["close"])
    if len(price) < 252:
        return None
    recent = price.tail(252)
    low = float(recent["close"].min())
    latest = float(recent.iloc[-1]["close"])
    if low <= 0:
        return None
    return latest / low - 1


def calc_breadth_ma_pct(price_histories: dict[str, pd.DataFrame], window: int) -> float | None:
    values: list[bool] = []
    for frame in price_histories.values():
        price = _normalize_prices(frame).dropna(subset=["close"])
        if len(price) < window:
            continue
        ma = float(price["close"].tail(window).mean())
        latest = float(price.iloc[-1]["close"])
        values.append(latest > ma)
    if not values:
        return None
    return sum(values) / len(values)


def compute_confidence_lite(
    ticker_count: int,
    valid_price_count: int,
    missing_market_cap: bool,
    stale_price_data: bool,
    missing_indicator_count: int,
) -> int:
    score = 100
    missing_price_count = max(ticker_count - valid_price_count, 0)
    missing_price_pct = missing_price_count / ticker_count if ticker_count else 1

    if missing_price_pct > 0.30:
        score -= 30
    elif missing_price_pct >= 0.10:
        score -= 15
    elif missing_price_pct > 0:
        score -= 5

    if missing_market_cap:
        score -= 10
    if stale_price_data:
        score -= 20
    score -= max(missing_indicator_count, 0) * 5
    return max(0, min(100, int(score)))


def render_weekly_report(
    indicators: pd.DataFrame,
    summary: pd.DataFrame,
    data_quality: pd.DataFrame,
    metadata: dict[str, Any],
) -> str:
    generated_at = metadata.get("generated_at", MISSING)
    as_of = metadata.get("as_of", MISSING)
    universe_count = metadata.get("universe_row_count", 0)
    icb2_count = len(indicators) if not indicators.empty else 0
    warnings = _report_warnings(indicators, data_quality)

    lines = [
        "# Weekly Sector MVP Report",
        "",
        f"- Generated at: {generated_at}",
        f"- As of: {as_of}",
        f"- Universe rows: {universe_count}",
        f"- ICB2 sectors: {icb2_count}",
        f"- Data warnings: {warnings}",
        "",
        "## Overview",
        "",
        f"- Top 1w return: {_top_sector(indicators, 'sector_return_1w_equal_weight')}",
        f"- Top 1m return: {_top_sector(indicators, 'sector_return_1m_equal_weight')}",
        f"- Best 1m relative strength: {_top_sector(indicators, 'relative_strength_1m_vs_vnindex')}",
        f"- Strongest MA50 breadth: {_top_sector(indicators, 'breadth_ma50_pct')}",
        f"- Deepest 52w drawdown: {_bottom_sector(indicators, 'drawdown_from_52w_high')}",
        "",
        "## Sector Table",
        "",
        "| ICB2 | 1w return | 1m return | relative strength | MA50 breadth | 52w drawdown | liquidity 4w | confidence_lite | data quality |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    if indicators.empty:
        lines.append("| N/A | N/A (MISSING_DATA) | N/A (MISSING_DATA) | N/A (MISSING_DATA) | N/A (MISSING_DATA) | N/A (MISSING_DATA) | N/A (MISSING_DATA) | 0 | MISSING_DATA |")
    else:
        for _, row in indicators.iterrows():
            summary_row = _find_summary(summary, row["icb2"])
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(row["icb2"]),
                        _fmt_value(row["sector_return_1w_equal_weight"]),
                        _fmt_value(row["sector_return_1m_equal_weight"]),
                        _fmt_value(row["relative_strength_1m_vs_vnindex"]),
                        _fmt_value(row["breadth_ma50_pct"]),
                        _fmt_value(row["drawdown_from_52w_high"]),
                        _fmt_value(row["liquidity_trend_4w"]),
                        str(summary_row.get("confidence_lite", 0)),
                        str(row["data_quality_status"]),
                    ]
                )
                + " |"
            )

    lines.extend(["", "## Sector Notes", ""])
    if summary.empty:
        lines.extend(
            [
                "### N/A",
                "",
                "- Main signal: Data is not sufficient for sector notes.",
                "- Supporting evidence: N/A (MISSING_DATA)",
                "- Contradicting evidence: N/A (MISSING_DATA)",
                "- Missing data: Universe has no accepted sector rows.",
                "- Trading conclusion: Not provided.",
                "",
            ]
        )
    else:
        for _, row in summary.iterrows():
            indicator_row = _find_indicator(indicators, row["icb2"])
            lines.extend(
                [
                    f"### {row['icb2']}",
                    "",
                    f"- Main signal: {row['main_signal']}",
                    f"- Supporting evidence: {row['supporting_evidence']}",
                    f"- Contradicting evidence: {row['contradicting_evidence']}",
                    f"- Missing data: {indicator_row.get('missing_fields', MISSING)}",
                    "- Trading conclusion: Not provided.",
                    "",
                ]
            )

    lines.extend(
        [
            "## Appendix",
            "",
            "### Data Quality",
            "",
        ]
    )
    if data_quality.empty:
        lines.append("- N/A (MISSING_DATA)")
    else:
        for _, row in data_quality.iterrows():
            lines.append(
                f"- {row['icb2']}: {row['data_quality_status']}; missing fields: {row['missing_fields']}; valid prices: {row['valid_price_count']}/{row['ticker_count']}."
            )

    lines.extend(
        [
            "",
            "### How To Read",
            "",
            "- This MVP uses market data only.",
            "- `confidence_lite` measures data completeness, not investment merit.",
            "- `N/A (MISSING_DATA)` means the source did not provide enough usable data.",
            "- The report intentionally avoids transaction advice and specific price objectives.",
            "",
        ]
    )
    return "\n".join(lines)


def build_run_metadata(universe_path: Path, universe: pd.DataFrame, as_of: str, source: str) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    return {
        "run_id": f"weekly-mvp-{generated_at}",
        "generated_at": generated_at,
        "as_of": as_of,
        "git_commit_if_available": _git_commit(),
        "python_version": platform.python_version(),
        "package_versions": _package_versions(["pandas", "pyarrow", "pytest", "tenacity", "pydantic", "vnstock"]),
        "universe_row_count": int(len(universe)),
        "universe_hash": _file_hash(universe_path),
        "source": source,
    }


def _read_universe(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["ticker", "icb2", "market_cap", "status"])
    return pd.read_csv(path, keep_default_na=False)


def _accepted_universe(universe: pd.DataFrame) -> pd.DataFrame:
    if universe.empty:
        return pd.DataFrame(columns=["ticker", "icb2", "market_cap", "status"])
    frame = universe.copy()
    if "status" in frame.columns:
        frame = frame[frame["status"].astype(str).str.upper() == "ACCEPTED"]
    for column in ("ticker", "icb2", "market_cap"):
        if column not in frame.columns:
            frame[column] = ""
    return frame


def _normalize_prices(data: Any) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        frame = data.copy()
    elif isinstance(data, FetchResult):
        frame = _normalize_prices(data.data)
    elif data is None:
        frame = pd.DataFrame()
    else:
        frame = pd.DataFrame(data)
    if frame.empty:
        return pd.DataFrame(columns=["date", "close", "volume", "value"])

    date_col = _first_existing(frame, ["date", "time", "trading_date", "tradingDate", "datetime"])
    close_col = _first_existing(frame, ["close", "close_price", "closePrice", "adj_close", "match_price"])
    volume_col = _first_existing(frame, ["volume", "trading_volume", "tradingVolume", "total_volume", "nmVolume"])
    value_col = _first_existing(frame, ["value", "trading_value", "tradingValue", "total_value", "totalTradingValue", "nmValue"])

    result = pd.DataFrame()
    result["date"] = pd.to_datetime(frame[date_col], errors="coerce") if date_col else pd.NaT
    result["close"] = _numeric(frame[close_col]) if close_col else pd.NA
    result["volume"] = _numeric(frame[volume_col]) if volume_col else pd.NA
    result["value"] = _numeric(frame[value_col]) if value_col else pd.NA
    return result.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)


def _ticker_returns(price_histories: dict[str, pd.DataFrame], lookback: int) -> dict[str, float]:
    values: dict[str, float] = {}
    for ticker, frame in price_histories.items():
        value = calc_return(frame, lookback)
        if value is not None:
            values[ticker] = value
    return values


def _mean_or_none(values: dict[str, float] | list[float]) -> float | None:
    data = list(values.values()) if isinstance(values, dict) else list(values)
    if not data:
        return None
    return float(sum(data) / len(data))


def _mean_or_missing(values: dict[str, float] | list[float]) -> float | str:
    value = _mean_or_none(values)
    return MISSING if value is None else value


def _cap_weighted_or_missing(universe_rows: pd.DataFrame, returns: dict[str, float]) -> float | str:
    if not returns:
        return MISSING
    frame = universe_rows[universe_rows["ticker"].astype(str).isin(returns.keys())].copy()
    frame["market_cap"] = _numeric(frame["market_cap"])
    if frame["market_cap"].isna().any() or (frame["market_cap"] <= 0).any() or len(frame) != len(returns):
        return MISSING
    total = float(frame["market_cap"].sum())
    if total <= 0:
        return MISSING
    return float(sum(returns[str(row["ticker"])] * float(row["market_cap"]) for _, row in frame.iterrows()) / total)


def _relative_strength(sector_return_1m: float | None, index_return_1m: float | None) -> float | str:
    if sector_return_1m is None or index_return_1m is None:
        return MISSING
    return float(sector_return_1m - index_return_1m)


def _breadth_ma_pct(price_histories: dict[str, pd.DataFrame], window: int) -> float | str:
    value = calc_breadth_ma_pct(price_histories, window)
    return MISSING if value is None else float(value)


def _drawdowns_52w(price_histories: dict[str, pd.DataFrame]) -> list[float]:
    return [value for value in (calc_drawdown_52w(frame) for frame in price_histories.values()) if value is not None]


def _distances_52w_low(price_histories: dict[str, pd.DataFrame]) -> list[float]:
    return [value for value in (calc_distance_52w_low(frame) for frame in price_histories.values()) if value is not None]


def _liquidity_trends_4w(price_histories: dict[str, pd.DataFrame]) -> list[float]:
    values: list[float] = []
    for frame in price_histories.values():
        price = _with_trading_value(frame)
        valid = price.dropna(subset=["trading_value"])
        if len(valid) < 40:
            continue
        latest = float(valid.tail(20)["trading_value"].mean())
        previous = float(valid.iloc[-40:-20]["trading_value"].mean())
        if previous > 0:
            values.append(latest / previous - 1)
    return values


def _volatilities_20d(price_histories: dict[str, pd.DataFrame]) -> list[float]:
    return [value for value in (calc_volatility_20d(frame) for frame in price_histories.values()) if value is not None]


def _with_trading_value(price: pd.DataFrame) -> pd.DataFrame:
    result = _normalize_prices(price)
    if result.empty:
        return result.assign(trading_value=pd.Series(dtype="float64"))
    result["trading_value"] = result["value"]
    missing = result["trading_value"].isna()
    proxy_ready = missing & result["close"].notna() & result["volume"].notna()
    result.loc[proxy_ready, "trading_value"] = result.loc[proxy_ready, "close"] * result.loc[proxy_ready, "volume"]
    return result


def _quality_row(icb2: str, group: pd.DataFrame, histories: dict[str, pd.DataFrame], indicator_row: dict[str, Any], source: str) -> dict[str, Any]:
    ticker_count = len(group)
    valid_price_count = int(indicator_row["valid_price_count"])
    missing_price_count = max(ticker_count - valid_price_count, 0)
    missing_price_pct = missing_price_count / ticker_count if ticker_count else 1
    return {
        "as_of": indicator_row["as_of"],
        "icb2": icb2,
        "ticker_count": ticker_count,
        "valid_price_count": valid_price_count,
        "missing_price_count": missing_price_count,
        "missing_price_pct": missing_price_pct,
        "missing_fields": indicator_row["missing_fields"],
        "data_quality_status": indicator_row["data_quality_status"],
        "source": source,
    }


def _summary_row(indicator_row: dict[str, Any], quality_row: dict[str, Any], source: str) -> dict[str, Any]:
    missing_fields = [] if indicator_row["missing_fields"] == "NONE" else str(indicator_row["missing_fields"]).split("|")
    confidence = compute_confidence_lite(
        ticker_count=int(indicator_row["ticker_count"]),
        valid_price_count=int(indicator_row["valid_price_count"]),
        missing_market_cap=(
            indicator_row["sector_return_1w_cap_weight"] == MISSING
            or indicator_row["sector_return_1m_cap_weight"] == MISSING
        ),
        stale_price_data="stale_price_data" in missing_fields,
        missing_indicator_count=sum(1 for field in missing_fields if field != "stale_price_data"),
    )

    return {
        "as_of": indicator_row["as_of"],
        "icb2": indicator_row["icb2"],
        "ticker_count": indicator_row["ticker_count"],
        "main_signal": _main_signal(indicator_row),
        "supporting_evidence": _supporting_evidence(indicator_row),
        "contradicting_evidence": _contradicting_evidence(indicator_row),
        "data_quality_status": quality_row["data_quality_status"],
        "confidence_lite": confidence,
        "source": source,
    }


def _main_signal(row: dict[str, Any]) -> str:
    one_month = row["sector_return_1m_equal_weight"]
    breadth = row["breadth_ma50_pct"]
    if one_month == MISSING:
        return "Data is not sufficient to describe a sector signal."
    if isinstance(one_month, float) and one_month > 0 and breadth != MISSING and float(breadth) >= 0.5:
        return "Sector is worth monitoring because 1m return and MA50 breadth are positive."
    if isinstance(one_month, float) and one_month < 0:
        return "Recovery signal is still weak because 1m return is negative."
    return "Sector is worth monitoring further; market evidence is mixed."


def _supporting_evidence(row: dict[str, Any]) -> str:
    parts = []
    for field in ("sector_return_1w_equal_weight", "sector_return_1m_equal_weight", "breadth_ma50_pct"):
        parts.append(f"{field}={_fmt_value(row[field])}")
    return "; ".join(parts)


def _contradicting_evidence(row: dict[str, Any]) -> str:
    parts = []
    for field in ("drawdown_from_52w_high", "volatility_20d", "missing_fields"):
        parts.append(f"{field}={_fmt_value(row[field])}")
    return "; ".join(parts)


def _data_quality_status(ticker_count: int, valid_price_count: int, missing_fields: list[str], stale_count: int) -> str:
    if ticker_count == 0 or valid_price_count == 0:
        return "MISSING_DATA"
    if stale_count or missing_fields or valid_price_count < ticker_count:
        return "PARTIAL_DATA"
    return "OK"


def _max_price_date(histories: dict[str, pd.DataFrame]) -> str | None:
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
    dates = pd.to_datetime(indicators["as_of"], errors="coerce").dropna()
    return dates.max().date().isoformat() if not dates.empty else fallback


def _report_warnings(indicators: pd.DataFrame, data_quality: pd.DataFrame) -> str:
    if indicators.empty:
        return "No accepted universe rows; all sector indicators are unavailable."
    statuses = sorted(set(data_quality["data_quality_status"].astype(str)))
    if statuses == ["OK"]:
        return "None"
    return "Data quality issues: " + ", ".join(statuses)


def _top_sector(indicators: pd.DataFrame, column: str) -> str:
    row = _sector_extreme(indicators, column, largest=True)
    return row


def _bottom_sector(indicators: pd.DataFrame, column: str) -> str:
    row = _sector_extreme(indicators, column, largest=False)
    return row


def _sector_extreme(indicators: pd.DataFrame, column: str, largest: bool) -> str:
    if indicators.empty or column not in indicators:
        return MISSING
    numeric = pd.to_numeric(indicators[column], errors="coerce")
    if numeric.dropna().empty:
        return MISSING
    idx = numeric.idxmax() if largest else numeric.idxmin()
    return f"{indicators.loc[idx, 'icb2']} ({_fmt_value(numeric.loc[idx])})"


def _find_summary(summary: pd.DataFrame, icb2: str) -> dict[str, Any]:
    if summary.empty:
        return {}
    match = summary[summary["icb2"] == icb2]
    return match.iloc[0].to_dict() if not match.empty else {}


def _find_indicator(indicators: pd.DataFrame, icb2: str) -> dict[str, Any]:
    if indicators.empty:
        return {}
    match = indicators[indicators["icb2"] == icb2]
    return match.iloc[0].to_dict() if not match.empty else {}


def _fmt_value(value: Any) -> str:
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


def _as_fetch_result(value: Any, source: str) -> FetchResult:
    if isinstance(value, FetchResult):
        return value
    if value is None:
        return FetchResult(False, pd.DataFrame(), status="MISSING_DATA", source=source)
    return FetchResult(True, value, source=source)


def _first_existing(frame: pd.DataFrame, candidates: list[str]) -> str | None:
    exact = {str(col): str(col) for col in frame.columns}
    lower = {str(col).lower(): str(col) for col in frame.columns}
    for candidate in candidates:
        if candidate in exact:
            return exact[candidate]
        if candidate.lower() in lower:
            return lower[candidate.lower()]
    return None


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False), errors="coerce")


def _package_versions(packages: list[str]) -> dict[str, str]:
    versions = {}
    for package in packages:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "not installed"
    return versions


def _file_hash(path: Path) -> str:
    if not path.exists():
        return MISSING
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str:
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
