"""Browser contracts for Task-54's map and report interaction pass."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST_INDEX = (ROOT / "dist" / "index.html").resolve().as_uri()
PACK = json.loads((ROOT / "data" / "out" / "data_pack.json").read_text(encoding="utf-8"))
PHONE = {"width": 360, "height": 780}
WADEYE = 426


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


def _row_state(page):
    return page.locator("ol.map-list > li").evaluate_all(
        """rows => rows.map(row => ({
            selected: new URLSearchParams(
                row.querySelector('a').getAttribute('href').split('?')[1] || ''
            ).get('selected'),
            dim: row.classList.contains('map-list__item--dim'),
        }))"""
    )


def test_brand_and_segmented_map_control(browser):
    page, blocked, errors = _open_page(browser, "#/map?lens=service")

    title = page.locator("a.top-bar__title")
    expect(title).to_contain_text("Crosscheck")
    expect(title.locator("svg.brand-mark[aria-hidden=true]")).to_have_count(1)

    lens = page.locator("nav.map-lens")
    options = lens.locator(".map-lens__option")
    expect(options).to_have_count(3)
    expect(lens.locator(".map-lens__option[aria-current=page]")).to_have_count(1)
    assert all(box["height"] >= 44 for box in [item.bounding_box() for item in options.all()])
    assert lens.evaluate("el => getComputedStyle(el).borderTopStyle") == "solid"

    assert blocked == []
    assert errors == []
    page.close()


def test_map_card_zoom_and_compact_service_selector(browser):
    page, blocked, errors = _open_page(browser, "#/map?lens=service")

    frame = page.locator(".map-frame")
    assert frame.evaluate("el => getComputedStyle(el).overflow") == "hidden"
    assert frame.evaluate("el => getComputedStyle(el).borderTopStyle") == "solid"

    selector_width = frame.locator("select.map-service").bounding_box()["width"]
    assert selector_width < frame.bounding_box()["width"]

    map_svg = frame.locator("svg.map")
    base_view = map_svg.get_attribute("viewBox")
    page.get_by_role("button", name="Zoom in").click()
    assert map_svg.get_attribute("viewBox") != base_view
    page.get_by_role("button", name="Zoom out").click()
    page.get_by_role("button", name="Zoom in").click()
    page.get_by_role("button", name="Reset view").click()
    expect(map_svg).to_have_attribute("viewBox", base_view)

    assert blocked == []
    assert errors == []
    page.close()


def test_highlight_count_and_layers_have_separate_effects(browser):
    filter_row = next(one for one in PACK["filters"] if one["id"] == "clinic-no-terrestrial")
    page, blocked, errors = _open_page(browser, "#/map?filter=clinic-no-terrestrial")

    more = page.locator("details.map-more")
    assert more.evaluate("el => el.open") is True
    expect(more.locator(".map-more__group-title")).to_have_text(
        ["Highlight communities", "Map layers"]
    )
    expect(page.locator(".map-list-heading__count")).to_have_text(
        f"{len(filter_row['ids'])} highlighted of {PACK['count']}"
    )
    before = _row_state(page)

    page.locator(".layer-chip").first.click()
    page.wait_for_load_state()
    expect(page.locator(".map-list-heading__count")).to_have_text(
        f"{len(filter_row['ids'])} highlighted of {PACK['count']}"
    )
    assert _row_state(page) == before

    page.locator("details.map-more > summary").click()
    assert more.evaluate("el => el.open") is False
    page.locator("details.map-more > summary").click()
    assert more.evaluate("el => el.open") is True

    assert blocked == []
    assert errors == []
    page.close()


def test_report_here_toggles_and_reports_have_one_named_group(browser):
    page, blocked, errors = _open_page(browser, f"#/community/{WADEYE}")

    button = page.locator(".report-button")
    expect(button).to_have_text("Report here")
    expect(button).to_have_attribute("aria-expanded", "false")
    button.click()
    expect(page.locator(".report-form")).to_have_count(1)
    button = page.locator(".report-button")
    expect(button).to_have_text("Close report")
    expect(button).to_have_attribute("aria-expanded", "true")
    button.click()
    expect(page.locator(".report-form")).to_have_count(0)
    expect(page.locator(".report-button")).to_have_text("Report here")

    reports = page.locator("section.community-reports")
    expect(reports).to_have_count(1)
    expect(reports.locator(".community-reports__title")).to_have_text("Community reports")
    expect(reports.locator(".reports-line")).to_contain_text("Saved on this phone")
    expect(reports.locator(".reports-fold > summary")).to_have_text(
        "Import report lines from another phone"
    )

    assert blocked == []
    assert errors == []
    page.close()
