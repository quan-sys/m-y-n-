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
API_ERROR = "API_ERROR"
STALE_DATA = "STALE_DATA"
LIMITED_HISTORY = "LIMITED_HISTORY"
SOURCE = "vnstock_vci_quote_history"
VNINDEX_SYMBOLS = ("VNINDEX", "VN30")
INDEX_SOURCE_PROXY = "UNIVERSE_EQUAL_WEIGHT_PROXY"
CACHE_STATE_CACHED = "CACHED"
CACHE_STATE_FETCHED = "FETCHED"

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
    "missing_price_count",
    "api_error_count",
    "api_error_tickers",
    "missing_indicator_count",
    "coverage_status",
    "coverage_warning",
    "index_source",
    "cap_weight_available",
    "source",
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
    progress: bool = True,
) -> WeeklyMvpResult:
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
    index_result = _fetch_index_prices(client)
    outputs = build_weekly_outputs(universe, price_results, index_result=index_result, source=SOURCE)

    report_date = date.today().isoformat()
    output_dir = reports_root / report_date
    output_dir.mkdir(parents=True, exist_ok=True)

    indicators = outputs.indicators
    summary = outputs.summary
    data_quality = outputs.data_quality
    as_of = _latest_as_of(indicators, fallback=report_date)
    metadata = build_run_metadata(
        universe_path=universe_path,
        universe=universe,
        as_of=as_of,
        source=SOURCE,
        output_dir=output_dir,
        extra=run_quality_metadata(data_quality),
    )

    indicators.to_csv(output_dir / "sector_indicators_tier1.csv", index=False)
    summary.to_csv(output_dir / "sector_summary.csv", index=False)
    data_quality.to_csv(output_dir / "data_quality.csv", index=False)
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
    valid_market_cap_count = int((_market_caps(universe_rows) > 0).sum())
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
        "missing_price_count": missing_price_count,
        "api_error_count": api_error_count,
        "api_error_tickers": "|".join(api_error_tickers) if api_error_tickers else "NONE",
        "missing_indicator_count": missing_indicator_count,
        "coverage_status": coverage_status,
        "coverage_warning": coverage_warning,
        "index_source": index_source,
        "cap_weight_available": "yes" if cap_weight_available else "no",
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
            f"index_source={row.get('index_source', MISSING)}; "
            f"cap_weight_available={row.get('cap_weight_available', 'no')}; "
            f"missing_indicator_count={row['missing_indicator_count']}."
        )

    lines.extend(
        [
            "",
            "### Missing Data",
            "",
            f"- `{MISSING}` nghĩa là nguồn dữ liệu chưa đủ để tính chỉ báo.",
            "- Cap-weight return cần market_cap từ universe; nếu market_cap trống thì chỉ báo cap-weight được để thiếu dữ liệu.",
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
    for column in ("ticker", "icb2", "market_cap"):
        if column not in frame.columns:
            frame[column] = ""
    frame["ticker"] = frame["ticker"].astype(str).str.strip().str.upper()
    frame["icb2"] = frame["icb2"].astype(str).str.strip()
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
