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
from src.universe import build_universe, print_summary  # noqa: E402


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
    return parser.parse_args()


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
    )
    print_summary(result.summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
