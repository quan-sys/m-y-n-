from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd


PROBE_TICKERS = ("VNM", "FPT", "VCB")
PUBLIC_METHODS = (
    ("VCI", "vnstock.api.company.Company", "overview"),
    ("VCI", "vnstock.api.trading.Trading", "price_board"),
    ("KBS", "vnstock.api.company.Company", "overview"),
    ("KBS", "vnstock.api.trading.Trading", "price_board"),
)
UNIVERSE_COLUMNS = [
    "ticker",
    "price_vnd",
    "price_as_of",
    "shares_outstanding",
    "shares_as_of",
    "market_cap_vnd",
    "source_method",
    "guard_flags",
]
SOURCE_METHOD = (
    "KBS Company.overview().outstanding_shares x "
    "KBS Trading.price_board().close_price (VND)"
)
PRICE_BOARD_BATCH_SIZE = 50
MAX_FAILURES = 20


def _json_value(value: Any) -> Any:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_value(item) for item in value]
    if isinstance(value, (datetime, date, pd.Timestamp)):
        return value.isoformat()
    if hasattr(value, "item"):
        value = value.item()
    if pd.isna(value):
        return None
    return value


def _compact_row(frame: pd.DataFrame, ticker: str, position: int = 0) -> dict[str, Any]:
    if frame.empty:
        return {}
    symbol_columns = [
        column
        for column in frame.columns
        if str(column).lower() in {"symbol", "ticker", "listing_symbol", "listing_ticker"}
        or str(column).lower().endswith("_symbol")
        or str(column).lower().endswith("_ticker")
    ]
    selected = frame.iloc[0:0]
    for column in symbol_columns:
        match = frame[column].astype(str).str.upper().eq(ticker)
        if match.any():
            selected = frame.loc[match]
            break
    if selected.empty and position < len(frame):
        selected = frame.iloc[[position]]
    if selected.empty:
        return {}
    return {str(key): _json_value(value) for key, value in selected.iloc[0].items()}


def _strict_ticker_row(frame: pd.DataFrame, ticker: str) -> dict[str, Any]:
    if frame.empty:
        return {}
    for column in frame.columns:
        if str(column).lower() not in {"symbol", "ticker"}:
            continue
        match = frame[column].astype(str).str.upper().eq(ticker)
        if match.any():
            return {
                str(key): _json_value(value)
                for key, value in frame.loc[match].iloc[0].items()
            }
    return {}


def _payload_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _trim_compact_row(provider: str, method: str, row: dict[str, Any]) -> dict[str, Any]:
    if method == "overview" and provider == "VCI":
        wanted = {
            "symbol",
            "current_price",
            "market_cap",
            "issue_share",
            "rating_as_of",
            "listing_date",
        }
    elif method == "overview":
        wanted = {
            "symbol",
            "listing_price",
            "listed_volume",
            "outstanding_shares",
            "as_of_date",
            "charter_capital",
        }
    elif provider == "VCI":
        wanted = {
            "listing_symbol",
            "listing_trading_date",
            "listing_listed_share",
            "listing_sending_time",
            "match_match_price",
            "match_sending_time",
            "match_reference_price",
        }
    else:
        wanted = {
            "symbol",
            "TD",
            "time",
            "close_price",
            "reference_price",
            "listed_shares",
            "total_listed_qty",
        }
    return {key: value for key, value in row.items() if key in wanted}


