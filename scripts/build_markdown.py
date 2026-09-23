"""Build a portable Markdown reading archive from the book manifest.

The repository Markdown remains canonical. This archive keeps chapter paths and
local figure assets, while linking to authoring-only files on GitHub.
"""

from __future__ import annotations

import argparse
import os
import re
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "book" / "manifest.txt"
DEFAULT_OUTPUT = ROOT / "output" / "markdown" / "agent-systems-md.zip"
ARCHIVE_ROOT = "agent-systems-md"
REPOSITORY_BASE = "https://github.com/chicogong/agent-systems"
MARKDOWN_LINK = re.compile(r"(!?\[[^\]]*\]\()([^\s)]+)(\))")
HTML_SOURCE = re.compile(r'(<(?:img|source)\b[^>]*\bsrc=")([^"]+)(")', re.I)
SUPPORT_FILES = (
    "docs/concepts/README.md",
    "docs/systems/README.md",
    "docs/comparisons/README.md",
    "sources/README.md",
    "sources/systems.json",
    "LICENSE-CONTENT.md",
    "LICENSE-CODE",
    "book/assets/cover-preview.png",
)


def manifest_entries() -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for raw in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("@part "):
            entries.append(("part", line.removeprefix("@part ")))
            continue
        if line.startswith("@front ") or line.startswith("@back "):
            kind, path = line.split(" ", 1)
            entries.append((kind[1:], path))
            continue
        if line.startswith("@"):
            raise ValueError(f"Unknown manifest directive: {line}")
        entries.append(("chapter", line))
    paths = [value for kind, value in entries if kind != "part"]
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate chapter in book/manifest.txt")
    for path in paths:
        source = ROOT / path
        if not source.resolve().is_relative_to(ROOT) or not source.is_file() or source.suffix != ".md":
            raise ValueError(f"Invalid manuscript path: {path}")
    return entries


def included_files(entries: list[tuple[str, str]]) -> set[Path]:
    files = {Path(value) for kind, value in entries if kind != "part"}
    files.update(Path(path) for path in SUPPORT_FILES)
    for folder in sorted((ROOT / "figures").iterdir()):
        if folder.is_dir() and (folder / "scene.excalidraw").is_file():
            files.update(Path("figures") / folder.name / name for name in
                         ("README.md", "scene.excalidraw", "diagram.svg", "preview.png"))
    for path in files:
        if not (ROOT / path).is_file():
            raise ValueError(f"Reading archive source missing: {path}")
    return files


def chapter_title(path: str) -> str:
    for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError(f"Chapter has no H1: {path}")


def repository_files(ref: str) -> str:
    if not ref or "/" in ref or ".." in ref:
        raise ValueError("Repository ref must be a tag or commit without a slash")
    return f"{REPOSITORY_BASE}/blob/{quote(ref, safe='')}/"


def reading_index(entries: list[tuple[str, str]], ref: str) -> str:
    lines = [
        "# 图解 Agent 系统 · Markdown 阅读版",
        "",
        "![图解 Agent 系统封面](book/assets/cover-preview.png)",
        "",
        "这是与 PDF 共用书稿清单的可携带阅读版。正文仍是普通 Markdown，",
        "图使用仓库导出的 SVG；同目录还提供 PNG 预览、可编辑图源和图的文字说明。",
        "章节中的项目结论对应注明的固定源码版本，不能当作实时运行评测。",
        "",
        "解压后可用 Markdown 阅读器打开本文件，或将整个文件夹作为 Obsidian vault 打开。",
        "请保留目录结构，否则章节间的相对链接和图片会失效。",
        "",
        "也可以按问题进入：[机制](docs/concepts/README.md) · "
        "[开源系统](docs/systems/README.md) · [横向对照](docs/comparisons/README.md) · "
        "[术语表](docs/glossary.md)。",
        "",
        "## 目录",
        "",
    ]
    section = ""
    for kind, value in entries:
        next_section = {"front": "卷首", "back": "卷末"}.get(kind)
        if kind == "part":
            next_section = value
        if next_section and next_section != section:
            if lines[-1]:
                lines.append("")
            lines.extend([f"### {next_section}", ""])
            section = next_section
        if kind != "part":
            lines.append(f"- [{chapter_title(value)}]({value})")
    lines.extend([
        "",
        "---",
        "",
        "[来源与证据规则](sources/README.md) · "
        f"[贡献方式]({repository_files(ref)}CONTRIBUTING.md) · "
        "[正文与图的许可](LICENSE-CONTENT.md) · [脚本许可](LICENSE-CODE)",
        "",
        "作者维护的研究计划、构建脚本和自动化配置不收进本阅读包；",
        f"如需参与维护，请查看[项目仓库]({REPOSITORY_BASE})。",
        "",
    ])
    return "\n".join(lines)


