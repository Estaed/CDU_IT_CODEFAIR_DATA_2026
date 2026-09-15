"""Browser tests for the map screen (Task-08): points per filter, selection ring and label,
selected panel, tap-to-select, open-community link, legend counts, offline and error-free."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST_INDEX = (ROOT / "dist" / "index.html").resolve().as_uri()
PACK = ROOT / "data" / "out" / "data_pack.json"

FILTER_COUNTS = {
    "all": 96,
    "clinic-no-terrestrial": 12,
    "carrier-yes-list-no": 14,
    "licensed-no-map": 11,
}


def _open_page(browser, hash_route: str):
    page = browser.new_page()
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


def _legend_counts(page) -> list[str]:
    return [text.strip() for text in page.locator(".map-legend__count").all_text_contents()]


def test_all_filter_renders_96(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    expect(page.locator(".map__community")).to_have_count(96)
    expect(page.locator(".map__land path")).to_have_count(1)
    expect(page.locator(".filter-tabs .tab")).to_have_count(4)
    expect(page.locator(".filter-tabs .tab[aria-selected=true]")).to_have_text(re.compile("^All"))
    expect(page.locator(".map__ring")).to_have_count(0)

    assert errors == []
    assert blocked == []
    page.close()


def test_filter_routes(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    for filter_id, count in FILTER_COUNTS.items():
        page.evaluate("(id) => { location.hash = `#/map?filter=${id}`; }", filter_id)
        expect(page.locator(".map__community")).to_have_count(count)
        active = page.locator(".filter-tabs .tab[aria-selected=true]")
        expect(active).to_have_count(1)
        expect(active.locator(".tab__count")).to_have_text(str(count))
        assert _legend_counts(page) == ["1", "58", "11", "26"]
        subject = " ".join(page.locator(".map-legend__subject").last.inner_text().split())
        assert subject == f"Showing {count} of 96"

    assert errors == []
    assert blocked == []
    page.close()


def test_licensed_no_map_verdicts(browser):
    page, blocked, errors = _open_page(browser, "#/map?filter=licensed-no-map")

    expect(page.locator(".map__community")).to_have_count(11)
    expect(page.locator(".map__community .map__pt--fails")).to_have_count(6)
    expect(page.locator(".map__community .map__pt--nodata")).to_have_count(5)

    assert errors == []
    assert blocked == []
    page.close()


def test_filter_tab_click_changes_route(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    page.locator(".filter-tabs .tab").filter(has_text="Licensed mast").click()
    expect(page).to_have_url(re.compile(r"#/map\?filter=licensed-no-map$"))
    expect(page.locator(".map__community")).to_have_count(11)

    assert errors == []
    assert blocked == []
    page.close()


def test_selected_baniyala(browser):
    page, blocked, errors = _open_page(browser, "#/map?selected=458")

    expect(page.locator(".map__ring")).to_have_count(1)
    expect(page.locator(".map__label")).to_have_text("Baniyala")
    expect(page.locator(".community-header__name")).to_have_text("Baniyala")

    headline = page.locator(".agreement__headline .fig")
    expect(headline).to_have_count(2)
    # 1 of 3, not the mock's 1 of 4: PRD decision 2026-09-13 (not-recorded is not a source)
    assert headline.all_text_contents() == ["1", "3"]
    expect(page.locator(".service-row .verdict-badge--fails")).to_have_count(1)
    assert _legend_counts(page) == ["1", "58", "11", "26"]

    page.locator(".text-link").click()
    expect(page).to_have_url(re.compile(r"#/community/458$"))
    expect(page.locator("h1.community-header__name")).to_have_text("Baniyala")

    assert errors == []
    assert blocked == []
    page.close()


def _isolated_community() -> dict:
    """The community farthest from its nearest neighbour; its hit circle (r 16) must overlap no
    other point's, so a real click lands on it and not on a neighbour drawn above it."""
    communities = json.loads(PACK.read_text(encoding="utf-8"))["communities"]

    def nearest(community: dict) -> float:
        return min(
            math.hypot(community["x"] - other["x"], community["y"] - other["y"])
            for other in communities
            if other is not community
        )

    best = max(communities, key=nearest)
    assert nearest(best) > 32, "no community with a non-overlapping hit circle"
    return best


def test_click_point_selects_it(browser):
    community = _isolated_community()
    page, blocked, errors = _open_page(browser, "#/map")

    group = page.locator(".map__community").filter(has_text=community["name"])
    expect(group).to_have_count(1)
    group.click()
    expect(page).to_have_url(re.compile(rf"#/map\?filter=all&selected={community['id']}$"))
    expect(page.locator(".map__ring")).to_have_count(1)
    expect(page.locator(".map__label")).to_have_text(community["name"])

    assert errors == []
    assert blocked == []
    page.close()


