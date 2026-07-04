from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import contextlib
import importlib
import io
import json
import random
import re
import time
from typing import Any, Iterable

import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential


CACHE_DIR = Path(__file__).resolve().parent / "cache"


@dataclass(frozen=True)
class FetchResult:
    ok: bool
    data: Any
    status: str = "OK"
    error: str | None = None
    source: str = "vnstock"
    as_of: str | None = None
    metadata: dict[str, Any] | None = None


class VnstockClient:
    """Small adapter around vnstock so pipeline code is source-agnostic."""

    def __init__(
        self,
        cache_dir: str | Path = CACHE_DIR,
        source: str = "vnstock",
        listing_source: str = "VCI",
        quote_source: str = "VCI",
        company_source: str = "VCI",
        min_sleep_seconds: float = 2.8,
        max_sleep_seconds: float = 3.6,
        use_cache: bool = True,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.source = source
        self.listing_source = listing_source
        self.quote_source = quote_source
        self.company_source = company_source
        self.min_sleep_seconds = min_sleep_seconds
        self.max_sleep_seconds = max_sleep_seconds
        self.use_cache = use_cache
        self._terminal_api_error: str | None = None

    def list_symbols(self, exchanges: Iterable[str] = ("HOSE", "HNX", "UPCOM")) -> FetchResult:
        if self._terminal_api_error:
            return self._terminal_error_result()
        cache_path = self._cache_path("symbols", "all")
        cached = self._read_cache(cache_path)
        cached_metadata = self._read_cache_metadata(cache_path)
        if self.use_cache and cached is not None and self._is_fresh(cache_path, max_age_days=7):
            return FetchResult(
                True,
                cached,
                source=self.source,
                as_of=self._today(),
                metadata=cached_metadata or {"raw_count": len(cached), "stock_count": len(cached), "cache": True},
            )

        try:
            data = self._fetch_symbols(tuple(exchanges))
            self._write_cache(cache_path, data)
            self._write_cache_metadata(cache_path, dict(data.attrs))
            return FetchResult(True, data, source=self.source, as_of=self._today(), metadata=dict(data.attrs))
        except BaseException as exc:  # noqa: BLE001 - API failures are converted to data status.
            self._record_terminal_error(exc)
            if cached is not None:
                return FetchResult(True, cached, status="STALE_DATA", error=str(exc), source=self.source)
            return self._error_result(exc)

    def get_icb_classification(self, tickers: Iterable[str] | None = None) -> FetchResult:
        if self._terminal_api_error:
            return self._terminal_error_result()
        cache_path = self._cache_path("icb", "classification")
        cached = self._read_cache(cache_path)
        cached_metadata = self._read_cache_metadata(cache_path)
        if self.use_cache and cached is not None and self._is_fresh(cache_path, max_age_days=30):
            data = self._filter_tickers(cached, tickers)
            return FetchResult(
                True,
                data,
                source=self.source,
                as_of=self._today(),
                metadata=cached_metadata or {"raw_count": len(cached), "cache": True},
            )

        try:
            raw_data = self._fetch_icb_classification()
            self._write_cache(cache_path, raw_data)
            self._write_cache_metadata(cache_path, {"raw_count": len(raw_data)})
            data = self._filter_tickers(raw_data, tickers)
            return FetchResult(
                True,
                data,
                source=self.source,
                as_of=self._today(),
                metadata={"raw_count": len(raw_data)},
            )
        except BaseException as exc:  # noqa: BLE001
            self._record_terminal_error(exc)
            if cached is not None:
                return FetchResult(True, cached, status="STALE_DATA", error=str(exc), source=self.source)
            return self._error_result(exc)

    def get_price_history(self, ticker: str, months: int = 6) -> FetchResult:
        if self._terminal_api_error:
            return self._terminal_error_result()
        normalized = self._safe_key(ticker)
        cache_path = self._cache_path("prices", normalized)
        cached = self._read_cache(cache_path)
        if self.use_cache and cached is not None and self._is_fresh(cache_path, max_age_days=2):
            return FetchResult(True, cached, source=self.source, as_of=self._latest_date(cached))

        try:
            data = self._fetch_price_history(ticker=ticker, months=months)
            self._write_cache(cache_path, data)
            return FetchResult(True, data, source=self.source, as_of=self._latest_date(data))
        except BaseException as exc:  # noqa: BLE001
            self._record_terminal_error(exc)
            if cached is not None:
                return FetchResult(
                    True,
                    cached,
                    status="STALE_DATA",
                    error=str(exc),
                    source=self.source,
                    as_of=self._latest_date(cached),
                )
            return self._error_result(exc)

    def get_market_cap(self, ticker: str) -> FetchResult:
        if self._terminal_api_error:
            return self._terminal_error_result()
        normalized = self._safe_key(ticker)
        cache_path = self._cache_path("market_cap", normalized)
        cached = self._read_cache(cache_path)
        if self.use_cache and cached is not None and self._is_fresh(cache_path, max_age_days=7):
            return FetchResult(True, cached, source=self.source, as_of=self._today())

        try:
            data = self._fetch_market_cap(ticker)
            self._write_cache(cache_path, data)
            return FetchResult(True, data, source=self.source, as_of=self._today())
        except BaseException as exc:  # noqa: BLE001
            self._record_terminal_error(exc)
            if cached is not None:
                return FetchResult(True, cached, status="STALE_DATA", error=str(exc), source=self.source)
            return self._error_result(exc)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    def _fetch_symbols(self, exchanges: tuple[str, ...]) -> pd.DataFrame:
        self._polite_sleep()
        vnstock = self._vnstock_module()
        listing_cls = getattr(vnstock, "Listing")
        listing = self._quiet_call(listing_cls, source=self.listing_source, random_agent=True, show_log=False)
        raw = self._quiet_call(listing.symbols_by_exchange)
        frame = self._to_frame(raw)
        if frame.empty:
            frame = self._to_frame(self._quiet_call(listing.all_symbols))
        raw_count = len(frame)
        stock_frame = self._filter_stock_rows(frame)
        stock_frame.attrs["raw_count"] = raw_count
        stock_frame.attrs["stock_count"] = len(stock_frame)
        return stock_frame

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    def _fetch_icb_classification(self) -> pd.DataFrame:
        self._polite_sleep()
        vnstock = self._vnstock_module()
        listing_cls = getattr(vnstock, "Listing")
        listing = self._quiet_call(listing_cls, source=self.listing_source, random_agent=True, show_log=False)

        method = getattr(listing, "symbols_by_industries")
        return self._to_frame(self._quiet_call(method))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    def _fetch_price_history(self, ticker: str, months: int) -> pd.DataFrame:
        self._polite_sleep()
        vnstock = self._vnstock_module()
        quote_cls = getattr(vnstock, "Quote")
        quote = self._quiet_call(
            quote_cls,
            source=self.quote_source,
            symbol=ticker,
            random_agent=True,
            show_log=False,
        )
        end = date.today()
        start = end - timedelta(days=31 * max(months, 1) + 10)
        return self._to_frame(
            self._quiet_call(
                quote.history,
                symbol=ticker,
                start=start.isoformat(),
                end=end.isoformat(),
                interval="1D",
            )
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    def _fetch_market_cap(self, ticker: str) -> pd.DataFrame:
        self._polite_sleep()
        vnstock = self._vnstock_module()
        company_cls = getattr(vnstock, "Company")
        company = self._quiet_call(
            company_cls,
            source=self.company_source,
            symbol=ticker,
            random_agent=True,
            show_log=False,
        )
        return self._to_frame(self._quiet_call(company.overview))

    def _vnstock_module(self) -> Any:
        return importlib.import_module("vnstock")

    @classmethod
    def _filter_tickers(cls, data: pd.DataFrame, tickers: Iterable[str] | None) -> pd.DataFrame:
        if tickers is None or data.empty:
            return data
        ticker_col = cls._first_existing(data, ["ticker", "symbol", "code", "stock_symbol", "stockSymbol"])
        if not ticker_col:
            return data
        wanted = {str(t).strip().upper() for t in tickers}
        return data[data[ticker_col].astype(str).str.upper().isin(wanted)].copy()

    def _record_terminal_error(self, exc: BaseException) -> None:
        if isinstance(exc, KeyboardInterrupt):
            raise exc
        if isinstance(exc, SystemExit):
            self._terminal_api_error = (
                "vnstock terminated the request, likely due to API rate limit or access limits"
            )

    def _terminal_error_result(self) -> FetchResult:
        return FetchResult(
            False,
            pd.DataFrame(),
            status="API_ERROR",
            error=self._terminal_api_error,
            source=self.source,
        )

    def _error_result(self, exc: BaseException) -> FetchResult:
        message = self._terminal_api_error or str(exc) or type(exc).__name__
        return FetchResult(False, pd.DataFrame(), status="API_ERROR", error=message, source=self.source)

    def _polite_sleep(self) -> None:
        time.sleep(random.uniform(self.min_sleep_seconds, self.max_sleep_seconds))

    @staticmethod
    def _quiet_call(func: Any, *args: Any, **kwargs: Any) -> Any:
        with contextlib.redirect_stdout(io.StringIO()):
            return func(*args, **kwargs)

    @staticmethod
    def _to_frame(value: Any) -> pd.DataFrame:
        if value is None:
            return pd.DataFrame()
        if isinstance(value, pd.DataFrame):
            return value.copy()
        if isinstance(value, pd.Series):
            return value.to_frame().T
        if isinstance(value, dict):
            return pd.DataFrame([value])
        if isinstance(value, list):
            return pd.DataFrame(value)
        return pd.DataFrame(value)

    @classmethod
    def _filter_stock_rows(cls, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return frame
        type_col = cls._first_existing(frame, ["type", "security_type", "securityType"])
        if not type_col:
            return frame
        return frame[frame[type_col].astype(str).str.upper() == "STOCK"].reset_index(drop=True)

    @staticmethod
    def _first_existing(frame: pd.DataFrame, candidates: list[str]) -> str | None:
        if frame.empty:
            return None
        exact = {str(col): str(col) for col in frame.columns}
        lower = {str(col).lower(): str(col) for col in frame.columns}
        for candidate in candidates:
            if candidate in exact:
                return exact[candidate]
            if candidate.lower() in lower:
                return lower[candidate.lower()]
        return None

    def _cache_path(self, namespace: str, key: str) -> Path:
        path = self.cache_dir / namespace
        path.mkdir(parents=True, exist_ok=True)
        return path / f"{self._safe_key(key)}.parquet"

    @staticmethod
    def _safe_key(value: str) -> str:
        return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value).strip().upper()) or "EMPTY"

    @staticmethod
    def _is_fresh(path: Path, max_age_days: int) -> bool:
        if not path.exists():
            return False
        age = pd.Timestamp.now() - pd.Timestamp.fromtimestamp(path.stat().st_mtime)
        return age <= pd.Timedelta(days=max_age_days)

    @staticmethod
    def _read_cache(path: Path) -> pd.DataFrame | None:
        if not path.exists():
            return None
        try:
            return pd.read_parquet(path)
        except Exception:
            csv_path = path.with_suffix(".csv")
            if csv_path.exists():
                return pd.read_csv(csv_path)
            return None

    @staticmethod
    def _write_cache(path: Path, data: pd.DataFrame) -> None:
        try:
            data.to_parquet(path, index=False)
        except Exception:
            data.to_csv(path.with_suffix(".csv"), index=False)

    @staticmethod
    def _metadata_path(path: Path) -> Path:
        return path.with_suffix(".metadata.json")

    @classmethod
    def _read_cache_metadata(cls, path: Path) -> dict[str, Any] | None:
        metadata_path = cls._metadata_path(path)
        if not metadata_path.exists():
            return None
        try:
            return json.loads(metadata_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    @classmethod
    def _write_cache_metadata(cls, path: Path, metadata: dict[str, Any]) -> None:
        if not metadata:
            return
        cls._metadata_path(path).write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _latest_date(data: pd.DataFrame) -> str | None:
        for column in ("date", "time", "trading_date", "tradingDate", "datetime"):
            if column in data.columns:
                dates = pd.to_datetime(data[column], errors="coerce").dropna()
                if not dates.empty:
                    return dates.max().date().isoformat()
        return None

    @staticmethod
    def _today() -> str:
        return date.today().isoformat()
