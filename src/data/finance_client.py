from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import calendar
import contextlib
import hashlib
import importlib
import io
import json
import random
import re
import time
from typing import Any

import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

from src.data.vnstock_client import FetchResult


FUNDAMENTALS_DIR = Path(__file__).resolve().parents[2] / "data" / "fundamentals"

LAG_QUARTER = 30
LAG_SEMIANNUAL = 60
LAG_ANNUAL = 90

STATEMENT_BALANCE_SHEET = "BALANCE_SHEET"
STATEMENT_INCOME_STATEMENT = "INCOME_STATEMENT"
STATEMENT_CASH_FLOW = "CASH_FLOW"

NORMALIZED_COLUMNS = [
    "ticker",
    "company_type",
    "statement_type",
    "period_type",
    "report_period",
    "period_end",
    "available_from",
    "item_id",
    "item",
    "item_en",
    "value",
    "currency",
    "source",
    "as_of",
    "data_status",
]

FETCH_STATUS_COLUMNS = [
    "ticker",
    "company_type",
    "statement_type",
    "period_type",
    "requested_at",
    "returned_period_count",
    "source",
    "as_of",
    "data_status",
    "error",
]

_STATEMENT_METHODS = {
    STATEMENT_BALANCE_SHEET: "balance_sheet",
    STATEMENT_INCOME_STATEMENT: "income_statement",
    STATEMENT_CASH_FLOW: "cash_flow",
}

_PERIOD_COLUMN_PATTERN = re.compile(
    r"^(?:\d{4}|\d{4}-?Q[1-4]|\d{4}-?(?:H|S)[12]|\d{4}-NĂM)$",
    flags=re.IGNORECASE,
)

_SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(
        r"(?i)((?:api[_-]?key|access[_-]?token|password|client[_-]?secret)\s*[:=]\s*)"
        r"[^\s,;]+"
    ),
]


@dataclass(frozen=True)
class PeriodInfo:
    report_period: str
    period_type: str
    period_end: date
    lag_days: int


@dataclass(frozen=True)
class CachedObservation:
    data: pd.DataFrame
    metadata: dict[str, Any]
    path: Path


