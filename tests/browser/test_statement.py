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

    # Task-34: the statement buttons fold behind "Share", closed by default.
    page.locator("details.share-fold > summary").click()
    button = page.locator("details.share-fold button.button--secondary")
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

    # Task-34: the freshness line moved into the "Share" fold (unchanged selector otherwise).
    page.locator("details.share-fold > summary").click()
    line = page.locator(".community-header__freshness", has_text="Oldest source:")
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


# Mesh (Meshtastic/LoRa) statement (Task-22): a third, byte-budgeted text for Screen 1.
MESH_MAX_BYTES = 200
MESH_SMS_LABEL = {
    "telehealth_video": "Telehealth video",
    "school_video_meeting": "School video",
    "mygov_text": "myGov",
    "voice_sms": "Voice/SMS",
}


def _mesh_word(verdict: str) -> str:
    return "NOT RECORDED" if verdict == "nodata" else verdict.upper()


def _expected_mesh_text(pack: dict, community: dict) -> str:
    """Mirrors app.js statementMesh: drops the least essential fields from the end (built
    date, then agreement, then each service, in reverse) until the line is <= 200 bytes UTF-8;
    the community name and "crosscheck" are never dropped."""
    service_parts = [
        f"{MESH_SMS_LABEL[service['service']]} {_mesh_word(service['verdict'])}"
        for service in community["services"]
    ]
    droppable = [
        *service_parts,
        f"agree {community['agreement']['covered']}/{community['agreement']['available']}",
        pack["built"][:10],
    ]
    for count in range(len(droppable), -1, -1):
        text = " - ".join([community["name"], *droppable[:count], "crosscheck"])
        if len(text.encode("utf-8")) <= MESH_MAX_BYTES:
            return text
    raise AssertionError(f"statementMesh: {community['name']} exceeds {MESH_MAX_BYTES} bytes")


def test_mesh_statement_under_limit_for_all(context):
    pack = _pack()
    page, blocked, errors = _open_page(context, "#/community/9")

    results = page.evaluate(
        """() => JSON.parse(document.getElementById("pack").textContent)
            .communities.map((c) => [c.name, window.__statement.mesh(c)])"""
    )
    assert len(results) == 96
    by_name = {community["name"]: community for community in pack["communities"]}
    for name, text in results:
        assert text == _expected_mesh_text(pack, by_name[name]), (name, text)
        assert text.startswith(name), text
        assert "crosscheck" in text, text
        assert text.isascii(), text
        assert len(text.encode("utf-8")) <= MESH_MAX_BYTES, (len(text.encode("utf-8")), text)

    assert errors == []
    assert blocked == []
    page.close()


def test_short_statement_has_no_middle_dot(context):
    # Task-26: "·" makes the SMS body UCS-2 (about 3 segments); "-" keeps it GSM-7. The "·" the
    # rest of the UI uses stays everywhere else (BACKLOG 2026-09-15, Task-13).
    page, blocked, errors = _open_page(context, "#/community/9")

    texts = page.evaluate(
        """() => JSON.parse(document.getElementById("pack").textContent)
            .communities.map((c) => window.__statement.short(c))"""
    )
    assert len(texts) == 96
    for text in texts:
        assert "·" not in text, text

    assert errors == []
    assert blocked == []
    page.close()


def test_copy_mesh_text(context):
    pack = _pack()
    community = next(c for c in pack["communities"] if c["name"] == "Wadeye")
    expected = _expected_mesh_text(pack, community)
    page, blocked, errors = _open_page(context, f"#/community/{community['id']}")

    # Task-34: the mesh-text button folds behind "Share", closed by default.
    page.locator("details.share-fold > summary").click()
    button = page.locator("button[data-text]")
    expect(button).to_have_count(1)
    expect(button).to_have_text("Copy mesh text")
    data_text = button.get_attribute("data-text")

    assert data_text == (
        "Wadeye - Telehealth video DEGRADED - School video DEGRADED - myGov WORKS - "
        "Voice/SMS WORKS - agree 4/4 - 2026-09-15 - crosscheck"
    )
    assert data_text == expected
    assert data_text.startswith(community["name"])
    assert "crosscheck" in data_text
    assert data_text.isascii()
    assert len(data_text.encode("utf-8")) <= MESH_MAX_BYTES

    button.click()
    expect(button).to_have_text("Copied")
    copied = page.evaluate("() => navigator.clipboard.readText()")
    assert copied == data_text
    expect(button).to_have_text("Copy mesh text", timeout=5000)

    caption = page.locator(".source-line", has_text="Fits one LoRa mesh packet")
    expect(caption).to_have_count(1)
    assert "200 bytes" in caption.inner_text()

    assert errors == []
    assert blocked == []
    page.close()
