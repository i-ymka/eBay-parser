"""The watch loop: check each search, alert on new matches, repeat."""

from __future__ import annotations

import random
import time

import requests

from . import notify
from .config import Config, SEEN_PATH
from .scraper import BlockedError, Scraper
from .store import SeenStore

# How long to back off after eBay shows its bot-protection page.
_BLOCKED_BACKOFF = 600


class Monitor:
    def __init__(self, config: Config):
        self.config = config
        self.scraper = Scraper()
        self.seen = SeenStore(SEEN_PATH)

    def run(self) -> None:
        searches = ", ".join(s.keyword for s in self.config.searches)
        print(f"Watching {len(self.config.searches)} search(es): {searches}")
        print(f"Checking every {self.config.interval_seconds}s. Press Ctrl+C to stop.\n")

        # Prime the store on the first pass so existing listings aren't all
        # reported at once; only genuinely new listings alert after this.
        first_pass = not self.seen_has_history()

        try:
            while True:
                self._check_all(silent=first_pass)
                if first_pass:
                    print("Ready. Watching for new listings...\n")
                    first_pass = False
                self._sleep()
        except KeyboardInterrupt:
            print("\nStopped.")

    def seen_has_history(self) -> bool:
        return bool(self.seen._ids)

    def _check_all(self, silent: bool) -> None:
        for search in self.config.searches:
            try:
                listings = self.scraper.search(search.keyword, search.category_id)
            except BlockedError:
                print(
                    f"eBay is throttling this connection. Backing off for "
                    f"{_BLOCKED_BACKOFF // 60} minutes. If this keeps happening, "
                    "run fewer searches, use a longer interval, or add a proxy.\n"
                )
                time.sleep(_BLOCKED_BACKOFF)
                return
            except requests.RequestException as exc:
                print(f"Network error on '{search.keyword}': {exc}")
                continue

            for listing in listings:
                if listing.total > search.max_price:
                    continue
                if self.seen.contains(listing.item_id):
                    continue
                self.seen.add(listing.item_id)
                if not silent:
                    notify.announce(listing, search.keyword)

    def _sleep(self) -> None:
        jitter = random.uniform(0.9, 1.1)
        time.sleep(self.config.interval_seconds * jitter)