class FinanceClient:
    """Point-in-time adapter around the public ``vnstock.api.Finance`` API."""

    def __init__(
        self,
        cache_dir: str | Path = FUNDAMENTALS_DIR,
        source: str = "vnstock_VCI_financial",
        provider: str = "VCI",
        min_sleep_seconds: float = 2.8,
        max_sleep_seconds: float = 3.6,
        use_cache: bool = True,
        cache_max_age_days: int | None = None,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.source = source
        self.provider = provider.upper()
        self.min_sleep_seconds = min_sleep_seconds
        self.max_sleep_seconds = max_sleep_seconds
        self.use_cache = use_cache
        self.cache_max_age_days = cache_max_age_days
        self._terminal_api_error: str | None = None
        self._status_records: list[dict[str, Any]] = []

    def get_balance_sheet(
        self,
        ticker: str,
        period: str,
        *,
        company_type: str = "UNKNOWN",
        expect_large_company_scale: bool = False,
    ) -> FetchResult:
        return self._get_statement(
            ticker,
            period,
            STATEMENT_BALANCE_SHEET,
            company_type=company_type,
            expect_large_company_scale=expect_large_company_scale,
        )

    def get_income_statement(
        self,
        ticker: str,
        period: str,
        *,
        company_type: str = "UNKNOWN",
        expect_large_company_scale: bool = False,
    ) -> FetchResult:
        return self._get_statement(
            ticker,
            period,
            STATEMENT_INCOME_STATEMENT,
            company_type=company_type,
            expect_large_company_scale=expect_large_company_scale,
        )

    def get_cash_flow(
        self,
        ticker: str,
        period: str,
        *,
        company_type: str = "UNKNOWN",
        expect_large_company_scale: bool = False,
    ) -> FetchResult:
        return self._get_statement(
            ticker,
            period,
            STATEMENT_CASH_FLOW,
            company_type=company_type,
            expect_large_company_scale=expect_large_company_scale,
        )

    def fetch_status_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self._status_records, columns=FETCH_STATUS_COLUMNS)

    def write_fetch_status(self, path: str | Path | None = None) -> Path:
        output_path = Path(path) if path is not None else self.cache_dir / "fetch_status.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.fetch_status_frame().to_csv(output_path, index=False)
        return output_path

    def _get_statement(
        self,
        ticker: str,
        period: str,
        statement_type: str,
        *,
        company_type: str,
        expect_large_company_scale: bool,
    ) -> FetchResult:
        normalized_ticker = _normalize_ticker(ticker)
        normalized_period = _normalize_requested_period(period)
        normalized_company_type = _normalize_company_type(company_type)
        requested_at = _utc_now()
        raw: pd.DataFrame | None = None
        raw_observation_path: Path | None = None
        raw_period_count = 0
        raw_shape: list[int] = [0, 0]

        cached = self._latest_cached(normalized_ticker, statement_type, normalized_period)
        if self.use_cache and cached is not None and self._cache_is_fresh(cached.path):
            result = FetchResult(
                True,
                cached.data,
                status="OK",
                source=self.source,
                as_of=str(cached.metadata.get("as_of") or _today()),
                metadata={
                    **cached.metadata,
                    "cache_state": "CACHED",
                    "cache_hit": True,
                },
            )
            self._record_status(
                result,
                normalized_ticker,
                normalized_company_type,
                statement_type,
                normalized_period,
                requested_at,
            )
            return result

        if self._terminal_api_error:
            result = self._terminal_error_result()
            self._record_status(
                result,
                normalized_ticker,
                normalized_company_type,
                statement_type,
                normalized_period,
                requested_at,
            )
            return result

        try:
            raw = self._fetch_statement(normalized_ticker, normalized_period, statement_type)
            as_of = _today()
            raw_period_count = len(_period_columns(raw)) if not raw.empty else 0
            raw_shape = [int(raw.shape[0]), int(raw.shape[1])]
            raw_observation_path = self._write_raw_observation(
                raw=raw,
                ticker=normalized_ticker,
                statement_type=statement_type,
                period=normalized_period,
                as_of=as_of,
            )
            if raw.empty:
                tidy = empty_financial_frame()
                result = FetchResult(
                    True,
                    tidy,
                    status="MISSING_DATA",
                    error=f"vnstock returned no {statement_type} data for {normalized_ticker}",
                    source=self.source,
                    as_of=as_of,
                    metadata={
                        "cache_state": "FETCHED",
                        "cache_hit": False,
                        "returned_period_count": raw_period_count,
                        "raw_shape": raw_shape,
                    },
                )
            else:
                tidy = normalize_financial_statement(
                    raw,
                    ticker=normalized_ticker,
                    statement_type=statement_type,
                    company_type=normalized_company_type,
                    source=self.source,
                    as_of=as_of,
                )
                if expect_large_company_scale:
                    validate_large_company_magnitude(tidy)
                result = FetchResult(
                    True,
                    tidy,
                    status="OK",
                    source=self.source,
                    as_of=as_of,
                    metadata={
                        "cache_state": "FETCHED",
                        "cache_hit": False,
                        "returned_period_count": raw_period_count,
                        "raw_shape": raw_shape,
                    },
                )

            observation_path = self._write_normalized_observation(
                observation_dir=raw_observation_path,
                tidy=tidy,
                ticker=normalized_ticker,
                statement_type=statement_type,
                period=normalized_period,
                result=result,
                requested_at=requested_at,
            )
            result = FetchResult(
                result.ok,
                result.data,
                status=result.status,
                error=result.error,
                source=result.source,
                as_of=result.as_of,
                metadata={**(result.metadata or {}), "observation_path": str(observation_path)},
            )
        except BaseException as exc:  # noqa: BLE001 - source failures become explicit data status.
            self._record_terminal_error(exc)
            error = _redact_secrets(self._terminal_api_error or str(exc) or type(exc).__name__)
            if cached is not None:
                result = FetchResult(
                    True,
                    cached.data,
                    status="STALE_DATA",
                    error=error,
                    source=self.source,
                    as_of=str(cached.metadata.get("as_of") or ""),
                    metadata={
                        **cached.metadata,
                        "cache_state": "STALE_DATA",
                        "cache_hit": True,
                        "stale": True,
                    },
                )
            else:
                result = FetchResult(
                    False,
                    empty_financial_frame(),
                    status="API_ERROR",
                    error=error,
                    source=self.source,
                    as_of=_today(),
                    metadata={"cache_state": "API_ERROR", "cache_hit": False, "returned_period_count": 0},
                )

            if raw_observation_path is not None:
                self._write_failed_observation(
                    observation_dir=raw_observation_path,
                    ticker=normalized_ticker,
                    statement_type=statement_type,
                    period=normalized_period,
                    requested_at=requested_at,
                    as_of=_today(),
                    returned_period_count=raw_period_count,
                    raw_shape=raw_shape,
                    error=error,
                )
                result = FetchResult(
                    result.ok,
                    result.data,
                    status=result.status,
                    error=result.error,
                    source=result.source,
                    as_of=result.as_of,
                    metadata={
                        **(result.metadata or {}),
                        "returned_period_count": raw_period_count,
                        "raw_shape": raw_shape,
                        "observation_path": str(raw_observation_path),
                    },
                )

        self._record_status(
            result,
            normalized_ticker,
            normalized_company_type,
            statement_type,
            normalized_period,
            requested_at,
        )
        return result

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    def _fetch_statement(self, ticker: str, period: str, statement_type: str) -> pd.DataFrame:
        self._polite_sleep()
        financial_module = importlib.import_module("vnstock.api.financial")
        finance_class = getattr(financial_module, "Finance")
        finance = _quiet_call(
            finance_class,
            source=self.provider,
            symbol=ticker,
            period=period,
            get_all=True,
            show_log=False,
        )
        method = getattr(finance, _STATEMENT_METHODS[statement_type])
        raw = _quiet_call(method, period=period, lang="en", dropna=False, show_log=False)
        return _to_frame(raw)

    def _latest_cached(self, ticker: str, statement_type: str, period: str) -> CachedObservation | None:
        base = self.cache_dir / _safe_key(ticker) / statement_type.lower() / period
        if not base.exists():
            return None
        candidates = list(base.rglob("normalized.parquet")) + list(base.rglob("normalized.csv"))
        if not candidates:
            return None
        latest = max(candidates, key=lambda item: item.stat().st_mtime)
        data = _read_frame(latest)
        if data is None:
            return None
        metadata_path = latest.parent / "metadata.json"
        metadata = _read_json(metadata_path)
        return CachedObservation(data=data, metadata=metadata, path=latest)

    def _cache_is_fresh(self, path: Path) -> bool:
        if self.cache_max_age_days is None:
            return True
        age = pd.Timestamp.now() - pd.Timestamp.fromtimestamp(path.stat().st_mtime)
        return age <= pd.Timedelta(days=self.cache_max_age_days)

    def _write_raw_observation(
        self,
        *,
        raw: pd.DataFrame,
        ticker: str,
        statement_type: str,
        period: str,
        as_of: str,
    ) -> Path:
        content_hash = _frame_hash(raw)
        observation_dir = (
            self.cache_dir
            / _safe_key(ticker)
            / statement_type.lower()
            / period
            / str(as_of or _today())
            / content_hash
        )
        observation_dir.mkdir(parents=True, exist_ok=True)
        _write_frame_once(observation_dir / "raw.parquet", raw)
        return observation_dir

    def _write_normalized_observation(
        self,
        *,
        observation_dir: Path,
        tidy: pd.DataFrame,
        ticker: str,
        statement_type: str,
        period: str,
        result: FetchResult,
        requested_at: str,
    ) -> Path:
        _write_frame_once(observation_dir / "normalized.parquet", tidy)
        metadata_path = observation_dir / "metadata.json"
        if not metadata_path.exists():
            metadata = {
                "ticker": ticker,
                "statement_type": statement_type,
                "period": period,
                "requested_at": requested_at,
                "as_of": result.as_of,
                "source": result.source,
                "data_status": result.status,
                "returned_period_count": int(tidy["report_period"].nunique()) if not tidy.empty else 0,
                "content_hash": observation_dir.name,
            }
            metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        return observation_dir

    def _write_failed_observation(
        self,
        *,
        observation_dir: Path,
        ticker: str,
        statement_type: str,
        period: str,
        requested_at: str,
        as_of: str,
        returned_period_count: int,
        raw_shape: list[int],
        error: str,
    ) -> Path:
        failure_path = observation_dir / "failure.json"
        if not failure_path.exists():
            failure = {
                "ticker": ticker,
                "statement_type": statement_type,
                "period": period,
                "requested_at": requested_at,
                "as_of": as_of,
                "source": self.source,
                "data_status": "API_ERROR",
                "returned_period_count": returned_period_count,
                "raw_shape": raw_shape,
                "error": _redact_secrets(error),
                "content_hash": observation_dir.name,
            }
            failure_path.write_text(json.dumps(failure, ensure_ascii=False, indent=2), encoding="utf-8")
        return observation_dir

    def _record_status(
        self,
        result: FetchResult,
        ticker: str,
        company_type: str,
        statement_type: str,
        period: str,
        requested_at: str,
    ) -> None:
        returned_period_count = 0
        if result.metadata and result.metadata.get("returned_period_count") is not None:
            returned_period_count = int(result.metadata["returned_period_count"])
        elif isinstance(result.data, pd.DataFrame) and "report_period" in result.data:
            returned_period_count = int(result.data["report_period"].nunique())
        self._status_records.append(
            {
                "ticker": ticker,
                "company_type": company_type,
                "statement_type": statement_type,
                "period_type": "QUARTER" if period == "quarter" else "ANNUAL",
                "requested_at": requested_at,
                "returned_period_count": returned_period_count,
                "source": result.source,
                "as_of": result.as_of,
                "data_status": result.status,
                "error": _redact_secrets(result.error or ""),
            }
        )

    def _record_terminal_error(self, exc: BaseException) -> None:
        if isinstance(exc, KeyboardInterrupt):
            raise exc
        if isinstance(exc, SystemExit):
            self._terminal_api_error = "vnstock terminated the request, likely due to API rate limit or access limits"
        elif isinstance(exc, ImportError):
            self._terminal_api_error = _redact_secrets(str(exc) or type(exc).__name__)

    def _terminal_error_result(self) -> FetchResult:
        return FetchResult(
            False,
            empty_financial_frame(),
            status="API_ERROR",
            error=self._terminal_api_error,
            source=self.source,
            as_of=_today(),
            metadata={"cache_state": "API_ERROR", "cache_hit": False, "returned_period_count": 0},
        )

    def _polite_sleep(self) -> None:
        time.sleep(random.uniform(self.min_sleep_seconds, self.max_sleep_seconds))


