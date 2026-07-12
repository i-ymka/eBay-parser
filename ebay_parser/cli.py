"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys

from . import __version__, config
from .monitor import Monitor


def main() -> None:
    # Ensure prices like £ print cleanly on Windows consoles.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(
        prog="ebay-parser",
        description="Watch eBay UK for underpriced Buy It Now listings.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["watch", "setup"],
        default="watch",
        help="'watch' (default) starts monitoring; 'setup' reconfigures searches.",
    )
    parser.add_argument("--version", action="version", version=f"ebay-parser {__version__}")
    args = parser.parse_args()

    if args.command == "setup" or not config.exists():
        cfg = config.run_setup()
        if args.command == "setup":
            return
    else:
        cfg = config.load()

    Monitor(cfg).run()
