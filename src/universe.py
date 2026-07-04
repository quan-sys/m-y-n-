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
) -> UniverseBuildResult:
    client = client or VnstockClient()
    output_dir = Path(output_dir)
    config_dir = Path(config_dir)
    source = getattr(client, "source", "vnstock")
    run_date = date.today().isoformat()

    symbols_result = _as_result(client.list_symbols(), source=source)
    symbols = _normalize_symbols(symbols_result.data)
    if symbols_result.status == "STALE_DATA":
        symbols["data_status"] = "STALE_DATA"

    tickers = symbols["ticker"].dropna().astype(str).tolist() if "ticker" in symbols else []
    icb_result = _as_result(client.get_icb_classification(tickers), source=source)
    icb = _normalize_icb(icb_result.data)
    icb = _merge_icb_overrides(icb, config_dir / "icb_overrides.csv")

    rows: list[dict[str, Any]] = []
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

        icb_row = _lookup_icb(icb, ticker)
        row.update({key: icb_row.get(key) for key in ("icb2", "icb3", "icb4")})
        if icb_row.get("source"):
            row["source"] = _combine_sources(row["source"], icb_row["source"])

        if not _clean_text(row.get("icb2")):
            rows.append(_reject(row, "MISSING_ICB_CLASSIFICATION", "MISSING_DATA"))
            continue

        price_result = _as_result(client.get_price_history(ticker, months=6), source=source)
        if not price_result.ok:
            rows.append(_reject(row, "API_ERROR", "API_ERROR"))
            continue

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
        if bool(valid_value.tail(20)["trading_value_is_proxy"].any()):
            row["source"] = _combine_sources(row["source"], "adtv_close_x_volume_proxy")

        if adtv_20d < min_adtv_20d:
            rows.append(_reject(row, "LOW_LIQUIDITY", row["data_status"]))
            continue

        market_cap_result = _as_result(client.get_market_cap(ticker), source=source)
        if market_cap_result.ok:
            row["market_cap"] = _extract_market_cap(market_cap_result.data)
            if market_cap_result.status == "STALE_DATA":
                row["data_status"] = "STALE_DATA"

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
        accepted=accepted,
        rejects=rejects,
        output_dir=output_dir,
        symbols_status=symbols_result.status,
        icb_status=icb_result.status,
    )
    return UniverseBuildResult(accepted=accepted, rejects=rejects, summary=summary)


def print_summary(summary: dict[str, Any]) -> None:
    print(f"Total symbols fetched: {summary['total_symbols']}")
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


def _as_result(value: Any, source: str) -> FetchResult:
    if isinstance(value, FetchResult):
        return value
    return FetchResult(True, value, source=source)


def _normalize_symbols(data: Any) -> pd.DataFrame:
    frame = _to_frame(data)
    if frame.empty:
        return pd.DataFrame(columns=["ticker", "exchange"])

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
    return result.drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)


def _normalize_icb(data: Any) -> pd.DataFrame:
    frame = _to_frame(data)
    if frame.empty:
        return pd.DataFrame(columns=["ticker", "icb2", "icb3", "icb4", "source"])

    ticker_col = _first_existing(frame, ["ticker", "symbol", "code", "stock_symbol", "stockSymbol"])
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
    missing = result["trading_value"].isna()
    proxy_ready = missing & result["close"].notna() & result["volume"].notna()
    # Fallback uses close * volume only when vnstock does not provide traded value.
    result.loc[proxy_ready, "trading_value"] = result.loc[proxy_ready, "close"] * result.loc[proxy_ready, "volume"]
    result.loc[proxy_ready, "trading_value_is_proxy"] = True
    return result


def _has_six_month_span(price: pd.DataFrame) -> bool:
    if price.empty:
        return False
    latest = price["date"].max()
    earliest = price["date"].min()
    return earliest <= latest - pd.DateOffset(months=6)


def _extract_market_cap(data: Any) -> float | None:
    frame = _to_frame(data)
    if frame.empty:
        return None
    col = _first_existing(
        frame,
        ["market_cap", "marketCap", "market_capitalization", "marketCapitalization", "listedValue"],
    )
    if not col:
        return None
    values = _numeric(frame[col]).dropna()
    if values.empty:
        return None
    return float(values.iloc[-1])


def _build_summary(
    total_symbols: int,
    accepted: pd.DataFrame,
    rejects: pd.DataFrame,
    output_dir: Path,
    symbols_status: str,
    icb_status: str,
) -> dict[str, Any]:
    icb2_counts = accepted["icb2"].replace("", pd.NA).dropna().value_counts() if not accepted.empty else pd.Series()
    top_rejects = list(rejects["reject_reason"].value_counts().head(10).items()) if not rejects.empty else []
    sparse = [f"{icb2}: {count} accepted" for icb2, count in icb2_counts.items() if count < 3]

    warnings: list[str] = []
    if len(accepted) < MIN_ACCEPTED_SYMBOLS:
        warnings.append(f"accepted {len(accepted)} < {MIN_ACCEPTED_SYMBOLS}")
    if len(icb2_counts) < EXPECTED_ICB2_COUNT:
        warnings.append(f"ICB2 coverage {len(icb2_counts)} < {EXPECTED_ICB2_COUNT}")
    if symbols_status in {"API_ERROR", "STALE_DATA"}:
        warnings.append(f"symbol source status {symbols_status}")
    if icb_status in {"API_ERROR", "STALE_DATA"}:
        warnings.append(f"ICB source status {icb_status}")

    return {
        "total_symbols": total_symbols,
        "accepted_count": len(accepted),
        "rejected_count": len(rejects),
        "icb2_covered": int(len(icb2_counts)),
        "top_reject_reasons": top_rejects,
        "sparse_or_missing_icb2": sparse,
        "warnings": warnings,
        "universe_path": str((output_dir / "universe.csv").resolve()),
        "rejects_path": str((output_dir / "universe_rejects.csv").resolve()),
    }


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
    if "HOSE" in text or text in {"HSX", "VNINDEX"}:
        return "HOSE"
    if "HNX" in text:
        return "HNX"
    if "UPCOM" in text or "UPCoM".upper() in text:
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
