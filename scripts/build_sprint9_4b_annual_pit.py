from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
from typing import Any, Iterable
from zoneinfo import ZoneInfo

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

from scripts.probe_fundamentals_coverage import classify_universe  # noqa: E402
from scripts.audit_sprint6_readiness import (  # noqa: E402
    PROPOSED_FRANCHISE_MIN_YEARS,
)
from scripts.verify_required_items_v1_sample_sprint3 import (  # noqa: E402
    REQUIRED_ITEMS,
)
from src.data.finance_client import (  # noqa: E402
    LAG_ANNUAL,
    NORMALIZED_COLUMNS,
    FinanceClient,
)
from src.screener.step1_data import (  # noqa: E402
    FORMULA_INPUT_MAP,
    M_SCORE_INPUTS,
)


TIME_ZONE = ZoneInfo("Asia/Ho_Chi_Minh")
UNIVERSE_PATH = ROOT / "data" / "universe.csv"
REPORT_PATH = ROOT / "docs" / "REPORT_SPRINT_9_4B_ANNUAL_PIT.md"
RUN_STATE_ROOT = ROOT / "data" / "fundamentals" / "run_state"
OUTPUT_ROOT = ROOT / "data" / "fundamentals" / "annual_pit"
REQUIRED_ITEMS_SOURCE = (
    ROOT / "scripts" / "verify_required_items_v1_sample_sprint3.py"
)
STEP1_DATA_SOURCE = ROOT / "src" / "screener" / "step1_data.py"
STEP1_CLEANING_SOURCE = ROOT / "src" / "screener" / "step1_cleaning.py"
FSCORE_SOURCE = ROOT / "scripts" / "build_sprint6_fscore.py"
FRANCHISE_SOURCE = ROOT / "scripts" / "build_sprint6_franchise.py"
EXPECTED_TICKER_COUNT = 243
MAX_API_ERROR_SHARE = Decimal("0.05")
UNIT_MIN_VND = Decimal("1e9")
UNIT_MAX_VND = Decimal("1e15")
FIRST_COVERAGE_YEAR = 2018
VALUE_BASKET_START = date(2019, 3, 31)
STATEMENTS = ("balance_sheet", "income_statement", "cash_flow")
STATEMENT_METHODS = {
    "balance_sheet": FinanceClient.get_balance_sheet,
    "income_statement": FinanceClient.get_income_statement,
    "cash_flow": FinanceClient.get_cash_flow,
}
OUTPUT_COLUMNS = (
    "ticker",
    "fiscal_year",
    "period_end",
    "available_from",
    "statement_type",
    "item_id",
    "value",
    "currency",
    "source",
    "as_of",
    "data_status",
)
RESTATED_LIMITATION = """Data fetched today is AS-RESTATED, not as-originally-
reported. For past years this is an unfixable look-ahead bias that `available_from` does NOT remove:
the DATE the number became public is modelled, but the VALUE is today's restated value. This table
is therefore QUASI point-in-time and is valid for RELATIVE walk-forward comparison only."""


def derive_annual_dates(fiscal_year: int | str) -> tuple[str, str]:
    year = int(fiscal_year)
    period_end = date(year, 12, 31)
    available_from = period_end + timedelta(days=LAG_ANNUAL)
    return period_end.isoformat(), available_from.isoformat()


def internal_gap_years(years: Iterable[int | str]) -> list[int]:
    observed = sorted({int(value) for value in years})
    if len(observed) < 2:
        return []
    present = set(observed)
    return [
        year
        for year in range(observed[0], observed[-1] + 1)
        if year not in present
    ]


def _source_assignment(path: Path, target_name: str) -> tuple[str, int, int]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        if any(
            isinstance(target, ast.Name) and target.id == target_name
            for target in targets
        ):
            segment = ast.get_source_segment(source, node)
            if segment is None:
                raise ValueError(f"cannot extract {target_name} from {path}")
            return segment, node.lineno, int(node.end_lineno or node.lineno)
    raise ValueError(f"{target_name} not found in {path}")


def required_items_source_text() -> tuple[str, int, int]:
    return _source_assignment(REQUIRED_ITEMS_SOURCE, "REQUIRED_ITEMS")


