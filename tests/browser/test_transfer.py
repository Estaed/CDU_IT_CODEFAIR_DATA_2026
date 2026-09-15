"""Browser tests for transfer by camera v2 (Task-27): the `CY` frame contract, the peeling
receiver's lossless and lossy-drop round trips, and the progress UI on both ends. Headless
Chromium may lack BarcodeDetector and a camera (Part 2), so every round trip below pushes frame
texts straight into CrosscheckTransfer.receiver() (or the mounted receive UI's testPushFrame
hook) instead of scanning.

test_seeded_ten_percent_drop_completes_within_budget and
test_sources_0_to_19_never_delivered_still_completes assert a pushed-frame budget of `1.75 * K`,
Tarik's decision (2026-09-15) after the first cut's pinned robust-soliton parameters could not
clear a 10% loss within the DoD's original `1.5 * K` at the app's real K (see
`tasks/Task-27.md`'s Status section for the full history). The repair algorithm changed to match:
after the first pass of K source frames, only new repair frames are sent (no cycling source
resend), and a repair frame's degree is a uniform integer in 6..12 (clamped to K) instead of a
robust soliton draw. Measured with a standalone simulation of this exact code path, 50 seeded
10%-drop trials at K = 224 (the app's real size): `1.5 * K` (cap 336) clears 45 of 50, worst
case exceeds the cap; `1.75 * K` (cap 392) clears all 50, worst case 345 pushed frames -- the
smallest multiplier of the six tried (1.5, 1.75, 2.0, 2.25, 2.5, 3.0) that reaches 50/50. Full
table in `tasks/Task-27.md`'s Status section."""

from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist" / "index.html"
DIST_INDEX = DIST.resolve().as_uri()

FRAME_RE = re.compile(r"^CY[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{6}[A-Za-z0-9+/]{1000}$")

# A small seeded PRNG (mulberry32), reused by the drop test below so the drop pattern is fixed
# run to run without pulling in a dependency for one test.
MULBERRY32_JS = """
(seed) => {
    let state = seed | 0;
    return () => {
        state |= 0; state = (state + 0x6D2B79F5) | 0;
        let t = Math.imul(state ^ (state >>> 15), 1 | state);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}
"""


@pytest.fixture
def context(browser):
    context = browser.new_context()
    yield context
    context.close()


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


def _dist_html_text() -> str:
    return DIST.read_bytes().decode("utf-8")


def test_frame_regex_matches_source_and_repair_frames(context):
    html_text = _dist_html_text()
    page, blocked, errors = _open_page(context, "#/share")

    result = page.evaluate(
        """
        async (html) => {
            const built = await window.CrosscheckTransfer.encoder(html);
            const texts = [];
            for (let i = 0; i < built.k; i++) texts.push(built.frameAt(i));
            for (let i = built.k; i < built.k + 20; i++) texts.push(built.frameAt(i));
            return { k: built.k, texts };
        }
        """,
        html_text,
    )
    assert result["k"] >= 1
    for text in result["texts"]:
        assert FRAME_RE.match(text), text

    assert errors == []
    assert blocked == []
    page.close()


def test_lossless_completion_at_exactly_k_frames(context):
    dist_bytes = DIST.read_bytes()
    html_text = dist_bytes.decode("utf-8")
    page, blocked, errors = _open_page(context, "#/share")

    result = page.evaluate(
        """
        async (html) => {
            const built = await window.CrosscheckTransfer.encoder(html);
            const rx = window.CrosscheckTransfer.receiver();
            let status;
            for (let i = 0; i < built.k; i++) {
                status = rx.push(built.frameAt(i));
            }
            if (!status.complete) {
                return { complete: false };
            }
            const inflatedText = await window.CrosscheckTransfer.inflate(rx.bytes());
            const encoded = new TextEncoder().encode(inflatedText);
            const digest = await crypto.subtle.digest("SHA-256", encoded);
            const hex = Array.from(new Uint8Array(digest))
                .map((b) => b.toString(16).padStart(2, "0"))
                .join("");
            return { complete: true, known: status.known, total: status.total, sha256: hex };
        }
        """,
        html_text,
    )

    assert result["complete"], result
    assert result["known"] == result["total"]
    assert result["sha256"] == hashlib.sha256(dist_bytes).hexdigest()

    assert errors == []
    assert blocked == []
    page.close()


