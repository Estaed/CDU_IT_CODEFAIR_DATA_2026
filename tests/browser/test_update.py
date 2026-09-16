"""Browser tests for Task-24: a pack received by light that is newer than the
built-in one is kept in the browser's own storage (store.js, IndexedDB) and used on every later
start, with an update chip and a way back to the built-in pack (CLAUDE.md Part 2, "Pack header"
seam; Tarik's decision 2026-09-15: "update atsin"). A fresh browser context per test keeps
IndexedDB from leaking between tests, since the file:// origin is shared."""

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


def test_no_stored_pack_shows_no_update_chip(context):
    page, blocked, errors = _open_page(context)

    expect(page.locator(".update-chip")).to_be_hidden()
    stored = page.evaluate("() => window.CrosscheckStore.load()")
    assert stored is None

    assert errors == []
    assert blocked == []
    page.close()


def test_stored_pack_newer_renders_after_reload_and_use_built_in_reverts(context):
    page, blocked, errors = _open_page(context)

    original_name = page.locator(".community-header__name").text_content()

    changed = page.evaluate(
        """
        async () => {
            const pack = JSON.parse(document.getElementById("pack").textContent);
            const [year, month, day] = pack.built.split("-").map(Number);
            const next = new Date(Date.UTC(year, month - 1, day + 1));
            pack.built = next.toISOString().slice(0, 10);
            const target = pack.communities.find((c) => c.id === 426);
            target.name = target.name + " (updated)";
            const result = await window.CrosscheckStore.save(JSON.stringify(pack));
            return { built: result.built, name: target.name };
        }
        """
    )
    assert changed["built"] is not None

    page.reload()
    page.wait_for_load_state()

    expect(page.locator(".update-chip")).to_be_visible()
    expect(page.locator(".update-chip")).to_contain_text(f"Pack updated {changed['built']}")
    expect(page.locator(".community-header__name")).to_have_text(changed["name"])

    with page.expect_navigation(wait_until="load"):
        page.get_by_role("button", name="Use built-in pack").click()

    expect(page.locator(".update-chip")).to_be_hidden()
    expect(page.locator(".community-header__name")).to_have_text(original_name)
    stored = page.evaluate("() => window.CrosscheckStore.load()")
    assert stored is None

    assert errors == []
    assert blocked == []
    page.close()


def test_save_rejects_wrong_version_or_community_count(context):
    page, blocked, errors = _open_page(context)

    result = page.evaluate(
        """
        async () => {
            const pack = JSON.parse(document.getElementById("pack").textContent);

            const wrongVersion = { ...pack, pack_version: pack.pack_version + 1 };
            const r1 = await window.CrosscheckStore.save(JSON.stringify(wrongVersion));

            const fewerCommunities = { ...pack, communities: pack.communities.slice(0, 95) };
            const r2 = await window.CrosscheckStore.save(JSON.stringify(fewerCommunities));

            const stored = await window.CrosscheckStore.load();
            return { r1: r1.built, r2: r2.built, stored };
        }
        """
    )
    assert result["r1"] is None
    assert result["r2"] is None
    assert result["stored"] is None

    assert errors == []
    assert blocked == []
    page.close()


def test_transfer_receive_completion_stores_pack(context):
    dist_bytes = DIST.read_bytes()
    html_text = dist_bytes.decode("utf-8")
    pack_match = re.search(
        r'<script type="application/json" id="pack">(.*?)</script>', html_text, re.S
    )
    expected_built = json.loads(pack_match.group(1))["built"]

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
            await window.CrosscheckTransfer.testReceiveComplete(rx.bytes());
            const stored = await window.CrosscheckStore.load();
            return { complete: true, storedBuilt: stored ? stored.built : null };
        }
        """,
        html_text,
    )
    assert result["complete"]
    assert result["storedBuilt"] == expected_built

    use_received = page.locator(".transfer__button", has_text="Use received pack now")
    expect(use_received).to_be_visible()

    assert errors == []
    assert blocked == []
    page.close()


def test_transfer_and_store_module_have_no_network_or_camera_literals():
    store_source = (ROOT / "app" / "store.js").read_text(encoding="utf-8")
    for token in ("fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "http://", "https://"):
        assert token not in store_source
    assert "getUserMedia" not in store_source
