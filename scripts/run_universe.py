from __future__ import annotations

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


def main() -> int:
    client = VnstockClient()
    result = build_universe(client=client, output_dir=ROOT / "data", config_dir=ROOT / "config")
    print_summary(result.summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