def _method_assessment(provider: str, method: str, row: dict[str, Any]) -> dict[str, Any]:
    columns = set(row)
    price_fields = sorted(
        field
        for field in columns
        if field.lower()
        in {
            "current_price",
            "match_match_price",
            "match_price",
            "close_price",
        }
    )
    direct_fields = sorted(
        field
        for field in columns
        if field.lower() in {"market_cap", "market_capitalization", "market_cap_vnd"}
    )
    share_fields = sorted(
        field
        for field in columns
        if "share" in field.lower() or field.lower() in {"total_listed_qty"}
    )
    as_of_fields = sorted(
        field
        for field in columns
        if field.lower() in {"date", "time", "trading_date", "update_date", "as_of_date", "td"}
        or field.lower().endswith("_trading_date")
        or field.lower().endswith("_sending_time")
    )
    notes: list[str] = []
    if provider == "VCI" and method == "overview" and "issue_share" in columns:
        notes.append(
            "Installed public provider maps number_of_shares_mkt_cap to issue_share; "
            "it does not document this as true shares outstanding."
        )
    if provider == "KBS" and method == "price_board" and share_fields:
        notes.append(
            "Returned fields are named listed_shares/total_listed_qty, not shares_outstanding."
        )
    if price_fields:
        notes.append("No explicit price-unit metadata is attached to the returned DataFrame.")
    return {
        "direct_market_cap_fields": direct_fields,
        "supplies_direct_market_cap": bool(direct_fields),
        "explicit_market_cap_unit_evidence": "NONE_IN_PUBLIC_RETURN_OR_METHOD_DOCSTRING",
        "current_price_fields": price_fields,
        "supplies_current_unadjusted_price": bool(price_fields),
        "explicit_price_unit_evidence": "NONE_IN_PUBLIC_RETURN_OR_METHOD_DOCSTRING",
        "share_fields": share_fields,
        "supplies_true_shares_outstanding": bool(
            {field.lower() for field in columns}
            & {"shares_outstanding", "outstanding_shares"}
        ),
        "as_of_fields": as_of_fields,
        "notes": notes,
    }


def _call_company(provider: str, ticker: str) -> pd.DataFrame:
    from vnstock.api.company import Company

    return Company(source=provider, symbol=ticker, random_agent=False, show_log=False).overview()


def _call_board(provider: str, tickers: list[str]) -> pd.DataFrame:
    from vnstock.api.trading import Trading

    kwargs: dict[str, Any] = {"symbols_list": tickers}
    if provider == "VCI":
        kwargs["flatten_columns"] = True
    if provider == "KBS":
        kwargs["get_all"] = True
    return Trading(source=provider, random_agent=False, show_log=False).price_board(**kwargs)


def record_passes_contract(record: dict[str, Any]) -> bool:
    direct_pass = bool(
        record.get("supplies_direct_market_cap")
        and record.get("explicit_market_cap_unit_evidence") == "VND"
        and record.get("as_of_fields")
    )
    proxy_pass = bool(
        record.get("supplies_current_unadjusted_price")
        and record.get("explicit_price_unit_evidence") in {"VND", "THOUSAND_VND"}
        and record.get("supplies_true_shares_outstanding")
        and record.get("as_of_fields")
    )
    return direct_pass or proxy_pass


def _finite_number(value: Any) -> float | None:
    if value is None or value is pd.NA or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def guard_market_cap_inputs(price_vnd: Any, shares_outstanding: Any) -> list[str]:
    price = _finite_number(price_vnd)
    shares = _finite_number(shares_outstanding)
    if price is None or shares is None:
        return ["MISSING_INPUT"]
    flags: list[str] = []
    if price < 1_000 or price > 1_000_000:
        flags.append("PRICE_OUT_OF_RANGE")
    if shares <= 1_000_000:
        flags.append("SHARES_SUSPECT")
    return flags


def calculate_market_cap_vnd(price_vnd: Any, shares_outstanding: Any) -> int | None:
    if guard_market_cap_inputs(price_vnd, shares_outstanding):
        return None
    price = _finite_number(price_vnd)
    shares = _finite_number(shares_outstanding)
    assert price is not None and shares is not None
    return int(round(price * shares))


def _normalized_integer(value: Any) -> int | str:
    number = _finite_number(value)
    if number is None:
        return ""
    return int(round(number))


def _normalized_date(value: Any) -> str:
    if value is None or value is pd.NA or value == "":
        return ""
    parsed = pd.to_datetime(value, dayfirst="/" in str(value), errors="coerce")
    return "" if pd.isna(parsed) else parsed.strftime("%Y-%m-%d")


