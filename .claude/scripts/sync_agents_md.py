"""Keep the generated Codex project instructions identical to CLAUDE.md."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    root = args.project.resolve()
    source = (root / "CLAUDE.md").read_bytes()
    target = root / "AGENTS.md"
    existing = target.read_bytes()
    marker = b"# CLAUDE.md"
    if marker not in existing:
        raise SystemExit("AGENTS.md has no generated header to preserve")
    header = existing.split(marker, 1)[0]
    expected = header + source
    if args.check:
        if existing != expected:
            raise SystemExit("AGENTS.md is out of sync with CLAUDE.md")
        print("AGENTS.md is in sync")
    else:
        target.write_bytes(expected)
        print("AGENTS.md updated")


if __name__ == "__main__":
    main()
