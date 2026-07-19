from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


PROBE_TICKERS = ("VNM", "FPT", "VCB")
PUBLIC_METHODS = (
    ("VCI", "vnstock.api.company.Company", "overview"),
    ("VCI", "vnstock.api.trading.Trading", "price_board"),
    ("KBS", "vnstock.api.company.Company", "overview"),
    ("KBS", "vnstock.api.trading.Trading", "price_board"),
)


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
    parser.add_argument("--probe-only", action="store_true", required=True)
    parser.add_argument("--cache-only", action="store_true")
    parser.add_argument("--output-root", type=Path, default=Path("data/market_cap"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_root / args.evaluation_date
    summary = run_probe(output_dir, cache_only=args.cache_only)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if summary["contract_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
