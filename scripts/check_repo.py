"""Check figure bundles and local Markdown links without network access."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
SOURCE_MARKDOWN_FILES = (
    "AGENTS.md", "README.md", "CONTRIBUTING.md", "LICENSE-CONTENT.md",
    "book/README.md", "scripts/README.md", "site/README.md",
)
SOURCE_MARKDOWN_DIRS = (
    "book/frontmatter", "book/backmatter", "docs", "figures", "sources",
)


def check_figures() -> list[str]:
    errors: list[str] = []
    for scene_file in sorted((ROOT / "figures").glob("*/scene.excalidraw")):
        folder = scene_file.parent
        for name in ("diagram.svg", "preview.png", "README.md"):
            if not (folder / name).is_file():
                errors.append(f"{folder.relative_to(ROOT)} missing {name}")
        try:
            scene = json.loads(scene_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{scene_file.relative_to(ROOT)} invalid JSON: {error}")
            continue
        if scene.get("type") != "excalidraw":
            errors.append(f"{scene_file.relative_to(ROOT)} is not a native scene")
        elements = scene.get("elements", [])
        ids = [element.get("id") for element in elements]
        if len(ids) != len(set(ids)):
            errors.append(f"{scene_file.relative_to(ROOT)} has duplicate element IDs")
        for element in elements:
            if element.get("type") == "text":
                family = element.get("fontFamily")
                if not isinstance(family, int) or family <= 0:
                    errors.append(f"{scene_file.relative_to(ROOT)} text {element.get('id')} has invalid fontFamily")
    return errors


def check_links() -> list[str]:
    errors: list[str] = []
    # Only author-maintained sources: a site build adds generated Markdown and
    # npm may add hundreds of third-party READMEs with unrelated link targets.
    markdown_files = [ROOT / name for name in SOURCE_MARKDOWN_FILES]
    for directory in SOURCE_MARKDOWN_DIRS:
        markdown_files.extend((ROOT / directory).rglob("*.md"))
    for markdown in sorted(path for path in markdown_files if path.is_file()):
        for destination in LINK.findall(markdown.read_text(encoding="utf-8")):
            path = destination.split("#", 1)[0].strip("<>")
            if not path or "://" in path or path.startswith("mailto:"):
                continue
            target = (markdown.parent / path).resolve()
            if not target.is_relative_to(ROOT) or not target.exists():
                errors.append(f"{markdown.relative_to(ROOT)} -> {destination}")
    return errors


if __name__ == "__main__":
    found = check_figures() + check_links()
    if found:
        for item in found:
            print(f"ERROR: {item}")
        raise SystemExit(1)
    print("Figure bundles and local Markdown links: OK")
