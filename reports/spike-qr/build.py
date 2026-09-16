"""Build the transfer v3 spike pages: dist/spike/send.html and dist/spike/receive.html.

Task-31 round two, 2026-09-16. Concatenation only, the same shape as scripts/build_app.py but
its own script: the spike is outside the app and is deleted when Task-36 lands, so build_app.py
is not touched. The app files it inlines are read read-only and never copied into reports/.

Round two carries the real thing instead of a pseudorandom stand-in. The payload is the **lite
copy** of the built app, derived here from dist/index.html (run ``scripts/build_app.py`` first):

* the vendored jsQR is dropped -- a copy that cannot read QR frames cannot pass the app on by
  camera, but it renders every screen, and it is the biggest single block of bytes in the page;
* the pack's ``layers`` value becomes ``[]`` -- the map's carrier and region overlays are most
  of the pack and the community screens do not need them;
* ``<html>`` gets ``data-lite="1"`` so a received copy can say what it is.

The result is gzipped at level 6 and written into both pages base64-encoded, with the SHA-256
of those gzipped bytes: the receive page declares DONE only when the bytes it reassembled hash
to that constant, so a completed run proves the received bytes are the sent bytes.

Run from the project root: ``PYTHONUTF8=1 .venv/Scripts/python reports/spike-qr/build.py``.
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT_DIR = ROOT / "dist/spike"
TEMPLATE = HERE / "page.html"
CSS = HERE / "spike.css"
SPIKE_JS = HERE / "spike.js"
# Read from app/ and dist/, never copied here: the spike must measure the app's own encoder,
# the app's own reader and the app's own bytes.
JSQR = ROOT / "app/vendor/jsQR.js"
APP_JS = (ROOT / "app/qr.js", ROOT / "app/scan.js")
APP_PAGE = ROOT / "dist/index.html"
PAGES = ("send", "receive")

# The fountain code's block size, only so this script can print the K the pages will use.
BLOCK_BYTES = 750

# How scripts/build_app.py marks the vendored copy inside the one inlined <script>. The app's
# JS files are concatenated into a single element, so "drop the jsQR script" means cutting the
# marker plus the vendored file's own text -- both read from the tree, so the cut is exact and
# fails loudly if build_app.py ever stops matching.
JSQR_MARKER = (
    "/*! jsQR 1.4.0, Apache-2.0, (c) Cosmo Wolfe; one comment URL removed; licence text in "
    "app/vendor/jsQR.LICENSE of the source repository */"
)
PACK_RE = re.compile(r'(<script type="application/json" id="pack">)(.*?)(</script>)', re.S)
HTML_TAG_RE = re.compile(r"<html\b")


def strip_jsqr(page: str) -> str:
    """Remove the vendored jsQR from the built page's inlined script."""
    block = f"{JSQR_MARKER}\n{JSQR.read_text(encoding='utf-8')}\n"
    if block not in page:
        raise ValueError("the built page does not contain the marked jsQR block")
    return page.replace(block, "", 1)


def empty_layers(page: str) -> str:
    """Replace the inlined pack's `layers` value with an empty list, keeping every other key.

    The pack is read through json, not patched by regex: the layer paths are full of brackets.
    `</` is escaped on the way back in exactly as build_app.py escapes it.
    """
    match = PACK_RE.search(page)
    if match is None:
        raise ValueError("the built page has no inlined pack script")
    pack = json.loads(match.group(2))
    if "layers" not in pack:
        raise ValueError("the inlined pack has no layers key")
    pack["layers"] = []
    lite = json.dumps(pack, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return page[: match.start(2)] + lite + page[match.end(2) :]


def mark_lite(page: str) -> str:
    """Put data-lite="1" on <html> so a received copy can say what it is."""
    page, count = HTML_TAG_RE.subn('<html data-lite="1"', page, count=1)
    if count != 1:
        raise ValueError("the built page has no <html> tag")
    return page


def lite_payload() -> tuple[bytes, bytes]:
    """The lite copy of the built app and its gzipped bytes."""
    if not APP_PAGE.exists():
        raise FileNotFoundError(f"{APP_PAGE} is missing; run scripts/build_app.py first")
    page = mark_lite(empty_layers(strip_jsqr(APP_PAGE.read_text(encoding="utf-8"))))
    html = page.encode("utf-8")
    # mtime=0: the payload must be the same bytes on every build, so a run recorded on one
    # build can be compared with a run recorded on another.
    return html, gzip.compress(html, compresslevel=6, mtime=0)


def script(source: str) -> str:
    """One inline script element.

    A `</` in the source would end the element early; no file inlined here contains the
    sequence, so this refuses instead of escaping, and the refusal is the check.
    """
    if "</" in source:
        raise ValueError("inlined source contains '</' and cannot be placed in a script element")
    return f"<script>{source}</script>"


def payload_script(gzipped: bytes, html_bytes: int) -> str:
    """The payload constant both pages read: base64 of the gzipped lite copy, and its hash."""
    return script(
        "window.SpikePayload = {"
        f'b64: "{base64.b64encode(gzipped).decode("ascii")}", '
        f'sha256: "{hashlib.sha256(gzipped).hexdigest()}", '
        f"gzippedBytes: {len(gzipped)}, "
        f"htmlBytes: {html_bytes}"
        "};"
    )


def build_page(template: str, page: str, css: str, scripts: list[str]) -> str:
    """Fill the template's two placeholders and its page name."""
    for placeholder, block in (
        ("<!-- CSS -->", f"<style>{css}</style>"),
        ("<!-- JS -->", "".join(scripts)),
    ):
        if placeholder not in template:
            raise ValueError(f"the template has no {placeholder} placeholder")
        template = template.replace(placeholder, block)
    return template.replace("__PAGE__", page)


def main() -> None:
    html, gzipped = lite_payload()
    k = max(1, math.ceil(len(gzipped) / BLOCK_BYTES))
    print(f"lite copy: {len(html)} bytes, gzipped {len(gzipped)} bytes, K {k}")

    template = TEMPLATE.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    scripts = [script(JSQR.read_text(encoding="utf-8"))]
    scripts += [script(path.read_text(encoding="utf-8")) for path in APP_JS]
    scripts.append(payload_script(gzipped, len(html)))
    scripts.append(script(SPIKE_JS.read_text(encoding="utf-8")))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for page in PAGES:
        out = OUT_DIR / f"{page}.html"
        text = build_page(template, page, css, scripts)
        out.write_text(text, encoding="utf-8", newline="\n")
        print(f"{out.relative_to(ROOT)}: {len(text.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
