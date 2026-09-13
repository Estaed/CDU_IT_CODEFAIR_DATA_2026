"""Browser smoke test: dist/index.html opens offline from file:// and renders the app shell."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]


def test_offline_smoke(browser):
    page = browser.new_page()
    blocked: list[str] = []

    def handler(route):
        url = route.request.url
        if not url.startswith("file:"):
            blocked.append(url)
            route.abort()
        else:
            route.continue_()

    page.route("**/*", handler)
    page.goto((ROOT / "dist" / "index.html").resolve().as_uri())
    page.wait_for_load_state()

    assert blocked == []
    assert page.evaluate("JSON.parse(document.getElementById('pack').textContent).count") == 96
    assert page.locator("[role=tab]").count() == 3
    assert "96 communities" in page.locator("main").inner_text()
    assert page.evaluate("location.hash") == "#/community/426"

    page.close()
