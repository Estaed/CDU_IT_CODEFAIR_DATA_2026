"""Inline the tokens, the app CSS/JS and the data pack into one file: dist/index.html.

Concatenation only - this script imports nothing from the pipeline and computes no verdict.
It also renders the share screen's QR code, records the pack and app sizes in a meta tag and
writes the host-only PWA files next to the page: sw.js, the templated manifest and the three
home-screen icons drawn from the colour tokens (Task-28).
Run from the project root: ``PYTHONUTF8=1 .venv/Scripts/python scripts/build_app.py``.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "app/index.html"
OUT = ROOT / "dist/index.html"
PACK = ROOT / "data/out/data_pack.json"
# Order fixed by CLAUDE.md Part 2: vendor/jsQR.js, qr.js, scan.js, transfer.js, nearby.js,
# store.js, app.js; later tasks append. store.js sits before app.js because app.js reads
# window.CrosscheckStore at startup; scan.js sits before transfer.js and nearby.js because both
# call window.CrosscheckScan (Task-25).
JS_FILES = (
    ROOT / "app/vendor/jsQR.js",
    ROOT / "app/qr.js",
    ROOT / "app/scan.js",
    ROOT / "app/transfer.js",
    ROOT / "app/nearby.js",
    ROOT / "app/store.js",
    ROOT / "app/app.js",
)
# jsQR 1.4.0, Apache-2.0 (Task-25, OQ15): the one library exception CLAUDE.md Part 2 allows.
# Prefixed only onto the vendored file's own text, never onto the rest of JS_FILES; the full
# notice and the three recorded SHA-256 values are in app/vendor/jsQR.LICENSE.
JSQR_LICENSE_HEADER = (
    "/*! jsQR 1.4.0, Apache-2.0, (c) Cosmo Wolfe; one comment URL removed; licence text in "
    "app/vendor/jsQR.LICENSE of the source repository */"
)
# Served by the host only; dist/index.html never depends on them.
SW_SRC = ROOT / "app/sw.js"
MANIFEST_SRC = ROOT / "app/manifest.webmanifest"
TOKENS_CSS = ROOT / "design/ds/design/tokens/colors.css"
SIZES_PLACEHOLDER = "<!-- SIZES -->"
BUILD_PLACEHOLDER = b"__BUILD__"
THEME_PLACEHOLDER = "__THEME_COLOR__"
TOKEN_RE = re.compile(r"--([a-z0-9-]+):(#[0-9a-fA-F]{3,8});")

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


def read_tokens(names: tuple[str, ...]) -> dict[str, str]:
    """Parse the requested custom properties out of colors.css; never retype a hex value."""
    found = dict(TOKEN_RE.findall(TOKENS_CSS.read_text(encoding="utf-8")))
    missing = [name for name in names if name not in found]
    if missing:
        raise ValueError(f"{TOKENS_CSS.name} is missing token(s): {', '.join(missing)}")
    return {name: found[name] for name in names}


def draw_icon(size: int, ink: str, mark: str) -> Image.Image:
    """A full-bleed ink square with a bold rounded check mark in mark, inside the central 60%.

    Drawn at 4x and downsampled with LANCZOS for clean edges (Task-28 Execution Guide).
    """
    scale = 4
    canvas = size * scale
    image = Image.new("RGB", (canvas, canvas), ink)
    draw = ImageDraw.Draw(image)

    margin = canvas * 0.2
    span = canvas - 2 * margin
    # The vertex sits exactly on the canvas centre (margin + span * 0.5 == canvas / 2) so the
    # centre pixel is always mark-coloured, whatever size the icon is drawn at.
    points = [
        (margin + span * 0.05, margin + span * 0.38),
        (margin + span * 0.50, margin + span * 0.50),
        (margin + span * 0.98, margin + span * 0.05),
    ]
    stroke = round(canvas * 0.11)
    draw.line(points, fill=mark, width=stroke, joint="curve")
    radius = stroke / 2
    for x, y in (points[0], points[-1]):
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=mark)

    return image.resize((size, size), Image.Resampling.LANCZOS)


def write_host_files(dist_dir: Path, html_bytes: bytes, tokens: dict[str, str]) -> None:
    """Write sw.js (build-hashed), the templated manifest and the three home-screen icons."""
    build_id = hashlib.sha256(html_bytes).hexdigest()[:12].encode("ascii")
    sw_bytes = SW_SRC.read_bytes().replace(BUILD_PLACEHOLDER, build_id)
    (dist_dir / SW_SRC.name).write_bytes(sw_bytes)

    manifest_text = MANIFEST_SRC.read_text(encoding="utf-8")
    if THEME_PLACEHOLDER not in manifest_text:
        raise ValueError(f"{MANIFEST_SRC.name} has no {THEME_PLACEHOLDER} placeholder")
    manifest_text = manifest_text.replace(THEME_PLACEHOLDER, tokens["color-canvas"])
    (dist_dir / MANIFEST_SRC.name).write_text(manifest_text, encoding="utf-8", newline="\n")

    ink, mark = tokens["color-ink"], tokens["color-on-primary"]
    icons = {
        "icon-192.png": draw_icon(192, ink, mark),
        "icon-512.png": draw_icon(512, ink, mark),
        "apple-touch-icon.png": draw_icon(180, ink, mark),
    }
    for name, image in icons.items():
        image.save(dist_dir / name, format="PNG", optimize=False)


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
    """Build dist/index.html, write the host-only files, and return what was written."""
    pack_text = PACK.read_text(encoding="utf-8")
    # APP_URL comes from constants.md through the pack, so the QR and the share button agree.
    qr = qr_svg(json.loads(pack_text)["app_url"])
    tokens = read_tokens(("color-canvas", "color-ink", "color-on-primary"))
    js_parts = []
    for path in JS_FILES:
        text = path.read_text(encoding="utf-8")
        if path.name == "jsQR.js":
            text = f"{JSQR_LICENSE_HEADER}\n{text}"
        js_parts.append(text)
    page = inline(
        add_share_blocks(TEMPLATE.read_text(encoding="utf-8"), qr),
        [path.read_text(encoding="utf-8") for path in CSS_FILES],
        "\n".join(js_parts),
        pack_text.strip(),
    )
    if THEME_PLACEHOLDER not in page:
        raise ValueError(f"the template has no {THEME_PLACEHOLDER} placeholder")
    page = page.replace(THEME_PLACEHOLDER, tokens["color-canvas"])
    # Sizes are computed after the theme colour is filled in, so the meta reflects the byte
    # count of what is actually written to disk.
    page = with_sizes(page, PACK.stat().st_size)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dist_index_bytes = page.encode("utf-8")
    OUT.write_bytes(dist_index_bytes)
    # A new cache name every build (Task-26): a stale __BUILD__ literal would serve one page
    # forever, so sw.js is written by write_host_files, not copied plain.
    write_host_files(OUT.parent, dist_index_bytes, tokens)
    print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size} bytes")
    return page


if __name__ == "__main__":
    main()