def test_seeded_ten_percent_drop_completes_within_budget(context):
    # Budget: 1.75 * K (Tarik's decision, 2026-09-15 -- see the module docstring and
    # tasks/Task-27.md's Status section for the 50-seed measurement this comes from). Same
    # seed the test has always used (20260915), not chosen to make this pass -- at K = 224 it
    # completes at 321 pushed frames, well inside every multiplier tried.
    dist_bytes = DIST.read_bytes()
    html_text = dist_bytes.decode("utf-8")
    page, blocked, errors = _open_page(context, "#/share")

    result = page.evaluate(
        f"""
        async (html) => {{
            const built = await window.CrosscheckTransfer.encoder(html);
            const seq = window.CrosscheckTransfer.createSequence(built.k);
            const mulberry32 = {MULBERRY32_JS};
            const rand = mulberry32(20260915);

            const rx = window.CrosscheckTransfer.receiver();
            const cap = Math.ceil(built.k * 1.75);
            let pushed = 0;
            let offered = 0;
            const maxOffered = cap * 4; // enough send-order frames to find `cap` survivors
            let status = {{ complete: false, known: 0, total: built.k }};
            while (!status.complete && pushed < cap && offered < maxOffered) {{
                const {{ index }} = seq.next();
                offered += 1;
                if (rand() < 0.1) {{
                    continue; // dropped, as if the camera missed this frame
                }}
                status = rx.push(built.frameAt(index));
                pushed += 1;
            }}
            if (!status.complete) {{
                return {{ complete: false, pushed, k: built.k }};
            }}
            const inflatedText = await window.CrosscheckTransfer.inflate(rx.bytes());
            const encoded = new TextEncoder().encode(inflatedText);
            const digest = await crypto.subtle.digest("SHA-256", encoded);
            const hex = Array.from(new Uint8Array(digest))
                .map((b) => b.toString(16).padStart(2, "0"))
                .join("");
            return {{ complete: true, pushed, k: built.k, sha256: hex }};
        }}
        """,
        html_text,
    )

    assert result["complete"], result
    assert result["pushed"] <= math.ceil(result["k"] * 1.75)
    assert result["sha256"] == hashlib.sha256(dist_bytes).hexdigest()

    assert errors == []
    assert blocked == []
    page.close()


def test_sources_0_to_19_never_delivered_still_completes(context):
    # Same 1.75 * K budget as the drop test above (Tarik's decision, 2026-09-15). This scenario
    # has no randomness beyond the fixed omission, so it is deterministic: at K = 224 it
    # completes at 302 pushed frames, well inside the budget.
    dist_bytes = DIST.read_bytes()
    html_text = dist_bytes.decode("utf-8")
    page, blocked, errors = _open_page(context, "#/share")

    result = page.evaluate(
        """
        async (html) => {
            const built = await window.CrosscheckTransfer.encoder(html);
            if (built.k <= 20) {
                return { skip: true };
            }
            const seq = window.CrosscheckTransfer.createSequence(built.k);
            const rx = window.CrosscheckTransfer.receiver();
            const cap = Math.ceil(built.k * 1.75);
            let pushed = 0;
            let offered = 0;
            const maxOffered = cap * 4;
            let status = { complete: false, known: 0, total: built.k };
            while (!status.complete && pushed < cap && offered < maxOffered) {
                const { index } = seq.next();
                offered += 1;
                if (index < 20) {
                    continue; // never delivered, no other loss
                }
                status = rx.push(built.frameAt(index));
                pushed += 1;
            }
            if (!status.complete) {
                return { complete: false, pushed, k: built.k };
            }
            const inflatedText = await window.CrosscheckTransfer.inflate(rx.bytes());
            const encoded = new TextEncoder().encode(inflatedText);
            const digest = await crypto.subtle.digest("SHA-256", encoded);
            const hex = Array.from(new Uint8Array(digest))
                .map((b) => b.toString(16).padStart(2, "0"))
                .join("");
            return { complete: true, pushed, k: built.k, sha256: hex };
        }
        """,
        html_text,
    )

    assert not result.get("skip"), "dist/index.html is too small for this test (k <= 20)"
    assert result["complete"], result
    assert result["pushed"] <= math.ceil(result["k"] * 1.75)
    assert result["sha256"] == hashlib.sha256(dist_bytes).hexdigest()

    assert errors == []
    assert blocked == []
    page.close()


