"""Check that every system chapter records its fixed upstream source version."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ROOT / "docs" / "systems"
INDEX = ROOT / "sources" / "systems.json"
PINNED_TREE = re.compile(r"^https://github\.com/[^/]+/[^/]+/tree/[0-9a-f]{40}$")


def main() -> None:
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    articles = {path.parent.name: path for path in SYSTEMS.glob("*/README.md")}
    if set(data) != set(articles):
        raise ValueError(f"Source register mismatch: missing={sorted(set(articles)-set(data))}, orphan={sorted(set(data)-set(articles))}")
    for system, info in sorted(data.items()):
        article = articles[system].read_text(encoding="utf-8")
        versions = info.get("versions", [])
        if not versions or not info.get("scope") or not info.get("status"):
            raise ValueError(f"Incomplete source record: {system}")
        for url in versions:
            if not PINNED_TREE.fullmatch(url):
                raise ValueError(f"Unpinned upstream source: {system}: {url}")
            if url not in article:
                raise ValueError(f"Source version missing from article: {system}: {url}")
    print(f"Pinned source register: {len(data)} system articles OK")


if __name__ == "__main__":
    main()
