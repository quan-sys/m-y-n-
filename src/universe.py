from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from src.data.vnstock_client import FetchResult, VnstockClient


REQUIRED_COLUMNS = [
    "ticker",
    "exchange",
    "icb2",
    "icb3",
    "icb4",
    "market_cap",
    "adtv_20d",
    "status",
    "reject_reason",
    "as_of",
    "source",
]
OUTPUT_COLUMNS = REQUIRED_COLUMNS + ["data_status"]

MIN_ADTV_20D = 500_000_000
MIN_ACCEPTED_SYMBOLS = 700
EXPECTED_ICB2_COUNT = 19
SUPPORTED_EXCHANGES = {"HOSE", "HNX", "UPCOM"}
UNSUPPORTED_EXCHANGE_REASON = "UNSUPPORTED_EXCHANGE"
PRICE_TO_VND_MULTIPLIER = 1000.0
MARKET_CAP_SOURCE_PROXY = "SHARES_X_LAST_CLOSE_X1000_PROXY"


@dataclass(frozen=True)
class UniverseBuildResult:
    accepted: pd.DataFrame
    rejects: pd.DataFrame
    summary: dict[str, Any]


def build_universe(
    client: Any | None = None,
    output_dir: str | Path = "data",
    config_dir: str | Path = "config",
    write_outputs: bool = True,
    min_adtv_20d: float = MIN_ADTV_20D,
    limit: int | None = None,
    max_consecutive_api_errors: int = 10,
    fetch_market_cap: bool = False,
    market_cap_limit: int | None = None,
) -> UniverseBuildResult:
    if fetch_market_cap and market_cap_limit is None:
        raise ValueError("market_cap_limit is required when fetch_market_cap is enabled")
    if market_cap_limit is not None and market_cap_limit < 0:
        raise ValueError("market_cap_limit must be zero or greater")
    client = client or VnstockClient()
    output_dir = Path(output_dir)
    config_dir = Path(config_dir)
    source = getattr(client, "source", "vnstock")
    run_date = date.today().isoformat()

    symbols_result = _as_result(client.list_symbols(), source=source)
    symbols = _normalize_symbols(symbols_result.data)
    if symbols_result.status == "STALE_DATA":
        symbols["data_status"] = "STALE_DATA"
    stock_symbol_count = len(symbols)
    raw_symbol_count = _metadata_int(symbols_result, "raw_count", fallback=stock_symbol_count)
    if limit is not None:
        symbols = symbols.head(max(limit, 0)).copy()

    tickers = symbols["ticker"].dropna().astype(str).tolist() if "ticker" in symbols else []
    icb_result = _as_result(client.get_icb_classification(tickers), source=source)
    icb = _normalize_icb(icb_result.data)
    icb = _merge_icb_overrides(icb, config_dir / "icb_overrides.csv")
    tickers_with_icb2 = _count_tickers_with_icb2(symbols, icb)

    rows: list[dict[str, Any]] = []
    consecutive_api_errors = 0
    soft_stop_reason = ""
    market_cap_fetch_count = 0
    for _, symbol_row in symbols.iterrows():
        ticker = _clean_text(symbol_row.get("ticker"))
        exchange = _clean_text(symbol_row.get("exchange"))
        base_data_status = symbol_row.get("data_status") or "OK"

        row = _base_row(
            ticker=ticker,
            exchange=exchange,
            source=source,
            as_of=run_date,
            data_status=base_data_status,
        )

        if not ticker:
            rows.append(_reject(row, "MISSING_TICKER", "MISSING_DATA"))
            continue
        if not exchange:
            rows.append(_reject(row, "MISSING_EXCHANGE", "MISSING_DATA"))
            continue
        if exchange not in SUPPORTED_EXCHANGES:
            rows.append(_reject(row, UNSUPPORTED_EXCHANGE_REASON, "MISSING_DATA"))
            continue

        icb_row = _lookup_icb(icb, ticker)
        row.update({key: icb_row.get(key) for key in ("icb2", "icb3", "icb4")})
        if icb_row.get("source"):
            row["source"] = _combine_sources(row["source"], icb_row["source"])

        if not _clean_text(row.get("icb2")):
            rows.append(_reject(row, "MISSING_ICB_CLASSIFICATION", "MISSING_DATA"))
            continue

        if soft_stop_reason:
            rows.append(_reject(row, "API_ERROR", "API_ERROR"))
            continue

        price_result = _as_result(client.get_price_history(ticker, months=6), source=source)
        if not price_result.ok:
            rows.append(_reject(row, "API_ERROR", "API_ERROR"))
            consecutive_api_errors += 1
            if consecutive_api_errors >= max_consecutive_api_errors:
                soft_stop_reason = (
                    f"stopped API calls after {consecutive_api_errors} consecutive API_ERROR results"
                )
            continue
        consecutive_api_errors = 0

        price = _normalize_prices(price_result.data)
        if price.empty:
            rows.append(_reject(row, "MISSING_PRICE_6M", "MISSING_DATA"))
            continue

        as_of = price["date"].max().date().isoformat()
        row["as_of"] = as_of
        if price_result.status == "STALE_DATA":
            row["data_status"] = "STALE_DATA"

        if not _has_six_month_span(price):
            rows.append(_reject(row, "MISSING_PRICE_6M", row["data_status"]))
            continue

        price_with_value = _with_trading_value(price)
        valid_value = price_with_value.dropna(subset=["trading_value"])
        if len(valid_value) < 20:
            rows.append(_reject(row, "INSUFFICIENT_PRICE_HISTORY", "MISSING_DATA"))
            continue

        adtv_20d = float(valid_value.tail(20)["trading_value"].mean())
        row["adtv_20d"] = adtv_20d
        proxy_tail = valid_value.tail(20)
        if bool(proxy_tail["trading_value_is_proxy"].any()):
            proxy_source = (
                "adtv_close_x_volume_x1000_proxy"
                if "trading_value_proxy_scale" in proxy_tail
                and float(proxy_tail["trading_value_proxy_scale"].max()) == 1000.0
                else "adtv_close_x_volume_proxy"
            )
            row["source"] = _combine_sources(row["source"], proxy_source)

        if adtv_20d < min_adtv_20d:
            rows.append(_reject(row, "LOW_LIQUIDITY", row["data_status"]))
            continue

        should_fetch_market_cap = (
            fetch_market_cap
            and market_cap_limit is not None
            and market_cap_fetch_count < market_cap_limit
        )
        if should_fetch_market_cap:
            market_cap_fetch_count += 1
            market_cap_result = _as_result(client.get_market_cap(ticker), source=source)
            if market_cap_result.ok:
                market_cap, market_cap_source = _extract_market_cap_with_source(market_cap_result.data)
                row["market_cap"] = market_cap
                if market_cap_source:
                    row["source"] = _combine_sources(row["source"], market_cap_source)
                if market_cap is None:
                    row["source"] = _combine_sources(row["source"], "market_cap_MISSING_DATA")
                if market_cap_result.status == "STALE_DATA":
                    row["data_status"] = "STALE_DATA"
            else:
                row["source"] = _combine_sources(row["source"], "market_cap_API_ERROR")
                row["data_status"] = "API_ERROR"
        elif fetch_market_cap:
            row["source"] = _combine_sources(row["source"], "market_cap_not_fetched_batch_limit")

        row["status"] = "ACCEPTED"
        row["reject_reason"] = ""
        rows.append(row)

    all_rows = pd.DataFrame(rows, columns=OUTPUT_COLUMNS) if rows else pd.DataFrame(columns=OUTPUT_COLUMNS)
    accepted = all_rows[all_rows["status"] == "ACCEPTED"].copy()
    rejects = all_rows[all_rows["status"] == "REJECTED"].copy()

    if write_outputs:
        output_dir.mkdir(parents=True, exist_ok=True)
        accepted.to_csv(output_dir / "universe.csv", index=False)
        rejects.to_csv(output_dir / "universe_rejects.csv", index=False)

    summary = _build_summary(
        total_symbols=len(symbols),
        raw_symbol_count=raw_symbol_count,
        stock_symbol_count=stock_symbol_count,
        tickers_with_icb2=tickers_with_icb2,
        accepted=accepted,
        rejects=rejects,
        output_dir=output_dir,
        symbols_status=symbols_result.status,
        icb_status=icb_result.status,
        limit=limit,
        soft_stop_reason=soft_stop_reason,
        market_cap_fetch_limit=market_cap_limit,
        market_cap_fetch_count=market_cap_fetch_count,
    )
    return UniverseBuildResult(accepted=accepted, rejects=rejects, summary=summary)