def _string_assignments_between(
    path: Path, start_name: str, end_name: str
) -> tuple[dict[str, str], int, int]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    assignments: list[tuple[str, str, int, int]] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            continue
        if isinstance(value, str):
            assignments.append(
                (
                    target.id,
                    value,
                    node.lineno,
                    int(node.end_lineno or node.lineno),
                )
            )
    names = [item[0] for item in assignments]
    start = names.index(start_name)
    end = names.index(end_name)
    chosen = assignments[start : end + 1]
    return (
        {name: value for name, value, _, _ in chosen},
        chosen[0][2],
        chosen[-1][3],
    )


def required_item_ids() -> tuple[str, ...]:
    return tuple(
        item_id
        for statement_type in REQUIRED_ITEMS
        for item_id in REQUIRED_ITEMS[statement_type]
    )


def relevant_tickers() -> list[str]:
    universe = classify_universe(pd.read_csv(UNIVERSE_PATH))
    tickers = sorted(
        universe.loc[
            universe["sector_class"].eq("SCREENER_RELEVANT"), "ticker"
        ]
        .astype(str)
        .str.strip()
        .str.upper()
        .tolist()
    )
    if len(tickers) != EXPECTED_TICKER_COUNT:
        raise ValueError(
            f"expected {EXPECTED_TICKER_COUNT} SCREENER_RELEVANT tickers, "
            f"got {len(tickers)}"
        )
    if "VNM" not in tickers:
        raise ValueError("VNM is missing from the SCREENER_RELEVANT universe")
    return tickers


def _run_paths(run_date: str) -> dict[str, Path]:
    annual_root = RUN_STATE_ROOT / run_date / "annual"
    return {
        "annual_root": annual_root,
        "normalized": annual_root / "normalized",
        "status": annual_root / "status",
        "finance_cache": annual_root / "finance_cache",
        "output": OUTPUT_ROOT
        / run_date
        / "annual_items_point_in_time.csv.gz",
    }


def _statement_path(paths: dict[str, Path], ticker: str, statement: str) -> Path:
    return paths["normalized"] / ticker / f"{statement}.parquet"


def _status_path(paths: dict[str, Path], ticker: str, statement: str) -> Path:
    return paths["status"] / ticker / f"{statement}.json"


