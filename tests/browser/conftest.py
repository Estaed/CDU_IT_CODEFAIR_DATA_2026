"""Module-scoped Playwright Chromium fixture for the browser smoke test."""

from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="module")
def browser():
    pw = sync_playwright().start()
    browser = pw.chromium.launch()
    yield browser
    browser.close()
    assert not browser.is_connected()
    pw.stop()


@pytest.fixture
def blocking_page(browser):
    """Open a page with every non-`file:` request aborted and recorded.

    The same handler every browser test has used inline, hoisted here since Task-36 because the
    lite page's `Complete this copy` needs it as the assertion rather than only as a guard: the
    full page must record nothing, the lite page nothing until the tap, and exactly one URL
    after it. Aborting is also what keeps the suite honest offline.
    """
    context = browser.new_context()
    pages = []

    def open_page(url: str):
        page = context.new_page()
        blocked: list[str] = []
        errors: list[str] = []

        def handler(route):
            if route.request.url.startswith("file:"):
                route.continue_()
            else:
                blocked.append(route.request.url)
                route.abort()

        page.route("**/*", handler)
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.goto(url)
        page.wait_for_load_state()
        pages.append(page)
        return page, blocked, errors

    yield open_page
    context.close()
