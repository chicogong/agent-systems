"""Rebuild every generated Excalidraw source before checking Git parity."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDERS = [
    ROOT / "scripts" / "build_pi_figures.py",
    ROOT / "scripts" / "build_context_figure.py",
    *sorted(
        builder
        for pattern in ("*/build.py", "*/build_scene.py")
        for builder in (ROOT / "figures").glob(pattern)
    ),
]


def main() -> None:
    for builder in BUILDERS:
        print(f"Rebuilding {builder.relative_to(ROOT)}", flush=True)
        subprocess.run([sys.executable, str(builder)], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
