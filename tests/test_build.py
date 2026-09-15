"""Unit tests for scripts/build_app.py: inlining CSS, JS and the pack into dist/index.html."""

from __future__ import annotations

import json
import re
from pathlib import Path

import build_app
import pytest
import qrcode

from pipeline.pack import read_constant

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = "<html><head><!-- CSS --></head><body><!-- PACK --><!-- JS --></body></html>"


def test_inline_replaces_placeholders():
    result = build_app.inline(
        TEMPLATE,
        css_parts=["a{}", "b{}"],
        js="x=1",
        pack_json='{"a":"</script>"}',
    )
    assert "<style>a{}\nb{}</style>" in result
    assert (
        '<script type="application/json" id="pack">{"a":"<\\/script>"}</script>' in result
    )
    assert "<script>x=1</script>" in result


def test_inline_missing_placeholder_raises():
    with pytest.raises(ValueError, match="PACK"):
        build_app.inline(
            "<html><head><!-- CSS --></head><body><!-- JS --></body></html>",
            css_parts=["a{}"],
            js="x=1",
            pack_json="{}",
        )


def test_real_build():
    build_app.main()
    html = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")

    assert html.count('id="pack"') == 1
    assert "<link" not in html
    assert "<script src" not in html
    assert len(html.encode("utf-8")) <= 1_048_576

    stripped = re.sub(
        r'<script type="application/json" id="pack">.*?</script>', "", html, flags=re.S
    )
    assert "http://" not in stripped
    assert "https://" not in stripped
    assert "DIC005" not in stripped


def test_qr_decodes_to_app_url():
    build_app.main()
    html = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")

    match = re.search(
        r'<template id="qr"><svg class="qr" role="img"[^>]* viewBox="0 0 (\d+) \1"[^>]*>'
        r'<path class="qr__modules" d="([^"]*)"/></svg></template>',
        html,
    )
    assert match, "no QR template in dist/index.html"
    size = int(match.group(1))
    drawn = {(int(x), int(y)) for x, y in re.findall(r"M(\d+) (\d+)h1v1h-1z", match.group(2))}
    assert re.sub(r"M\d+ \d+h1v1h-1z", "", match.group(2)) == ""

    # Compared module for module with qrcode's own matrix for APP_URL, as design/screens did.
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
    code.add_data(read_constant("APP_URL"))
    code.make(fit=True)
    matrix = code.get_matrix()
    expected = {(x, y) for y, row in enumerate(matrix) for x, dark in enumerate(row) if dark}

    assert size == len(matrix)
    assert drawn == expected
    assert html.count('<template id="qr">') == 1


def test_sizes_meta_matches_files():
    build_app.main()
    out = ROOT / "dist" / "index.html"
    html = out.read_text(encoding="utf-8")

    sizes = re.findall(r'<meta name="crosscheck-sizes" content="pack=(\d+);app=(\d+)">', html)
    assert len(sizes) == 1
    pack_bytes, app_bytes = (int(value) for value in sizes[0])
    assert pack_bytes == (ROOT / "data" / "out" / "data_pack.json").stat().st_size
    assert app_bytes == out.stat().st_size


def test_host_files_copied():
    build_app.main()
    for name in ("sw.js", "manifest.webmanifest"):
        assert (ROOT / "dist" / name).read_bytes() == (ROOT / "app" / name).read_bytes()
    manifest = json.loads((ROOT / "dist" / "manifest.webmanifest").read_text(encoding="utf-8"))
    assert manifest["name"] == "Crosscheck"
    assert manifest["display"] == "standalone"
    assert manifest["start_url"] == "./"
    assert "icons" not in manifest


def test_with_sizes_counts_its_own_meta():
    page = build_app.with_sizes(f"<head>{build_app.SIZES_PLACEHOLDER}</head>", 7)
    app_bytes = int(re.search(r"app=(\d+)", page).group(1))
    assert app_bytes == len(page.encode("utf-8"))
    assert "pack=7;" in page


def test_qr_js_inlined_once_before_app_js():
    build_app.main()
    html = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")

    assert html.count("window.CrosscheckQR = ") == 1
    qr_index = html.index("window.CrosscheckQR = ")
    # DEFAULT_HASH is a unique app.js identifier (Task-17 Execution Guide: qr.js before app.js).
    app_index = html.index("DEFAULT_HASH")
    assert qr_index < app_index
