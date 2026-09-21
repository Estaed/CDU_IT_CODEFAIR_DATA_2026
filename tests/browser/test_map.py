"""Browser tests for the map v3 contract (Task-48 and Task-49)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST_INDEX = (ROOT / "dist" / "index.html").resolve().as_uri()
PHONE = {"width": 360, "height": 780}
VERDICT_NAMES = ("works", "degraded", "fails", "nodata")
MAP_LIST_WORDS = ("Fails", "Degraded", "No data", "Works")


def _open_page(browser, hash_route: str, viewport: dict | None = None):
    page = browser.new_page()
    if viewport:
        page.set_viewport_size(viewport)
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


def _pack(page) -> dict:
    return page.evaluate("() => JSON.parse(document.getElementById('pack').textContent)")


def _params(page) -> dict[str, str]:
    return page.evaluate(
        """() => Object.fromEntries(
            new URLSearchParams(location.hash.split('?')[1] || '')
        )"""
    )


def _legend_counts(page) -> list[str]:
    return [
        re.search(r"\d+", text).group()
        for text in page.locator(".map-legend__count").all_text_contents()
    ]


def _filter_ids(pack: dict, filter_id: str) -> set[str]:
    entry = next(one for one in pack["filters"] if one["id"] == filter_id)
    return {str(community_id) for community_id in entry["ids"]}


def _source_bucket(community: dict) -> str:
    measured = next(
        (line for line in community["publishers"] if line["kind"] == "measured"),
        None,
    )
    if measured and measured["says_covered"] == "not-covered":
        return "measured"
    if community["agreement"]["note"] == "Sources disagree":
        return "disagree"
    return "agree"


def _region_slug(label: str) -> str:
    return label.lower().replace(" ", "-")


def _open_layers_fold(page):
    details = page.locator("details.map-more")
    if not details.evaluate("el => el.open"):
        details.locator("summary").click()


def test_default_map_contract(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    pack = _pack(page)

    expect(page.locator(".map-lens__option[aria-selected=true]")).to_have_text("Fix first")
    expect(page.locator("svg.map[data-lens=fix]")).to_have_attribute("viewBox", "0 0 300 480")
    expect(page.locator("g.map__community")).to_have_count(96)
    expect(page.locator(".map__cluster")).to_have_count(0)
    expect(page.locator("select")).to_have_count(0)

    ranks = {str(row["id"]): row["rank"] for row in pack["priority"]}
    expected_tiers = {
        "1": sum(rank <= 10 for rank in ranks.values()),
        "2": sum(11 <= rank <= 30 for rank in ranks.values()),
        "3": sum(rank > 30 for rank in ranks.values()),
    }
    for tier, count in expected_tiers.items():
        expect(page.locator(f'g.map__community[data-tier="{tier}"]')).to_have_count(count)

    rank_labels = [int(text.strip()) for text in page.locator("text.map__rank").all_text_contents()]
    assert rank_labels == list(range(1, 11))
    legend = page.locator(".map-legend__item")
    expect(legend).to_have_count(3)
    for label, count in (("Top 10", 10), ("11 to 30", 20), ("The rest", 66)):
        item = legend.filter(has_text=label)
        expect(item).to_have_count(1)
        assert str(count) in item.inner_text()

    assert errors == []
    assert blocked == []
    page.close()


def test_filters_keep_all_points_and_dim_excluded_points(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    pack = _pack(page)

    for filter_id in ("all", "clinic-no-terrestrial", "carrier-yes-list-no", "licensed-no-map"):
        page.evaluate("id => { location.hash = `#/map?filter=${id}`; }", filter_id)
        page.wait_for_timeout(50)
        expected_ids = _filter_ids(pack, filter_id)
        expect(page.locator("g.map__community")).to_have_count(96)
        expect(page.locator("g.map__community.map__community--dim")).to_have_count(
            96 - len(expected_ids)
        )
        active = page.locator(".filter-tabs .tab[aria-selected=true]")
        expect(active).to_have_count(1)
        expect(active.locator(".tab__count")).to_have_text(str(len(expected_ids)))

    assert errors == []
    assert blocked == []
    page.close()


def test_lenses_sources_and_service_match_pack(browser):
    page, blocked, errors = _open_page(browser, "#/map?lens=sources")
    pack = _pack(page)
    communities = {str(one["id"]): one for one in pack["communities"]}

    actual_sources = page.locator("g.map__community").evaluate_all(
        """els => Object.fromEntries(
            els.map(el => [el.getAttribute('data-id'), el.getAttribute('data-sources')])
        )"""
    )
    expected_sources = {
        community_id: _source_bucket(one) for community_id, one in communities.items()
    }
    assert actual_sources == expected_sources
    source_counts = {
        bucket: sum(value == bucket for value in expected_sources.values())
        for bucket in ("measured", "disagree", "agree")
    }
    expect(page.locator(".map-lens__option[aria-selected=true]")).to_have_text("Sources")
    for label, bucket in (
        ("Drive test found no signal", "measured"),
        ("Sources disagree", "disagree"),
        ("Sources agree", "agree"),
    ):
        item = page.locator(".map-legend__item").filter(has_text=label)
        expect(item).to_have_count(1)
        assert str(source_counts[bucket]) in item.inner_text()

    page.evaluate("""() => { location.hash = '#/map?lens=service'; }""")
    page.wait_for_timeout(50)
    expect(page.locator("select")).to_have_count(1)
    service_id = page.locator("select").input_value()
    expected_verdicts = {
        verdict: sum(
            next(
                service for service in one["services"] if service["service"] == service_id
            )["verdict"]
            == verdict
            for one in pack["communities"]
        )
        for verdict in VERDICT_NAMES
    }
    for verdict, count in expected_verdicts.items():
        expect(page.locator(f".map__pt--{verdict}")).to_have_count(count)

    assert errors == []
    assert blocked == []
    page.close()


def test_lens_control_keeps_selected_and_filter(browser):
    page, blocked, errors = _open_page(browser, "#/map?filter=clinic-no-terrestrial&selected=426")

    page.get_by_role("tab", name="Sources", exact=True).click()
    params = _params(page)
    assert params == {"lens": "sources", "filter": "clinic-no-terrestrial", "selected": "426"}

    assert errors == []
    assert blocked == []
    page.close()


def test_filter_tab_click_changes_route(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    _open_layers_fold(page)
    pack = _pack(page)

    page.locator(".filter-tabs .tab").filter(has_text="Licensed mast").click()
    expect(page.locator("g.map__community")).to_have_count(96)
    assert _params(page)["filter"] == "licensed-no-map"
    expect(page.locator("g.map__community.map__community--dim")).to_have_count(
        96 - len(_filter_ids(pack, "licensed-no-map"))
    )

    assert errors == []
    assert blocked == []
    page.close()


def test_selected_baniyala(browser):
    page, blocked, errors = _open_page(browser, "#/map?selected=458")

    expect(page.locator('g.map__community[data-id="458"].map__community--selected')).to_have_count(1)
    expect(page.locator(".map-card__name")).to_have_text("Baniyala")
    expect(page.get_by_role("link", name="Open Baniyala", exact=True)).to_have_count(1)

    assert errors == []
    assert blocked == []
    page.close()


def test_click_point_selects_it_and_keeps_lens(browser):
    page, blocked, errors = _open_page(browser, "#/map?lens=sources")
    community = page.evaluate(
        """() => {
            const pack = JSON.parse(document.getElementById('pack').textContent);
            const distance = (one, other) => Math.hypot(one.x - other.x, one.y - other.y);
            return pack.communities.reduce((best, one) => {
                const nearest = Math.min(...pack.communities
                    .filter(other => other.id !== one.id)
                    .map(other => distance(one, other)));
                if (!best || nearest > best.nearest) return {id: one.id, nearest};
                return best;
            }, null);
        }"""
    )
    page.locator(f'g.map__community[data-id="{community["id"]}"]').dispatch_event("click")
    params = _params(page)
    assert params["lens"] == "sources"
    assert params["selected"] == str(community["id"])
    expect(page.locator(".map-card__name")).to_be_visible()

    assert errors == []
    assert blocked == []
    page.close()


def test_regions_order_zoom_dimming_and_reset(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    pack = _pack(page)
    region_labels = []
    for community in pack["communities"]:
        if community["region"] not in region_labels:
            region_labels.append(community["region"])
    chips = page.locator(".map-regions a.chip")
    expect(chips).to_have_count(6)
    assert chips.all_text_contents() == ["All NT", *region_labels]

    rest_view_box = page.locator("svg.map").get_attribute("viewBox")
    selected_region = region_labels[0]
    slug = _region_slug(selected_region)
    chips.nth(1).click()
    page.wait_for_timeout(500)
    expect(page.locator("svg.map")).to_have_attribute("data-region", slug)
    assert page.locator("svg.map").get_attribute("viewBox") != rest_view_box
    expected_dimmed = {
        str(community["id"])
        for community in pack["communities"]
        if community["region"] != selected_region
    }
    actual_dimmed = set(
        page.locator("g.map__community.map__community--dim").evaluate_all(
            "els => els.map(el => el.getAttribute('data-id'))"
        )
    )
    assert actual_dimmed == expected_dimmed

    page.get_by_role("button", name="Reset view", exact=True).click()
    expect(page.locator("svg.map")).not_to_have_attribute("data-region", "")
    assert "region" not in _params(page)

    assert errors == []
    assert blocked == []
    page.close()


def test_map_legend_fits_phone_viewport(browser):
    page, blocked, errors = _open_page(browser, "#/map", viewport=PHONE)

    box = page.locator("div.map-legend").bounding_box()
    assert box is not None
    assert box["y"] + box["height"] <= PHONE["height"]
    assert page.evaluate("window.scrollY") == 0

    assert errors == []
    assert blocked == []
    page.close()


def test_visible_labels_follow_markers_without_tier_one_collisions(browser):
    page, blocked, errors = _open_page(browser, "#/map", viewport=PHONE)

    def violations() -> dict:
        return page.evaluate(
            """() => {
                const visible = element => {
                    const box = element.getBoundingClientRect();
                    const style = getComputedStyle(element);
                    return style.display !== 'none' && style.visibility !== 'hidden'
                        && box.width > 0 && box.height > 0;
                };
                const box = element => {
                    const value = element.getBoundingClientRect();
                    return {left: value.left, top: value.top, right: value.right,
                        bottom: value.bottom, width: value.width, height: value.height};
                };
                const centre = value => ({
                    x: (value.left + value.right) / 2,
                    y: (value.top + value.bottom) / 2,
                });
                const overlaps = (one, other) => one.left < other.right
                    && one.right > other.left && one.top < other.bottom
                    && one.bottom > other.top;
                const markerBox = group => {
                    const disc = group.querySelector('circle, .map__pt, .map__marker');
                    return box(disc || group);
                };
                const groups = [...document.querySelectorAll('g.map__community[data-id]')];
                const towns = [...document.querySelectorAll('.map__town[data-for]')];
                const markerFor = id => groups.find(group => group.dataset.id === id)
                    || towns.find(town => town.dataset.for === id);
                const labels = [...document.querySelectorAll('.map__label[data-for]')]
                    .filter(visible);
                const tierOne = groups.filter(group => group.dataset.tier === '1');
                const alignment = [];
                const collisions = [];
                for (const label of labels) {
                    const id = label.dataset.for;
                    const marker = markerFor(id);
                    if (!marker) continue;
                    const labelBox = box(label);
                    const markerBoxValue = markerBox(marker);
                    const labelCentre = centre(labelBox);
                    const markerCentre = centre(markerBoxValue);
                    const distance = Math.hypot(
                        labelCentre.x - markerCentre.x,
                        labelCentre.y - markerCentre.y,
                    );
                    if (distance > 40 + labelBox.width / 2) {
                        alignment.push({label: id, marker: marker.dataset.id || id, distance});
                    }
                    for (const other of tierOne) {
                        if (other === marker) continue;
                        const disc = markerBox(other);
                        if (overlaps(labelBox, disc)) {
                            collisions.push({
                                label: id,
                                marker: other.dataset.id,
                            });
                        }
                    }
                }
                return {alignment, collisions};
            }"""
        )

    assert violations() == {"alignment": [], "collisions": []}

    page.goto(f"{DIST_INDEX}#/map?region=top-end")
    page.wait_for_load_state()
    page.wait_for_timeout(500)
    assert violations() == {"alignment": [], "collisions": []}

    page.goto(f"{DIST_INDEX}#/map?selected=426")
    page.wait_for_load_state()
    wadeye = page.locator('.map__label[data-for="426"]')
    assert wadeye.count() == 1
    expect(wadeye).to_be_visible()

    assert errors == []
    assert blocked == []
    page.close()


def test_selection_card_and_open_link(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    expect(page.locator("p.map-card__hint")).to_have_text("Tap a community.")

    page.goto(f"{DIST_INDEX}#/map?selected=426")
    page.wait_for_load_state()
    pack = _pack(page)
    priority = next(one for one in pack["priority"] if str(one["id"]) == "426")
    intervention = pack["priority_interventions"][priority["i"]]["word"]
    expect(page.locator(".map-card__name")).to_have_text("Wadeye")
    expect(page.locator(".community-summary")).to_have_text(
        "All 4 sources say Wadeye has mobile coverage. A video call with a doctor is not proven "
        "to work here. It could work over Telstra 4G if latency is under 100 ms. "
        "No measurement exists here."
    )
    expect(page.locator(".map-card__fix")).to_have_text(
        f"Fix first #{priority['rank']} of {len(pack['communities'])} · {intervention}"
    )
    expect(page.locator(".map-card .verdict-badge")).to_have_count(4)
    open_link = page.get_by_role("link", name="Open Wadeye", exact=True)
    expect(open_link).to_have_attribute("href", "#/community/426")
    open_link.click()
    expect(page).to_have_url(re.compile(r"#/community/426$"))

    assert errors == []
    assert blocked == []
    page.close()


def test_declutter_is_pure_bounded_and_separates_real_points(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    result = page.evaluate(
        """() => {
            const pack = JSON.parse(document.getElementById('pack').textContent);
            const points = pack.communities.map(({id, x, y}) => ({id, x, y}));
            const a = window.__map.declutter(points, 1);
            const b = window.__map.declutter(points, 1);
            const zoom8 = window.__map.declutter(points, 8);
            const displacement = a.map((one, index) => Math.hypot(
                one.x - points[index].x,
                one.y - points[index].y,
            ));
            let minimumDistance = Infinity;
            for (let i = 0; i < a.length; i += 1) {
                for (let j = i + 1; j < a.length; j += 1) {
                    minimumDistance = Math.min(
                        minimumDistance,
                        Math.hypot(a[i].x - a[j].x, a[i].y - a[j].y),
                    );
                }
            }
            return {
                points,
                a,
                b,
                zoom8,
                maxDisplacement: Math.max(...displacement),
                minimumDistance,
            };
        }"""
    )
    assert result["a"] == result["b"]
    assert [one["id"] for one in result["a"]] == [one["id"] for one in result["points"]]
    assert result["maxDisplacement"] <= 14
    assert result["zoom8"] == result["points"]
    assert result["minimumDistance"] >= 6

    assert errors == []
    assert blocked == []
    page.close()


def test_map_more_fold_state(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    details = page.locator("details.map-more")
    assert details.evaluate("el => el.open") is False

    page.goto(f"{DIST_INDEX}#/map?filter=clinic-no-terrestrial")
    page.wait_for_load_state()
    assert page.locator("details.map-more").evaluate("el => el.open") is True

    assert errors == []
    assert blocked == []
    page.close()


def test_map_list_order_and_filter_dimming(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    pack = _pack(page)

    def row_ids() -> list[str]:
        return page.locator("ol.map-list > li").evaluate_all(
            """els => els.map(el => {
                const href = el.querySelector('a').getAttribute('href');
                return new URLSearchParams(href.split('?')[1] || '').get('selected');
            })"""
        )

    expect(page.locator("ol.map-list > li")).to_have_count(96)
    rank_one = str(next(one for one in pack["priority"] if one["rank"] == 1)["id"])
    assert row_ids()[0] == rank_one

    page.goto(f"{DIST_INDEX}#/map?lens=sources")
    page.wait_for_load_state()
    source_ids = row_ids()
    expected_source_ids = [
        str(community["id"])
        for community in sorted(
            pack["communities"],
            key=lambda one: (
                ("measured", "disagree", "agree").index(_source_bucket(one)),
                one["name"],
            ),
        )
    ]
    assert source_ids == expected_source_ids

    page.goto(f"{DIST_INDEX}#/map?filter=clinic-no-terrestrial")
    page.wait_for_load_state()
    filtered_ids = row_ids()
    active_ids = _filter_ids(pack, "clinic-no-terrestrial")
    first_excluded = next(
        (
            index
            for index, community_id in enumerate(filtered_ids)
            if community_id not in active_ids
        ),
        None,
    )
    assert first_excluded is not None
    assert all(community_id in active_ids for community_id in filtered_ids[:first_excluded])
    assert all(community_id not in active_ids for community_id in filtered_ids[first_excluded:])

    assert errors == []
    assert blocked == []
    page.close()


def test_service_selector_recolours_and_recounts(browser):
    page, blocked, errors = _open_page(browser, "#/map?lens=service")
    pack = _pack(page)

    select = page.locator("select")
    expect(select).to_have_value("telehealth_video")
    select.select_option("voice_sms")
    params = _params(page)
    assert params["lens"] == "service"
    assert params["service"] == "voice_sms"

    expected = {
        verdict: sum(
            next(
                service for service in community["services"] if service["service"] == "voice_sms"
            )["verdict"]
            == verdict
            for community in pack["communities"]
        )
        for verdict in VERDICT_NAMES
    }
    assert _legend_counts(page) == [str(expected[verdict]) for verdict in VERDICT_NAMES]
    for verdict in VERDICT_NAMES:
        expect(page.locator(f".map__pt--{verdict}")).to_have_count(expected[verdict])

    assert errors == []
    assert blocked == []
    page.close()


def test_map_list_service_is_worst_first(browser):
    page, blocked, errors = _open_page(browser, "#/map?lens=service&filter=clinic-no-terrestrial")

    rows = page.locator("ol.map-list > li")
    expect(rows).to_have_count(96)
    ranks = []
    for text in rows.all_text_contents():
        stripped = text.strip()
        ranks.append(next(index for index, word in enumerate(MAP_LIST_WORDS) if word in stripped))
    assert ranks == sorted(ranks)

    params = page.evaluate(
        """() => {
            const href = document.querySelector('ol.map-list > li a').getAttribute('href');
            return Object.fromEntries(new URLSearchParams(href.split('?')[1] || ''));
        }"""
    )
    assert params["lens"] == "service"
    assert params["filter"] == "clinic-no-terrestrial"
    assert params["selected"]

    assert errors == []
    assert blocked == []
    page.close()


def test_one_layer_group_per_pack_layer(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    for layer in _pack(page)["layers"]:
        expect(page.locator(f'g[data-layer="{layer["id"]}"]')).to_have_count(1)
    expect(page.locator("g.map__community")).to_have_count(96)

    assert errors == []
    assert blocked == []
    page.close()


def test_area_chip_toggles_hidden_on_its_group(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    _open_layers_fold(page)
    area_layer = next(layer for layer in _pack(page)["layers"] if layer["kind"] == "area")
    group = page.locator(f'g[data-layer="{area_layer["id"]}"]')
    chip = page.locator(".layer-chip").filter(has_text=area_layer["label"])
    expect(chip).to_have_count(1)
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
    for layer in _pack(page)["layers"]:
        if layer["kind"] == "area":
            expect(page.locator(f'g[data-layer="{layer["id"]}"]')).to_be_hidden()
    expect(page.locator('g[data-layer="towns"]')).to_be_visible()
    expect(page.locator(".map__town")).to_have_count(5)

    assert errors == []
    assert blocked == []
    page.close()


def test_region_chip_shows_the_sa3_layer(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    _open_layers_fold(page)
    layer = next(layer for layer in _pack(page)["layers"] if layer["id"] == "regions-sa3")
    chip = page.locator(".layer-chip").filter(has_text=layer["label"])
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
    towns_layer = next(layer for layer in _pack(page)["layers"] if layer["kind"] == "point")
    expected = {point["label"] for point in towns_layer["paths"]}
    markers = page.locator(".map__town")
    expect(markers).to_have_count(5)
    assert set(markers.all_text_contents()) == expected

    assert errors == []
    assert blocked == []
    page.close()


def _wheel_zoom_in(page, ticks: int = 10):
    box = page.locator(".map").bounding_box()
    assert box is not None
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
    assert float(view_box.split(" ")[2]) < 300
    assert int(svg.get_attribute("data-zoom")) > 1

    assert errors == []
    assert blocked == []
    page.close()


def test_zoomed_in_labels_become_visible(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    _wheel_zoom_in(page, ticks=12)
    assert int(page.locator(".map").get_attribute("data-zoom")) >= 3
    labels = page.locator(".map__zoom-labels .map__label")
    expect(labels.first).to_be_visible()
    assert labels.first.evaluate("el => getComputedStyle(el).display") != "none"

    assert errors == []
    assert blocked == []
    page.close()


def test_reset_view_restores_default_viewbox(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    svg = page.locator(".map")
    _wheel_zoom_in(page, ticks=6)
    assert svg.get_attribute("viewBox") != "0 0 300 480"
    page.get_by_role("button", name="Reset view", exact=True).click()
    expect(svg).to_have_attribute("viewBox", "0 0 300 480")
    expect(svg).to_have_attribute("data-zoom", "1")

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


def test_map_has_no_requests_or_page_errors_across_routes(browser):
    page, blocked, errors = _open_page(browser, "#/map")
    page.evaluate("""() => { location.hash = '#/map?lens=sources'; }""")
    page.wait_for_timeout(100)
    page.locator(".map-regions a.chip").nth(1).click()
    page.wait_for_timeout(500)
    page.evaluate("""() => { location.hash = '#/map?lens=sources&selected=426'; }""")
    page.wait_for_timeout(100)

    assert errors == []
    assert blocked == []
    page.close()


def test_older_version_pack_is_refused(browser, tmp_path):
    built = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")
    assert '"pack_version":3' in built
    downgraded = built.replace('"pack_version":3', '"pack_version":2', 1)
    copy_path = tmp_path / "version2.html"
    copy_path.write_text(downgraded, encoding="utf-8")

    page = browser.new_page()
    page.goto(copy_path.resolve().as_uri())
    page.wait_for_load_state()
    expect(page.locator("main")).to_have_text("Unknown data pack")
    page.close()