def normalize_financial_statement(
    data: Any,
    *,
    ticker: str,
    statement_type: str,
    company_type: str,
    source: str,
    as_of: str,
) -> pd.DataFrame:
    frame = _to_frame(data)
    if frame.empty:
        return empty_financial_frame()
    if statement_type not in _STATEMENT_METHODS:
        raise ValueError(f"unsupported statement_type: {statement_type}")
    if "item_id" not in frame.columns:
        raise ValueError("financial statement is missing required item_id")

    work = frame.copy()
    for column in ("item", "item_en"):
        if column not in work.columns:
            work[column] = ""

    missing_item_id = work["item_id"].isna() | (work["item_id"].astype(str).str.strip() == "")
    if bool(missing_item_id.any()):
        raise ValueError(f"financial statement has {int(missing_item_id.sum())} rows with missing item_id")

    period_columns = _period_columns(work)
    if not period_columns:
        raise ValueError("financial statement has no recognized period columns")

    period_info = {str(column): parse_report_period(column) for column in period_columns}
    melted = work[["item", "item_en", "item_id", *period_columns]].melt(
        id_vars=["item", "item_en", "item_id"],
        value_vars=period_columns,
        var_name="_source_period",
        value_name="_raw_value",
    )

    raw_value = melted["_raw_value"]
    raw_text = raw_value.astype("string").str.strip()
    is_missing = raw_value.isna() | raw_text.isna() | raw_text.isin(["", "nan", "None", "<NA>"])
    numeric = pd.to_numeric(raw_text.str.replace(",", "", regex=False), errors="coerce")
    invalid = ~is_missing & numeric.isna()
    if bool(invalid.any()):
        raise ValueError(f"financial statement has {int(invalid.sum())} non-numeric values")

    melted["value"] = numeric
    melted.loc[is_missing, "value"] = pd.NA
    melted["item_id"] = melted["item_id"].astype(str).str.strip()
    melted["item"] = melted["item"].fillna("").astype(str)
    melted["item_en"] = melted["item_en"].fillna("").astype(str)

    melted["report_period"] = melted["_source_period"].map(
        lambda value: period_info[str(value)].report_period
    )
    melted["period_type"] = melted["_source_period"].map(
        lambda value: period_info[str(value)].period_type
    )
    melted["period_end"] = melted["_source_period"].map(
        lambda value: period_info[str(value)].period_end.isoformat()
    )
    melted["available_from"] = melted["_source_period"].map(
        lambda value: (
            period_info[str(value)].period_end + timedelta(days=period_info[str(value)].lag_days)
        ).isoformat()
    )
    melted["ticker"] = _normalize_ticker(ticker)
    melted["company_type"] = _normalize_company_type(company_type)
    melted["statement_type"] = statement_type
    melted["currency"] = "VND"
    melted["source"] = str(source).strip()
    melted["as_of"] = str(as_of)
    melted["data_status"] = melted["value"].notna().map({True: "OK", False: "MISSING_DATA"})

    result = melted[NORMALIZED_COLUMNS].copy()
    key = ["ticker", "statement_type", "report_period", "item_id"]
    duplicated = result.duplicated(subset=key, keep=False)
    if bool(duplicated.any()):
        raise ValueError(f"financial statement has {int(duplicated.sum())} rows with duplicate tidy keys")
    if bool(result["available_from"].isna().any()):
        raise ValueError("financial statement has missing available_from")
    return result.reset_index(drop=True)


