"""Build the transfer v3 spike pages: dist/spike/send.html and dist/spike/receive.html.

Task-31, 2026-09-16. Concatenation only, the same shape as scripts/build_app.py but its own
script: the spike is outside the app and is deleted when Task-36 lands, so build_app.py is not
touched. The three app files it inlines are read read-only and never copied into reports/.

jsQR goes into a script element with an id, not an anonymous one, because spike.js reads its own
textContent back to build the Web Worker from a Blob -- one copy of the 380 KB source in the
page, not two, and still no second file to request.

Run from the project root: ``PYTHONUTF8=1 .venv/Scripts/python reports/spike-qr/build.py``.
"""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT_DIR = ROOT / "dist/spike"
TEMPLATE = HERE / "page.html"
CSS = HERE / "spike.css"
SPIKE_JS = HERE / "spike.js"
# Read from app/, never copied here: the spike must measure the app's own encoder and reader.
JSQR = ROOT / "app/vendor/jsQR.js"
APP_JS = (ROOT / "app/qr.js", ROOT / "app/scan.js")
PAGES = ("send", "receive")


def script(source: str, element_id: str | None = None) -> str:
    """One inline script element.

    A `</` in the source would end the element early, and the usual `<\\/` escape cannot be used
    here: spike.js reads the jsQR element's textContent back as worker source, where the escape
    would be a syntax error. No file inlined here contains the sequence, so this refuses instead.
    """
    if "</" in source:
        raise ValueError("inlined source contains '</' and cannot be escaped in a read-back script")
    opening = "<script>" if element_id is None else f'<script id="{element_id}">'
    return opening + source + "</script>"


def build_page(template: str, page: str, css: str, scripts: list[str]) -> str:
    """Fill the template's two placeholders and its page name."""
    for placeholder, block in (("<!-- CSS -->", f"<style>{css}</style>"), ("<!-- JS -->", "".join(scripts))):
        if placeholder not in template:
            raise ValueError(f"the template has no {placeholder} placeholder")
        template = template.replace(placeholder, block)
    return template.replace("__PAGE__", page)


def main() -> None:
    template = TEMPLATE.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    scripts = [script(JSQR.read_text(encoding="utf-8"), "jsqr-src")]
    scripts += [script(path.read_text(encoding="utf-8")) for path in APP_JS]
    scripts.append(script(SPIKE_JS.read_text(encoding="utf-8")))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for page in PAGES:
        out = OUT_DIR / f"{page}.html"
        html = build_page(template, page, css, scripts)
        out.write_text(html, encoding="utf-8", newline="\n")
        print(f"{out.relative_to(ROOT)}: {len(html.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
