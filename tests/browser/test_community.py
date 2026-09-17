"""Browser tests for the community screen (Task-07): search, header, sources,
services with expandable panels and assumption notes, publishers, footer."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST_INDEX = (ROOT / "dist" / "index.html").resolve().as_uri()


def _route_blocker(blocked: list[str]):
    def handler(route):
        url = route.request.url
        if not url.startswith("file:"):
            blocked.append(url)
            route.abort()
        else:
            route.continue_()

    return handler


def _open_page(browser, hash_route: str):
    page = browser.new_page()
    blocked: list[str] = []
    page.route("**/*", _route_blocker(blocked))
    page.goto(f"{DIST_INDEX}{hash_route}")
    page.wait_for_load_state()
    return page, blocked


def _community_ids() -> list[int]:
    pack = json.loads((ROOT / "data" / "out" / "data_pack.json").read_text(encoding="utf-8"))
    return [community["id"] for community in pack["communities"]]


def test_wadeye_renders(browser):
    page, blocked = _open_page(browser, "#/community/426")

    expect(page.locator("h1.community-header__name")).to_have_text("Wadeye")

    expect(page.locator(".service-row")).to_have_count(4)

    badges = page.locator(".service-row .verdict-badge")
    expect(badges).to_have_count(4)
    # textContent, not innerText: the badge is inline-flex with a gap, and Chromium renders
    # that gap as a line break in innerText while the DOM text is the glyph and the word.
    texts = ["".join(text.split()) for text in badges.all_text_contents()]
    assert texts == ["◐Degraded", "◐Degraded", "●Works", "●Works"]

    # design/screens/community.html shows an .assumption-note both on the one row
    # that is expanded and on a collapsed row (aria-expanded="false"), so an
    # assumption note does not depend on expand state there. We still click every
    # .service-row__button open before counting: that is a superset-safe check
    # that holds either way the implementation gates the note on expand state.
    buttons = page.locator(".service-row__button")
    for i in range(buttons.count()):
        buttons.nth(i).click()
    expect(page.locator(".assumption-note")).to_have_count(2)

    # Task-34: the agreement line and the publisher rows fold behind "Sources", closed by
    # default.
    page.locator("details.sources-fold > summary").click()
    headline_text = page.locator(".agreement__headline").inner_text()
    assert headline_text.count("4") >= 2

    # Four claims, then the National Audit's measured line (Task-38).
    expect(page.locator(".publisher-row")).to_have_count(5)

    footer_text = page.locator("footer").inner_text()
    assert "DIC005" in footer_text

    assert blocked == []
    page.close()


def test_search_port_keats(browser):
    page, blocked = _open_page(browser, "#/community/458")

    page.locator(".search-input").fill("Port Keats")

    results = page.locator(".result-row")
    expect(results).to_have_count(1)
    assert "Wadeye" in results.inner_text()

    results.first.click()
    expect(page).to_have_url(re.compile(r"#/community/426$"))

    assert blocked == []
    page.close()


def test_service_row_toggle(browser):
    # Task-34: the row is `button.service-row` itself; the toggled detail is its sibling
    # `.service-row__detail`, present in the DOM either way and shown or hidden by aria-expanded.
    page, blocked = _open_page(browser, "#/community/426")

    button = page.locator("button.service-row").first
    detail = page.locator(".service-row__detail").first
    sources_panel = detail.locator(".service-row__sources")
    expect(button).to_have_attribute("aria-expanded", "false")
    expect(detail).to_be_hidden()
    expect(sources_panel).to_have_count(1)

    button.click()
    expect(button).to_have_attribute("aria-expanded", "true")
    expect(detail).to_be_visible()
    expect(sources_panel.locator(".source-line")).to_have_count(3)

    button.click()
    expect(button).to_have_attribute("aria-expanded", "false")
    expect(detail).to_be_hidden()

    assert blocked == []
    page.close()


def test_all_96_routes(browser):
    page, blocked = _open_page(browser, "#/community/426")

    console_errors: list[str] = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    for community_id in _community_ids():
        page.evaluate("(id) => { location.hash = `#/community/${id}`; }", community_id)
        expect(page.locator(".service-row").first).to_be_attached()
        expect(page.locator(".service-row")).not_to_have_count(0)

    assert console_errors == []
    assert blocked == []
    page.close()


def test_no_literals():
    pattern = re.compile(r"#[0-9a-fA-F]{3}|[0-9]px")
    for relative_path in ("app/app.css", "app/app.js"):
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        matches = pattern.findall(text)
        assert matches == [], f"literal colour/size found in {relative_path}: {matches}"
