"""Browser tests for the clarity batch (Task-30): top bar tabs at 360 wide, scroll hints on tab
rows, one search bar, use my location, intro line, section order, verdict legend, facilities as
text, collapsed footer sources, and the QR reading helpers."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST_INDEX = (ROOT / "dist" / "index.html").resolve().as_uri()

PHONE = {"width": 360, "height": 780}
WADEYE = {"latitude": -14.2404, "longitude": 129.5205}


def _open_page(target, hash_route: str, viewport: dict | None = None):
    """Open dist/index.html on a new page of `target` (a browser or a browser context), with
    every non-file request aborted and counted."""
    page = target.new_page(**({"viewport": viewport} if viewport else {}))
    blocked: list[str] = []
    errors: list[str] = []
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda error: errors.append(str(error)))

    def handler(route):
        url = route.request.url
        if not url.startswith("file:"):
            blocked.append(url)
            route.abort()
        else:
            route.continue_()

    page.route("**/*", handler)
    page.goto(f"{DIST_INDEX}{hash_route}")
    page.wait_for_load_state()
    return page, blocked, errors


def _id_by_name(page, name: str) -> int:
    return page.evaluate(
        """(name) => JSON.parse(document.getElementById('pack').textContent)
            .communities.find((c) => c.name === name).id""",
        name,
    )


def _result_item(page, name: str):
    return page.locator("li").filter(has=page.locator(".result-row").filter(has_text=name))


# 1. Top bar -----------------------------------------------------------------------------------


def test_top_bar_tabs_fit_360(browser):
    page, blocked, errors = _open_page(browser, "#/community/426", viewport=PHONE)

    header = page.locator("header.top-bar")
    tabs = header.locator("[role=tab]")
    # Task-41, 2026-09-17: a fourth tab, Priority, sits between Community and Map.
    expect(tabs).to_have_count(4)
    title = header.get_by_text("Crosscheck", exact=True)
    title_box = title.bounding_box()
    for i in range(4):
        box = tabs.nth(i).bounding_box()
        assert box["x"] >= 0
        assert box["x"] + box["width"] <= 360
        # Their own row under the title.
        assert box["y"] >= title_box["y"] + title_box["height"] - 1

    tablist = header.locator("[role=tablist]")
    assert tablist.evaluate("el => el.scrollWidth <= el.clientWidth")

    assert errors == []
    assert blocked == []
    page.close()


# 2. Scrollable tab rows show that they scroll -------------------------------------------------


def test_filter_tabs_overflow_hint(browser):
    page, blocked, errors = _open_page(browser, "#/map?filter=all", viewport=PHONE)

    row = page.locator(".filter-tabs")
    expect(row).to_be_visible()
    expect(page.locator(".filter-tabs .tab").first).to_have_attribute("aria-selected", "true")
    assert page.locator(".tabs").evaluate_all(
        "els => els.every((el) => el.hasAttribute('data-overflow'))"
    )
    expect(row).to_have_attribute("data-overflow", re.compile(r"right"))

    row.evaluate(
        """el => {
            el.scrollLeft = el.scrollWidth;
            el.dispatchEvent(new Event('scroll'));
        }"""
    )
    expect(row).to_have_attribute("data-overflow", re.compile(r"^(?!.*right).*left.*$"))

    assert errors == []
    assert blocked == []
    page.close()


# 3. One search bar ----------------------------------------------------------------------------


def test_one_search_bar_with_compare_buttons(browser):
    page, blocked, errors = _open_page(browser, "#/community/426")

    current_id = _id_by_name(page, "Amoonguna")
    other_id = _id_by_name(page, "Baniyala")
    page.evaluate("(id) => { location.hash = `#/community/${id}`; }", current_id)
    expect(page.locator("h1.community-header__name")).to_have_text("Amoonguna")

    expect(page.locator(".search-input")).to_have_count(1)
    expect(page.locator(".compare-search")).to_have_count(0)

    search = page.locator(".search-input")
    search.fill("Amoonguna")
    own = _result_item(page, "Amoonguna")
    expect(own).to_have_count(1)
    expect(own.locator(".result-row__compare")).to_have_count(0)

    search.fill("Bani")
    item = _result_item(page, "Baniyala")
    expect(item).to_have_count(1)
    expect(item.locator(".result-row__compare")).to_have_count(0)
    item.locator(".result-row").click()

    expect(page).to_have_url(re.compile(rf"#/community/{other_id}$"))
    expect(page.locator("h1.community-header__name")).to_have_text("Baniyala")

    assert errors == []
    assert blocked == []
    page.close()


# 4. Use my location ---------------------------------------------------------------------------


def test_use_my_location_opens_nearest(browser):
    context = browser.new_context(geolocation=WADEYE, permissions=["geolocation"])
    try:
        page, blocked, errors = _open_page(context, "#/community/458")

        button = page.locator("button.locate-button")
        expect(button).to_have_text("Use my location")
        button.click()

        expect(page).to_have_url(re.compile(r"#/community/426$"))
        expect(page.locator(".locate-status")).to_have_text(
            re.compile(r"Nearest community: Wadeye, \d+ km away")
        )

        assert errors == []
        assert blocked == []
        page.close()
    finally:
        context.close()


def test_use_my_location_refused(browser):
    context = browser.new_context(permissions=[])
    try:
        page, blocked, errors = _open_page(context, "#/community/458")

        page.locator("button.locate-button").click()
        expect(page.locator(".locate-status")).to_have_text(
            "Location not available on this phone", timeout=20_000
        )

        assert errors == []
        assert blocked == []
        page.close()
    finally:
        context.close()


# 5-9. Community screen ------------------------------------------------------------------------


# Task-34, 2026-09-16: the community screen's third pass folds everything past the four
# service rows behind a `details`/`summary`, closed by default, so the whole first screen fits
# above the fold (item 7). test_intro_line and test_verdict_legend_in_first_section are gone
# with the elements they tested (item 3: no intro line, no verdict legend on this screen).


def test_folds_in_order(browser):
    page, blocked, errors = _open_page(browser, "#/community/426")

    summaries = page.locator("main details > summary").all_text_contents()
    assert {
        "Do the sources agree? Yes, 4 of 4",
        "Share",
        # Task-35, 2026-09-16: Report here's paste-in fold, below the actions row.
        "Add reports",
        "What exists here",
        "Who to ask",
    }.issubset(summaries)
    reliability = [
        text
        for text in summaries
        if text.startswith("How far to trust the coverage map here: ")
    ]
    assert len(reliability) == 1
    assert reliability[0].split()[-1] in {"high", "medium", "low", "none"}

    assert errors == []
    assert blocked == []
    page.close()


def test_what_exists_here_is_text(browser):
    page, blocked, errors = _open_page(browser, "#/community/426")

    fold = page.locator("details.present-fold")
    expect(fold.locator("summary")).to_have_text("What exists here")
    present = fold.locator(".present-list")
    expect(present).to_have_count(1)
    for facility in ("Health centre", "School", "Store"):
        expect(present).to_contain_text(facility)
    expect(page.locator("main .chip")).to_have_count(0)

    assert errors == []
    assert blocked == []
    page.close()


def test_four_rows_with_new_glyphs(browser):
    page, blocked, errors = _open_page(browser, "#/community/426")

    rows = page.locator("button.service-row")
    expect(rows).to_have_count(4)
    glyph_texts = rows.locator(".service-row__glyph").all_text_contents()
    for glyph in glyph_texts:
        assert glyph in "●◐○◌"
    badge_texts = [
        "".join(text.split()) for text in rows.locator(".service-row__badge").all_text_contents()
    ]
    assert badge_texts == ["◐Degraded", "◐Degraded", "●Works", "●Works"]

    assert errors == []
    assert blocked == []
    page.close()


def test_row_toggle_opens_detail(browser):
    page, blocked, errors = _open_page(browser, "#/community/426")

    button = page.locator("button.service-row").first
    detail = page.locator(".service-row__detail").first
    expect(button).to_have_attribute("aria-expanded", "false")
    expect(detail).to_be_hidden()

    button.click()

    expect(button).to_have_attribute("aria-expanded", "true")
    expect(detail).to_be_visible()
    expect(detail.locator(".service-row__reason")).not_to_be_empty()

    assert errors == []
    assert blocked == []
    page.close()


def test_first_screen_holds_actions_at_360x780(browser):
    # Item 7: the acceptance criterion this task exists for. Checked for the Wadeye id, the
    # community with the longest name, and one whose rows include an assumption (closed, so
    # the assumption text does not add height).
    probe_page, _, _ = _open_page(browser, "#/community/426")
    ids = probe_page.evaluate(
        """() => {
            const pack = JSON.parse(document.getElementById('pack').textContent);
            const longest = pack.communities.reduce(
                (a, b) => (b.name.length > a.name.length ? b : a),
            );
            const withAssumption = pack.communities.find(
                (c) => c.id !== 426 && c.id !== longest.id
                    && c.services.some((s) => s.assumption),
            );
            return [426, longest.id, withAssumption.id];
        }"""
    )
    probe_page.close()

    for community_id in ids:
        page, blocked, errors = _open_page(
            browser, f"#/community/{community_id}", viewport=PHONE
        )
        actions = page.locator(".actions").first
        box = actions.bounding_box()
        assert box is not None
        assert box["y"] + box["height"] <= 780, f"community {community_id}: {box}"
        assert page.evaluate("() => window.scrollY") == 0

        assert errors == []
        assert blocked == []
        page.close()


def test_footer_sources_collapsed(browser):
    page, blocked, errors = _open_page(browser, "#/community/426")

    details = page.locator("details.footer__sources")
    expect(details).to_have_count(1)
    assert details.evaluate("el => !el.open && !el.hasAttribute('open')")
    summary = details.locator("summary")
    expect(summary).to_contain_text("Sources and licences")
    expect(page.locator(".footer__team")).to_be_visible()

    attribution = details.get_by_text("ACCC Mobile Infrastructure Report 2025")
    expect(attribution).not_to_be_visible()
    summary.click()
    expect(attribution).to_be_visible()

    assert errors == []
    assert blocked == []
    page.close()


# 10. QR reading helpers -----------------------------------------------------------------------


def _facing_mode(value) -> str | None:
    if isinstance(value, dict):
        return value.get("exact", value.get("ideal"))
    return value


@pytest.mark.parametrize(("w", "h"), [(1920, 1080), (640, 480), (480, 640)])
def test_scan_constraints_and_crop(browser, w, h):
    page, blocked, errors = _open_page(browser, "#/community/426")

    constraints = page.evaluate("() => window.CrosscheckScan.constraints()")
    video = constraints["video"]
    assert _facing_mode(video["facingMode"]) == "environment"
    assert video["width"]["ideal"] >= 1280

    rect = page.evaluate("([w, h]) => window.CrosscheckScan.cropRect(w, h)", [w, h])
    side = min(w, h)
    assert rect == {
        "sx": (w - side) // 2,
        "sy": (h - side) // 2,
        "side": side,
        "outSide": min(side, 1024),
    }

    assert errors == []
    assert blocked == []
    page.close()
