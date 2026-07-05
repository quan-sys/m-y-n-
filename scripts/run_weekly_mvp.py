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

from src.weekly import run_weekly_mvp  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Sprint 2 MVP sector weekly report.")
    parser.add_argument(
        "--limit-sectors",
        type=int,
        default=None,
        help="Process only the first N ICB2 sectors for a quick local check. Do not use for final report.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_weekly_mvp(
        universe_path=ROOT / "data" / "universe.csv",
        reports_root=ROOT / "reports",
        limit_sectors=args.limit_sectors,
    )

    warnings = result.data_quality["coverage_status"].value_counts().to_dict()
    cached_total = int(result.data_quality["cached_price_count"].sum())
    stale_total = int(result.data_quality["stale_price_count"].sum())
    api_error_total = int(result.data_quality["api_error_count"].sum())
    valid_price_total = int(result.data_quality["valid_price_count"].sum())
    index_source = "|".join(sorted(result.data_quality["index_source"].dropna().astype(str).unique()))
    cap_weight_available = int((result.data_quality["cap_weight_available"].astype(str) == "yes").sum())
    print("Sprint 2 weekly MVP summary:")
    print(f"- sector count: {result.indicators['icb2'].nunique()}")
    print(f"- universe row count: {result.metadata['universe_row_count']}")
    print(f"- report path: {result.output_dir / 'WEEKLY_REPORT.md'}")
    print(f"- indicators generated: {len(result.indicators)}")
    print(f"- data quality warnings: {warnings}")
    print(f"- valid price total: {valid_price_total}")
    print(f"- cached price count: {cached_total}")
    print(f"- stale price count: {stale_total}")
    print(f"- API_ERROR count: {api_error_total}")
    print(f"- index source: {index_source}")
    print(f"- cap-weight available sectors: {cap_weight_available}")
    print(f"- output directory: {result.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
