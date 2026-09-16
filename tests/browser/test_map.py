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

    expect(page.locator(".map__pt-group")).to_have_count(96)
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

    expect(page.locator(".map__pt-group")).to_have_count(11)
    expect(page.locator(".map__pt-group .map__pt--fails")).to_have_count(6)
    expect(page.locator(".map__pt-group .map__pt--nodata")).to_have_count(5)
    # Task-33: both are circles now, coloured by stroke, not a triangle/square pair.
    for verdict in ("fails", "nodata"):
        tag = page.locator(f".map__pt--{verdict}").first.evaluate("el => el.tagName")
        assert tag == "circle"

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


def _open_layers_fold(page):
    """Task-33: the layer chips now live behind details.map-layers, closed by default; a chip
    is not actionable (native `display: none` on the fold's content) until it is opened."""
    page.locator(".map-layers summary").click()


def test_area_chip_toggles_hidden_on_its_group(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    _open_layers_fold(page)

    layer_id = AREA_LAYER_IDS[0]
    label = next(layer["label"] for layer in PACK_LAYERS if layer["id"] == layer_id)
    group = page.locator(f'g[data-layer="{layer_id}"]')
    chip = page.locator(".layer-chip").filter(has_text=label)
    expect(chip).to_have_count(1)

    # Task-33: layers off by default (contract item 4), reversed from Task-21's all-on default.
    expect(group).to_have_attribute("hidden", "")
    chip.click()
    expect(group).not_to_have_attribute("hidden", "")
    chip.click()
    expect(group).to_have_attribute("hidden", "")

    assert errors == []
    assert blocked == []
    page.close()


def test_area_layers_start_hidden(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    # `to_be_hidden()`, not just `to_have_attribute("hidden", "")`: the attribute alone does not
    # prove the layer is off-screen -- the HTML `[hidden]{display:none}` UA rule does not reach
    # an SVG `<g>` in this engine, so a build without `.map__layer[hidden]{display:none}` in
    # app.css passed the attribute check while the coverage blobs and the SA3 borders were still
    # painted on first load (the defect this test exists to catch).
    for layer_id in AREA_LAYER_IDS:
        expect(page.locator(f'g[data-layer="{layer_id}"]')).to_be_hidden()
    expect(page.locator('g[data-layer="regions-sa3"]')).to_be_hidden()
    # Towns are never toggled: no chip, always visible.
    expect(page.locator('g[data-layer="towns"]')).to_be_visible()
    expect(page.locator(".map__town")).to_have_count(5)

    assert errors == []
    assert blocked == []
    page.close()


def test_region_chip_shows_the_sa3_layer(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    _open_layers_fold(page)

    label = next(layer["label"] for layer in PACK_LAYERS if layer["id"] == "regions-sa3")
    chip = page.locator(".layer-chip").filter(has_text=label)
    expect(chip).to_have_count(1)
    group = page.locator('g[data-layer="regions-sa3"]')

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


# --- Task-29: map points cluster by zoom -----------------------------------------------------

VERDICT_NAMES = ("works", "degraded", "fails", "nodata")


def _cluster_data(locator) -> list[dict]:
    return locator.evaluate_all(
        """els => els.map(el => ({
            id: el.getAttribute('data-id'),
            count: Number(el.getAttribute('data-count')),
            aria: el.getAttribute('aria-label'),
            text: el.querySelector('.map__cluster-count').textContent,
            verdictTotal: ['works', 'degraded', 'fails', 'nodata']
                .reduce((sum, v) => sum + Number(el.getAttribute(`data-${v}`) || 0), 0),
        }))"""
    )


def test_clusters_at_zoom1_sum_to_96(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    clusters = page.locator(".map__cluster")
    expect(clusters.first).to_be_visible()
    data = _cluster_data(clusters)
    assert len(data) >= 1

    for entry in data:
        assert entry["aria"] == f"{entry['count']} communities"
        assert entry["text"] == str(entry["count"])
        assert entry["verdictTotal"] == entry["count"]

    total_clustered = sum(entry["count"] for entry in data)
    visible_points = page.locator(".map__community:not([hidden])").count()
    assert total_clustered + visible_points == 96

    assert errors == []
    assert blocked == []
    page.close()


def test_zoom_8_shows_no_clusters(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    _wheel_zoom_in(page, ticks=20)
    expect(page.locator(".map")).to_have_attribute("data-zoom", "8")
    expect(page.locator(".map__cluster")).to_have_count(0)
    expect(page.locator(".map__community:not([hidden])")).to_have_count(96)

    assert errors == []
    assert blocked == []
    page.close()


def test_click_first_cluster_zooms_in_and_splits_it(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    svg = page.locator(".map")
    first_cluster = page.locator(".map__cluster").first
    expect(first_cluster).to_be_visible()
    original_id = first_cluster.get_attribute("data-id")

    # dispatch_event, not .click(): neighbouring cluster hit circles can overlap on screen at
    # zoom 1 (the same reason test_click_point_selects_it above needs an isolated community), so
    # a real pointer click can land on the wrong cluster; dispatching targets this element only.
    first_cluster.dispatch_event("click")
    expect(svg).not_to_have_attribute("data-zoom", "1")

    def remaining_ids() -> list[str]:
        return page.locator(".map__cluster").evaluate_all(
            "els => els.map(el => el.getAttribute('data-id'))"
        )

    # expect() alone only retries truthy/equality checks; poll directly since the assertion is
    # "this id is absent from a list", which Playwright's Python API has no built-in matcher for.
    for _ in range(50):
        if original_id not in remaining_ids():
            break
        page.wait_for_timeout(100)
    assert original_id not in remaining_ids()

    assert errors == []
    assert blocked == []
    page.close()


def test_clinic_filter_clusters_and_points_sum_to_filter_count(browser):
    page, blocked, errors = _open_page(browser, "#/map?filter=clinic-no-terrestrial")

    clusters = page.locator(".map__cluster")
    expect(page.locator(".map__community")).to_have_count(FILTER_COUNTS["clinic-no-terrestrial"])
    data = _cluster_data(clusters)
    total_clustered = sum(entry["count"] for entry in data)
    visible_points = page.locator(".map__community:not([hidden])").count()
    assert total_clustered + visible_points == FILTER_COUNTS["clinic-no-terrestrial"]

    assert errors == []
    assert blocked == []
    page.close()


def test_selected_community_at_zoom1_is_visible_and_unclustered(browser):
    page, blocked, errors = _open_page(browser, "#/map?selected=458")

    point = page.locator(".map__community").filter(has_text="Baniyala")
    expect(point).not_to_have_attribute("hidden", "")
    member_lists = page.locator(".map__cluster").evaluate_all(
        "els => els.map(el => (el.getAttribute('data-id') || '').split('-'))"
    )
    assert all("458" not in members for members in member_lists)

    assert errors == []
    assert blocked == []
    page.close()


def test_cluster_function_is_pure_and_deterministic(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    result = page.evaluate(
        """() => {
            const pack = JSON.parse(document.getElementById('pack').textContent);
            const points = pack.communities.map((c) => ({
                id: c.id,
                x: c.x,
                y: c.y,
                verdict: c.services.find((s) => s.service === 'telehealth_video').verdict,
            }));
            const a = window.__map.cluster(points, 1);
            const b = window.__map.cluster(points, 1);
            return { a, b };
        }"""
    )
    assert result["a"]["clusters"] == result["b"]["clusters"]
    assert result["a"]["singles"] == result["b"]["singles"]
    assert len(result["a"]["clusters"]) >= 1
    total = sum(c["count"] for c in result["a"]["clusters"]) + len(result["a"]["singles"])
    assert total == 96

    assert errors == []
    assert blocked == []
    page.close()


# --- Task-33: map, third pass ------------------------------------------------------------------


def _service_counts(service_id: str) -> dict[str, int]:
    communities = json.loads(PACK.read_text(encoding="utf-8"))["communities"]
    counts = {"works": 0, "degraded": 0, "fails": 0, "nodata": 0}
    for community in communities:
        verdict = next(s["verdict"] for s in community["services"] if s["service"] == service_id)
        counts[verdict] += 1
    return counts


def test_service_selector_recolours_and_recounts(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    select = page.locator("select.map-service")
    expect(select).to_have_value("telehealth_video")

    select.select_option("voice_sms")
    expect(page).to_have_url(re.compile(r"#/map\?filter=all&service=voice_sms$"))

    expected = _service_counts("voice_sms")
    assert _legend_counts(page) == [
        str(expected["works"]),
        str(expected["degraded"]),
        str(expected["fails"]),
        str(expected["nodata"]),
    ]
    for verdict in VERDICT_NAMES:
        expect(page.locator(f".map__pt--{verdict}")).to_have_count(expected[verdict])

    assert errors == []
    assert blocked == []
    page.close()


MAP_LIST_WORDS = ("Fails", "Degraded", "No data", "Works")


def test_map_list_sorted_worst_first(browser):
    page, blocked, errors = _open_page(browser, "#/map?filter=clinic-no-terrestrial")

    rows = page.locator(".map-list__row")
    expect(rows).to_have_count(FILTER_COUNTS["clinic-no-terrestrial"])

    def rank(text: str) -> int:
        stripped = text.strip()
        return next(i for i, word in enumerate(MAP_LIST_WORDS) if stripped.endswith(word))

    ranks = [rank(text) for text in rows.all_text_contents()]
    assert ranks == sorted(ranks)

    rows.first.click()
    expect(page).to_have_url(re.compile(r"#/community/\d+$"))

    assert errors == []
    assert blocked == []
    page.close()


def test_no_polygon_points(browser):
    page, blocked, errors = _open_page(browser, "#/map")

    expect(page.locator(".map polygon")).to_have_count(0)
    expect(page.locator(".map__pt-group rect")).to_have_count(0)

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
