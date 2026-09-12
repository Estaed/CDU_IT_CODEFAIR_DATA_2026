"""The quality gate. Run from the project root: ``.venv/Scripts/python scripts/gate.py``.

Steps run in order and stop at the first failure; the exit code is what verify-task reads.
  1. ruff check .                      static analysis, zero errors and zero warnings
  2. pytest -m "not browser"           unit tests (pipeline rules, data pack, build helpers)
  3. python scripts/build_app.py       the single-file app -> dist/index.html
  4. size check                        dist/index.html <= 1 MiB, data/out/data_pack.json <= 300 KiB
  5. pytest -m browser                 Playwright smoke: dist/index.html opens from file:// with
                                       zero network requests and renders the three screens
The build sits before the browser step because that step tests the built file.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_MAX_BYTES = 1_048_576
PACK_MAX_BYTES = 307_200
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}


def run(step: str, cmd: list[str]) -> None:
    print(f"\n== {step}: {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=ROOT, env=ENV)
    if result.returncode != 0:
        print(f"\nGATE RED at '{step}' (exit {result.returncode})", flush=True)
        sys.exit(result.returncode or 1)


def check_size(path: Path, limit: int) -> None:
    if not path.exists():
        print(f"\nGATE RED: {path.relative_to(ROOT)} was not produced", flush=True)
        sys.exit(1)
    size = path.stat().st_size
    verdict = "ok" if size <= limit else "OVER"
    print(f"   {path.relative_to(ROOT)}: {size:,} bytes (limit {limit:,}) {verdict}", flush=True)
    if size > limit:
        print("\nGATE RED at 'size'", flush=True)
        sys.exit(1)


def main() -> None:
    if not (ROOT / "pyproject.toml").exists():
        sys.exit("gate.py must live in scripts/ under the project root")
    py = sys.executable
    run("lint", [py, "-m", "ruff", "check", "."])
    run("unit tests", [py, "-m", "pytest", "-m", "not browser"])
    run("build", [py, "scripts/build_app.py"])
    print("\n== size", flush=True)
    check_size(ROOT / "dist" / "index.html", APP_MAX_BYTES)
    check_size(ROOT / "data" / "out" / "data_pack.json", PACK_MAX_BYTES)
    run("browser smoke", [py, "-m", "pytest", "-m", "browser"])
    print("\nGATE GREEN", flush=True)


if __name__ == "__main__":
    main()
