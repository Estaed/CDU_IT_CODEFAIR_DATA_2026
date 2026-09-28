"""Phone-width screenshots of the built app (dist/index.html) for design review.

Usage: .venv/Scripts/python design/shots.py <out_dir> [light|dark ...]   (default: light dark)
The theme is chosen the way a person chooses it: the stored preference the toggle writes.
A build without themes (the original design) ignores it; pass one theme name for that.
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = (ROOT / "dist/index.html").as_uri()
ROUTES = {"home": "#/", "community": "#/community/426", "priority": "#/priority",
          "map": "#/map", "share": "#/share"}

out = Path(sys.argv[1])
themes = sys.argv[2:] or ["light", "dark"]
out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch()
    for theme in themes:
        page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        page.add_init_script(f"localStorage.setItem('crosscheck-theme', '{theme}')")
        for name, route in ROUTES.items():
            page.goto(URL + route)
            page.wait_for_timeout(600)
            page.screenshot(path=str(out / f"{theme}-{name}.png"))
        page.close()
    browser.close()
print(f"wrote {len(ROUTES) * len(themes)} screenshots to {out}")
