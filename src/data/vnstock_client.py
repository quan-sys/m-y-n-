from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import contextlib
import importlib
import io
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


class VnstockClient:
    """Small adapter around vnstock so pipeline code is source-agnostic."""

    def __init__(
        self,
        cache_dir: str | Path = CACHE_DIR,
        source: str = "vnstock",
        listing_source: str = "kbs",
        quote_source: str = "VCI",
        company_source: str = "KBS",
        min_sleep_seconds: float = 0.15,
        max_sleep_seconds: float = 0.65,
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

    def list_symbols(self, exchanges: Iterable[str] = ("HOSE", "HNX", "UPCOM")) -> FetchResult:
        cache_path = self._cache_path("symbols", "all")
        cached = self._read_cache(cache_path)
        if self.use_cache and cached is not None and self._is_fresh(cache_path, max_age_days=7):
            return FetchResult(True, cached, source=self.source, as_of=self._today())

        try:
            data = self._fetch_symbols(tuple(exchanges))
            self._write_cache(cache_path, data)
            return FetchResult(True, data, source=self.source, as_of=self._today())
        except Exception as exc:  # noqa: BLE001 - API failures are converted to data status.
            if cached is not None:
                return FetchResult(True, cached, status="STALE_DATA", error=str(exc), source=self.source)
            return FetchResult(False, pd.DataFrame(), status="API_ERROR", error=str(exc), source=self.source)

    def get_icb_classification(self, tickers: Iterable[str] | None = None) -> FetchResult:
        cache_path = self._cache_path("icb", "classification")
        cached = self._read_cache(cache_path)
        if self.use_cache and cached is not None and self._is_fresh(cache_path, max_age_days=30):
            return FetchResult(True, cached, source=self.source, as_of=self._today())

        try:
            data = self._fetch_icb_classification()
            if tickers is not None and not data.empty and "ticker" in data.columns:
                wanted = {str(t).strip().upper() for t in tickers}
                data = data[data["ticker"].astype(str).str.upper().isin(wanted)]
            self._write_cache(cache_path, data)
            return FetchResult(True, data, source=self.source, as_of=self._today())
        except Exception as exc:  # noqa: BLE001
            if cached is not None:
                return FetchResult(True, cached, status="STALE_DATA", error=str(exc), source=self.source)
            return FetchResult(False, pd.DataFrame(), status="API_ERROR", error=str(exc), source=self.source)

    def get_price_history(self, ticker: str, months: int = 6) -> FetchResult:
        normalized = self._safe_key(ticker)
        cache_path = self._cache_path("prices", f"{normalized}_{months}m")
        cached = self._read_cache(cache_path)
        if self.use_cache and cached is not None and self._is_fresh(cache_path, max_age_days=2):
            return FetchResult(True, cached, source=self.source, as_of=self._latest_date(cached))

        try:
            data = self._fetch_price_history(ticker=ticker, months=months)
            self._write_cache(cache_path, data)
            return FetchResult(True, data, source=self.source, as_of=self._latest_date(data))
        except Exception as exc:  # noqa: BLE001
            if cached is not None:
                return FetchResult(
                    True,
                    cached,
                    status="STALE_DATA",
                    error=str(exc),
                    source=self.source,
                    as_of=self._latest_date(cached),
                )
            return FetchResult(False, pd.DataFrame(), status="API_ERROR", error=str(exc), source=self.source)

    def get_market_cap(self, ticker: str) -> FetchResult:
        normalized = self._safe_key(ticker)
        cache_path = self._cache_path("market_cap", normalized)
        cached = self._read_cache(cache_path)
        if self.use_cache and cached is not None and self._is_fresh(cache_path, max_age_days=7):
            return FetchResult(True, cached, source=self.source, as_of=self._today())

        try:
            data = self._fetch_market_cap(ticker)
            self._write_cache(cache_path, data)
            return FetchResult(True, data, source=self.source, as_of=self._today())
        except Exception as exc:  # noqa: BLE001
            if cached is not None:
                return FetchResult(True, cached, status="STALE_DATA", error=str(exc), source=self.source)
            return FetchResult(False, pd.DataFrame(), status="API_ERROR", error=str(exc), source=self.source)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    def _fetch_symbols(self, exchanges: tuple[str, ...]) -> pd.DataFrame:
        self._polite_sleep()
        vnstock = self._vnstock_module()
        listing_cls = getattr(vnstock, "Listing")
        listing = self._quiet_call(listing_cls, source=self.listing_source, random_agent=True, show_log=False)

        frames: list[pd.DataFrame] = []
        for exchange in exchanges:
            try:
                raw = self._quiet_call(listing.symbols_by_exchange, exchange=exchange)
            except TypeError:
                raw = self._quiet_call(listing.symbols_by_exchange, exchange)
            frame = self._to_frame(raw)
            if not frame.empty and "exchange" not in {c.lower() for c in frame.columns}:
                frame["exchange"] = exchange
            frames.append(frame)

        combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        if combined.empty:
            combined = self._to_frame(self._quiet_call(listing.all_symbols))
        return combined

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    def _fetch_icb_classification(self) -> pd.DataFrame:
        self._polite_sleep()
        vnstock = self._vnstock_module()
        listing_cls = getattr(vnstock, "Listing")
        listing = self._quiet_call(listing_cls, source=self.listing_source, random_agent=True, show_log=False)

        frames: list[pd.DataFrame] = []
        for method_name in ("symbols_by_industries", "industries_icb"):
            method = getattr(listing, method_name, None)
            if method is None:
                continue
            try:
                frames.append(self._to_frame(self._quiet_call(method)))
            except Exception:
                continue

        return pd.concat([f for f in frames if not f.empty], ignore_index=True) if frames else pd.DataFrame()

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