def _valid_checkpoint_row(row: pd.Series) -> bool:
    flags = "" if pd.isna(row.get("guard_flags")) else str(row.get("guard_flags", ""))
    market_cap = _finite_number(row.get("market_cap_vnd"))
    return not flags and market_cap is not None and market_cap > 0


def _write_checkpoint(rows: list[dict[str, Any]], tickers: list[str], output_path: Path) -> None:
    frame = pd.DataFrame(rows, columns=UNIVERSE_COLUMNS)
    if not frame.empty:
        order = {ticker: index for index, ticker in enumerate(tickers)}
        frame = frame.drop_duplicates("ticker", keep="last")
        frame["_order"] = frame["ticker"].map(order)
        frame = frame.sort_values("_order").drop(columns="_order")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(".tmp")
    frame.to_csv(temporary, index=False, lineterminator="\n")
    temporary.replace(output_path)


def _retry_frame(
    call: Callable[[], pd.DataFrame],
    *,
    max_retries: int,
    backoff_base: float,
    sleep_fn: Callable[[float], None],
) -> tuple[pd.DataFrame, int, str]:
    calls = 0
    last_error = ""
    for attempt in range(max_retries + 1):
        calls += 1
        try:
            frame = call()
            if frame is None or frame.empty:
                raise ValueError("provider returned an empty DataFrame")
            return frame, calls, ""
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < max_retries:
                sleep_fn(backoff_base * (2**attempt))
    return pd.DataFrame(), calls, last_error


