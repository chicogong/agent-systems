"""Check figure bundles and local Markdown links without network access."""

from __future__ import annotations

import json
import html
import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
HTML_IMAGE = re.compile(r'<(?:img|source)\b[^>]*\bsrc=["\']([^"\']+)["\']', re.I)
SOURCE_MARKDOWN_FILES = (
    "AGENTS.md", "README.md", "CONTRIBUTING.md", "LICENSE-CONTENT.md",
    "book/README.md", "book/CONTENTS.md", "book/assets/README.md", "book/print-proof-brief.md",
    "scripts/README.md", "site/README.md",
)
SOURCE_MARKDOWN_DIRS = (
    "book/frontmatter", "book/backmatter", "docs", "figures", "sources", "examples",
)


def markdown_anchors(content: str) -> set[str]:
    """GitHub-style ATX heading anchors for this repository's Markdown subset.

    Includes duplicate-heading suffixes and explicit HTML anchors; fenced code
    is not a heading. Rendered website anchors are checked by its own gate.
    """
    anchors = set(re.findall(r'<(?:a|h[1-6])\b[^>]*\b(?:id|name)=["\']([^"\']+)["\']', content, re.I))
    counts: dict[str, int] = {}
    fence: tuple[str, int] | None = None
    for line in content.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1]:
                fence = None
            continue
        if fence:
            continue
        heading = re.match(r"^\s{0,3}#{1,6}\s+(.+?)(?:\s+#+)?\s*$", line)
        if not heading:
            continue
        title = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading[1])
        title = html.unescape(re.sub(r"<[^>]*>", "", title)).lower()
        slug = "".join(char for char in title if char in " -_" or unicodedata.category(char)[0] in "LNM").replace(" ", "-")
        index = counts.get(slug, 0)
        candidate = slug if index == 0 else f"{slug}-{index}"
        while candidate in anchors:
            index += 1
            candidate = f"{slug}-{index}"
        counts[slug] = index + 1
        anchors.add(candidate)
    return anchors


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
        content = markdown.read_text(encoding="utf-8")
        for destination in LINK.findall(content) + HTML_IMAGE.findall(content):
            parsed = urlsplit(destination.strip("<>"))
            if parsed.scheme or parsed.netloc:
                continue
            target = (markdown.parent / unquote(parsed.path)).resolve() if parsed.path else markdown
            if not target.is_relative_to(ROOT) or not target.exists():
                errors.append(f"{markdown.relative_to(ROOT)} -> {destination}")
            elif parsed.fragment and target.is_file() and target.suffix == ".md":
                if unquote(parsed.fragment) not in markdown_anchors(target.read_text(encoding="utf-8")):
                    errors.append(f"{markdown.relative_to(ROOT)} -> {destination} (missing heading anchor)")
    return errors


if __name__ == "__main__":
    found = check_figures() + check_links()
    if found:
        for item in found:
            print(f"ERROR: {item}")
        raise SystemExit(1)
    print("Figure bundles and local Markdown links: OK")