def test_cx_frame_is_ignored(context):
    page, blocked, errors = _open_page(context, "#/share")

    status = page.evaluate(
        """
        () => {
            const rx = window.CrosscheckTransfer.receiver();
            return rx.push(`CX0000${"0".repeat(4)}${"A".repeat(1000)}`);
        }
        """
    )
    assert status == {"complete": False, "known": 0, "total": 0}

    assert errors == []
    assert blocked == []
    page.close()


def test_receive_controls_and_show_stage_hidden_before_use(context):
    # Task-26: buildReceive() already set the `hidden` attribute on these three elements, but
    # .transfer__button and .transfer__stage each set their own `display` as normal-author CSS,
    # which outranks the UA stylesheet's [hidden]{display:none} in the cascade regardless of
    # specificity -- so `hidden` had no visual effect until app.css added [hidden] overrides.
    page, blocked, errors = _open_page(context, "#/share")

    stage = page.locator(".transfer__stage")
    open_button = page.locator("button.transfer__button", has_text="Open received app")
    download_link = page.locator("a.transfer__button", has_text="Download crosscheck.html")
    progress = page.locator(".transfer__progress")

    expect(stage).to_be_hidden()
    expect(open_button).to_be_hidden()
    expect(download_link).to_be_hidden()
    expect(progress).to_be_hidden()

    show_button = page.locator(".transfer").get_by_role("button", name="Show", exact=True)
    show_button.click()
    expect(stage).to_be_visible()

    assert errors == []
    assert blocked == []
    page.close()


def test_show_and_stop_controls_report_frame_and_pass(context):
    page, blocked, errors = _open_page(context, "#/share")

    transfer = page.locator(".transfer")
    expect(transfer).to_have_count(1)
    show_button = transfer.get_by_role("button", name="Show", exact=True)
    receive_button = transfer.get_by_role("button", name="Receive", exact=True)
    expect(show_button).to_have_count(1)
    expect(receive_button).to_have_count(1)

    show_button.click()
    expect(transfer.locator("svg")).to_have_count(1)
    counter = transfer.locator(".transfer__counter")
    expect(counter).to_have_text(re.compile(r"frame \d+"), timeout=10_000)
    expect(counter).to_have_text(re.compile(r"pass \d+"))

    note = transfer.locator(".transfer__stage .transfer__note")
    expect(note).to_have_text("Keep showing until the other phone says Received.")

    stop_button = transfer.get_by_role("button", name="Stop", exact=True)
    expect(stop_button).to_have_count(1)
    stop_button.click()

    frozen = counter.text_content()
    page.wait_for_timeout(500)
    assert counter.text_content() == frozen

    assert errors == []
    assert blocked == []
    page.close()


def test_receiving_screen_progress_and_received_message(context):
    html_text = _dist_html_text()
    page, blocked, errors = _open_page(context, "#/share")

    push_result = page.evaluate(
        """
        async (html) => {
            const built = await window.CrosscheckTransfer.encoder(html);
            let status;
            for (let i = 0; i < built.k; i++) {
                status = await window.CrosscheckTransfer.testPushFrame(built.frameAt(i));
            }
            return { k: built.k, status };
        }
        """,
        html_text,
    )
    assert push_result["status"]["complete"]

    progress = page.locator(".transfer__progress")
    expect(progress).to_be_visible()
    progress_value = page.evaluate("() => document.querySelector('.transfer__progress').value")
    progress_max = page.evaluate("() => document.querySelector('.transfer__progress').max")
    assert progress_value == progress_max == push_result["k"]

    status_el = page.locator(".transfer__status")
    expect(status_el).to_have_text("Received. Tap Open.")

    open_button = page.locator("button.transfer__button", has_text="Open received app")
    expect(open_button).to_be_visible()

    assert errors == []
    assert blocked == []
    page.close()


def test_transfer_module_has_no_network_literals():
    source = (ROOT / "app" / "transfer.js").read_text(encoding="utf-8")
    for token in ("fetch(", "XMLHttpRequest", "WebSocket", "http://", "https://"):
        assert token not in source