def run_full_universe(
    *,
    survivors_path: Path,
    output_path: Path,
    expected_count: int = 156,
    sleep_seconds: float = 1.0,
    max_retries: int = 3,
    backoff_base: float = 1.0,
    sleep_fn: Callable[[float], None] = time.sleep,
    overview_fetcher: Callable[[str], pd.DataFrame] | None = None,
    board_fetcher: Callable[[list[str]], pd.DataFrame] | None = None,
    include_probe_tickers: bool = False,
) -> dict[str, Any]:
    survivors = pd.read_csv(survivors_path)
    if "ticker" not in survivors.columns:
        raise ValueError("survivor input is missing ticker")
    survivor_tickers = survivors["ticker"].astype(str).str.strip().str.upper().tolist()
    if len(survivor_tickers) != expected_count or len(set(survivor_tickers)) != expected_count:
        raise ValueError(
            f"survivor input must contain exactly {expected_count} unique tickers; "
            f"found rows={len(survivor_tickers)} unique={len(set(survivor_tickers))}"
        )
    tickers = list(survivor_tickers)
    if include_probe_tickers:
        tickers.extend(ticker for ticker in PROBE_TICKERS if ticker not in tickers)
    overview_fetcher = overview_fetcher or (lambda ticker: _call_company("KBS", ticker))
    board_fetcher = board_fetcher or (lambda batch: _call_board("KBS", batch))

    saved_rows: list[dict[str, Any]] = []
    completed: set[str] = set()
    if output_path.exists():
        checkpoint = pd.read_csv(output_path)
        missing_columns = [column for column in UNIVERSE_COLUMNS if column not in checkpoint.columns]
        if missing_columns:
            raise ValueError(f"checkpoint missing columns: {missing_columns}")
        checkpoint = checkpoint[checkpoint["ticker"].astype(str).isin(tickers)]
        for _, row in checkpoint.iterrows():
            if _valid_checkpoint_row(row):
                record = {
                    column: ("" if pd.isna(row[column]) else row[column])
                    for column in UNIVERSE_COLUMNS
                }
                record["ticker"] = str(record["ticker"]).upper()
                for column in ("price_vnd", "shares_outstanding", "market_cap_vnd"):
                    record[column] = _normalized_integer(record[column])
                record["price_as_of"] = _normalized_date(record["price_as_of"])
                record["shares_as_of"] = _normalized_date(record["shares_as_of"])
                saved_rows.append(record)
                completed.add(record["ticker"])

    pending = [ticker for ticker in tickers if ticker not in completed]
    api_calls = 0
    price_rows: dict[str, dict[str, Any]] = {}
    price_errors: dict[str, str] = {}
    for start in range(0, len(pending), PRICE_BOARD_BATCH_SIZE):
        batch = pending[start : start + PRICE_BOARD_BATCH_SIZE]
        frame, calls, error = _retry_frame(
            lambda batch=batch: board_fetcher(batch),
            max_retries=max_retries,
            backoff_base=backoff_base,
            sleep_fn=sleep_fn,
        )
        api_calls += calls
        if error:
            price_errors.update({ticker: error for ticker in batch})
            continue
        for ticker in batch:
            price_rows[ticker] = _strict_ticker_row(frame, ticker)

    rows = list(saved_rows)
    failures: list[dict[str, str]] = []
    previous_overview_called = False
    for ticker in pending:
        price_row = price_rows.get(ticker, {})
        if previous_overview_called:
            sleep_fn(sleep_seconds)
        overview, calls, overview_error = _retry_frame(
            lambda ticker=ticker: overview_fetcher(ticker),
            max_retries=max_retries,
            backoff_base=backoff_base,
            sleep_fn=sleep_fn,
        )
        api_calls += calls
        previous_overview_called = True
        overview_row = _strict_ticker_row(overview, ticker)

        price = _normalized_integer(price_row.get("close_price"))
        shares = _normalized_integer(overview_row.get("outstanding_shares"))
        flags = guard_market_cap_inputs(price, shares)
        market_cap = calculate_market_cap_vnd(price, shares)
        record = {
            "ticker": ticker,
            "price_vnd": price,
            "price_as_of": _normalized_date(price_row.get("TD")),
            "shares_outstanding": shares,
            "shares_as_of": _normalized_date(overview_row.get("as_of_date")),
            "market_cap_vnd": "" if market_cap is None else market_cap,
            "source_method": SOURCE_METHOD,
            "guard_flags": ";".join(flags),
        }
        rows.append(record)
        _write_checkpoint(rows, tickers, output_path)
        if flags:
            failure_parts = list(flags)
            if ticker in price_errors:
                failure_parts.append(f"PRICE_API_ERROR={price_errors[ticker]}")
            if overview_error:
                failure_parts.append(f"OVERVIEW_API_ERROR={overview_error}")
            failures.append({"ticker": ticker, "reason": ";".join(failure_parts)})
            if len(failures) > MAX_FAILURES:
                return {
                    "status": "STOPPED_TOO_MANY_FAILURES",
                    "api_calls": api_calls,
                    "cache_hits": len(completed),
                    "rows": len(pd.DataFrame(rows).drop_duplicates("ticker")),
                    "selected_coverage": sum(
                        _finite_number(row.get("market_cap_vnd")) is not None for row in rows
                    ),
                    "failures": failures,
                    "output": output_path.as_posix(),
                }

    final = pd.read_csv(output_path) if output_path.exists() else pd.DataFrame(columns=UNIVERSE_COLUMNS)
    survivor_final = final[final["ticker"].isin(survivor_tickers)]
    selected = int(
        pd.to_numeric(survivor_final["market_cap_vnd"], errors="coerce").notna().sum()
    )
    return {
        "status": "OK",
        "api_calls": api_calls,
        "cache_hits": len(completed),
        "rows": len(final),
        "survivor_rows": len(survivor_final),
        "selected_coverage": selected,
        "failures": failures,
        "output": output_path.as_posix(),
    }


