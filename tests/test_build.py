"""Unit tests for scripts/build_app.py: inlining CSS, JS and the pack into dist/index.html."""

from __future__ import annotations

import hashlib
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
    # CSS is still inlined, not linked; the manifest and icon <link> tags are host-relative
    # (Task-28) and are covered by their own checks below.
    assert '<link rel="stylesheet"' not in html
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


def _token(name: str) -> str:
    css = (ROOT / "design" / "ds" / "design" / "tokens" / "colors.css").read_text(encoding="utf-8")
    match = re.search(rf"--{name}:(#[0-9a-fA-F]+);", css)
    assert match, f"{name} not found in colors.css"
    return match.group(1)


def test_host_files_copied():
    build_app.main()
    # sw.js is not a plain copy since Task-26 (build-hashed cache name); manifest.webmanifest
    # is not a plain copy since Task-28 (theme_color/background_color templated from the tokens).
    manifest_text = (ROOT / "dist" / "manifest.webmanifest").read_text(encoding="utf-8")
    assert "__THEME_COLOR__" not in manifest_text
    manifest = json.loads(manifest_text)
    canvas = _token("color-canvas")

    assert manifest["name"] == "Crosscheck"
    assert manifest["display"] == "standalone"
    assert manifest["start_url"] == "./"
    assert manifest["theme_color"] == canvas
    assert manifest["background_color"] == canvas

    for size, src in ((192, "icon-192.png"), (512, "icon-512.png")):
        entries = [icon for icon in manifest["icons"] if icon["src"] == src]
        assert {icon["purpose"] for icon in entries} == {"any", "maskable"}
        assert all(icon["sizes"] == f"{size}x{size}" for icon in entries)


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


def test_nearby_js_no_stun_turn_and_empty_ice_servers():
    source = (ROOT / "app" / "nearby.js").read_text(encoding="utf-8")
    assert "iceServers: []" in source
    assert "stun:" not in source
    assert "turn:" not in source


def test_get_user_media_only_in_transfer_and_nearby():
    # The Python equivalent of `grep -l getUserMedia app/*.js` (CLAUDE.md Part 2, layer rule 8);
    # no shelling out, Windows has no `grep` on PATH by default.
    files = sorted(
        path.name
        for path in (ROOT / "app").glob("*.js")
        if "getUserMedia" in path.read_text(encoding="utf-8")
    )
    assert files == ["nearby.js", "transfer.js"]


def test_sw_cache_name_is_build_hash():
    # Task-26: a phone that opened Pages once kept showing that build forever because the
    # cache name never changed. dist/sw.js now carries this build's own hash.
    build_app.main()
    dist_index_bytes = (ROOT / "dist" / "index.html").read_bytes()
    build_id = hashlib.sha256(dist_index_bytes).hexdigest()[:12]
    sw = (ROOT / "dist" / "sw.js").read_text(encoding="utf-8")

    assert f"crosscheck-{build_id}" in sw
    assert "__BUILD__" not in sw
    assert "skipWaiting" in sw
    assert "clients.claim" in sw
    assert "navigate" in sw


def test_dist_head_has_pwa_tags():
    build_app.main()
    html = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")
    canvas = _token("color-canvas")

    assert '<link rel="manifest" href="manifest.webmanifest">' in html
    assert '<link rel="apple-touch-icon" href="apple-touch-icon.png">' in html
    assert 'name="apple-mobile-web-app-capable" content="yes"' in html
    assert f'<meta name="theme-color" content="{canvas}">' in html
    assert "__THEME_COLOR__" not in html


def test_icons_written_at_declared_sizes_and_deterministic():
    from PIL import Image

    build_app.main()
    dist = ROOT / "dist"
    sizes = {"icon-192.png": 192, "icon-512.png": 512, "apple-touch-icon.png": 180}
    for name, size in sizes.items():
        with Image.open(dist / name) as img:
            assert img.size == (size, size)
            assert img.mode == "RGB"

    ink = _token("color-ink")
    ink_rgb = tuple(int(ink[i : i + 2], 16) for i in (1, 3, 5))
    with Image.open(dist / "icon-512.png") as img:
        corner = img.getpixel((0, 0))
        centre = img.getpixel((256, 256))
    assert corner == ink_rgb
    assert centre != corner

    first_build = {name: (dist / name).read_bytes() for name in sizes}
    build_app.main()
    for name, data in first_build.items():
        assert (dist / name).read_bytes() == data


def test_sw_precaches_manifest_and_icons():
    build_app.main()
    sw = (ROOT / "dist" / "sw.js").read_text(encoding="utf-8")
    for name in ("manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png"):
        assert name in sw
