from __future__ import annotations

import argparse
from pathlib import Path
import sys


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_console()
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.screener.step1_data import (  # noqa: E402
    load_accepted_universe,
    prepare_ticker_from_cache,
    write_vnm_evidence,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate cached VNM Sprint 4 formula evidence")
    parser.add_argument("--evaluation-date", required=True)
    parser.add_argument("--universe", type=Path, default=ROOT / "data" / "universe.csv")
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument(
        "--csv-output",
        type=Path,
        default=ROOT / "docs" / "VNM_FORMULA_EVIDENCE_SPRINT_4.csv",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=ROOT / "docs" / "VNM_FORMULA_CALCULATIONS_SPRINT_4.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    universe = load_accepted_universe(args.universe)
    matches = universe.loc[universe["ticker"].astype(str).eq("VNM")]
    if len(matches) != 1:
        raise ValueError(f"expected one ACCEPTED VNM row, found {len(matches)}")
    prepared = prepare_ticker_from_cache(
        matches.iloc[0].to_dict(),
        args.cache_root,
        args.evaluation_date,
        hose_warning=None,
    )
    row_count, csv_path, markdown_path = write_vnm_evidence(
        prepared, args.csv_output, args.markdown_output
    )
    print(
        f"VNM EVIDENCE COMPLETE: pair={prepared.pair[0]}/{prepared.pair[1]}; "
        f"rows={row_count}; csv={csv_path.resolve()}; markdown={markdown_path.resolve()}; "
        "source=existing cached annual parquet; live_api_calls=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
