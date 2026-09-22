"""Browser tests for the Priority tab (Task-41): the analyst's sixty seconds end to end, the
All chip, the tab row, and the pack version the app now accepts. A fresh browser context per
test keeps IndexedDB from leaking between tests, as tests/browser/test_report.py does."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST_INDEX = (ROOT / "dist" / "index.html").resolve().as_uri()
PACK = ROOT / "data" / "out" / "data_pack.json"

RELIABILITY_WORDS = {"high", "medium", "low", "none"}
CHIP_WORD = "low-latency backhaul"


@pytest.fixture
def context(browser):
    context = browser.new_context()
    yield context
    context.close()


def _open_page(context, hash_route: str = ""):
    """A page with every non-file: request aborted and counted (CLAUDE.md Blueprint, gate 3b)."""
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


def _pack() -> dict:
    return json.loads(PACK.read_text(encoding="utf-8"))


def _chip_index(pack: dict, word: str) -> int:
    return next(i for i, one in enumerate(pack["priority_interventions"]) if one["word"] == word)


def test_sixty_seconds(context):
    """PRD §2: open with no network, see the ranked list, narrow it, open one community, read
    why it ranks there and whether its coverage claim holds, copy the evidence."""
    pack = _pack()
    by_id = {community["id"]: community for community in pack["communities"]}
    page, blocked, errors = _open_page(context, "#/priority")

    # 1. The whole list, in the pack's own rank order.
    expect(page.locator(".priority-row")).to_have_count(96)
    assert page.locator(".priority-row__name").all_text_contents() == [
        by_id[row["id"]]["name"] for row in pack["priority"]
    ]
    assert page.locator(".priority-row__rank").all_text_contents() == [
        f"#{row['rank']}" for row in pack["priority"]
    ]

    # 2. One intervention chip narrows it to that word's count in the pack.
    index = _chip_index(pack, CHIP_WORD)
    expected = [row for row in pack["priority"] if row["i"] == index]
    assert expected, CHIP_WORD
    page.get_by_role("button", name=CHIP_WORD, exact=True).click()
    expect(page.locator(".priority-row")).to_have_count(len(expected))
    expect(page.locator(".priority-chip[aria-pressed=true]")).to_have_text(CHIP_WORD)

    # 3. The first row opens its community.
    first = expected[0]
    page.locator(".priority-row__link").first.click()
    page.wait_for_function("() => location.hash.startsWith('#/community/')")
    assert page.evaluate("location.hash") == f"#/community/{first['id']}"

    # 4. That screen says where it ranks, whether the claim is reliable, and who says what.
    priority_line = page.locator(".priority-line")
    expect(priority_line).to_have_count(1)
    expect(priority_line).to_contain_text(f"Priority #{first['rank']} of 96")
    expect(priority_line).to_contain_text(CHIP_WORD)
    reliability_line = page.locator(".reliability-line")
    expect(reliability_line).to_have_count(1)
    assert reliability_line.evaluate("el => !el.open && !el.hasAttribute('open')")
    summary = reliability_line.locator("summary").text_content()
    assert summary.startswith("How far to trust the coverage map here: ")
    assert summary.split()[-1] in RELIABILITY_WORDS
    word = reliability_line.locator(".reliability-line__word").text_content()
    assert word in RELIABILITY_WORDS, word
    expect(page.locator(".publisher-row")).to_have_count(5)

    # 5. Copy evidence carries both lines.
    page.evaluate(
        """() => {
            window.__copied = null;
            const stub = {
                writeText: (text) => {
                    window.__copied = text;
                    return Promise.resolve();
                },
            };
            Object.defineProperty(navigator, "clipboard", { value: stub, configurable: true });
        }"""
    )
    page.locator(".evidence-button").click()
    page.wait_for_function("() => window.__copied !== null")
    copied = page.evaluate("() => window.__copied")
    assert f"Priority #{first['rank']} of 96 · {CHIP_WORD}" in copied
    assert f"Map claim reliability: {word} · " in copied

    # 6. Nothing left the phone at any step.
    assert errors == []
    assert blocked == []
    page.close()


def test_all_chip_restores_96(context):
    pack = _pack()
    index = _chip_index(pack, CHIP_WORD)
    narrowed = sum(1 for row in pack["priority"] if row["i"] == index)
    page, blocked, errors = _open_page(
        context, f"#/priority?intervention={CHIP_WORD.replace(' ', '%20')}"
    )

    expect(page.locator(".priority-row")).to_have_count(narrowed)
    page.get_by_role("button", name="All", exact=True).click()
    expect(page.locator(".priority-row")).to_have_count(96)
    assert page.evaluate("location.hash") == "#/priority"

    assert errors == []
    assert blocked == []
    page.close()


def test_tab_order_and_selected(context):
    page, blocked, errors = _open_page(context, "#/priority")

    links = page.locator("header.top-bar nav[aria-label='Main navigation'] .tab")
    expect(links).to_have_text(["Community", "Fix first", "Map", "Share"])
    expect(page.locator("nav[aria-label='Main navigation'] [aria-current=page]")).to_have_text(
        "Fix first"
    )

    assert errors == []
    assert blocked == []
    page.close()


def test_version_3_only(browser, tmp_path):
    built = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")
    assert '"pack_version":3' in built
    downgraded = built.replace('"pack_version":3', '"pack_version":2', 1)
    copy_path = tmp_path / "version2.html"
    copy_path.write_text(downgraded, encoding="utf-8")

    page = browser.new_page()
    page.goto(copy_path.resolve().as_uri())
    page.wait_for_load_state()
    expect(page.locator("main")).to_have_text(
        "This copy cannot read its data. Open the latest address once with internet."
    )
    page.close()