def print_summary(summary: dict[str, Any]) -> None:
    print(f"Total raw symbols fetched: {summary['raw_symbol_count']}")
    print(f"Stock symbols after filtering: {summary['stock_symbol_count']}")
    print(f"Symbols processed: {summary['total_symbols']}")
    if summary.get("limit") is not None:
        print(f"Limit applied: {summary['limit']}")
    print(f"Tickers with ICB2: {summary['tickers_with_icb2']}")
    print(f"Accepted symbols: {summary['accepted_count']}")
    print(f"Rejected symbols: {summary['rejected_count']}")
    print(f"ICB2 sectors covered: {summary['icb2_covered']}")

    if summary["top_reject_reasons"]:
        print("Top reject reasons:")
        for reason, count in summary["top_reject_reasons"]:
            print(f"- {reason}: {count}")
    else:
        print("Top reject reasons: none")

    if summary["sparse_or_missing_icb2"]:
        print("Sparse or missing ICB2 sectors:")
        for item in summary["sparse_or_missing_icb2"]:
            print(f"- {item}")
    else:
        print("Sparse or missing ICB2 sectors: none detected")

    if summary["warnings"]:
        print("WARNING: Acceptance threshold not met.")
        print(f"Reason: {'; '.join(summary['warnings'])}")
        print("Suggested checks: vnstock API, ICB classification source, liquidity filter, cache freshness.")

    print(f"Universe output: {summary['universe_path']}")
    print(f"Reject log output: {summary['rejects_path']}")
    if summary.get("market_cap_fetch_limit") is not None:
        print(
            "Market-cap fetches: "
            f"{summary['market_cap_fetch_count']}/{summary['market_cap_fetch_limit']} controlled requests"
        )
    if summary.get("snapshot_path"):
        print(f"Universe snapshot: {summary['snapshot_path']}")
    elif summary.get("snapshot_status"):
        print(f"Universe snapshot status: {summary['snapshot_status']}")


