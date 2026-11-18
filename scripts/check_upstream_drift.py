"""Audit deep-linked upstream paths against sources/systems.json and optionally check remote HEAD drift."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PINNED_TREE_RE = re.compile(r"^https://github\.com/([^/]+/[^/]+)/tree/([0-9a-f]{40})$")
GITHUB_REF_RE = re.compile(
    r"https://github\.com/([^/\s)#]+/[^/\s)#]+)/(?:blob|tree)/([^/\s)#]+)(?:/([^\s)#`\"'>]+))?"
)


def parse_pinned_repos(systems_data: dict) -> tuple[dict[str, dict], dict[str, dict]]:
    """Build per-repo and per-system pin lookup tables from systems.json."""
    by_repo: dict[str, dict] = {}
    by_system: dict[str, dict] = {}
    for system, info in sorted(systems_data.items()):
        repos: list[dict] = []
        for tree_url in info.get("versions", []):
            match = PINNED_TREE_RE.fullmatch(tree_url)
            if not match:
                raise ValueError(f"Unpinned version entry in systems.json for {system}: {tree_url}")
            repo, sha = match.groups()
            entry = {"repo": repo, "commit": sha, "system": system}
            by_repo[repo.lower()] = entry
            repos.append({"repo": repo, "commit": sha})
        by_system[system] = {
            "scope": info.get("scope", ""),
            "status": info.get("status", ""),
            "upstream_license": info.get("upstream_license", ""),
            "license_reviewed_at": info.get("license_reviewed_at", ""),
            "pins": repos,
            "referenced_paths": [],
        }
    return by_repo, by_system


def audit_repository(root: Path = ROOT) -> dict:
    """Verify every deep link under docs/systems/ and sources/ matches pinned revisions."""
    index_path = root / "sources" / "systems.json"
    systems_data = json.loads(index_path.read_text(encoding="utf-8"))
    by_repo, by_system = parse_pinned_repos(systems_data)

    scan_files: list[Path] = []
    systems_dir = root / "docs" / "systems"
    if systems_dir.exists():
        scan_files.extend(sorted(systems_dir.rglob("*.md")))
    sources_dir = root / "sources"
    if sources_dir.exists():
        scan_files.extend(sorted(sources_dir.glob("*.md")))

    seen_paths: dict[str, set[str]] = {system: set() for system in by_system}
    total_links = 0

    for md_path in scan_files:
        text = md_path.read_text(encoding="utf-8")
        rel = md_path.relative_to(root).as_posix()
        for match in GITHUB_REF_RE.finditer(text):
            repo, ref, sub_path = match.groups()
            pin = by_repo.get(repo.lower())
            if not pin:
                continue
            total_links += 1
            if ref != pin["commit"]:
                raise ValueError(
                    f"Unpinned or mismatched revision in {rel}: {repo} uses {ref!r}, expected {pin['commit']!r}"
                )
            if sub_path:
                clean_sub = sub_path.rstrip(".,;:)]")
                if clean_sub:
                    seen_paths[pin["system"]].add(f"{repo}:{clean_sub}")

    total_paths = 0
    for system, paths in seen_paths.items():
        ordered = sorted(paths)
        by_system[system]["referenced_paths"] = ordered
        total_paths += len(ordered)

    return {
        "system_count": len(by_system),
        "link_count": total_links,
        "path_count": total_paths,
        "systems": by_system,
    }


def check_remote_heads(audit: dict, timeout_seconds: int = 10) -> list[dict]:
    """Compare pinned revisions against live GitHub HEADs via git ls-remote."""
    results: list[dict] = []
    for system, info in sorted(audit["systems"].items()):
        for pin in info["pins"]:
            repo = pin["repo"]
            pinned = pin["commit"]
            url = f"https://github.com/{repo}.git"
            try:
                proc = subprocess.run(
                    ["git", "ls-remote", url, "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                    check=True,
                )
                head_sha = proc.stdout.strip().split()[0] if proc.stdout.strip() else None
                results.append(
                    {
                        "system": system,
                        "repo": repo,
                        "pinned": pinned,
                        "remote_head": head_sha,
                        "drifted": bool(head_sha and head_sha != pinned),
                    }
                )
            except (subprocess.SubprocessError, OSError, IndexError) as exc:
                results.append(
                    {
                        "system": system,
                        "repo": repo,
                        "pinned": pinned,
                        "remote_head": None,
                        "error": str(exc),
                    }
                )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON audit inventory")
    parser.add_argument(
        "--check-remote",
        action="store_true",
        help="Query upstream HEAD via git ls-remote and report commit drift",
    )
    args = parser.parse_args(argv)

    audit = audit_repository(ROOT)
    if args.check_remote:
        audit["remote_drift"] = check_remote_heads(audit)

    if args.json:
        print(json.dumps(audit, ensure_ascii=False, indent=2))
        return 0

    print(
        f"Pinned upstream audit: {audit['system_count']} systems, "
        f"{audit['path_count']} deep-linked source paths, 0 unpinned or mismatched revisions"
    )
    if args.check_remote:
        for item in audit["remote_drift"]:
            if "error" in item:
                print(f"  [error] {item['system']} ({item['repo']}): {item['error']}", file=sys.stderr)
            elif item["drifted"]:
                print(
                    f"  [drift] {item['system']} ({item['repo']}): "
                    f"pinned={item['pinned'][:12]} remote_head={item['remote_head'][:12]}"
                )
            else:
                print(f"  [match] {item['system']} ({item['repo']}): {item['pinned'][:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
