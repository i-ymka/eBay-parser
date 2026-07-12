"""Remember which listings have already been reported."""

from __future__ import annotations

import json
from pathlib import Path


class SeenStore:
    """A persistent set of item IDs, so each listing is alerted only once."""

    def __init__(self, path: Path):
        self.path = path
        self._ids = self._load()

    def _load(self) -> set[str]:
        if not self.path.exists():
            return set()
        try:
            return set(json.loads(self.path.read_text(encoding="utf-8")))
        except (ValueError, OSError):
            return set()

    def contains(self, item_id: str) -> bool:
        return item_id in self._ids

    def add(self, item_id: str) -> None:
        self._ids.add(item_id)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(sorted(self._ids)), encoding="utf-8")