def _as_result(value: Any, source: str) -> FetchResult:
    if isinstance(value, FetchResult):
        return value
    return FetchResult(True, value, source=source)


def _metadata_int(result: FetchResult, key: str, fallback: int) -> int:
    if result.metadata and key in result.metadata:
        try:
            return int(result.metadata[key])
        except (TypeError, ValueError):
            return fallback
    return fallback


def _normalize_symbols(data: Any) -> pd.DataFrame:
    frame = _to_frame(data)
    if frame.empty:
        return pd.DataFrame(columns=["ticker", "exchange"])

    type_col = _first_existing(frame, ["type", "security_type", "securityType"])
    if type_col:
        frame = frame[frame[type_col].map(_clean_text) == "STOCK"].copy()

    ticker_col = _first_existing(
        frame,
        ["ticker", "symbol", "code", "stock_symbol", "stockSymbol", "organ_code", "organCode"],
    )
    exchange_col = _first_existing(
        frame,
        ["exchange", "floor", "stock_exchange", "stockExchange", "exchange_name", "exchangeName", "comGroupCode"],
    )

    result = pd.DataFrame()
    result["ticker"] = frame[ticker_col].map(_clean_text) if ticker_col else ""
    result["exchange"] = frame[exchange_col].map(_normalize_exchange) if exchange_col else ""
    result = result.drop_duplicates(subset=["ticker"], keep="first")
    exchange_rank = {"HOSE": 0, "HNX": 1, "UPCOM": 2}
    result["_exchange_rank"] = result["exchange"].map(exchange_rank).fillna(9)
    result = result.sort_values(["_exchange_rank", "ticker"]).drop(columns=["_exchange_rank"])
    return result.reset_index(drop=True)


