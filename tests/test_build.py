"""Unit tests for scripts/build_app.py: inlining CSS, JS and the pack into dist/index.html."""

from __future__ import annotations

import base64
import gzip
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


def test_get_user_media_only_in_transfer():
    # The Python equivalent of `grep -l getUserMedia app/*.js` (CLAUDE.md Part 2, layer rule 8);
    # no shelling out, Windows has no `grep` on PATH by default.
    files = sorted(
        path.name
        for path in (ROOT / "app").glob("*.js")
        if "getUserMedia" in path.read_text(encoding="utf-8")
    )
    assert files == ["transfer.js"]


def test_no_rtc_peer_connection_in_app():
    # CLAUDE.md Part 2, layer rule 7 (2026-09-16, Task-32): no file under app/ may construct
    # a WebRTC peer connection.
    for path in (ROOT / "app").rglob("*.js"):
        assert "RTCPeerConnection" not in path.read_text(encoding="utf-8")


def test_store_js_inlined_once_before_app_js():
    # Task-24: store.js sits between transfer.js and app.js (build_app.JS_FILES); app.js reads
    # window.CrosscheckStore at startup, so it must already be defined by then.
    build_app.main()
    html = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")

    assert html.count("window.CrosscheckStore = ") == 1
    store_index = html.index("window.CrosscheckStore = ")
    app_index = html.index("DEFAULT_HASH")
    assert store_index < app_index


