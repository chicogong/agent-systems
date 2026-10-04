"""Verify a published reading ZIP against the deterministic source build."""

from __future__ import annotations

import argparse
import hashlib
import tempfile
from pathlib import Path

from build_markdown import build


def check_archive(archive: Path, commit: str) -> None:
    if len(commit) != 40 or any(char not in "0123456789abcdef" for char in commit):
        raise ValueError("Reading archive requires a full source commit")
    with tempfile.TemporaryDirectory(prefix="agent-reading-check-") as directory:
        expected = Path(directory) / "expected.zip"
        build(expected, commit)
        if hashlib.sha256(archive.read_bytes()).digest() != hashlib.sha256(expected.read_bytes()).digest():
            raise ValueError("Reading archive is not the deterministic approved source bundle")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--expected-commit", required=True)
    args = parser.parse_args()
    check_archive(args.archive, args.expected_commit)
    print("Reading archive matches the source file whitelist, local links and fixed reference.")