def _normalize_icb(data: Any) -> pd.DataFrame:
    frame = _to_frame(data)
    if frame.empty:
        return pd.DataFrame(columns=["ticker", "icb2", "icb3", "icb4", "source"])

    ticker_col = _first_existing(frame, ["ticker", "symbol", "code", "stock_symbol", "stockSymbol"])
    level_col = _first_existing(frame, ["icb_level", "icbLevel", "level"])
    long_value_col = _first_existing(frame, ["icb_name", "icbName", "icb_code", "icbCode"])
    if ticker_col and level_col and long_value_col:
        source_col = _first_existing(frame, ["source"])
        return _pivot_icb_long(frame, ticker_col, level_col, long_value_col, source_col)

    icb2_col = _first_existing(frame, ["icb2", "icb_code2", "icbCode2", "icb_name2", "icbName2", "industry2"])
    icb3_col = _first_existing(frame, ["icb3", "icb_code3", "icbCode3", "icb_name3", "icbName3", "industry3"])
    icb4_col = _first_existing(frame, ["icb4", "icb_code4", "icbCode4", "icb_name4", "icbName4", "industry4"])
    source_col = _first_existing(frame, ["source"])

    result = pd.DataFrame()
    result["ticker"] = frame[ticker_col].map(_clean_text) if ticker_col else ""
    result["icb2"] = frame[icb2_col].map(_clean_text) if icb2_col else ""
    result["icb3"] = frame[icb3_col].map(_clean_text) if icb3_col else ""
    result["icb4"] = frame[icb4_col].map(_clean_text) if icb4_col else ""
    result["source"] = frame[source_col].map(_clean_text) if source_col else ""
    return result[result["ticker"] != ""].drop_duplicates(subset=["ticker"], keep="last")


