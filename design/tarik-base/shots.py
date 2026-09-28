"""Screenshots of the built app (dist/index.html) for the Tarik Base review, both colour schemes.

Usage: uv run python design/tarik-base/shots.py [out_dir]   (default design/tarik-base/shots)
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "design/tarik-base/shots"
URL = (ROOT / "dist/index.html").as_uri()
ROUTES = {"home": "#/", "community": "#/community/426", "priority": "#/priority",
          "map": "#/map", "share": "#/share"}

OUT.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch()
    for scheme in ("dark", "light"):
        page = browser.new_page(viewport={"width": 390, "height": 844}, color_scheme=scheme,
                                device_scale_factor=2)
        for name, route in ROUTES.items():
            page.goto(URL + route)
            page.wait_for_timeout(700)
            page.screenshot(path=str(OUT / f"{scheme}-{name}.png"), full_page=False)
        page.close()
    browser.close()
print(f"wrote {len(ROUTES) * 2} screenshots to {OUT}")
