"""Browser tests for the QR reader adapter (Task-25): jsQR takes over when the browser has no
BarcodeDetector (Safari on iPhone, broken since iOS 18), and the native reader is used when one
exists. Headless Chromium has no camera, so every code here is drawn onto a canvas by the page
itself (fillRect at 4 units per module, a 4-module quiet zone) and decoded back through
CrosscheckScan; no video element or getUserMedia is involved (CLAUDE.md Part 2, layer rule 8).

Vendored jsQR 1.4.0 shipped with a wrong `alignmentPatternCenters` entry for version 23 (its own
table read `[6, 30, 54, 74, 102]`; the ISO/IEC 18004 value is `[6, 30, 54, 78, 102]`), found while
first writing this test: every QR code jsQR sized at version 23 failed to decode, content- and
scale-independent, including one rendered from Python's own `qrcode` matrix via Pillow, bypassing
this app's code entirely. Fixed as a second recorded edit in app/vendor/jsQR.js (see
app/vendor/jsQR.LICENSE for the full citation and verification); test_all_versions_1_to_40 below
is the regression check that would catch this again."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist" / "index.html"
DIST_INDEX = DIST.resolve().as_uri()

# Byte-mode capacity per QR version (index 0 = version 1) at error-correction level L: from
# Python's own qrcode.util.BIT_LIMIT_TABLE[ERROR_CORRECT_L], through the same formula app/qr.js
# uses in bestVersion (floor((bit_limit - 4 mode bits - char-count bits) / 8)).
BYTE_CAPACITY_L = [
    17, 32, 53, 78, 106, 134, 154, 192, 230, 271, 321, 367, 425, 458, 520, 586, 644, 718, 792,
    858, 929, 1003, 1091, 1171, 1273, 1367, 1465, 1528, 1628, 1732, 1840, 1952, 2068, 2188, 2303,
    2431, 2563, 2699, 2809, 2953,
]

# Draws each text as CrosscheckQR.encode(text, level) onto a fresh canvas with fillRect (white
# background, black modules, 4 units per module, a 4-module quiet zone), then decodes it back
# through CrosscheckScan.decodeImageData -- the jsQR path alone, no camera needed. Returns both
# the decoded text and the version jsQR itself was asked to read.
DRAW_AND_DECODE = """
([texts, level]) => {
    const UNIT = 4;
    const QUIET = 4;
    const results = [];
    for (const text of texts) {
        const result = window.CrosscheckQR.encode(text, level);
        const modulesPerSide = result.size + 2 * QUIET;
        const canvas = document.createElement("canvas");
        canvas.width = modulesPerSide * UNIT;
        canvas.height = modulesPerSide * UNIT;
        const ctx = canvas.getContext("2d");
        ctx.fillStyle = "white";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "black";
        for (let y = 0; y < result.size; y++) {
            for (let x = 0; x < result.size; x++) {
                if (result.modules[y * result.size + x]) {
                    ctx.fillRect((x + QUIET) * UNIT, (y + QUIET) * UNIT, UNIT, UNIT);
                }
            }
        }
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const decoded = window.CrosscheckScan.decodeImageData(imageData);
        results.push({ decoded, version: result.version });
    }
    return results;
}
"""


def _open_page(context, hash_route: str = ""):
    page = context.new_page()
    blocked: list[str] = []
    errors: list[str] = []

    def handler(route):
        url = route.request.url
        if not url.startswith("file:"):
            blocked.append(url)
            route.abort()
        else:
            route.continue_()

    page.route("**/*", handler)
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(f"{DIST_INDEX}{hash_route}")
    page.wait_for_load_state()
    return page, blocked, errors


def test_jsqr_path_decodes_frames_offer_and_wifi_text(browser):
    context = browser.new_context()
    # Force the jsQR path even where headless Chromium does support BarcodeDetector.
    context.add_init_script("delete window.BarcodeDetector;")
    page, blocked, errors = _open_page(context, "#/share")

    assert page.evaluate('() => "BarcodeDetector" in window') is False
    assert page.evaluate("() => window.CrosscheckScan.kind()") == "jsqr"

    html_text = DIST.read_text(encoding="utf-8")
    frame_texts = page.evaluate(
        "(html) => window.CrosscheckTransfer.frames(html)", html_text
    )
    n = len(frame_texts)
    assert n >= 1
    # The first, the last and every 16th frame.
    sample_indices = sorted({0, n - 1, *range(0, n, 16)})
    sample_frames = [frame_texts[i] for i in sample_indices]

    offer_text = page.evaluate("() => window.CrosscheckNearby.start()")
    wifi_text = "WIFI:T:WPA;S:Crosscheck;P:pass\\;word;;"

    texts = [*sample_frames, offer_text, wifi_text]
    results = page.evaluate(DRAW_AND_DECODE, [texts, "L"])

    for text, result in zip(texts, results, strict=True):
        assert result["decoded"] == text, (text, result)

    page.evaluate("() => window.CrosscheckNearby.close()")

    assert errors == []
    assert blocked == []
    page.close()
    context.close()


def test_all_versions_1_to_40_decode_at_byte_mode_capacity(browser):
    # Regression check for the jsQR alignment-table fix (module docstring): one text per QR
    # version 1-40, each exactly at that version's byte-mode capacity at level L, so
    # CrosscheckQR.encode is forced to land on every version in turn.
    context = browser.new_context()
    context.add_init_script("delete window.BarcodeDetector;")
    page, blocked, errors = _open_page(context, "#/share")

    assert page.evaluate("() => window.CrosscheckScan.kind()") == "jsqr"

    texts = [
        "".join(chr(33 + (i % 94)) for i in range(capacity)) for capacity in BYTE_CAPACITY_L
    ]
    results = page.evaluate(DRAW_AND_DECODE, [texts, "L"])

    for version, (text, result) in enumerate(zip(texts, results, strict=True), start=1):
        assert result["version"] == version, (version, result["version"])
        assert result["decoded"] == text, version

    assert errors == []
    assert blocked == []
    page.close()
    context.close()


def test_native_path_used_when_barcode_detector_is_present(browser):
    context = browser.new_context()
    # A stub BarcodeDetector, present regardless of what headless Chromium itself supports.
    context.add_init_script(
        """
        window.__stubDetectCalls = 0;
        window.BarcodeDetector = class {
            constructor(options) { this.options = options; }
            async detect(video) {
                window.__stubDetectCalls += 1;
                return [{ rawValue: "stub-value" }];
            }
        };
        """
    )
    page, blocked, errors = _open_page(context, "#/share")

    assert page.evaluate('() => "BarcodeDetector" in window') is True
    assert page.evaluate("() => window.CrosscheckScan.kind()") == "native"

    result = page.evaluate(
        """
        async () => {
            const video = document.createElement("video");
            const values = await window.CrosscheckScan.reader().detect(video);
            return { values, calls: window.__stubDetectCalls };
        }
        """
    )
    assert result["values"] == ["stub-value"]
    assert result["calls"] == 1

    assert errors == []
    assert blocked == []
    page.close()
    context.close()
