"""Browser test for the Changes section on the Share screen (Task-14)."""

from __future__ import annotations

import json
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
    context = browser.new_context()
    yield context
    context.close()


def _open_page(context, hash_route: str, init_script: str | None = None):
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
    if init_script:
        page.add_init_script(init_script)
    page.goto(f"{DIST_INDEX}{hash_route}")
    page.wait_for_load_state()
    return page, blocked, errors


def test_changes_section_lists_milingimbi(context):
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    changes = pack["changes"]
    page, blocked, errors = _open_page(context, "#/share")

    title = page.locator(".section__title", has_text="Changes")
    expect(title).to_have_text(f"Changes {changes['from']} -> {changes['to']}")

    rows = page.locator(".section:has(.section__title:has-text('Changes')) .link-row")
    expect(rows).to_have_count(len(changes["items"]))
    expect(rows.filter(has_text="Milingimbi")).to_have_count(1)

    link = rows.filter(has_text="Milingimbi").locator(".text-link")
    expect(link).to_have_attribute("href", "#/community/531")
    link.click()
    page.wait_for_load_state()
    expect(page).to_have_url(f"{DIST_INDEX}#/community/531")
    expect(page.locator(".community-header__name")).to_have_text("Milingimbi")

    assert errors == []
    assert blocked == []
    page.close()


def test_changes_items_have_no_trailing_dot(context):
    # Task-26: renderChanges used to join the sentence and the date with " · ", printing a
    # trailing "·" before the date; the row now carries no separator dot at all.
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    changes = pack["changes"]
    page, blocked, errors = _open_page(context, "#/share")

    rows = page.locator(".section:has(.section__title:has-text('Changes')) .link-row")
    expect(rows).to_have_count(len(changes["items"]))
    assert len(changes["items"]) > 0

    for i in range(rows.count()):
        text = rows.nth(i).locator(".link-row__text").inner_text()
        assert not text.rstrip().endswith("·"), text

    assert errors == []
    assert blocked == []
    page.close()


def test_changes_section_shows_no_changes_line_when_items_empty(context):
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    changes = pack["changes"]
    # Patches the pack the app reads before app.js runs: JSON.parse is wrapped so the one
    # call app.js makes against the pack's own text (identified by "changes" in the payload)
    # comes back with an empty items list. Everything else is passed through untouched.
    init_script = """
    const originalParse = JSON.parse;
    JSON.parse = (text, ...rest) => {
      const data = originalParse(text, ...rest);
      if (data && data.changes && Array.isArray(data.changes.items)) {
        data.changes.items = [];
      }
      return data;
    };
    """
    page, blocked, errors = _open_page(context, "#/share", init_script)

    no_changes_text = f"No changes between {changes['from']} and {changes['to']}"
    changes_section = page.locator(".section:has(.section__title:has-text('Changes'))")

    expect(page.locator(".section__title", has_text="Changes")).to_have_count(1)
    expect(page.locator(".source-line", has_text=no_changes_text)).to_have_count(1)
    expect(changes_section.locator(".link-row")).to_have_count(0)

    assert errors == []
    assert blocked == []
    page.close()
