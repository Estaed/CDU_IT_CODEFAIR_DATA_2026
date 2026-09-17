"""Build the zip that gets emailed to the organiser.

Run from the project root: ``PYTHONUTF8=1 .venv/Scripts/python scripts/package_submission.py``.

Writes ``dist/DataChallenge_Team <team number>_Submission.zip`` (team number read from
``constants.md``, never hardcoded) containing the interactive prototype, this README, the
Python solution, its outputs, and any committed raw snapshot. The report PDF and slide deck
are picked up from ``submission/`` if present under their expected names; if either is
missing, this prints a warning naming the expected path and still builds the zip.
"""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.pack import read_constant  # noqa: E402

MAX_FILE_BYTES = 50 * 1024 * 1024

# (source path relative to ROOT, arcname in the zip) for files that move to the zip's root.
ROOT_FILES = (
    ("dist/index.html", "index.html"),
    ("dist/sw.js", "sw.js"),
    ("dist/manifest.webmanifest", "manifest.webmanifest"),
    ("README.md", "README.md"),
    ("pyproject.toml", "pyproject.toml"),
    ("uv.lock", "uv.lock"),
)

# Directories packaged with their existing layout kept.
PACKAGE_DIRS = ("pipeline", "scripts", "tests", "data/out")

EXCLUDE_DIR_NAMES = {"__pycache__", ".pytest_cache", ".ruff_cache"}
EXCLUDE_SUFFIXES = {".pyc"}
# data/out/cache/ is the gitignored ACCC parse cache, rebuilt from data/raw/ when stale
# (CLAUDE.md Blueprint) - a build artefact, not a deliverable.
EXCLUDE_RELATIVE_DIRS = ("data/out/cache",)


def committed_raw_files() -> list[Path]:
    """Raw snapshots tracked by git under data/raw/ (none today; BushTel reuse terms are open)."""
    result = subprocess.run(
        ["git", "ls-files", "data/raw"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line]


def iter_dir_files(directory: Path):
    for path in sorted(directory.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDE_DIR_NAMES for part in rel.parts):
            continue
        if any(rel.as_posix().startswith(f"{excluded}/") for excluded in EXCLUDE_RELATIVE_DIRS):
            continue
        if path.suffix in EXCLUDE_SUFFIXES:
            continue
        yield path


def warn_missing(kind: str, path: Path) -> None:
    print(f"WARNING: {kind} not found at {path.relative_to(ROOT)}; add it before emailing")


def main() -> Path:
    team = read_constant("TEAM_NUMBER")
    out_path = ROOT / "dist" / f"DataChallenge_Team {team}_Submission.zip"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # (path, arcname) pairs.
    entries: list[tuple[Path, str]] = []

    for rel, arcname in ROOT_FILES:
        path = ROOT / rel
        if not path.exists():
            raise SystemExit(f"required file missing: {rel}")
        entries.append((path, arcname))

    for rel in PACKAGE_DIRS:
        directory = ROOT / rel
        for path in iter_dir_files(directory):
            entries.append((path, path.relative_to(ROOT).as_posix()))

    for path in committed_raw_files():
        entries.append((path, path.relative_to(ROOT).as_posix()))

    report_pdf = ROOT / "submission" / f"DataChallenge_Team {team}_Report.pdf"
    if report_pdf.exists():
        entries.append((report_pdf, report_pdf.name))
    else:
        warn_missing("report PDF", report_pdf)

    slide_deck = ROOT / "submission" / f"DataChallenge_Team {team}_Slides.pdf"
    if slide_deck.exists():
        entries.append((slide_deck, slide_deck.name))
    else:
        warn_missing("slide deck", slide_deck)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, arcname in entries:
            size = path.stat().st_size
            if size > MAX_FILE_BYTES:
                print(f"SKIPPED (over 50 MB): {arcname}")
                continue
            archive.write(path, arcname)

    print(f"{out_path.relative_to(ROOT)}: {out_path.stat().st_size:,} bytes")
    return out_path


if __name__ == "__main__":
    main()
