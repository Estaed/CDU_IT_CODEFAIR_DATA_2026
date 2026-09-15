"""Browser test for the runtime QR encoder (Task-17): app/qr.js checked module for module
against the Python qrcode package, the oracle CLAUDE.md Part 2 names for the QR encoder."""

from __future__ import annotations

from pathlib import Path

import pytest
import qrcode

from pipeline.pack import read_constant

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist" / "index.html"
DIST_INDEX = DIST.resolve().as_uri()

# A 32-bit LCG (Numerical Recipes constants): the Python oracle and the page each derive the
# same 1,000-byte input independently from this seed and this integer sequence, with no
# fixture shipped between them (Task-17 DoD).
PRNG_SEED = 20260915
PRNG_MULT = 1103515245
PRNG_INC = 12345


def _prng_bytes(n: int) -> bytes:
    state = PRNG_SEED
    out = bytearray(n)
    for i in range(n):
        state = (PRNG_MULT * state + PRNG_INC) & 0xFFFFFFFF
        out[i] = (state >> 16) & 0xFF
    return bytes(out)


def _oracle(data: bytes, level: str) -> tuple[int, int, set[tuple[int, int]]]:
    ec = qrcode.constants.ERROR_CORRECT_L if level == "L" else qrcode.constants.ERROR_CORRECT_M
    code = qrcode.QRCode(error_correction=ec, border=0)
    # optimize=0: one QRData in byte mode, matching qr.js, which encodes byte mode only.
    code.add_data(data, optimize=0)
    code.make(fit=True)
    matrix = code.get_matrix()
    dark = {(x, y) for y, row in enumerate(matrix) for x, value in enumerate(row) if value}
    return code.version, len(matrix), dark


@pytest.fixture
def context(browser):
    context = browser.new_context()
    yield context
    context.close()


def _open_page(context):
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
    page.goto(DIST_INDEX)
    page.wait_for_load_state()
    return page, blocked, errors


def _assert_matches_oracle(result: dict, data: bytes, level: str):
    version, size, expected = _oracle(data, level)
    assert result["version"] == version
    assert result["size"] == size
    got = {
        (x, y)
        for y in range(result["size"])
        for x in range(result["size"])
        if result["modules"][y * result["size"] + x]
    }
    assert got == expected


def test_encode_short_text_at_m(context):
    page, blocked, errors = _open_page(context)
    data = b"Crosscheck"
    result = page.evaluate(
        """([bytes, level]) => {
            const r = window.CrosscheckQR.encode(new Uint8Array(bytes), level);
            return { version: r.version, size: r.size, modules: Array.from(r.modules) };
        }""",
        [list(data), "M"],
    )
    _assert_matches_oracle(result, data, "M")
    assert errors == []
    assert blocked == []
    page.close()


def test_encode_app_url_at_m(context):
    page, blocked, errors = _open_page(context)
    data = read_constant("APP_URL").encode("utf-8")
    result = page.evaluate(
        """([bytes, level]) => {
            const r = window.CrosscheckQR.encode(new Uint8Array(bytes), level);
            return { version: r.version, size: r.size, modules: Array.from(r.modules) };
        }""",
        [list(data), "M"],
    )
    _assert_matches_oracle(result, data, "M")
    assert errors == []
    assert blocked == []
    page.close()


def test_encode_seeded_1000_bytes_at_l(context):
    page, blocked, errors = _open_page(context)
    data = _prng_bytes(1000)
    # The page derives the same 1,000 bytes itself, from the same seed and the same LCG
    # constants, rather than receiving the array computed on the Python side.
    result = page.evaluate(
        """([seed, mult, inc, n, level]) => {
            let state = seed >>> 0;
            const bytes = new Uint8Array(n);
            for (let i = 0; i < n; i++) {
                state = ((Math.imul(mult, state) >>> 0) + inc) >>> 0;
                bytes[i] = (state >>> 16) & 0xFF;
            }
            const r = window.CrosscheckQR.encode(bytes, level);
            return { version: r.version, size: r.size, modules: Array.from(r.modules) };
        }""",
        [PRNG_SEED, PRNG_MULT, PRNG_INC, 1000, "L"],
    )
    _assert_matches_oracle(result, data, "L")
    assert errors == []
    assert blocked == []
    page.close()
