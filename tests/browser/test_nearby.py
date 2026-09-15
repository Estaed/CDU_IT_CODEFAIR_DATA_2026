"""Browser tests for nearby chat over Wi-Fi (Task-19): the offer/answer handshake through
CrosscheckNearby, a message each way, a pack request, and the Wi-Fi join QR text. Two pages in
the one fixture browser stand in for two phones (CLAUDE.md Part 2, verification rule 3(e)); no
signalling server, the offer and answer text move between the pages as Python strings, exactly
what a QR scan would hand over."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist" / "index.html"
DIST_INDEX = DIST.resolve().as_uri()


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


def test_handshake_message_and_pack_request(context):
    page_a, blocked_a, errors_a = _open_page(context, "#/nearby")
    page_b, blocked_b, errors_b = _open_page(context, "#/nearby")

    offer_text = page_a.evaluate("() => window.CrosscheckNearby.start()")
    assert len(offer_text) <= 2900, f"offer text is {len(offer_text)} characters"

    answer_text = page_b.evaluate(
        "(offer) => window.CrosscheckNearby.accept(offer)", offer_text
    )
    page_a.evaluate("(answer) => window.CrosscheckNearby.finish(answer)", answer_text)

    expect(page_a.locator(".nearby__state")).to_have_text("open", timeout=10_000)
    expect(page_b.locator(".nearby__state")).to_have_text("open", timeout=10_000)

    page_a.evaluate("() => window.CrosscheckNearby.send('hello')")
    expect(page_b.locator(".nearby__messages .nearby__msg--peer")).to_have_text("hello")
    expect(page_a.locator(".nearby__messages .nearby__msg--me")).to_have_text("hello")

    page_b.evaluate("() => window.CrosscheckNearby.requestPack()")
    pack_json = page_b.evaluate(
        """
        async () => {
            const start = Date.now();
            while (Date.now() - start < 5000) {
                const event = window.__nearby.events.find((e) => e.type === "pack");
                if (event) return event.json;
                await new Promise((resolve) => setTimeout(resolve, 50));
            }
            return null;
        }
        """
    )
    assert pack_json is not None, "no pack event arrived within 5s"
    pack = json.loads(pack_json)
    assert len(pack["communities"]) == 96

    page_a.evaluate("() => window.CrosscheckNearby.close()")
    page_b.evaluate("() => window.CrosscheckNearby.close()")
    expect(page_a.locator(".nearby__state")).to_have_text("closed")
    expect(page_b.locator(".nearby__state")).to_have_text("closed")

    assert errors_a == []
    assert errors_b == []
    assert blocked_a == []
    assert blocked_b == []
    page_a.close()
    page_b.close()


def test_wifi_join_qr_text_is_escaped(context):
    page, blocked, errors = _open_page(context, "#/nearby")

    page.get_by_placeholder("Network name").fill("Crosscheck")
    page.get_by_placeholder("Password").fill("pass;word")

    qr = page.locator(".nearby__wifi-qr")
    expect(qr).to_have_attribute("data-text", r"WIFI:T:WPA;S:Crosscheck;P:pass\;word;;")
    expect(qr.locator("svg.nearby__qr")).to_have_count(1)

    assert errors == []
    assert blocked == []
    page.close()


def test_nearby_js_has_no_camera_or_network_literals():
    source = (ROOT / "app" / "nearby.js").read_text(encoding="utf-8")
    assert "iceServers: []" in source
    assert "stun:" not in source
    assert "turn:" not in source
    assert re.search(r"fetch\(|XMLHttpRequest|WebSocket|EventSource|https?://", source) is None
