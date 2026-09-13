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