def _pivot_icb_long(
    frame: pd.DataFrame,
    ticker_col: str,
    level_col: str,
    value_col: str,
    source_col: str | None = None,
) -> pd.DataFrame:
    work = pd.DataFrame()
    work["ticker"] = frame[ticker_col].map(_clean_text)
    work["level"] = pd.to_numeric(frame[level_col], errors="coerce")
    work["value"] = frame[value_col].map(_clean_text)
    work = work[
        (work["ticker"] != "")
        & (work["value"] != "")
        & work["level"].isin([2, 3, 4])
    ].copy()
    if work.empty:
        return pd.DataFrame(columns=["ticker", "icb2", "icb3", "icb4", "source"])

    work["field"] = "icb" + work["level"].astype(int).astype(str)
    wide = (
        work.pivot_table(
            index="ticker",
            columns="field",
            values="value",
            aggfunc=lambda values: next((value for value in reversed(list(values)) if value), ""),
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )
    for column in ("icb2", "icb3", "icb4"):
        if column not in wide.columns:
            wide[column] = ""

    if source_col and source_col in frame.columns:
        sources = pd.DataFrame(
            {
                "ticker": frame[ticker_col].map(_clean_text),
                "source": frame[source_col].map(_clean_text),
            }
        )
        sources = sources[sources["ticker"] != ""].drop_duplicates(subset=["ticker"], keep="last")
        wide = wide.merge(sources, on="ticker", how="left")
        wide["source"] = wide["source"].replace("", "vnstock_vci_symbols_by_industries")
    else:
        wide["source"] = "vnstock_vci_symbols_by_industries"

    return wide[["ticker", "icb2", "icb3", "icb4", "source"]].drop_duplicates(subset=["ticker"], keep="last")


def _merge_icb_overrides(icb: pd.DataFrame, path: Path) -> pd.DataFrame:
    if not path.exists():
        return icb
    overrides = _normalize_icb(pd.read_csv(path))
    if overrides.empty:
        return icb
    overrides["source"] = overrides["source"].replace("", "manual_icb_override")
    merged = pd.concat([icb, overrides], ignore_index=True)
    return merged.drop_duplicates(subset=["ticker"], keep="last")


def _lookup_icb(icb: pd.DataFrame, ticker: str) -> dict[str, Any]:
    if icb.empty:
        return {}
    match = icb[icb["ticker"].astype(str).str.upper() == ticker.upper()]
    if match.empty:
        return {}
    return match.iloc[-1].to_dict()


def _count_tickers_with_icb2(symbols: pd.DataFrame, icb: pd.DataFrame) -> int:
    if symbols.empty or icb.empty or "ticker" not in icb.columns or "icb2" not in icb.columns:
        return 0
    wanted = set(symbols["ticker"].dropna().astype(str).str.upper())
    has_icb2 = icb[
        icb["ticker"].astype(str).str.upper().isin(wanted)
        & (icb["icb2"].astype(str).str.strip() != "")
    ]
    return int(has_icb2["ticker"].nunique())


def _normalize_prices(data: Any) -> pd.DataFrame:
    frame = _to_frame(data)
    if frame.empty:
        return pd.DataFrame(columns=["date", "close", "volume", "value"])

    date_col = _first_existing(frame, ["date", "time", "trading_date", "tradingDate", "datetime"])
    close_col = _first_existing(frame, ["close", "close_price", "closePrice", "adj_close", "match_price"])
    volume_col = _first_existing(frame, ["volume", "trading_volume", "tradingVolume", "total_volume", "nmVolume"])
    value_col = _first_existing(
        frame,
        ["value", "trading_value", "tradingValue", "total_value", "totalTradingValue", "nmValue"],
    )

    result = pd.DataFrame()
    result["date"] = pd.to_datetime(frame[date_col], errors="coerce") if date_col else pd.NaT
    result["close"] = _numeric(frame[close_col]) if close_col else pd.NA
    result["volume"] = _numeric(frame[volume_col]) if volume_col else pd.NA
    result["value"] = _numeric(frame[value_col]) if value_col else pd.NA
    result = result.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return result


def _with_trading_value(price: pd.DataFrame) -> pd.DataFrame:
    result = price.copy()
    result["trading_value"] = result["value"]
    result["trading_value_is_proxy"] = False
    result["trading_value_proxy_scale"] = 1.0
    missing = result["trading_value"].isna()
    proxy_ready = missing & result["close"].notna() & result["volume"].notna()
    # VCI history prices are often quoted in thousand VND, while volume is shares.
    proxy_scale = 1000.0 if result.loc[proxy_ready, "close"].median() < 1000 else 1.0
    # Fallback uses close * volume only when vnstock does not provide traded value.
    result.loc[proxy_ready, "trading_value"] = (
        result.loc[proxy_ready, "close"] * result.loc[proxy_ready, "volume"] * proxy_scale
    )
    result.loc[proxy_ready, "trading_value_is_proxy"] = True
    result.loc[proxy_ready, "trading_value_proxy_scale"] = proxy_scale
    return result


def _has_six_month_span(price: pd.DataFrame) -> bool:
    if price.empty:
        return False
    latest = price["date"].max()
    earliest = price["date"].min()
    return earliest <= latest - pd.DateOffset(months=6)


def _extract_market_cap(data: Any) -> float | None:
    value, _source = _extract_market_cap_with_source(data)
    return value


def _extract_market_cap_with_source(data: Any) -> tuple[float | None, str | None]:
    frame = _to_frame(data)
    if frame.empty:
        return None, None
    col = _first_existing(
        frame,
        ["market_cap", "marketCap", "market_capitalization", "marketCapitalization", "listedValue"],
    )
    if col:
        values = _numeric(frame[col]).dropna()
        if not values.empty:
            value = float(values.iloc[-1])
            if value > 0:
                return value, "SOURCE_REPORTED_MARKET_CAP"

    shares_col = _first_existing(
        frame,
        [
            "issue_share",
            "issueShare",
            "outstanding_share",
            "outstandingShare",
            "listed_share",
            "listedShare",
            "shares_outstanding",
            "sharesOutstanding",
        ],
    )
    close_col = _first_existing(frame, ["last_close", "lastClose", "current_price", "currentPrice", "close"])
    if shares_col and close_col:
        shares = _numeric(frame[shares_col]).dropna()
        closes = _numeric(frame[close_col]).dropna()
        if not shares.empty and not closes.empty:
            shares_value = float(shares.iloc[-1])
            close_value = float(closes.iloc[-1])
            if shares_value > 0 and close_value > 0:
                return shares_value * close_value * PRICE_TO_VND_MULTIPLIER, MARKET_CAP_SOURCE_PROXY

    return None, None


def _build_summary(
    total_symbols: int,
    raw_symbol_count: int,
    stock_symbol_count: int,
    tickers_with_icb2: int,
    accepted: pd.DataFrame,
    rejects: pd.DataFrame,
    output_dir: Path,
    symbols_status: str,
    icb_status: str,
    limit: int | None,
    soft_stop_reason: str,
    market_cap_fetch_limit: int | None,
    market_cap_fetch_count: int,
) -> dict[str, Any]:
    icb2_counts = accepted["icb2"].replace("", pd.NA).dropna().value_counts() if not accepted.empty else pd.Series()
    top_rejects = list(rejects["reject_reason"].value_counts().head(10).items()) if not rejects.empty else []
    sparse = [f"{icb2}: {count} accepted" for icb2, count in icb2_counts.items() if count < 3]

    warnings: list[str] = []
    if len(accepted) < MIN_ACCEPTED_SYMBOLS:
        warnings.append(f"accepted {len(accepted)} < {MIN_ACCEPTED_SYMBOLS}")
    if len(icb2_counts) < EXPECTED_ICB2_COUNT:
        warnings.append(f"ICB2 coverage {len(icb2_counts)} < {EXPECTED_ICB2_COUNT}")
    api_error_count = int((rejects["reject_reason"] == "API_ERROR").sum()) if not rejects.empty else 0
    if api_error_count:
        warnings.append(f"API_ERROR rejects {api_error_count}; check vnstock rate limits/source access")
    if symbols_status in {"API_ERROR", "STALE_DATA"}:
        warnings.append(f"symbol source status {symbols_status}")
    if icb_status in {"API_ERROR", "STALE_DATA"}:
        warnings.append(f"ICB source status {icb_status}")
    if soft_stop_reason:
        warnings.append(soft_stop_reason)

    return {
        "raw_symbol_count": raw_symbol_count,
        "stock_symbol_count": stock_symbol_count,
        "total_symbols": total_symbols,
        "limit": limit,
        "tickers_with_icb2": tickers_with_icb2,
        "accepted_count": len(accepted),
        "rejected_count": len(rejects),
        "icb2_covered": int(len(icb2_counts)),
        "top_reject_reasons": top_rejects,
        "sparse_or_missing_icb2": sparse,
        "warnings": warnings,
        "universe_path": str((output_dir / "universe.csv").resolve()),
        "rejects_path": str((output_dir / "universe_rejects.csv").resolve()),
        "market_cap_fetch_limit": market_cap_fetch_limit,
        "market_cap_fetch_count": market_cap_fetch_count,
    }


def write_universe_snapshot(
    accepted: pd.DataFrame,
    rejects: pd.DataFrame,
    snapshots_root: str | Path,
    *,
    run_date: str | None = None,
) -> Path:
    snapshot_date = run_date or date.today().isoformat()
    if not pd.Series([snapshot_date]).str.fullmatch(r"\d{4}-\d{2}-\d{2}").iloc[0]:
        raise ValueError("snapshot run_date must use YYYY-MM-DD")

    frames = {
        "universe.csv": accepted,
        "universe_rejects.csv": rejects,
    }
    if not accepted.empty and not accepted["status"].eq("ACCEPTED").all():
        raise ValueError("universe.csv snapshot contains non-ACCEPTED rows")
    if not rejects.empty:
        if not rejects["status"].eq("REJECTED").all():
            raise ValueError("universe_rejects.csv snapshot contains non-REJECTED rows")
        missing_reason = rejects["reject_reason"].fillna("").astype(str).str.strip().eq("")
        if bool(missing_reason.any()):
            raise ValueError("universe_rejects.csv snapshot has an empty reject_reason")
    serialized: dict[str, str] = {}
    for name, frame in frames.items():
        if list(frame.columns) != OUTPUT_COLUMNS:
            raise ValueError(f"{name} does not match the required universe schema")
        serialized[name] = frame.to_csv(index=False, lineterminator="\n")

    snapshot_dir = Path(snapshots_root) / snapshot_date
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    for name, content in serialized.items():
        path = snapshot_dir / name
        if path.exists() and path.read_text(encoding="utf-8") != content:
            raise FileExistsError(
                f"snapshot conflict for {path}: an observation for {snapshot_date} already exists"
            )

    for name, content in serialized.items():
        path = snapshot_dir / name
        if not path.exists():
            path.write_text(content, encoding="utf-8", newline="")

    return snapshot_dir


def _base_row(ticker: str, exchange: str, source: str, as_of: str, data_status: str) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "exchange": exchange,
        "icb2": "",
        "icb3": "",
        "icb4": "",
        "market_cap": None,
        "adtv_20d": None,
        "status": "",
        "reject_reason": "",
        "as_of": as_of,
        "source": source,
        "data_status": data_status,
    }


