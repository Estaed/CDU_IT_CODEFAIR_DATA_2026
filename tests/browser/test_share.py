"""Browser tests for the share screen (Task-09): QR, pack date and sizes, the two buttons,
Save file downloading the page itself, no service worker over file://, offline and error-free."""

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
PACK = ROOT / "data" / "out" / "data_pack.json"


@pytest.fixture
def context(browser):
    context = browser.new_context(accept_downloads=True)
    yield context
    context.close()


def _open_page(context, hash_route: str):
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


def _sizes() -> tuple[int, int]:
    html = DIST.read_text(encoding="utf-8")
    pack_bytes, app_bytes = re.search(
        r'<meta name="crosscheck-sizes" content="pack=(\d+);app=(\d+)">', html
    ).groups()
    return int(pack_bytes), int(app_bytes)


def test_share_card_renders(context):
    built = json.loads(PACK.read_text(encoding="utf-8"))["built"]
    pack_bytes, app_bytes = _sizes()
    page, blocked, errors = _open_page(context, "#/share")

    expect(page.locator(".share-card")).to_have_count(1)
    expect(page.locator(".qr")).to_have_count(1)
    expect(page.locator(".qr .qr__modules")).to_have_count(1)
    expect(page.locator(".button")).to_have_count(2)
    expect(page.locator(".button--primary")).to_have_text("Share this app")
    expect(page.locator(".button--secondary")).to_have_text("Save file")

    meta = page.locator(".share-card__meta")
    figs = [text.strip() for text in meta.locator(".fig").all_text_contents()]
    assert built in figs
    assert f"{pack_bytes // 1024} KB" in figs
    assert f"{app_bytes // 1024} KB" in figs
    assert built in meta.inner_text()
    expect(page.locator(".share-card__statement")).to_contain_text("It does not measure signal.")
    expect(page.locator(".footer__team")).to_have_count(1)
    expect(page.locator("[role=tab][aria-selected=true]")).to_have_text("Share")

    assert page.evaluate("window.__swRegistered === undefined")
    # Task-28: the manifest link is a static <head> tag present on every route, not a runtime
    # service-worker registration; __swRegistered above stays unset offline either way.
    assert page.locator("link[rel=manifest]").count() == 1
    assert errors == []
    assert blocked == []
    page.close()


def test_save_file_downloads_the_page(context):
    page, blocked, errors = _open_page(context, "#/share")

    with page.expect_download() as download_info:
        page.locator(".button--secondary").click()
    download = download_info.value
    assert download.suggested_filename == "crosscheck.html"
    content = Path(download.path()).read_text(encoding="utf-8")

    assert content.startswith("<!DOCTYPE html>")
    assert content.count('id="pack"') == 1
    assert content.count('<template id="qr">') == 1
    assert 'name="crosscheck-sizes"' in content

    assert page.evaluate("window.__swRegistered === undefined")
    assert errors == []
    assert blocked == []
    page.close()


def test_saved_file_opens_offline(context, tmp_path):
    page, _, _ = _open_page(context, "#/share")
    with page.expect_download() as download_info:
        page.locator(".button--secondary").click()
    saved = tmp_path / "crosscheck.html"
    download_info.value.save_as(saved)
    page.close()

    copy = context.new_page()
    blocked: list[str] = []
    errors: list[str] = []

    def handler(route):
        url = route.request.url
        if not url.startswith("file:"):
            blocked.append(url)
            route.abort()
        else:
            route.continue_()

    copy.route("**/*", handler)
    copy.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    copy.on("pageerror", lambda exc: errors.append(str(exc)))
    copy.goto(f"{saved.resolve().as_uri()}#/share")
    copy.wait_for_load_state()

    expect(copy.locator(".share-card")).to_have_count(1)
    expect(copy.locator(".qr")).to_have_count(1)
    assert errors == []
    assert blocked == []
    copy.close()