def _write_parquet_atomic(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.parquet")
    frame.to_parquet(temporary, index=False)
    temporary.replace(path)


def _write_json_atomic(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.json")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.replace(path)


def _effective_status(result: Any) -> str:
    metadata = result.metadata or {}
    return str(metadata.get("data_status") or result.status)


def _status_record(
    ticker: str,
    statement: str,
    result: Any,
    frame: pd.DataFrame,
) -> dict[str, Any]:
    annual = (
        frame.loc[frame["period_type"].astype(str).eq("ANNUAL")]
        if not frame.empty
        else frame
    )
    return {
        "ticker": ticker,
        "statement": statement,
        "data_status": _effective_status(result),
        "ok": bool(result.ok),
        "error": str(result.error or ""),
        "source": str(result.source or ""),
        "as_of": str(result.as_of or ""),
        "n_years": (
            int(annual["report_period"].astype(str).nunique())
            if not annual.empty
            else 0
        ),
        "cache_state": str((result.metadata or {}).get("cache_state") or ""),
    }


def _load_status(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_all(tickers: list[str], paths: dict[str, Path]) -> None:
    client = FinanceClient(cache_dir=paths["finance_cache"], use_cache=True)
    fetch_order = ["VNM", *[ticker for ticker in tickers if ticker != "VNM"]]
    for position, ticker in enumerate(fetch_order, start=1):
        for statement in STATEMENTS:
            frame_path = _statement_path(paths, ticker, statement)
            status_path = _status_path(paths, ticker, statement)
            if frame_path.exists() and status_path.exists():
                frame = pd.read_parquet(frame_path)
                status = _load_status(status_path)
                print(
                    f"[{position}/{len(tickers)}] {ticker} {statement}: "
                    f"RESUME status={status['data_status']}; "
                    f"years={status['n_years']}",
                    flush=True,
                )
            else:
                result = STATEMENT_METHODS[statement](
                    client,
                    ticker,
                    "year",
                    company_type="NON_FINANCIAL",
                )
                frame = (
                    result.data.copy()
                    if isinstance(result.data, pd.DataFrame)
                    else pd.DataFrame(columns=NORMALIZED_COLUMNS)
                )
                if frame.empty:
                    frame = pd.DataFrame(columns=NORMALIZED_COLUMNS)
                status = _status_record(ticker, statement, result, frame)
                _write_parquet_atomic(frame, frame_path)
                _write_json_atomic(status, status_path)
                print(
                    f"[{position}/{len(tickers)}] {ticker} {statement}: "
                    f"status={status['data_status']}; years={status['n_years']}; "
                    f"cache_state={status['cache_state']}",
                    flush=True,
                )
            if ticker == "VNM" and statement == "income_statement":
                if int(status["n_years"]) < 6:
                    raise RuntimeError(
                        "STOP: VNM returned fewer than 6 fiscal years: "
                        f"{status['n_years']}"
                    )


def load_run_state(
    tickers: list[str], paths: dict[str, Path]
) -> tuple[dict[str, dict[str, pd.DataFrame]], list[dict[str, Any]]]:
    frames: dict[str, dict[str, pd.DataFrame]] = {}
    statuses: list[dict[str, Any]] = []
    for ticker in tickers:
        frames[ticker] = {}
        for statement in STATEMENTS:
            frame_path = _statement_path(paths, ticker, statement)
            status_path = _status_path(paths, ticker, statement)
            if not frame_path.exists() or not status_path.exists():
                raise FileNotFoundError(
                    f"incomplete run state: {ticker}/{statement}"
                )
            frames[ticker][statement] = pd.read_parquet(frame_path)
            statuses.append(_load_status(status_path))
    return frames, statuses


def select_required_item_rows(
    statement_frames: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    selected: list[pd.DataFrame] = []
    for statement_name, method in STATEMENT_METHODS.items():
        frame = statement_frames.get(statement_name, pd.DataFrame())
        if frame.empty:
            continue
        missing = sorted(set(NORMALIZED_COLUMNS) - set(frame.columns))
        if missing:
            raise ValueError(
                f"{statement_name} normalized cache missing columns: {missing}"
            )
        statement_type = method.__name__.removeprefix("get_").upper()
        required = REQUIRED_ITEMS.get(statement_type, ())
        rows = frame.loc[
            frame["period_type"].astype(str).eq("ANNUAL")
            & frame["item_id"].astype(str).isin(required)
        ].copy()
        if not rows.empty:
            selected.append(rows)
    if not selected:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    combined = pd.concat(selected, ignore_index=True)
    combined["fiscal_year"] = combined["report_period"].astype(str)
    output = combined.loc[:, OUTPUT_COLUMNS].sort_values(
        ["ticker", "fiscal_year", "item_id"], kind="stable"
    ).reset_index(drop=True)
    duplicate = output.duplicated(
        ["ticker", "fiscal_year", "item_id"], keep=False
    )
    if bool(duplicate.any()):
        raise ValueError(
            "duplicate output keys: "
            + output.loc[
                duplicate, ["ticker", "fiscal_year", "item_id"]
            ]
            .drop_duplicates()
            .to_json(orient="records")
        )
    return output


def assemble_output(
    tickers: list[str],
    frames: dict[str, dict[str, pd.DataFrame]],
) -> pd.DataFrame:
    parts = [select_required_item_rows(frames[ticker]) for ticker in tickers]
    usable = [frame for frame in parts if not frame.empty]
    if not usable:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return (
        pd.concat(usable, ignore_index=True)
        .loc[:, OUTPUT_COLUMNS]
        .sort_values(["ticker", "fiscal_year", "item_id"], kind="stable")
        .reset_index(drop=True)
    )


def validate_stop_gates(
    output: pd.DataFrame,
    tickers: list[str],
    statuses: list[dict[str, Any]],
) -> None:
    vnm_years = output.loc[output["ticker"].eq("VNM"), "fiscal_year"].nunique()
    if vnm_years < 6:
        raise RuntimeError(
            f"STOP: VNM returned fewer than 6 fiscal years: {vnm_years}"
        )
    api_error_tickers = sorted(
        {
            str(record["ticker"])
            for record in statuses
            if str(record["data_status"]) == "API_ERROR"
        }
    )
    if Decimal(len(api_error_tickers)) / Decimal(len(tickers)) > MAX_API_ERROR_SHARE:
        raise RuntimeError(
            "STOP: more than 5 percent of tickers ended in API_ERROR: "
            f"{len(api_error_tickers)}/{len(tickers)}; "
            f"tickers={api_error_tickers}"
        )
    if output.empty:
        raise RuntimeError("STOP: assembled annual output is empty")
    period_end = pd.to_datetime(output["period_end"], errors="raise")
    available_from = pd.to_datetime(output["available_from"], errors="raise")
    invalid_available = output.loc[
        available_from.le(period_end),
        ["ticker", "fiscal_year", "period_end", "available_from", "item_id"],
    ]
    if not invalid_available.empty:
        raise RuntimeError(
            "STOP: available_from is on or before period_end: "
            + invalid_available.to_json(orient="records")
        )
    invalid_period = output.loc[
        ~(
            period_end.dt.month.eq(12)
            & period_end.dt.day.eq(31)
            & period_end.dt.year.astype(str).eq(output["fiscal_year"])
        ),
        ["ticker", "fiscal_year", "period_end", "item_id"],
    ]
    if not invalid_period.empty:
        raise RuntimeError(
            "STOP: invalid annual period_end: "
            + invalid_period.to_json(orient="records")
        )


def write_deterministic_gzip_csv(frame: pd.DataFrame, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as binary:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=binary,
            compresslevel=9,
            mtime=0,
        ) as compressed:
            with io.TextIOWrapper(
                compressed, encoding="utf-8", newline=""
            ) as text:
                frame.to_csv(text, index=False, lineterminator="\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _all_normalized_rows(
    frames: dict[str, dict[str, pd.DataFrame]],
) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for ticker_frames in frames.values():
        for frame in ticker_frames.values():
            if not frame.empty:
                parts.append(
                    frame.loc[
                        frame["period_type"].astype(str).eq("ANNUAL")
                    ].copy()
                )
    if not parts:
        return pd.DataFrame(columns=NORMALIZED_COLUMNS)
    return pd.concat(parts, ignore_index=True)


def _roles_from_formula_names(
    formula_names: Iterable[str],
) -> dict[str, set[int]]:
    roles: dict[str, set[int]] = defaultdict(set)
    for formula in formula_names:
        for _, item_id, period_role in FORMULA_INPUT_MAP[formula].values():
            roles[item_id].add(0 if period_role == "N" else -1)
    return dict(roles)


def gate_definitions() -> dict[str, dict[str, Any]]:
    fscore, fscore_start, fscore_end = _string_assignments_between(
        FSCORE_SOURCE, "NET_INCOME", "COMMON_SHARES"
    )
    franchise, franchise_start, franchise_end = _string_assignments_between(
        FRANCHISE_SOURCE, "PBT", "COGS"
    )
    fscore_offsets = {
        "NET_INCOME": {0, -1},
        "PARENT_NET_INCOME": {0},
        "CFO": {0},
        "TOTAL_ASSETS": {0, -1, -2},
        "LONG_TERM_DEBT": {0, -1},
        "CURRENT_ASSETS": {0, -1},
        "CURRENT_LIABILITIES": {0, -1},
        "REVENUE": {0, -1},
        "GROSS_PROFIT": {0, -1},
        "COGS": {0, -1},
        "ISSUE_PROCEEDS": {0},
        "COMMON_SHARES": {0, -1},
    }
    franchise_offsets = {
        "PBT": {0},
        "INTEREST": {0},
        "EQUITY": {0, -1},
        "SHORT_DEBT": {0, -1},
        "LONG_DEBT": {0, -1},
        "CASH": {0, -1},
        "NET_SALES": {0},
        "GROSS_PROFIT": {0},
        "COGS": {0},
    }
    return {
        "ACCRUALS_STA": {
            "roles": _roles_from_formula_names(("STA",)),
            "source": "src/screener/step1_data.py:88-130",
            "history": "N and N-1",
        },
        "ACCRUALS_SNOA": {
            "roles": _roles_from_formula_names(("SNOA",)),
            "source": "src/screener/step1_data.py:131-143",
            "history": "N and N-1",
        },
        "BENEISH_M_SCORE": {
            "roles": _roles_from_formula_names(M_SCORE_INPUTS),
            "source": "src/screener/step1_data.py:144-242,262",
            "history": "N and N-1",
        },
        "DISTRESS": {
            "roles": _roles_from_formula_names(("DISTRESS",)),
            "source": "src/screener/step1_data.py:243-246 and "
            "src/screener/step1_cleaning.py:474-521",
            "history": "N only for statement item_ids",
        },
        "PIOTROSKI_F_SCORE": {
            "roles": {
                fscore[symbol]: offsets
                for symbol, offsets in fscore_offsets.items()
            },
            "source": f"scripts/build_sprint6_fscore.py:"
            f"{fscore_start}-{fscore_end},153-446",
            "history": "three-year run N, N-1 and N-2",
        },
        "FRANCHISE_POWER": {
            "roles": {
                franchise[symbol]: offsets
                for symbol, offsets in franchise_offsets.items()
            },
            "source": f"scripts/build_sprint6_franchise.py:"
            f"{franchise_start}-{franchise_end},118-248,398-411",
            "history": (
                f"at least {PROPOSED_FRANCHISE_MIN_YEARS} usable overlapping "
                "ROC/margin years; the code counts usable years and does not "
                "require adjacency"
            ),
            "minimum_usable_years": PROPOSED_FRANCHISE_MIN_YEARS,
        },
    }


def _presence_index(rows: pd.DataFrame) -> set[tuple[str, int, str]]:
    usable = rows.loc[pd.to_numeric(rows["value"], errors="coerce").notna()]
    return {
        (str(row.ticker), int(row.report_period), str(row.item_id))
        for row in usable.itertuples(index=False)
        if str(row.report_period).isdigit()
    }


def _roles_present(
    presence: set[tuple[str, int, str]],
    ticker: str,
    fiscal_year: int,
    roles: dict[str, set[int]],
) -> bool:
    return all(
        (ticker, fiscal_year + offset, item_id) in presence
        for item_id, offsets in roles.items()
        for offset in offsets
    )


def gate_buildability(
    rows: pd.DataFrame,
    tickers: list[str],
    *,
    definitions: dict[str, dict[str, Any]] | None = None,
) -> tuple[pd.DataFrame, dict[str, dict[str, Any]]]:
    definitions = definitions or gate_definitions()
    presence = _presence_index(rows)
    years_by_ticker: dict[str, list[int]] = {}
    for ticker in tickers:
        years_by_ticker[ticker] = sorted(
            {
                int(value)
                for value in rows.loc[
                    rows["ticker"].astype(str).eq(ticker), "report_period"
                ].astype(str)
                if value.isdigit()
            }
        )
    records: list[dict[str, Any]] = []
    for gate, definition in definitions.items():
        roles = definition["roles"]
        minimum = int(definition.get("minimum_usable_years", 1))
        for ticker in tickers:
            usable_years: list[int] = []
            for fiscal_year in years_by_ticker[ticker]:
                item_complete = _roles_present(
                    presence, ticker, fiscal_year, roles
                )
                if item_complete:
                    usable_years.append(fiscal_year)
                buildable = (
                    item_complete
                    if minimum == 1
                    else len(
                        [
                            year
                            for year in usable_years
                            if year <= fiscal_year
                        ]
                    )
                    >= minimum
                )
                records.append(
                    {
                        "gate": gate,
                        "ticker": ticker,
                        "fiscal_year": fiscal_year,
                        "item_complete": item_complete,
                        "buildable": buildable,
                    }
                )
    return pd.DataFrame(records), definitions


def _markdown_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                str(value).replace("|", "\\|").replace("\n", " ")
                for value in row
            )
            + " |"
        )
    return "\n".join(lines)


def _raw_value(value: Any) -> str:
    if pd.isna(value):
        return ""
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        return str(value)
    text = format(number, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _depth_and_gaps(
    all_rows: pd.DataFrame, tickers: list[str]
) -> tuple[pd.Series, list[tuple[str, list[int]]]]:
    depth = (
        all_rows.loc[:, ["ticker", "report_period"]]
        .drop_duplicates()
        .assign(
            report_period=lambda frame: frame["report_period"].astype(str)
        )
    )
    depth = depth.loc[depth["report_period"].str.fullmatch(r"\d{4}")]
    counts = (
        depth.groupby("ticker")["report_period"]
        .nunique()
        .reindex(tickers, fill_value=0)
    )
    gaps = []
    for ticker in tickers:
        years = depth.loc[
            depth["ticker"].astype(str).eq(ticker), "report_period"
        ].tolist()
        missing = internal_gap_years(years)
        if missing:
            gaps.append((ticker, missing))
    return counts, gaps


def _required_presence_rows(
    output: pd.DataFrame,
) -> tuple[list[list[Any]], list[str]]:
    years = sorted(int(value) for value in output["fiscal_year"].unique())
    denominator = (
        output.loc[:, ["ticker", "fiscal_year"]]
        .drop_duplicates()
        .groupby("fiscal_year")
        .size()
        .to_dict()
    )
    rows: list[list[Any]] = []
    below: set[str] = set()
    for item_id in required_item_ids():
        item = output.loc[
            output["item_id"].eq(item_id)
            & pd.to_numeric(output["value"], errors="coerce").notna()
        ]
        present = (
            item.loc[:, ["ticker", "fiscal_year"]]
            .drop_duplicates()
            .groupby("fiscal_year")
            .size()
            .to_dict()
        )
        for year in years:
            total = int(denominator.get(str(year), denominator.get(year, 0)))
            count = int(present.get(str(year), present.get(year, 0)))
            percentage = Decimal(count) * Decimal(100) / Decimal(total)
            if percentage < Decimal(90):
                below.add(item_id)
            rows.append(
                [
                    item_id,
                    year,
                    count,
                    total,
                    f"{percentage:.6f}%",
                ]
            )
    return rows, sorted(below)


def _gate_report_rows(
    buildability: pd.DataFrame,
    definitions: dict[str, dict[str, Any]],
) -> tuple[list[list[Any]], list[list[Any]]]:
    item_rows: list[list[Any]] = []
    coverage_rows: list[list[Any]] = []
    for gate, definition in definitions.items():
        item_rows.append(
            [
                gate,
                definition["source"],
                definition["history"],
                ", ".join(sorted(definition["roles"])),
            ]
        )
        gate_frame = buildability.loc[buildability["gate"].eq(gate)]
        for year in sorted(
            value
            for value in gate_frame["fiscal_year"].unique()
            if int(value) >= FIRST_COVERAGE_YEAR
        ):
            year_frame = gate_frame.loc[
                gate_frame["fiscal_year"].eq(year)
            ]
            total = len(year_frame)
            count = int(year_frame["buildable"].sum())
            percentage = (
                Decimal(count) * Decimal(100) / Decimal(total)
                if total
                else Decimal("0")
            )
            coverage_rows.append(
                [
                    gate,
                    year,
                    count,
                    total,
                    f"{percentage:.6f}%",
                    int(
                        gate_frame.loc[
                            gate_frame["buildable"], "ticker"
                        ].nunique()
                    ),
                ]
            )
    return item_rows, coverage_rows


def _next_quarter_end(value: date) -> date:
    quarter_months = (3, 6, 9, 12)
    for year in range(value.year, value.year + 2):
        for month in quarter_months:
            end = pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd()
            if end.date() >= value:
                return end.date()
    raise RuntimeError("cannot find next quarter end")


def _quarter_ordinal(value: date) -> int:
    return value.year * 4 + (value.month - 1) // 3


def _earliest_gate_dates(
    buildability: pd.DataFrame,
) -> tuple[list[list[Any]], str, int]:
    rows: list[list[Any]] = []
    dates: dict[str, date] = {}
    for gate, frame in buildability.groupby("gate", sort=True):
        usable = frame.loc[frame["buildable"]]
        if usable.empty:
            rows.append([gate, "NONE"])
            continue
        fiscal_year = int(usable["fiscal_year"].min())
        _, available = derive_annual_dates(fiscal_year)
        evaluation = _next_quarter_end(date.fromisoformat(available))
        dates[gate] = evaluation
        rows.append([gate, evaluation.isoformat()])
    all_gate = (
        max(dates.values())
        if len(dates) == buildability["gate"].nunique()
        else None
    )
    if all_gate is None:
        return rows, "NONE", -1
    lost = max(
        0, _quarter_ordinal(all_gate) - _quarter_ordinal(VALUE_BASKET_START)
    )
    return rows, all_gate.isoformat(), lost


def _vnm_rows(output: pd.DataFrame) -> tuple[list[str], list[list[str]]]:
    vnm = output.loc[output["ticker"].eq("VNM")].copy()
    years = sorted(vnm["fiscal_year"].astype(str).unique())
    selected = [years[0], years[-1]]
    pivot = vnm.pivot(index="item_id", columns="fiscal_year", values="value")
    rows = []
    for item_id in required_item_ids():
        rows.append(
            [
                item_id,
                *[
                    (
                        _raw_value(pivot.at[item_id, year])
                        if item_id in pivot.index and year in pivot.columns
                        else ""
                    )
                    for year in selected
                ],
            ]
        )
    return selected, rows


def write_report(
    *,
    run_date: str,
    output: pd.DataFrame,
    output_path: Path,
    sha256: str,
    tickers: list[str],
    statuses: list[dict[str, Any]],
    all_rows: pd.DataFrame,
    buildability: pd.DataFrame,
    definitions: dict[str, dict[str, Any]],
) -> None:
    depth, gaps = _depth_and_gaps(all_rows, tickers)
    years = sorted(
        int(value)
        for value in all_rows["report_period"].astype(str).unique()
        if str(value).isdigit()
    )
    required_source, required_start, required_end = (
        required_items_source_text()
    )
    presence_rows, below_items = _required_presence_rows(output)
    gate_items, gate_coverage = _gate_report_rows(
        buildability, definitions
    )
    gate_dates, all_gate_date, periods_lost = _earliest_gate_dates(
        buildability
    )
    ambiguous = sorted(
        (
            str(record["ticker"]),
            str(record["statement"]),
        )
        for record in statuses
        if str(record["data_status"]) == "REQUIRED_ITEM_AMBIGUOUS"
    )
    numeric = pd.to_numeric(output["value"], errors="coerce")
    below = output.loc[numeric.notna() & numeric.abs().lt(float(UNIT_MIN_VND))]
    above = output.loc[numeric.notna() & numeric.abs().gt(float(UNIT_MAX_VND))]
    cache_counts = pd.Series(
        [str(record.get("cache_state", "")) for record in statuses]
    ).value_counts()
    vnm_years, vnm_table = _vnm_rows(output)

    lines = [
        "# Sprint 9-4B Annual Quasi Point-in-Time Fundamentals",
        "",
        "## Restated-data limitation",
        "",
        *[f"> {line}" for line in RESTATED_LIMITATION.splitlines()],
        "",
        "## A1 — Annual depth",
        "",
        f"- Tickers measured: `{len(tickers)}`.",
        f"- Minimum annual depth: `{int(depth.min())}`.",
        f"- Median annual depth: `{float(depth.median()):g}`.",
        f"- Maximum annual depth: `{int(depth.max())}`.",
        f"- Earliest fiscal_year: `{years[0]}`.",
        f"- Latest fiscal_year: `{years[-1]}`.",
        f"- Tickers with fewer than 2 years: `{int(depth.lt(2).sum())}`.",
        f"- Tickers with an internal gap: `{len(gaps)}`.",
        "- Internal-gap list: "
        + (
            "; ".join(
                f"`{ticker}: {','.join(map(str, missing))}`"
                for ticker, missing in gaps
            )
            if gaps
            else "NONE"
        ),
        "",
        "## A2 — REQUIRED_ITEMS v1 presence",
        "",
        f"- Source: `scripts/verify_required_items_v1_sample_sprint3.py:{required_start}-{required_end}`.",
        "",
        "```python",
        required_source,
        "```",
        "",
        _markdown_table(
            [
                "item_id",
                "fiscal_year",
                "present_ticker_years",
                "ticker_years_present",
                "pct_present",
            ],
            presence_rows,
        ),
        "",
        "- Items below 90 percent in at least one year: "
        + (
            ", ".join(f"`{item}`" for item in below_items)
            if below_items
            else "NONE"
        ),
        "",
        "## A3 — Gate buildability",
        "",
        "### Exact item_id sets and time requirements read from existing code",
        "",
        _markdown_table(
            ["gate", "source", "time requirement", "item_id set"],
            gate_items,
        ),
        "",
        "### Buildability by fiscal year",
        "",
        _markdown_table(
            [
                "gate",
                "fiscal_year",
                "buildable_ticker_years",
                "ticker_years_present",
                "pct_buildable",
                "243 tickers buildable in at least one year",
            ],
            gate_coverage,
        ),
        "",
        "This section measures input presence only; it computes no gate value, score or ratio.",
        "",
        "## A4 — Earliest gated rebalance date",
        "",
        _markdown_table(["gate", "earliest evaluation_date"], gate_dates),
        "",
        f"- Earliest date with all gates computable: `{all_gate_date}`.",
        f"- Sprint 9-4A value-basket start: `{VALUE_BASKET_START.isoformat()}`.",
        f"- Rebalance periods lost by adding all gates: `{periods_lost}`.",
        f"Adding all gates costs `{periods_lost}` rebalance periods versus the Sprint 9-4A start.",
        "",
        "## A5 — Required-item ambiguity",
        "",
        f"- Ticker-statements with `REQUIRED_ITEM_AMBIGUOUS`: `{len(ambiguous)}`.",
        "- List: "
        + (
            ", ".join(
                f"`{ticker}/{statement}`" for ticker, statement in ambiguous
            )
            if ambiguous
            else "NONE"
        ),
        "",
        "## A6 — Unit buckets",
        "",
        f"- Absolute value below 1e9 VND: `{len(below)}`.",
        f"- Absolute value above 1e15 VND: `{len(above)}`.",
        "",
        (
            _markdown_table(
                ["ticker", "fiscal_year", "item_id", "value"],
                [
                    [
                        row.ticker,
                        row.fiscal_year,
                        row.item_id,
                        _raw_value(row.value),
                    ]
                    for row in above.itertuples(index=False)
                ],
            )
            if not above.empty
            else "Values above 1e15 VND: NONE"
        ),
        "",
        "## A7 — Cache states",
        "",
        f"- CACHED ticker-statements: `{int(cache_counts.get('CACHED', 0))}`.",
        f"- FETCHED ticker-statements: `{int(cache_counts.get('FETCHED', 0))}`.",
        "- Resumption is detected per ticker-statement: an existing normalized parquet file plus its matching status JSON skips that provider call; the dedicated FinanceClient cache is co-located under this run's annual run-state directory.",
        "",
        "## A8 — VNM oldest and newest REQUIRED_ITEMS v1 values",
        "",
        _markdown_table(["item_id", *vnm_years], vnm_table),
        "",
        "## A9 — Output identity",
        "",
        f"- RUN_DATE: `{run_date}`.",
        f"- Output path: `{output_path.relative_to(ROOT).as_posix()}`.",
        f"- Row count: `{len(output)}`.",
        f"- SHA-256: `{sha256}`.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Sprint 9-4B annual quasi point-in-time fundamentals."
    )
    parser.add_argument(
        "--run-date", help="Asia/Ho_Chi_Minh run date (YYYY-MM-DD)."
    )
    parser.add_argument(
        "--assemble-only",
        action="store_true",
        help="Reassemble from completed per-ticker run state without provider calls.",
    )
    args = parser.parse_args(argv)
    if args.assemble_only and not args.run_date:
        parser.error("--assemble-only requires --run-date")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_date = args.run_date or datetime.now(TIME_ZONE).date().isoformat()
    print(f"RUN_DATE={run_date}", flush=True)
    paths = _run_paths(run_date)
    tickers = relevant_tickers()
    if not args.assemble_only:
        fetch_all(tickers, paths)
    frames, statuses = load_run_state(tickers, paths)
    output = assemble_output(tickers, frames)
    validate_stop_gates(output, tickers, statuses)
    all_rows = _all_normalized_rows(frames)
    buildability, definitions = gate_buildability(all_rows, tickers)
    sha256 = write_deterministic_gzip_csv(output, paths["output"])
    write_report(
        run_date=run_date,
        output=output,
        output_path=paths["output"],
        sha256=sha256,
        tickers=tickers,
        statuses=statuses,
        all_rows=all_rows,
        buildability=buildability,
        definitions=definitions,
    )
    print(f"SHA256={sha256}")
    print(f"ROW_COUNT={len(output)}")
    print(f"OUTPUT={paths['output']}")
    print(f"REPORT={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