def test_store_js_has_no_network_words():
    # The Python equivalent of `grep -nE "fetch\\(|XMLHttpRequest|WebSocket|EventSource|https?://"
    # app/store.js` (CLAUDE.md Part 2, layer rule 7); no shelling out, Windows has no `grep` on
    # PATH by default.
    source = (ROOT / "app" / "store.js").read_text(encoding="utf-8")
    for token in ("fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "http://", "https://"):
        assert token not in source


def test_report_js_inlined_once_between_store_js_and_app_js():
    # Task-35: report.js sits after store.js (it calls window.CrosscheckStore) and before
    # app.js (which calls window.CrosscheckReport while rendering a community).
    build_app.main()
    html = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")

    assert html.count("window.CrosscheckReport = ") == 1
    store_index = html.index("window.CrosscheckStore = ")
    report_index = html.index("window.CrosscheckReport = ")
    app_index = html.index("DEFAULT_HASH")
    assert store_index < report_index < app_index


def test_report_js_makes_no_request_and_holds_no_verdict():
    # Task-35, CLAUDE.md Part 2 layer rules 4 and 7: report.js requests nothing, and a report
    # never touches a badge -- `grep -n "verdict" app/report.js` prints nothing. The Python
    # equivalent of the greps; Windows has no `grep` on PATH by default.
    source = (ROOT / "app" / "report.js").read_text(encoding="utf-8")
    for token in (
        "fetch(",
        "XMLHttpRequest",
        "WebSocket",
        "EventSource",
        "RTCPeerConnection",
        "http://",
        "https://",
        "verdict",
    ):
        assert token not in source
    # The position is asked for in exactly one place, the save handler's own helper, and only
    # when the checkbox is ticked.
    assert source.count("getCurrentPosition") == 1


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


def test_jsqr_licence_header_once_before_scan_before_transfer():
    # Task-25: the vendored jsQR block carries its own one-line notice (Apache-2.0 section
    # 4(b)) exactly once, ahead of window.CrosscheckScan (which uses it); CrosscheckScan itself
    # is defined before window.CrosscheckTransfer (which calls it), per build_app.JS_FILES.
    build_app.main()
    html = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")

    assert html.count(build_app.JSQR_LICENSE_HEADER) == 1
    assert html.count("window.CrosscheckScan = ") == 1

    header_index = html.index(build_app.JSQR_LICENSE_HEADER)
    scan_index = html.index("window.CrosscheckScan = ")
    transfer_index = html.index("window.CrosscheckTransfer")
    assert header_index < scan_index < transfer_index

    assert len(html.encode("utf-8")) <= 1_048_576


def test_vendored_jsqr_sha256_matches_license_file():
    # The Execution Guide's own audit trail: app/vendor/jsQR.LICENSE records the SHA-256 of the
    # edited file as vendored; a hand-edit to app/vendor/jsQR.js that is not also re-recorded
    # there is exactly the drift this check exists to catch.
    vendored = (ROOT / "app" / "vendor" / "jsQR.js").read_bytes()
    digest = hashlib.sha256(vendored).hexdigest()

    license_text = (ROOT / "app" / "vendor" / "jsQR.LICENSE").read_text(encoding="utf-8")
    match = re.search(
        r"SHA-256, app/vendor/jsQR\.js, edited[^:]*:\s*\n\s*([0-9a-f]{64})", license_text
    )
    assert match, "no recorded SHA-256 for the edited app/vendor/jsQR.js in jsQR.LICENSE"
    assert digest == match.group(1)


def test_exactly_one_fetch_in_the_app_and_it_is_guarded():
    # CLAUDE.md Part 2, layer rule 7 and its single exception (2026-09-16, Task-36). The Python
    # equivalent of `grep -c "fetch(" app/**/*.js`; Windows has no `grep` on PATH by default.
    # sw.js is the host-only exception the rule already names and is never needed for first
    # render, so it is not in the count.
    counts = {
        path.name: path.read_text(encoding="utf-8").count("fetch(")
        for path in sorted((ROOT / "app").rglob("*.js"))
        if path.name != "sw.js"
    }
    assert sum(counts.values()) == 1, counts
    assert counts["transfer.js"] == 1

    # The exception is only legal guarded: a lite copy, and a tap. Both are in the source.
    transfer = (ROOT / "app" / "transfer.js").read_text(encoding="utf-8")
    assert 'document.documentElement.dataset.lite === "1"' in transfer
    guard_index = transfer.index("const isLite = ")
    fetch_index = transfer.index("fetch(")
    click_index = transfer.rindex('addEventListener("click"', 0, fetch_index)
    assert guard_index < click_index < fetch_index


def test_lite_page_is_built_and_is_lite():
    # Task-36: dist/lite.html is what the camera carries -- the same build with the vendored
    # jsQR cut, the pack's layers emptied and data-lite="1" on <html>. The gate's size check
    # stays on dist/index.html; the limit is asserted here for the second page.
    build_app.main()
    lite_path = ROOT / "dist" / "lite.html"
    lite = lite_path.read_text(encoding="utf-8")

    assert '<html data-lite="1"' in lite
    assert build_app.JSQR_LICENSE_HEADER not in lite
    assert "function jsQR(" not in lite
    # The name survives: transfer.js reads it, and transfer.js is inlined in every build. What
    # must be gone is the assignment -- a lite copy carries no payload of its own.
    assert "window.CrosscheckLite = " not in lite

    pack = json.loads(
        re.search(r'<script type="application/json" id="pack">(.*?)</script>', lite, re.S).group(1)
    )
    assert pack["layers"] == []
    assert len(pack["communities"]) == 96
    assert pack["app_url"] == read_constant("APP_URL")
    assert len(lite.encode("utf-8")) <= 1_048_576
    # The whole point of the cut: far fewer frames to read off a screen (Task-31).
    assert len(lite.encode("utf-8")) < len((ROOT / "dist" / "index.html").read_bytes())


def test_lite_constant_is_the_lite_page_gzipped():
    # The circularity resolved: the constant in the full page inflates to exactly the bytes
    # dist/lite.html holds, and nothing in the lite page is the constant itself.
    build_app.main()
    html = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")
    lite_bytes = (ROOT / "dist" / "lite.html").read_bytes()

    match = re.search(r'window\.CrosscheckLite = "([A-Za-z0-9+/=]+)";', html)
    assert match, "no lite payload constant in dist/index.html"
    assert gzip.decompress(base64.b64decode(match.group(1))) == lite_bytes
    assert build_app.LITE_PLACEHOLDER not in html


def test_lite_cut_raises_when_its_markers_are_missing():
    # A silent no-op here would ship a "lite" copy that is not lite; both cuts refuse instead.
    with pytest.raises(ValueError, match="jsQR"):
        build_app.strip_jsqr("<html></html>")
    with pytest.raises(ValueError, match="lite payload constant"):
        build_app.strip_lite_constant("<html></html>")
    with pytest.raises(ValueError, match="pack"):
        build_app.empty_layers("<html></html>")
    with pytest.raises(ValueError, match="<html>"):
        build_app.mark_lite("<body></body>")


def test_barcode_detector_only_in_scan_js():
    # The Python equivalent of `grep -l BarcodeDetector app/*.js` (Task-25 DoD); no shelling
    # out, Windows has no `grep` on PATH by default. app/vendor/jsQR.js is a decoder, not a
    # reader adapter, and never references BarcodeDetector either.
    files = sorted(
        path.name
        for path in (ROOT / "app").rglob("*.js")
        if "BarcodeDetector" in path.read_text(encoding="utf-8")
    )
    assert files == ["scan.js"]
