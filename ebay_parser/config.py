"""Load, save, and interactively create the user configuration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CONFIG_DIR = Path.home() / ".ebay-parser"
CONFIG_PATH = CONFIG_DIR / "config.json"
SEEN_PATH = CONFIG_DIR / "seen.json"

DEFAULT_INTERVAL = 60
MIN_INTERVAL = 30


@dataclass
class Search:
    keyword: str
    max_price: float
    category_id: int | None = None


@dataclass
class Config:
    searches: list[Search]
    interval_seconds: int = DEFAULT_INTERVAL


def exists() -> bool:
    return CONFIG_PATH.exists()


def load() -> Config:
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    searches = [
        Search(
            keyword=s["keyword"],
            max_price=float(s["max_price"]),
            category_id=s.get("category_id"),
        )
        for s in data["searches"]
    ]
    return Config(
        searches=searches,
        interval_seconds=int(data.get("interval_seconds", DEFAULT_INTERVAL)),
    )


def save(config: Config) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "interval_seconds": config.interval_seconds,
        "searches": [
            {
                "keyword": s.keyword,
                "max_price": s.max_price,
                **({"category_id": s.category_id} if s.category_id else {}),
            }
            for s in config.searches
        ],
    }
    CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def run_setup() -> Config:
    """Interactive first-run setup. Returns the saved configuration."""
    print("Let's set up what you want to track. Add one search at a time.\n")

    searches: list[Search] = []
    while True:
        keyword = input("  Keyword (e.g. 'nintendo switch'): ").strip()
        if not keyword:
            print("  Keyword can't be empty.")
            continue

        max_price = _ask_price("  Max price in £ (item + delivery): ")
        searches.append(Search(keyword=keyword, max_price=max_price))

        if input("  Add another search? [y/N]: ").strip().lower() != "y":
            break

    interval = _ask_interval(
        f"\nHow often to check, in seconds [{DEFAULT_INTERVAL}]: "
    )

    config = Config(searches=searches, interval_seconds=interval)
    save(config)
    print(f"\nSaved to {CONFIG_PATH}")
    return config


def _ask_price(prompt: str) -> float:
    while True:
        raw = input(prompt).strip().lstrip("£")
        try:
            value = float(raw)
            if value > 0:
                return value
        except ValueError:
            pass
        print("  Enter a price greater than 0, e.g. 50")


def _ask_interval(prompt: str) -> int:
    raw = input(prompt).strip()
    if not raw:
        return DEFAULT_INTERVAL
    try:
        return max(MIN_INTERVAL, int(raw))
    except ValueError:
        return DEFAULT_INTERVAL
