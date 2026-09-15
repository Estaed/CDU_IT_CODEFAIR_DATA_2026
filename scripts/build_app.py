"""Inline the tokens, the app CSS/JS and the data pack into one file: dist/index.html.

Concatenation only - this script imports nothing from the pipeline and computes no verdict.
It also renders the share screen's QR code, records the pack and app sizes in a meta tag and
copies the two host-only PWA files next to the page.
Run from the project root: ``PYTHONUTF8=1 .venv/Scripts/python scripts/build_app.py``.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import qrcode

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "app/index.html"
OUT = ROOT / "dist/index.html"
PACK = ROOT / "data/out/data_pack.json"
# Order fixed by CLAUDE.md Part 2: qr.js, transfer.js, nearby.js, app.js; later tasks append.
JS_FILES = (
    ROOT / "app/qr.js",
    ROOT / "app/transfer.js",
    ROOT / "app/nearby.js",
    ROOT / "app/app.js",
)
# Served by the host only; dist/index.html never depends on them.
SW_SRC = ROOT / "app/sw.js"
MANIFEST_SRC = ROOT / "app/manifest.webmanifest"
SIZES_PLACEHOLDER = "<!-- SIZES -->"
BUILD_PLACEHOLDER = b"__BUILD__"

# Order fixed by CLAUDE.md Part 2: tokens, base, the reference screens, then the app.
CSS_FILES = (
    ROOT / "design/ds/design/tokens/colors.css",
    ROOT / "design/ds/design/tokens/typography.css",
    ROOT / "design/ds/design/tokens/spacing.css",
    ROOT / "design/ds/design/base.css",
    ROOT / "design/screens/screens.css",
    ROOT / "app/app.css",
    ROOT / "app/layers.css",
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


def qr_svg(text: str) -> str:
    """The QR code for text as one inline SVG path, markup as design/screens/assets/qr.svg."""
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
    code.add_data(text)
    code.make(fit=True)
    matrix = code.get_matrix()
    modules = "".join(
        f"M{x} {y}h1v1h-1z"
        for y, row in enumerate(matrix)
        for x, dark in enumerate(row)
        if dark
    )
    n = len(matrix)
    return (
        '<svg class="qr" role="img" aria-label="QR code that opens Crosscheck on another phone"'
        f' viewBox="0 0 {n} {n}" shape-rendering="crispEdges">'
        f'<path class="qr__modules" d="{modules}"/></svg>'
    )


def add_share_blocks(template: str, qr: str) -> str:
    """Put the QR <template> before the pack (the JS reads it) and a sizes slot into <head>."""
    for marker in ("</head>", "<!-- PACK -->"):
        if marker not in template:
            raise ValueError(f"the template has no {marker}")
    template = template.replace("</head>", f"{SIZES_PLACEHOLDER}\n</head>", 1)
    return template.replace("<!-- PACK -->", f'<template id="qr">{qr}</template>\n<!-- PACK -->', 1)


def with_sizes(page: str, pack_bytes: int) -> str:
    """Fill the sizes meta; the app size includes the meta itself, so iterate until stable."""
    app_bytes = 0
    while True:
        meta = f'<meta name="crosscheck-sizes" content="pack={pack_bytes};app={app_bytes}">'
        result = page.replace(SIZES_PLACEHOLDER, meta, 1)
        size = len(result.encode("utf-8"))
        if size == app_bytes:
            return result
        app_bytes = size


def main() -> str:
    """Build dist/index.html, copy the host-only files, and return what was written."""
    pack_text = PACK.read_text(encoding="utf-8")
    # APP_URL comes from constants.md through the pack, so the QR and the share button agree.
    qr = qr_svg(json.loads(pack_text)["app_url"])
    page = inline(
        add_share_blocks(TEMPLATE.read_text(encoding="utf-8"), qr),
        [path.read_text(encoding="utf-8") for path in CSS_FILES],
        "\n".join(path.read_text(encoding="utf-8") for path in JS_FILES),
        pack_text.strip(),
    )
    page = with_sizes(page, PACK.stat().st_size)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dist_index_bytes = page.encode("utf-8")
    OUT.write_bytes(dist_index_bytes)
    # A new cache name every build (Task-26): a stale __BUILD__ literal would serve one page
    # forever, so this is the one file that is not a plain copy.
    build_id = hashlib.sha256(dist_index_bytes).hexdigest()[:12].encode("ascii")
    sw_bytes = SW_SRC.read_bytes().replace(BUILD_PLACEHOLDER, build_id)
    (OUT.parent / SW_SRC.name).write_bytes(sw_bytes)
    shutil.copyfile(MANIFEST_SRC, OUT.parent / MANIFEST_SRC.name)
    print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size} bytes")
    return page


if __name__ == "__main__":
    main()
