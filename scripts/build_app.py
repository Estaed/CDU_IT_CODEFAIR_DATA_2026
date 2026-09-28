"""Inline the tokens, the app CSS/JS and the data pack into one file: dist/index.html.

Concatenation only - this script imports nothing from the pipeline and computes no verdict.
It also renders the share screen's QR code, records the pack and app sizes in a meta tag and
writes the host-only PWA files next to the page: sw.js, the templated manifest and the three
home-screen icons drawn from the colour tokens (Task-28).

One page out, no second cut-down copy: Task-36's reduced page and its inlined payload constant
were withdrawn by Task-37 the same evening, because transfer by camera carries the data pack,
gzipped in the browser at Show time. CLAUDE.md Blueprint keeps that history.
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
# Order fixed by CLAUDE.md Blueprint: vendor/jsQR.js, qr.js, scan.js, transfer.js, store.js,
# report.js, app.js; later tasks append. store.js sits before app.js because app.js reads
# window.CrosscheckStore at startup; scan.js sits before transfer.js because it
# calls window.CrosscheckScan (Task-25); report.js sits after store.js and before app.js
# because app.js calls window.CrosscheckReport while rendering a community (Task-35).
JSQR_SRC = ROOT / "app/vendor/jsQR.js"
JS_FILES = (
    JSQR_SRC,
    ROOT / "app/qr.js",
    ROOT / "app/scan.js",
    ROOT / "app/transfer.js",
    ROOT / "app/store.js",
    ROOT / "app/report.js",
    ROOT / "app/app.js",
)
# jsQR 1.4.0, Apache-2.0 (Task-25, OQ15): the one library exception CLAUDE.md Blueprint allows.
# Prefixed only onto the vendored file's own text, never onto the rest of JS_FILES; the full
# notice and the three recorded SHA-256 values are in app/vendor/jsQR.LICENSE.
JSQR_LICENSE_HEADER = (
    "/*! jsQR 1.4.0, Apache-2.0, (c) Cosmo Wolfe; one comment URL removed; licence text in "
    "app/vendor/jsQR.LICENSE of the source repository */"
)
# Served by the host only; dist/index.html never depends on them.
SW_SRC = ROOT / "app/sw.js"
MANIFEST_SRC = ROOT / "app/manifest.webmanifest"
# Tarik Base theme (2026-09-28): its first block is the light default, which the manifest and
# the home-screen icons are drawn from.
TOKENS_CSS = ROOT / "app/theme.css"
SIZES_PLACEHOLDER = "<!-- SIZES -->"
BUILD_PLACEHOLDER = b"__BUILD__"
THEME_PLACEHOLDER = "__THEME_COLOR__"
TOKEN_RE = re.compile(r"--([a-z0-9-]+):(#[0-9a-fA-F]{3,8});")

# Order fixed by CLAUDE.md Blueprint: tokens, the theme that re-points them, base, the
# reference screens, then the app.
CSS_FILES = (
    ROOT / "design/ds/design/tokens/colors.css",
    ROOT / "design/ds/design/tokens/typography.css",
    ROOT / "design/ds/design/tokens/spacing.css",
    ROOT / "app/theme.css",
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
    """Parse the requested custom properties out of the theme's light (first) block."""
    found: dict[str, str] = {}
    for name, value in TOKEN_RE.findall(TOKENS_CSS.read_text(encoding="utf-8")):
        found.setdefault(name, value)
    missing = [name for name in names if name not in found]
    if missing:
        raise ValueError(f"{TOKENS_CSS.name} is missing token(s): {', '.join(missing)}")
    return {name: found[name] for name in names}


# The top bar's brand mark (app/index.html, `.brand-mark`): two strokes in a 24-unit box,
# stroke width 2, round caps and joins. The home-screen icons draw the same double check.
BRAND_MARK = (((3, 12), (7, 16), (15, 7)), ((9, 16), (12, 19), (21, 8)))
BRAND_STROKE = 2


def draw_icon(size: int, paper: str, ink: str) -> Image.Image:
    """The brand mark's double check in ink on a full-bleed paper square.

    The mark spans the central 60%, inside the maskable safe zone. Drawn at 4x and downsampled
    with LANCZOS for clean edges (Task-28 Execution Guide).
    """
    scale = 4
    canvas = size * scale
    image = Image.new("RGB", (canvas, canvas), paper)
    draw = ImageDraw.Draw(image)

    xs = [x for stroke in BRAND_MARK for x, _ in stroke]
    ys = [y for stroke in BRAND_MARK for _, y in stroke]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) + BRAND_STROKE
    unit = canvas * 0.6 / span
    centre_x = (min(xs) + max(xs)) / 2
    centre_y = (min(ys) + max(ys)) / 2
    width = round(BRAND_STROKE * unit)
    radius = width / 2
    for stroke in BRAND_MARK:
        points = [
            (canvas / 2 + (x - centre_x) * unit, canvas / 2 + (y - centre_y) * unit)
            for x, y in stroke
        ]
        draw.line(points, fill=ink, width=width, joint="curve")
        for x, y in (points[0], points[-1]):
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=ink)

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

    paper, ink = tokens["color-canvas"], tokens["color-ink"]
    icons = {
        "icon-192.png": draw_icon(192, paper, ink),
        "icon-512.png": draw_icon(512, paper, ink),
        "apple-touch-icon.png": draw_icon(180, paper, ink),
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
    tokens = read_tokens(("color-canvas", "color-ink"))
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
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # Sizes are computed after the theme colour is filled in, so the meta reflects the byte
    # count of what is actually written to disk.
    page = with_sizes(page, PACK.stat().st_size)
    dist_index_bytes = page.encode("utf-8")
    OUT.write_bytes(dist_index_bytes)
    # A new cache name every build (Task-26): a stale __BUILD__ literal would serve one page
    # forever, so sw.js is written by write_host_files, not copied plain.
    write_host_files(OUT.parent, dist_index_bytes, tokens)
    print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size} bytes")
    return page


if __name__ == "__main__":
    main()
