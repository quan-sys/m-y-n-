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

from src.data.vnstock_client import VnstockClient  # noqa: E402
from src.universe import build_universe, print_summary, write_universe_snapshot  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the M0 stock universe.")
    parser.add_argument("--limit", type=int, default=None, help="Process only the first N stock symbols.")
    parser.add_argument(
        "--max-consecutive-api-errors",
        type=int,
        default=10,
        help="Stop live API calls after this many consecutive ticker-level API errors.",
    )
    parser.add_argument("--min-sleep", type=float, default=2.8, help="Minimum random sleep between API requests.")
    parser.add_argument("--max-sleep", type=float, default=3.6, help="Maximum random sleep between API requests.")
    parser.add_argument(
        "--fetch-market-cap",
        action="store_true",
        help="Fetch per-ticker overview data for market cap. Disabled by default to reduce M0 API rate-limit pressure.",
    )
    parser.add_argument(
        "--market-cap-limit",
        type=int,
        default=None,
        help="Maximum controlled market-cap requests. Required with --fetch-market-cap.",
    )
    args = parser.parse_args()
    if args.fetch_market_cap and args.market_cap_limit is None:
        parser.error("--market-cap-limit is required with --fetch-market-cap")
    if args.market_cap_limit is not None and args.market_cap_limit < 0:
        parser.error("--market-cap-limit must be zero or greater")
    return args


def main() -> int:
    args = parse_args()
    client = VnstockClient(
        min_sleep_seconds=args.min_sleep,
        max_sleep_seconds=args.max_sleep,
    )
    result = build_universe(
        client=client,
        output_dir=ROOT / "data",
        config_dir=ROOT / "config",
        limit=args.limit,
        max_consecutive_api_errors=args.max_consecutive_api_errors,
        fetch_market_cap=args.fetch_market_cap,
        market_cap_limit=args.market_cap_limit,
    )
    if args.limit is None:
        snapshot_path = write_universe_snapshot(
            result.accepted,
            result.rejects,
            ROOT / "data" / "snapshots",
        )
        result.summary["snapshot_path"] = str(snapshot_path.resolve())
        result.summary["snapshot_status"] = "WRITTEN"
    else:
        result.summary["snapshot_status"] = "SKIPPED_LIMITED_RUN"
    print_summary(result.summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
