"""Mobile UI contract for Task-53."""

from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST_INDEX = (ROOT / "dist" / "index.html").resolve().as_uri()
PHONE = {"width": 360, "height": 780}


def _open_page(browser, hash_route: str):
    page = browser.new_page(viewport=PHONE)
    blocked: list[str] = []
    errors: list[str] = []

    def handler(route):
        if route.request.url.startswith("file:"):
            route.continue_()
        else:
            blocked.append(route.request.url)
            route.abort()

    page.route("**/*", handler)
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"{DIST_INDEX}{hash_route}")
    page.wait_for_load_state()
    return page, blocked, errors


def test_service_cards_are_two_columns_and_expand_across_grid(browser):
    page, blocked, errors = _open_page(browser, "#/community/426")

    cards = page.locator(".service-card")
    expect(cards).to_have_count(4)
    expect(cards.locator("svg.service-icon[aria-hidden=true]")).to_have_count(4)
    assert cards.evaluate_all("els => new Set(els.map(el => el.offsetTop)).size") == 2

    first = cards.first
    first.locator("button.service-row").click()
    expect(first).to_have_class("service-card service-card--expanded")
    expect(first.locator(".service-row__detail")).to_be_visible()
    assert first.evaluate("el => getComputedStyle(el).gridColumnEnd") == "-1"

    assert blocked == []
    assert errors == []
    page.close()


def test_service_selector_overlays_equal_height_map(browser):
    service_page, blocked, errors = _open_page(browser, "#/map?lens=service")
    service_frame = service_page.locator(".map-frame")
    selector = service_frame.locator("select.map-service")
    expect(selector).to_have_count(1)
    assert selector.evaluate("el => getComputedStyle(el).position") == "absolute"
    service_height = service_frame.bounding_box()["height"]

    fix_page, fix_blocked, fix_errors = _open_page(browser, "#/map?lens=fix")
    fix_height = fix_page.locator(".map-frame").bounding_box()["height"]
    assert abs(service_height - fix_height) < 1
    expect(service_page.locator("g.map__community")).to_have_count(96)

    assert blocked == []
    assert fix_blocked == []
    assert errors == []
    assert fix_errors == []
    service_page.close()
    fix_page.close()


def test_navigation_semantics_and_content_clearance(browser):
    page, blocked, errors = _open_page(browser, "#/share")

    navigation = page.locator("nav[aria-label='Main navigation']")
    expect(navigation.locator("[role=tab]")).to_have_count(0)
    expect(page.locator("nav.map-lens[role=tablist]")).to_have_count(0)
    expect(navigation.locator("[aria-current=page]")).to_have_text("Share")
    nav_top = navigation.bounding_box()["y"]
    content_bottom = page.locator(".content").evaluate(
        "el => parseFloat(getComputedStyle(el).paddingBottom)"
    )
    assert content_bottom >= PHONE["height"] - nav_top

    assert blocked == []
    assert errors == []
    page.close()