def parse_report_period(value: Any) -> PeriodInfo:
    text = str(value).strip().upper().replace(" ", "")
    quarter = re.fullmatch(r"(\d{4})-?Q([1-4])", text)
    if quarter:
        year = int(quarter.group(1))
        quarter_number = int(quarter.group(2))
        month = quarter_number * 3
        end = date(year, month, calendar.monthrange(year, month)[1])
        return PeriodInfo(f"{year}Q{quarter_number}", "QUARTER", end, LAG_QUARTER)

    semiannual = re.fullmatch(r"(\d{4})-?(?:H|S)([12])", text)
    if semiannual:
        year = int(semiannual.group(1))
        half = int(semiannual.group(2))
        month = 6 if half == 1 else 12
        end = date(year, month, calendar.monthrange(year, month)[1])
        return PeriodInfo(f"{year}H{half}", "SEMIANNUAL", end, LAG_SEMIANNUAL)

    annual = re.fullmatch(r"(\d{4})(?:-NĂM)?", text)
    if annual:
        year = int(annual.group(1))
        return PeriodInfo(str(year), "ANNUAL", date(year, 12, 31), LAG_ANNUAL)

    raise ValueError(f"unrecognized report period: {value}")


def validate_large_company_magnitude(data: pd.DataFrame) -> None:
    values = pd.to_numeric(data.get("value", pd.Series(dtype=float)), errors="coerce").abs().dropna()
    values = values[values > 0]
    if values.empty:
        return
    maximum = float(values.max())
    if maximum < 1_000_000_000:
        raise ValueError(
            "large-company financial statement failed raw-VND magnitude check: "
            f"maximum absolute value {maximum:g} is below 1e9 VND"
        )


