"""Browser tests for transfer by camera v3 (Task-36): the `CZ` frame contract, the peeling
receiver's lossless and lossy-drop round trips, the lite copy the camera actually carries, and
the progress UI on both ends. Headless Chromium may lack BarcodeDetector and a camera (Part 2),
so every round trip below pushes frame texts straight into CrosscheckTransfer.receiver() (or the
mounted receive UI's testPushFrame hook) instead of scanning.

The loss budgets come from the main loop's soliton simulation at K 233 (Task-36's Measurement
section): 10% loss completes within 1.6 * K pushed frames, 50% within 2.8 * K, 70% within
4.5 * K. They are budgets for the *shipped* code path, and they are loose on purpose -- the real
payload is the lite copy at K about 97, where the peel has far fewer blocks to resolve, while
these tests run against dist/index.html at K about 233. The sources-0..19 scenario keeps v2's
1.75 * K. v2's uniform 6..12 degree, tuned against 10% loss, is gone: it stalled near block 110
on a real phone, which is what Task-31 measured and Task-36 fixed."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist" / "index.html"
LITE = ROOT / "dist" / "lite.html"
DIST_INDEX = DIST.resolve().as_uri()

FRAME_RE = re.compile(r"^CZ[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{6}[A-Za-z0-9+/]{1000}$")

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


@pytest.mark.parametrize(
    ("loss", "budget"),
    [(0.1, 1.6), (0.5, 2.8), (0.7, 4.5)],
    ids=["loss10", "loss50", "loss70"],
)
def test_seeded_drop_completes_within_budget(context, loss, budget):
    # Task-36: three losses, not one. A phone reading a screen loses half the frames or more,
    # which is what v2's uniform 6..12 degree was never tuned for; the robust soliton is. The
    # budgets are the main loop's simulation at K 233 (module docstring). Same seed the test has
    # always used (20260915), not chosen to make this pass.
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
            const cap = Math.ceil(built.k * {budget});
            let pushed = 0;
            let offered = 0;
            // Enough send-order frames to find `cap` survivors at this loss, with headroom.
            const maxOffered = Math.ceil(cap / (1 - {loss})) * 4;
            let status = {{ complete: false, known: 0, total: built.k }};
            while (!status.complete && pushed < cap && offered < maxOffered) {{
                const {{ index }} = seq.next();
                offered += 1;
                if (rand() < {loss}) {{
                    continue; // dropped, as if the camera missed this frame
                }}
                status = rx.push(built.frameAt(index));
                pushed += 1;
            }}
            if (!status.complete) {{
                return {{ complete: false, pushed, offered, k: built.k }};
            }}
            const inflatedText = await window.CrosscheckTransfer.inflate(rx.bytes());
            const encoded = new TextEncoder().encode(inflatedText);
            const digest = await crypto.subtle.digest("SHA-256", encoded);
            const hex = Array.from(new Uint8Array(digest))
                .map((b) => b.toString(16).padStart(2, "0"))
                .join("");
            return {{ complete: true, pushed, offered, k: built.k, sha256: hex }};
        }}
        """,
        html_text,
    )

    assert result["complete"], result
    assert result["pushed"] <= math.ceil(result["k"] * budget), result
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


def test_cy_frame_is_ignored(context):
    # Task-36: a v2 sender's frame is well-formed in every way except its prefix, and a v3
    # receiver must not mix the two contracts -- the degree distribution behind a `CY` repair
    # index is a different one, so peeling them together would decode to nothing. `known` stays
    # at 0. (A v1 `CX` frame is not even the right shape and never matched.)
    page, blocked, errors = _open_page(context, "#/share")

    status = page.evaluate(
        """
        () => {
            const rx = window.CrosscheckTransfer.receiver();
            const header = `CY${"0".repeat(4)}${"0061"}${"0002ee"}`;
            return rx.push(`${header}${"A".repeat(1000)}`);
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


def test_transfer_module_has_no_network_literals_beyond_the_one_exception():
    # Task-36: transfer.js now holds layer rule 7's single exception, `Complete this copy`. The
    # count and the guard are asserted in tests/test_build.py (the app-wide grep); here only the
    # rest of the rule still holds -- no address is written down, and no other transport.
    source = (ROOT / "app" / "transfer.js").read_text(encoding="utf-8")
    for token in ("XMLHttpRequest", "WebSocket", "EventSource", "http://", "https://"):
        assert token not in source


def test_full_page_has_lite_constant_and_lite_page_does_not():
    # The circularity resolved (Task-36): the full page carries the lite copy's gzipped bytes,
    # the lite copy carries none of its own and plays its own already-lite bytes.
    full = DIST.read_text(encoding="utf-8")
    lite = LITE.read_text(encoding="utf-8")

    assert full.count("window.CrosscheckLite = ") == 1
    assert "__LITE_B64__" not in full
    assert "window.CrosscheckLite = " not in lite


def test_lite_page_shows_complete_this_copy_and_requests_only_on_the_tap(blocking_page):
    # Layer rule 7's one exception, proved from both sides: the full page never requests
    # anything, the lite page requests nothing until the tap, and the tap makes exactly one
    # request, to the pack's own app_url. The fixture aborts it, so the failure message is what
    # an offline phone sees.
    full_page, full_blocked, full_errors = blocking_page(f"{DIST_INDEX}#/share")
    complete = full_page.locator("button.transfer__button", has_text="Complete this copy")
    expect(complete).to_have_count(0)
    assert full_blocked == []
    assert full_errors == []

    app_url = full_page.evaluate(
        "() => JSON.parse(document.getElementById('pack').textContent).app_url"
    )
    full_page.close()

    page, blocked, errors = blocking_page(f"{LITE.resolve().as_uri()}#/share")
    assert page.evaluate("() => document.documentElement.dataset.lite") == "1"
    button = page.locator("button.transfer__button", has_text="Complete this copy")
    expect(button).to_be_visible()
    assert blocked == []

    button.click()
    status = page.locator(".transfer__section", has=button).locator(".transfer__status")
    expect(status).to_have_text("No network yet, try again when this phone is online")
    assert blocked == [app_url]
    page.close()


def test_lite_page_carries_no_vendored_jsqr_and_no_map_layers():
    # "No jsQR" is checked as "no vendored jsQR": app/scan.js names window.jsQR as its fallback
    # reader and is inlined in every build, so the literal string survives by design. What must
    # be gone is the library itself -- its licence marker and its own definition.
    lite = LITE.read_text(encoding="utf-8")
    assert "function jsQR(" not in lite
    assert "jsQR 1.4.0, Apache-2.0" not in lite
    pack = json.loads(
        re.search(
            r'<script type="application/json" id="pack">(.*?)</script>', lite, re.S
        ).group(1)
    )
    assert pack["layers"] == []
    assert len(pack["communities"]) == 96
    assert len(LITE.read_bytes()) <= 1_048_576
