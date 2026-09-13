"""Inline the tokens, the app CSS/JS and the data pack into one file: dist/index.html.

Concatenation only - this script imports nothing from the pipeline and computes nothing.
Run from the project root: ``PYTHONUTF8=1 .venv/Scripts/python scripts/build_app.py``.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "app/index.html"
OUT = ROOT / "dist/index.html"
PACK = ROOT / "data/out/data_pack.json"
JS = ROOT / "app/app.js"

# Order fixed by CLAUDE.md Part 2: tokens, base, the reference screens, then the app.
CSS_FILES = (
    ROOT / "design/ds/design/tokens/colors.css",
    ROOT / "design/ds/design/tokens/typography.css",
    ROOT / "design/ds/design/tokens/spacing.css",
    ROOT / "design/ds/design/base.css",
    ROOT / "design/screens/screens.css",
    ROOT / "app/app.css",
)


def inline(template: str, css_parts: list[str], js: str, pack_json: str) -> str:
    """Replace the three template placeholders with the inlined blocks."""
    blocks = {
        "<!-- CSS -->": "<style>" + "\n".join(css_parts) + "</style>",
        "<!-- PACK -->": (
            '<script type="application/json" id="pack">'
            + pack_json.replace("</", "<\\/")
            + "</script>"
        ),
        "<!-- JS -->": "<script>" + js + "</script>",
    }
    for placeholder, block in blocks.items():
        if placeholder not in template:
            raise ValueError(f"the template has no {placeholder} placeholder")
        template = template.replace(placeholder, block)
    return template


def main() -> str:
    """Build dist/index.html and return what was written."""
    page = inline(
        TEMPLATE.read_text(encoding="utf-8"),
        [path.read_text(encoding="utf-8") for path in CSS_FILES],
        JS.read_text(encoding="utf-8"),
        PACK.read_text(encoding="utf-8").strip(),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8", newline="\n")
    print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size} bytes")
    return page


if __name__ == "__main__":
    main()
