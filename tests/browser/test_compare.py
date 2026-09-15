"""Browser tests for the compare route (Task-15): two columns side by side, the compare box
on the community screen, and the fallback for an unknown id."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST_INDEX = (ROOT / "dist" / "index.html").resolve().as_uri()


def _open_page(browser, hash_route: str, viewport: dict | None = None):
    page = browser.new_page(**({"viewport": viewport} if viewport else {}))
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


def test_compare_renders_two_columns(browser):
    page, blocked, errors = _open_page(browser, "#/compare/9/458")

    expect(page.locator(".community-header__name")).to_have_text(["Amoonguna", "Baniyala"])
    expect(page.locator(".verdict-badge")).to_have_count(8)
    expect(page.locator(".agreement__headline")).to_have_count(2)
    expect(page.locator(".compare__column")).to_have_count(2)
    expect(page.locator("[role=tab][aria-selected=true]")).to_have_text("Community")

    links = page.locator(".community-header__name .text-link")
    expect(links).to_have_count(2)
    expect(links.first).to_have_attribute("href", "#/community/9")
    expect(links.last).to_have_attribute("href", "#/community/458")

    assert errors == []
    assert blocked == []
    page.close()


def test_column_name_links_back(browser):
    page, blocked, errors = _open_page(browser, "#/compare/9/458")

    page.locator(".community-header__name .text-link").last.click()
    expect(page).to_have_url(re.compile(r"#/community/458$"))
    expect(page.locator("h1.community-header__name")).to_have_text("Baniyala")

    assert errors == []
    assert blocked == []
    page.close()


def test_compare_box_navigates(browser):
    page, blocked, errors = _open_page(browser, "#/community/9")

    box = page.locator(".compare-search")
    box.get_by_role("searchbox", name="Compare with...").fill("Bani")
    result = box.locator(".result-row").filter(has_text="Baniyala")
    expect(result).to_have_count(1)
    result.click()

    expect(page).to_have_url(re.compile(r"#/compare/9/458$"))
    expect(page.locator(".community-header__name")).to_have_text(["Amoonguna", "Baniyala"])
    expect(page.locator("[role=tab][aria-selected=true]")).to_have_text("Community")

    assert errors == []
    assert blocked == []
    page.close()


def test_unknown_id_falls_back(browser):
    page, blocked, errors = _open_page(browser, "#/compare/9/999999")

    expect(page).to_have_url(re.compile(r"#/community/9$"))
    expect(page.locator("h1.community-header__name")).to_have_text("Amoonguna")

    assert errors == []
    assert blocked == []
    page.close()


def test_both_unknown_opens_search(browser):
    page, blocked, errors = _open_page(browser, "#/compare/888888/999999")

    expect(page).to_have_url(re.compile(r"#/community/426$"))
    expect(page.locator(".search-input")).to_be_focused()

    assert errors == []
    assert blocked == []
    page.close()


@pytest.mark.parametrize(
    ("width", "height", "stacked"),
    [(360, 780, True), (768, 1024, False)],
)
def test_columns_stack_on_phone(browser, width, height, stacked):
    page, blocked, errors = _open_page(
        browser, "#/compare/9/458", viewport={"width": width, "height": height}
    )

    columns = page.locator(".compare__column")
    expect(columns).to_have_count(2)
    first = columns.nth(0).bounding_box()
    second = columns.nth(1).bounding_box()
    if stacked:
        assert abs(second["x"] - first["x"]) < 1
        assert second["y"] >= first["y"] + first["height"] - 1
    else:
        assert abs(second["y"] - first["y"]) < 1
        assert second["x"] >= first["x"] + first["width"] - 1

    assert errors == []
    assert blocked == []
    page.close()


def test_no_literals():
    pattern = re.compile(r"#[0-9a-fA-F]{3}|[0-9]px")
    for relative_path in ("app/app.css", "app/app.js"):
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert pattern.findall(text) == [], f"literal colour/size found in {relative_path}"
