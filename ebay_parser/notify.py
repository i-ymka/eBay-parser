"""Deliver a match to the user: terminal line plus a best-effort desktop alert."""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime

from .scraper import Listing

# ANSI colours, used only when writing to a real terminal.
_GREEN = "\033[32m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_RESET = "\033[0m"


def _colour(text: str, code: str) -> str:
    if sys.stdout.isatty():
        return f"{code}{text}{_RESET}"
    return text


def announce(listing: Listing, keyword: str) -> None:
    """Print the match and try to raise a desktop notification."""
    _print_match(listing, keyword)
    _desktop(listing, keyword)


def _print_match(listing: Listing, keyword: str) -> None:
    stamp = datetime.now().strftime("%H:%M:%S")
    price = _colour(f"£{listing.total:.2f}", _GREEN + _BOLD)
    title = listing.title[:70]
    print(f"\a{_colour(stamp, _DIM)}  {price}  {title}  [{keyword}]")
    print(f"          {_colour(listing.url, _DIM)}")


def _desktop(listing: Listing, keyword: str) -> None:
    """Best-effort native notification; silently skipped where unavailable."""
    title = f"eBay match: £{listing.total:.2f}"
    body = listing.title[:120]
    try:
        if sys.platform == "darwin":
            script = f'display notification "{body}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], check=False)
        elif sys.platform.startswith("linux") and shutil.which("notify-send"):
            subprocess.run(["notify-send", title, body], check=False)
    except OSError:
        pass
