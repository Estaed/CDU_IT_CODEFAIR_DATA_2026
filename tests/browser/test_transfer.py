"""Browser tests for transfer by camera (Task-18): the frame contract and the round trip
without a camera, and the Show/Receive controls on the share screen. Headless Chromium may
lack BarcodeDetector and a camera (Part 2), so the round trip feeds frame texts straight to
CrosscheckTransfer.reassemble instead of scanning."""

from __future__ import annotations

import hashlib
import random
import re
from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist" / "index.html"
DIST_INDEX = DIST.resolve().as_uri()

FRAME_RE = re.compile(r"^CX([0-9a-f]{4})([0-9a-f]{4})([A-Za-z0-9+/=]{1,1000})$")


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


def test_frame_contract_and_round_trip_without_a_camera(context):
    dist_bytes = DIST.read_bytes()
    html_text = dist_bytes.decode("utf-8")

    page, blocked, errors = _open_page(context, "#/share")

    frame_data = page.evaluate(
        """
        async (html) => {
            const frames = await window.CrosscheckTransfer.frames(html);
            const versions = frames.map((f) => window.CrosscheckQR.encode(f, "L").version);
            return { frames, versions };
        }
        """,
        html_text,
    )
    frame_texts = frame_data["frames"]
    versions = frame_data["versions"]
    n = len(frame_texts)
    assert n >= 1

    for text, version in zip(frame_texts, versions, strict=True):
        match = FRAME_RE.match(text)
        assert match, text
        count = int(match.group(2), 16)
        assert count == n
        assert version <= 40

    # Shuffle, and throw in duplicates of the first and last frame: reassemble must still
    # complete, order-insensitive, with duplicates ignored.
    with_duplicates = [*frame_texts, frame_texts[0], frame_texts[-1]]
    random.Random(20260915).shuffle(with_duplicates)

    result = page.evaluate(
        """
        async (frameTexts) => {
            const reassembled = window.CrosscheckTransfer.reassemble(frameTexts);
            if (!reassembled.complete) {
                return { complete: false };
            }
            const inflatedText = await window.CrosscheckTransfer.inflate(reassembled.bytes);
            const bytes = new TextEncoder().encode(inflatedText);
            const digest = await crypto.subtle.digest("SHA-256", bytes);
            const hex = Array.from(new Uint8Array(digest))
                .map((b) => b.toString(16).padStart(2, "0"))
                .join("");
            return {
                complete: true,
                received: reassembled.received,
                total: reassembled.total,
                sha256: hex,
            };
        }
        """,
        with_duplicates,
    )

    assert result["complete"]
    assert result["received"] == n
    assert result["total"] == n
    assert result["sha256"] == hashlib.sha256(dist_bytes).hexdigest()

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

    expect(stage).to_be_hidden()
    expect(open_button).to_be_hidden()
    expect(download_link).to_be_hidden()

    show_button = page.locator(".transfer").get_by_role("button", name="Show", exact=True)
    show_button.click()
    expect(stage).to_be_visible()

    assert errors == []
    assert blocked == []
    page.close()


def test_show_and_stop_controls(context):
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
    expect(counter).to_have_text(re.compile(r"^frame 1 of \d+$"))

    stop_button = transfer.get_by_role("button", name="Stop", exact=True)
    expect(stop_button).to_have_count(1)
    stop_button.click()

    frozen = counter.text_content()
    page.wait_for_timeout(500)
    assert counter.text_content() == frozen

    assert errors == []
    assert blocked == []
    page.close()
