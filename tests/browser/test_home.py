"""Browser tests for the fifth-batch home and community wording contract (Task-45)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist" / "index.html"
DIST_INDEX = DIST.resolve().as_uri()
PHONE = {"width": 360, "height": 780}
VERDICTS = {"Works", "Degraded", "Fails", "No data"}
GLYPHS = "●◐○◌"


@pytest.fixture
def context(browser):
    context = browser.new_context()
    yield context
    context.close()


def _open_page(context, hash_route: str = "", viewport: dict | None = None, path=DIST):
    page = context.new_page()
    if viewport:
        page.set_viewport_size(viewport)
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
    page.goto(f"{path.resolve().as_uri()}{hash_route}")
    page.wait_for_load_state()
    return page, blocked, errors


def test_home_route_and_exact_contract(context):
    page, blocked, errors = _open_page(context, "#/")

    assert page.evaluate("location.hash") == "#/"
    expect(page.locator(".home__question")).to_have_text(
        "Coverage maps say there is signal. Can the clinic run a video call?"
    )
    expect(page.locator(".home__lead")).to_have_text(
        "Crosscheck puts every public source about 96 remote NT communities side by side: "
        "what the connection there allows, where the sources disagree, and what to fix first. "
        "It works with no network."
    )
    expect(page.locator("ul.home__figures .home__figure")).to_have_text(
        [
            "96 communities",
            "1 of 70 clinics where a video call is known to work",
            "33 where the sources disagree",
        ]
    )
    expect(page.locator(".home__lead .fig")).to_have_text("96")
    expect(page.locator("ul.home__figures .fig")).to_have_text(["96", "1", "70", "33"])
    expect(page.locator(".home__actions a")).to_have_text(
        ["Find a community", "What to fix first", "See the map"]
    )
    assert page.locator(".home__actions a").evaluate_all(
        "els => els.map(el => el.getAttribute('href'))"
    ) == ["#/community/426", "#/priority", "#/map"]
    expect(page.locator(".home__note")).to_have_text(
        "A diagnosis, not a fix: every figure is from a published source, and the app measures "
        "nothing."
    )
    expect(page.locator("nav[aria-label='Main navigation'] [aria-current=page]")).to_have_count(0)

    assert errors == []
    assert blocked == []
    page.close()


def test_home_actions_fit_phone_viewport(context):
    page, blocked, errors = _open_page(context, "#/", viewport=PHONE)

    box = page.locator(".home__actions a").last.bounding_box()
    assert box is not None
    assert box["y"] + box["height"] <= PHONE["height"]
    assert page.evaluate("window.scrollY") == 0

    assert errors == []
    assert blocked == []
    page.close()


def test_home_actions_open_their_declared_destinations(context):
    page, blocked, errors = _open_page(context, "#/")

    page.get_by_role("link", name="Find a community", exact=True).click()
    expect(page.locator("h1.community-header__name")).to_have_text("Wadeye")

    page.goto(f"{DIST_INDEX}#/")
    page.get_by_role("link", name="What to fix first", exact=True).click()
    expect(page.locator("nav[aria-label='Main navigation'] [aria-current=page]")).to_have_text(
        "Fix first"
    )

    page.goto(f"{DIST_INDEX}#/")
    page.get_by_role("link", name="See the map", exact=True).click()
    expect(page.locator(".map__community")).to_have_count(96)

    assert errors == []
    assert blocked == []
    page.close()


def test_top_bar_title_returns_home(context):
    page, blocked, errors = _open_page(context, "#/community/426")

    expect(page.locator("a.top-bar__title")).to_have_attribute("href", "#/")
    page.locator("a.top-bar__title").click()
    expect(page).to_have_url(re.compile(r"#/$"))
    expect(page.locator(".home__question")).to_be_visible()

    assert errors == []
    assert blocked == []
    page.close()


def test_home_without_headline_is_still_rendered(context, tmp_path):
    html = DIST.read_text(encoding="utf-8")
    match = re.search(
        r'<script type="application/json" id="pack">(.*?)</script>', html, re.S
    )
    assert match is not None
    pack = json.loads(match.group(1))
    del pack["headline"]
    without_headline = tmp_path / "without-headline.html"
    replacement = json.dumps(pack, ensure_ascii=False, separators=(",", ":"))
    without_headline.write_text(
        html[: match.start(1)] + replacement + html[match.end(1) :], encoding="utf-8"
    )

    page, blocked, errors = _open_page(context, "#/", path=without_headline)

    expect(page.locator(".home__question")).to_be_visible()
    expect(page.locator("ul.home__figures")).to_have_count(0)
    assert errors == []
    assert blocked == []
    page.close()


def test_community_summary_matches_every_pack_community(context):
    page, blocked, errors = _open_page(context, "#/community/426")

    results = page.evaluate(
        """
        async () => {
            const pack = JSON.parse(document.getElementById("pack").textContent);
                const finish = (reason) => {
                    const clean = reason.replaceAll("`", "");
                    return clean.endsWith(".") ? clean : `${clean}.`;
                };
            const coverage = (community) => {
                const { covered, available } = community.agreement;
                if (available === 0) {
                    return "No source makes a coverage claim about " + community.name + ".";
                }
                if (covered === available) {
                    return `All ${available} sources say ` + community.name
                        + " has mobile coverage.";
                }
                if (covered === 0) {
                    return `None of ${available} sources says ` + community.name
                        + " has mobile coverage.";
                }
                return `${covered} of ${available} sources say `
                    + community.name + " has mobile coverage; they disagree.";
            };
            const telehealth = (community) => {
                const service = community.services.find(
                    (one) => one.service === "telehealth_video",
                );
                if (service.verdict === "works") {
                    return "A video call with a doctor should work here.";
                }
                if (service.verdict === "degraded") {
                    if (service.assumption) {
                        const parts = service.assumption.split(". ");
                        if (parts.length >= 2) {
                            const firstPart = parts[0].replaceAll("`", "");
                            const secondPart = parts[1].replaceAll("`", "");
                            const first = firstPart.charAt(0).toLowerCase() + firstPart.slice(1);
                            return "A video call with a doctor is not proven to work here. It "
                                + first + ". " + secondPart + ".";
                        }
                    }
                    return "A video call with a doctor is not proven to work here: "
                        + finish(service.reason);
                }
                if (service.verdict === "fails") {
                    return "A video call with a doctor will not work here: "
                        + finish(service.reason);
                }
                return "No health centre is recorded here, so a doctor's video call is not "
                    + "assessed.";
            };
            const results = [];
            for (const community of pack.communities) {
                location.hash = `#/community/${community.id}`;
                await new Promise((resolve) => setTimeout(resolve, 0));
                const actual = document.querySelector("p.community-summary").textContent;
                results.push({
                    id: community.id,
                    actual,
                    expected: `${coverage(community)} ${telehealth(community)}`,
                });
            }
            return results;
        }
        """
    )

    assert len(results) == 96
    for result in results:
        assert result["actual"] == result["expected"], result["id"]
    assert "`" not in result["actual"]
    assert next(result for result in results if result["id"] == 426)["actual"] == (
        "All 4 sources say Wadeye has mobile coverage. A video call with a doctor is not proven "
        "to work here. It could work over Telstra 4G if latency is under 100 ms. "
        "No measurement exists here."
    )

    assert errors == []
    assert blocked == []
    page.close()


def test_community_questions_paths_badges_and_reliability(context):
    page, blocked, errors = _open_page(context, "#/community/426")

    services = page.locator(".services")
    assert services.locator(":scope > *").first.get_attribute("class") == "services__question"
    expect(services.locator(":scope > *").first).to_have_text("Can people here…")
    expect(page.locator(".service-row__name")).to_have_text(
        [
            "see a doctor by video",
            "join a school lesson by video",
            "use myGov and banking",
            "call and text",
        ]
    )

    for index in range(4):
        row = page.locator("button.service-row").nth(index)
        row.click()
        detail = page.locator(".service-row__detail").nth(index)
        expect(detail).to_be_visible()
        assert detail.evaluate(
            "el => el.lastElementChild.classList.contains('service-row__path')"
        )

    for text in page.locator(".verdict-badge").all_text_contents():
        compact = "".join(text.split())
        assert compact[0] in GLYPHS
        assert compact[1:] in VERDICTS

    reliability = page.locator("details.reliability-line")
    expect(reliability).to_have_count(1)
    assert reliability.evaluate("el => !el.open && !el.hasAttribute('open')")
    summary = reliability.locator("summary").text_content()
    assert summary.startswith("How far to trust the coverage map here: ")
    assert summary.split()[-1] in {"high", "medium", "low", "none"}

    assert errors == []
    assert blocked == []
    page.close()


def test_wadeye_kind_chips_and_share_transfer_fold(context):
    page, blocked, errors = _open_page(context, "#/community/426")

    page.locator("details.sources-fold > summary").click()
    expect(page.locator(".kind-chip")).to_have_text(
        [
            "carrier's prediction",
            "government list",
            "licence register",
            "community portal",
            "drive test",
        ]
    )

    page.goto(f"{DIST_INDEX}#/share")
    transfer = page.locator("details.transfer-fold")
    expect(transfer).to_have_count(1)
    assert transfer.evaluate("el => !el.open && !el.hasAttribute('open')")
    expect(transfer.locator("summary")).to_have_text("Update another phone by camera")
    assert transfer.locator(".qr").count() == 0
    expect(page.locator(".qr")).to_have_count(1)

    assert errors == []
    assert blocked == []
    page.close()