def local_target(source: Path, destination: str) -> Path | None:
    if destination.startswith(("#", "mailto:", "data:")) or "://" in destination:
        return None
    parsed = urlsplit(destination)
    if not parsed.path:
        return None
    target = (ROOT / source.parent / unquote(parsed.path)).resolve()
    if not target.is_relative_to(ROOT):
        raise ValueError(f"Link escapes repository: {source} -> {destination}")
    if not target.exists():
        raise ValueError(f"Broken source link: {source} -> {destination}")
    return target.relative_to(ROOT)


def rewrite_links(source: Path, content: str, files: set[Path], ref: str) -> str:
    def rewrite(destination: str) -> str:
        target = local_target(source, destination)
        if target is None or target in files or target == Path("README.md"):
            return destination
        parsed = urlsplit(destination)
        suffix = f"#{parsed.fragment}" if parsed.fragment else ""
        return repository_files(ref) + quote(target.as_posix(), safe="/") + suffix

    content = MARKDOWN_LINK.sub(lambda match: match[1] + rewrite(match[2]) + match[3], content)
    return HTML_SOURCE.sub(lambda match: match[1] + rewrite(match[2]) + match[3], content)


def validate_archive_files(files: dict[Path, bytes]) -> None:
    paths = set(files)
    for path, data in files.items():
        if path.suffix != ".md":
            continue
        text = data.decode("utf-8")
        destinations = [match[2] for match in MARKDOWN_LINK.finditer(text)]
        destinations.extend(match[2] for match in HTML_SOURCE.finditer(text))
        for destination in destinations:
            if destination.startswith(("#", "mailto:", "data:")) or "://" in destination:
                continue
            parsed = urlsplit(destination)
            target = (Path("/") / path.parent / unquote(parsed.path)).resolve().relative_to("/")
            if target not in paths:
                raise ValueError(f"Broken reading archive link: {path} -> {destination}")


def build(output: Path, ref: str = "main") -> tuple[int, int]:
    repository_files(ref)
    entries = manifest_entries()
    files = included_files(entries)
    result = {Path("README.md"): reading_index(entries, ref).encode("utf-8")}
    for path in sorted(files):
        source = ROOT / path
        data = source.read_bytes()
        if path.suffix == ".md":
            data = rewrite_links(path, data.decode("utf-8"), files, ref).encode("utf-8")
        result[path] = data
    validate_archive_files(result)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".zip", delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(temporary_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path, data in sorted(result.items()):
                member = zipfile.ZipInfo(f"{ARCHIVE_ROOT}/{path.as_posix()}", (1980, 1, 1, 0, 0, 0))
                member.compress_type = zipfile.ZIP_DEFLATED
                member.external_attr = 0o644 << 16
                archive.writestr(member, data)
        os.replace(temporary_path, output)
    finally:
        temporary_path.unlink(missing_ok=True)
    chapters = sum(kind != "part" for kind, _ in entries)
    return chapters, len(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--ref", default="main", help="Repository tag or commit for links to excluded authoring files")
    args = parser.parse_args()
    chapter_count, file_count = build(args.output.resolve(), args.ref)
    print(f"Markdown archive: {args.output} ({chapter_count} chapters, {file_count} files)")