def empty_financial_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=NORMALIZED_COLUMNS)


def _period_columns(frame: pd.DataFrame) -> list[Any]:
    attrs_periods = list(frame.attrs.get("periods", []))
    if attrs_periods:
        valid = [column for column in attrs_periods if column in frame.columns]
        if valid:
            return valid
    return [column for column in frame.columns if _PERIOD_COLUMN_PATTERN.fullmatch(str(column).strip())]


def _normalize_requested_period(period: str) -> str:
    normalized = str(period).strip().lower()
    if normalized not in {"quarter", "year"}:
        raise ValueError("period must be 'quarter' or 'year'")
    return normalized


def _normalize_ticker(ticker: str) -> str:
    normalized = str(ticker).strip().upper()
    if not normalized or not re.fullmatch(r"[A-Z0-9._-]+", normalized):
        raise ValueError(f"invalid ticker: {ticker}")
    return normalized


def _normalize_company_type(company_type: str) -> str:
    normalized = str(company_type).strip().upper()
    return normalized or "UNKNOWN"


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


def _quiet_call(func: Any, *args: Any, **kwargs: Any) -> Any:
    with contextlib.redirect_stdout(io.StringIO()):
        return func(*args, **kwargs)


def _frame_hash(frame: pd.DataFrame) -> str:
    digest = hashlib.sha256()
    digest.update(json.dumps([str(column) for column in frame.columns], ensure_ascii=False).encode("utf-8"))
    if not frame.empty:
        digest.update(pd.util.hash_pandas_object(frame, index=True).values.tobytes())
    return digest.hexdigest()[:16]


def _write_frame_once(path: Path, data: pd.DataFrame) -> Path:
    if path.exists() or path.with_suffix(".csv").exists():
        return path if path.exists() else path.with_suffix(".csv")
    try:
        data.to_parquet(path, index=False)
        return path
    except Exception:
        csv_path = path.with_suffix(".csv")
        data.to_csv(csv_path, index=False)
        return csv_path


def _read_frame(path: Path) -> pd.DataFrame | None:
    try:
        if path.suffix == ".parquet":
            return pd.read_parquet(path)
        return pd.read_csv(path)
    except Exception:
        return None


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _redact_secrets(value: str) -> str:
    redacted = str(value)
    for pattern in _SECRET_PATTERNS:
        if pattern.groups:
            redacted = pattern.sub(lambda match: f"{match.group(1)}[REDACTED]", redacted)
        else:
            redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def _safe_key(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value).strip().upper()) or "EMPTY"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _today() -> str:
    return date.today().isoformat()