def run_probe(output_dir: Path, cache_only: bool = False) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    api_requests = 0

    evidence_path = output_dir / "probe_public_methods.jsonl"
    if cache_only:
        if not evidence_path.exists():
            raise FileNotFoundError(f"probe cache not found: {evidence_path}")
        for line in evidence_path.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            record["compact_raw_example"] = _trim_compact_row(
                record["source_provider"],
                record["public_method"],
                record["compact_raw_example"],
            )
            assessment = _method_assessment(
                record["source_provider"],
                record["public_method"],
                record["compact_raw_example"],
            )
            record.update(assessment)
            record.pop("raw_payload_hash", None)
            record["compact_example_hash"] = _payload_hash(record["compact_raw_example"])
            records.append(record)

    for provider, class_name, method in (() if cache_only else PUBLIC_METHODS):
        if method == "overview":
            for ticker in PROBE_TICKERS:
                api_requests += 1
                try:
                    frame = _call_company(provider, ticker)
                    error = ""
                except Exception as exc:  # provider errors are evidence, not zero values
                    frame = pd.DataFrame()
                    error = f"{type(exc).__name__}: {exc}"
                row = _trim_compact_row(provider, method, _compact_row(frame, ticker))
                assessment = _method_assessment(provider, method, row)
                record = {
                    "ticker": ticker,
                    "source_provider": provider,
                    "public_class": class_name,
                    "public_method": method,
                    "documented_public_interface": True,
                    "returned_columns": [str(column) for column in frame.columns],
                    "dataframe_attrs": {str(k): _json_value(v) for k, v in frame.attrs.items()},
                    "compact_raw_example": row,
                    "error": error,
                    **assessment,
                }
                record["compact_example_hash"] = _payload_hash(record["compact_raw_example"])
                records.append(record)
        else:
            api_requests += 1
            try:
                frame = _call_board(provider, list(PROBE_TICKERS))
                error = ""
            except Exception as exc:
                frame = pd.DataFrame()
                error = f"{type(exc).__name__}: {exc}"
            for position, ticker in enumerate(PROBE_TICKERS):
                row = _trim_compact_row(provider, method, _compact_row(frame, ticker, position))
                assessment = _method_assessment(provider, method, row)
                record = {
                    "ticker": ticker,
                    "source_provider": provider,
                    "public_class": class_name,
                    "public_method": method,
                    "documented_public_interface": True,
                    "returned_columns": [str(column) for column in frame.columns],
                    "dataframe_attrs": {str(k): _json_value(v) for k, v in frame.attrs.items()},
                    "compact_raw_example": row,
                    "error": error,
                    **assessment,
                }
                record["compact_example_hash"] = _payload_hash(record["compact_raw_example"])
                records.append(record)

    with evidence_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    accepted = [record for record in records if record_passes_contract(record)]
    summary = {
        "probe_tickers": list(PROBE_TICKERS),
        "api_requests": api_requests,
        "cache_hits": len(records) if cache_only else 0,
        "record_count": len(records),
        "accepted_record_count": len(accepted),
        "contract_passed": bool(accepted),
        "accepted_source_method": "NONE" if not accepted else "REVIEW_REQUIRED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_file": evidence_path.as_posix(),
    }
    (output_dir / "probe_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe public vnstock market-cap inputs safely.")
    parser.add_argument("--evaluation-date", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--probe-only", action="store_true")
    mode.add_argument("--full-universe", action="store_true")
    parser.add_argument("--cache-only", action="store_true")
    parser.add_argument("--output-root", type=Path, default=Path("data/market_cap"))
    parser.add_argument(
        "--survivors", type=Path, default=Path("data/screener/step1_survivors.csv")
    )
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--backoff-base", type=float, default=1.0)
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args()
    output_dir = args.output_root / args.evaluation_date
    if args.full_universe:
        if args.cache_only:
            raise ValueError("--cache-only is available only with --probe-only")
        if args.sleep_seconds < 1:
            raise ValueError("--sleep-seconds must be at least 1 for live overview calls")
        summary = run_full_universe(
            survivors_path=args.survivors,
            output_path=output_dir / "universe_market_cap.csv",
            sleep_seconds=args.sleep_seconds,
            max_retries=args.max_retries,
            backoff_base=args.backoff_base,
            include_probe_tickers=True,
        )
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0 if summary["status"] == "OK" else 3
    summary = run_probe(output_dir, cache_only=args.cache_only)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if summary["contract_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
