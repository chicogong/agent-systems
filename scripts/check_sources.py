"""Check that every system chapter records its fixed upstream source version."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ROOT / "docs" / "systems"
INDEX = ROOT / "sources" / "systems.json"
PINNED_TREE = re.compile(r"^https://github\.com/[^/]+/[^/]+/tree/[0-9a-f]{40}$")
PINNED_LICENSE = re.compile(r"^https://github\.com/[^/]+/[^/]+/blob/[0-9a-f]{40}/LICENSE(?:\.[A-Za-z0-9_-]+)?$")


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
        license_sources = info.get("license_sources", [])
        if not info.get("upstream_license") or info["upstream_license"] == "pending-review":
            raise ValueError(f"Root license identification missing: {system}")
        try:
            date.fromisoformat(info["license_reviewed_at"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Root license review date missing: {system}") from exc
        if len(license_sources) != len(versions):
            raise ValueError(f"License evidence/version count mismatch: {system}")
        for version, license_url in zip(versions, license_sources):
            if not PINNED_LICENSE.fullmatch(license_url):
                raise ValueError(f"Unpinned root license source: {system}: {license_url}")
            if not license_url.startswith(version.replace("/tree/", "/blob/") + "/"):
                raise ValueError(f"License source has different revision: {system}: {license_url}")
    print(f"Pinned source register: {len(data)} system articles OK")


if __name__ == "__main__":
    main()