# --- Task-21: map layers, carrier toggles, zoom/pan, community labels ------------------------

PACK_LAYERS = json.loads(PACK.read_text(encoding="utf-8"))["layers"]
AREA_LAYER_IDS = [layer["id"] for layer in PACK_LAYERS if layer["kind"] == "area"]


def test_one_layer_group_per_pack_layer(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    for layer in PACK_LAYERS:
        expect(page.locator(f'g[data-layer="{layer["id"]}"]')).to_have_count(1)
    # The Task-08 filter behaviour and counts are unaffected by the new layer groups.
    expect(page.locator(".map__community")).to_have_count(96)

    assert errors == []
    assert blocked == []
    page.close()


def test_area_chip_toggles_hidden_on_its_group(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    layer_id = AREA_LAYER_IDS[0]
    label = next(layer["label"] for layer in PACK_LAYERS if layer["id"] == layer_id)
    group = page.locator(f'g[data-layer="{layer_id}"]')
    chip = page.locator(".layer-chip").filter(has_text=label)
    expect(chip).to_have_count(1)

    expect(group).not_to_have_attribute("hidden", "")
    chip.click()
    expect(group).to_have_attribute("hidden", "")
    chip.click()
    expect(group).not_to_have_attribute("hidden", "")

    assert errors == []
    assert blocked == []
    page.close()


def test_layers_query_shows_only_the_named_layer(browser):
    page, blocked, errors = _open_page(browser, "#/map?layers=telstra")

    expect(page.locator('g[data-layer="cov-telstra"]')).not_to_have_attribute("hidden", "")
    expect(page.locator('g[data-layer="cov-optus"]')).to_have_attribute("hidden", "")
    expect(page.locator('g[data-layer="cov-tpg"]')).to_have_attribute("hidden", "")

    assert errors == []
    assert blocked == []
    page.close()


def test_five_towns_with_names(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    towns_layer = next(layer for layer in PACK_LAYERS if layer["kind"] == "point")
    expected = {point["label"] for point in towns_layer["paths"]}
    markers = page.locator(".map__town")
    expect(markers).to_have_count(5)
    assert set(markers.all_text_contents()) == expected == {
        "Darwin",
        "Katherine",
        "Tennant Creek",
        "Alice Springs",
        "Nhulunbuy",
    }

    assert errors == []
    assert blocked == []
    page.close()


def _wheel_zoom_in(page, ticks: int = 10):
    box = page.locator(".map").bounding_box()
    cx = box["x"] + box["width"] / 2
    cy = box["y"] + box["height"] / 2
    for _ in range(ticks):
        page.locator(".map").dispatch_event(
            "wheel",
            {"deltaY": -100, "clientX": cx, "clientY": cy, "bubbles": True, "cancelable": True},
        )


def test_wheel_zooms_in_and_sets_data_zoom(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    svg = page.locator(".map")
    _wheel_zoom_in(page, ticks=3)
    view_box = svg.get_attribute("viewBox")
    width = float(view_box.split(" ")[2])
    assert width < 300
    assert int(svg.get_attribute("data-zoom")) > 1

    assert errors == []
    assert blocked == []
    page.close()


def test_zoomed_in_labels_become_visible(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    svg = page.locator(".map")
    _wheel_zoom_in(page, ticks=12)
    assert int(svg.get_attribute("data-zoom")) >= 3
    labels = page.locator(".map__zoom-labels .map__label")
    expect(labels.first).to_be_visible()
    display = labels.first.evaluate("el => getComputedStyle(el).display")
    assert display != "none"

    assert errors == []
    assert blocked == []
    page.close()


def test_reset_view_restores_default_viewbox(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    svg = page.locator(".map")
    _wheel_zoom_in(page, ticks=6)
    assert svg.get_attribute("viewBox") != "0 0 300 480"

    page.get_by_text("Reset view").click()
    expect(svg).to_have_attribute("viewBox", "0 0 300 480")
    expect(svg).to_have_attribute("data-zoom", "1")

    assert errors == []
    assert blocked == []
    page.close()


def test_version_1_pack_is_refused(browser, tmp_path):
    built = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")
    assert '"pack_version":2' in built
    downgraded = built.replace('"pack_version":2', '"pack_version":1', 1)
    copy_path = tmp_path / "version1.html"
    copy_path.write_text(downgraded, encoding="utf-8")

    page = browser.new_page()
    page.goto(copy_path.resolve().as_uri())
    page.wait_for_load_state()
    expect(page.locator("main")).to_have_text("Unknown data pack")
    page.close()
