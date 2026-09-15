"""Browser tests for the statement on the community screen (Task-13): Send as SMS link, Copy
statement to the clipboard, and the oldest-source freshness line."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST_INDEX = (ROOT / "dist" / "index.html").resolve().as_uri()
PACK = ROOT / "data" / "out" / "data_pack.json"
VERDICT_WORDS = ("FAILS", "DEGRADED", "WORKS")


@pytest.fixture
def context(browser):
    context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
    yield context
    context.close()


def _pack() -> dict:
    return json.loads(PACK.read_text(encoding="utf-8"))


def _open_page(context, hash_route: str):
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


def test_sms_link(context):
    pack = _pack()
    community = next(c for c in pack["communities"] if c["id"] == 9)
    page, blocked, errors = _open_page(context, "#/community/9")

    link = page.locator("a.button", has_text="Send as SMS")
    expect(link).to_have_count(1)
    href = link.get_attribute("href")
    assert href.startswith("sms:?body=")
    body = unquote(href[len("sms:?body="):])
    assert community["name"] in body
    assert any(word in body for word in VERDICT_WORDS)
    assert pack["built"] in body
    assert "`" not in body
    assert len(body) < 300

    assert errors == []
    assert blocked == []
    page.close()


def test_short_statement_under_limit_for_all(context):
    page, blocked, errors = _open_page(context, "#/community/9")

    texts = page.evaluate(
        """() => JSON.parse(document.getElementById("pack").textContent)
            .communities.map((c) => [c.name, window.__statement.short(c)])"""
    )
    assert len(texts) == 96
    for name, text in texts:
        assert text.startswith(f"{name}: "), text
        assert len(text) < 300, (len(text), text)

    assert errors == []
    assert blocked == []
    page.close()


def test_copy_statement(context):
    pack = _pack()
    community = next(c for c in pack["communities"] if c["id"] == 9)
    oldest_date = community["freshness"]["date"]
    page, blocked, errors = _open_page(context, "#/community/9")

    button = page.locator(".section button.button--secondary")
    expect(button).to_have_count(1)
    expect(button).to_have_text("Copy statement")
    button.click()
    expect(button).to_have_text("Copied")

    copied = page.evaluate("() => navigator.clipboard.readText()")
    assert community["name"] in copied
    assert "sources say covered" in copied
    assert oldest_date in copied
    assert "Every figure is from a published source; the app measures nothing." in copied
    assert "`" not in copied

    expect(button).to_have_text("Copy statement", timeout=5000)

    assert errors == []
    assert blocked == []
    page.close()


def test_freshness_line(context):
    pack = _pack()
    community = next(c for c in pack["communities"] if c["id"] == 9)
    source_name = pack["sources"][community["freshness"]["source"]]["source"]
    page, blocked, errors = _open_page(context, "#/community/9")

    line = page.locator(".community-header .source-line", has_text="Oldest source:")
    expect(line).to_have_count(1)
    text = line.inner_text()
    assert source_name in text
    assert community["freshness"]["date"] in text
    assert re.search(r"\d{4}", text)

    assert errors == []
    assert blocked == []
    page.close()


def test_no_figure_literals():
    text = (ROOT / "app" / "app.js").read_text(encoding="utf-8")
    assert re.findall(r"[0-9]+ ?ms|Mbps", text) == []
    for relative_path in ("app/app.css", "app/app.js"):
        source = (ROOT / relative_path).read_text(encoding="utf-8")
        assert re.findall(r"#[0-9a-fA-F]{3}|[0-9]px", source) == []
