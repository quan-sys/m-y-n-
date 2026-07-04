from __future__ import annotations

from pathlib import Path
import contextlib
import io
import sys
import traceback

import pandas as pd


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.universe import _first_existing, _normalize_icb, _normalize_symbols  # noqa: E402


def main() -> int:
    try:
        from vnstock import Listing

        with contextlib.redirect_stdout(io.StringIO()):
            listing = Listing(source="VCI", random_agent=True, show_log=False)
            raw_symbols = listing.symbols_by_exchange()
            raw_icb = listing.symbols_by_industries()

        symbols = _to_frame(raw_symbols)
        icb = _to_frame(raw_icb)
        _validate_symbols_shape(symbols)
        _validate_icb_shape(icb)

        normalized_symbols = _normalize_symbols(symbols)
        normalized_icb = _normalize_icb(icb)
        mapped = normalized_symbols.merge(normalized_icb[["ticker", "icb2"]], on="ticker", how="left")
        mapped = mapped[mapped["icb2"].astype(str).str.len() > 0]

        print(f"raw symbols rows: {len(symbols)}")
        print(f"stock rows: {len(normalized_symbols)}")
        print(f"raw ICB rows: {len(icb)}")
        print(f"tickers with ICB2: {len(mapped)}")
        print("sample mapped tickers:")
        for _, row in mapped.head(5).iterrows():
            print(f"- {row['ticker']}: {row['icb2']}")

        if symbols.empty:
            raise ValueError("symbols_by_exchange() returned an empty DataFrame")
        if len(normalized_symbols) < 100:
            raise ValueError(f"stock rows look too low after filtering: {len(normalized_symbols)}")
        if icb.empty:
            raise ValueError("symbols_by_industries() returned an empty DataFrame")
        if mapped.empty:
            raise ValueError("no ticker could be mapped to ICB2 after normalization")

        print("SMOKE TEST PASSED")
        return 0
    except Exception as exc:  # noqa: BLE001 - smoke script must print clear failure.
        print("SMOKE TEST FAILED")
        print(f"{type(exc).__name__}: {exc}")
        traceback.print_exc()
        return 1


def _to_frame(value: object) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        return value.copy()
    if value is None:
        return pd.DataFrame()
    if isinstance(value, list):
        return pd.DataFrame(value)
    if isinstance(value, dict):
        return pd.DataFrame([value])
    return pd.DataFrame(value)


def _validate_symbols_shape(symbols: pd.DataFrame) -> None:
    ticker_col = _first_existing(symbols, ["ticker", "symbol", "code", "stock_symbol", "stockSymbol"])
    exchange_col = _first_existing(symbols, ["exchange", "board", "floor", "stock_exchange", "stockExchange"])
    if not ticker_col:
        raise ValueError(f"symbols missing ticker/symbol column; columns={symbols.columns.tolist()}")
    if not exchange_col:
        raise ValueError(f"symbols missing exchange/board column; columns={symbols.columns.tolist()}")


def _validate_icb_shape(icb: pd.DataFrame) -> None:
    ticker_col = _first_existing(icb, ["ticker", "symbol", "code", "stock_symbol", "stockSymbol"])
    level_col = _first_existing(icb, ["icb_level", "icbLevel", "level"])
    value_col = _first_existing(icb, ["icb_name", "icbName", "icb_code", "icbCode", "icb2", "icb_name2"])
    if not ticker_col:
        raise ValueError(f"ICB missing ticker/symbol column; columns={icb.columns.tolist()}")
    if not value_col:
        raise ValueError(f"ICB missing name/code column; columns={icb.columns.tolist()}")
    if not level_col and not _first_existing(icb, ["icb2", "icb_code2", "icbName2", "icb_name2"]):
        raise ValueError(f"ICB is neither long nor wide enough to normalize; columns={icb.columns.tolist()}")


if __name__ == "__main__":
    raise SystemExit(main())