def _reject(row: dict[str, Any], reason: str, data_status: str) -> dict[str, Any]:
    row = dict(row)
    row["status"] = "REJECTED"
    row["reject_reason"] = reason
    row["data_status"] = data_status
    return row


def _to_frame(value: Any) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        return value.copy()
    if value is None:
        return pd.DataFrame()
    if isinstance(value, pd.Series):
        return value.to_frame().T
    if isinstance(value, dict):
        return pd.DataFrame([value])
    if isinstance(value, list):
        return pd.DataFrame(value)
    return pd.DataFrame(value)


def _first_existing(frame: pd.DataFrame, candidates: list[str]) -> str | None:
    exact = {str(col): str(col) for col in frame.columns}
    lower = {str(col).lower(): str(col) for col in frame.columns}
    for candidate in candidates:
        if candidate in exact:
            return exact[candidate]
        if candidate.lower() in lower:
            return lower[candidate.lower()]
    return None


def _clean_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip().upper()


def _normalize_exchange(value: Any) -> str:
    text = _clean_text(value)
    if text in {"HOSE", "HSX"}:
        return "HOSE"
    if text == "HNX":
        return "HNX"
    if text in {"UPCOM", "UPCoM".upper()}:
        return "UPCOM"
    return text


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False), errors="coerce")


def _combine_sources(*sources: Any) -> str:
    cleaned = []
    for source in sources:
        text = str(source).strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return "+".join(cleaned)
