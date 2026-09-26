"""Browser tests for the 2026-09-22 audit contract (Task-52)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST_INDEX = (ROOT / "dist" / "index.html").resolve().as_uri()
WADEYE = 426


def _open_page(context, hash_route: str = "", init_script: str | None = None):
    page = context.new_page()
    if init_script:
        page.add_init_script(init_script)
    blocked: list[str] = []

    def handler(route):
        if not route.request.url.startswith("file:"):
            blocked.append(route.request.url)
            route.abort()
        else:
            route.continue_()

    page.route("**/*", handler)
    page.goto(f"{DIST_INDEX}{hash_route}")
    page.wait_for_load_state()
    return page, blocked


@pytest.fixture
def context(browser):
    context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
    yield context
    context.close()


def test_search_empty_state(context):
    page, blocked = _open_page(context, f"#/community/{WADEYE}")
    page.locator(".search-input").fill("zzzz")
    expect(page.locator("p.results__empty")).to_have_text("No communities match that search.")
    assert blocked == []
    page.close()


def test_map_points_are_keyboard_links(context):
    page, blocked = _open_page(context, "#/map")
    pack = page.evaluate("() => JSON.parse(document.getElementById('pack').textContent)")
    points = page.locator("g.map__community")
    expect(points).to_have_count(96)
    assert points.evaluate_all(
        "(els) => els.every((el) => el.getAttribute('role') === 'link' && "
        "el.getAttribute('tabindex') === '0')"
    )
    expected = [
        f"{community['name']}, fix first #{community['priority']['rank']} of {pack['count']}"
        for community in pack["communities"]
    ]
    labels = points.evaluate_all("(els) => els.map((el) => el.getAttribute('aria-label'))")
    assert sorted(labels) == sorted(expected)

    first = points.first
    community_id = first.get_attribute("data-id")
    first.focus()
    first.press("Enter")
    expect(page).to_have_url(re.compile(rf"#/map\?selected={community_id}$"))
    assert blocked == []
    page.close()


@pytest.mark.parametrize(
    ("route", "heading"),
    [("#/priority", "What to fix first"), ("#/map", "Map"), ("#/share", "Share")],
)
def test_non_community_screens_have_one_heading(context, route, heading):
    page, blocked = _open_page(context, route)
    expect(page.locator("main > h1")).to_have_count(1)
    expect(page.locator("main > h1")).to_have_text(heading)
    assert blocked == []
    page.close()


def test_report_groups_have_legends(context):
    page, blocked = _open_page(context, f"#/community/{WADEYE}?report")
    expect(page.locator("fieldset > legend")).to_have_text(["Status", "Carrier (optional)"])
    assert blocked == []
    page.close()


def test_interactive_map_targets_are_touch_sized(context):
    page, blocked = _open_page(context, "#/map")
    page.wait_for_timeout(100)
    heights = page.locator(".chip, .map-lens__option, button.map-controls__reset").evaluate_all(
        "(els) => els.filter((el) => !el.hidden && getComputedStyle(el).display !== 'none' "
        "&& el.getBoundingClientRect().height > 0)"
        ".map((el) => el.getBoundingClientRect().height)"
    )
    assert heights and min(heights) >= 44, heights
    assert blocked == []
    page.close()


def test_sources_legend_and_service_labels(context):
    page, blocked = _open_page(context, "#/map?lens=sources")
    expect(page.locator(".map-legend")).to_contain_text(
        "Drive test found no signal inside claimed coverage"
    )
    expect(page.locator(".map-legend")).to_contain_text("Sources disagree on mobile coverage")
    expect(page.locator(".map-legend")).to_contain_text("Sources agree on mobile coverage")
    page.goto(f"{DIST_INDEX}#/map?lens=service")
    page.wait_for_load_state()
    assert page.locator("select.map-service option").all_text_contents() == [
        "See a doctor by video",
        "Join a school lesson by video",
        "Use myGov and banking",
        "Call and text",
    ]
    assert blocked == []
    page.close()


def test_priority_intro_and_map_filter_note(context):
    page, blocked = _open_page(context, "#/priority")
    expect(page.locator(".priority-intro")).to_have_text(
        "96 communities in action order. The score orders places within each group; "
        "method and weights are in the report."
    )
    page.goto(f"{DIST_INDEX}#/map")
    page.wait_for_load_state()
    expect(page.locator("p.map-legend__note")).to_have_count(0)
    page.goto(f"{DIST_INDEX}#/map?region=top-end")
    page.wait_for_load_state()
    expect(page.locator("p.map-legend__note")).to_have_text(
        "Faded points are outside this highlight."
    )
    assert blocked == []
    page.close()


def test_path_note_and_statement_keep_their_distinct_language(context):
    page, blocked = _open_page(context, f"#/community/{WADEYE}")
    page.locator("button.service-row").first.click()
    expect(page.locator(".service-row__detail").first).to_contain_text(
        "The best connection this community can get:"
    )
    page.locator("details.share-fold > summary").click()
    page.locator("details.share-fold button.button--secondary").click()
    copied = page.evaluate("() => navigator.clipboard.readText()")
    assert "Best available path" in copied
    assert blocked == []
    page.close()


def test_unknown_pack_has_recovery_message(browser, tmp_path):
    built = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")
    changed = built.replace('"pack_version":3', '"pack_version":99', 1)
    copy_path = tmp_path / "version99.html"
    copy_path.write_text(changed, encoding="utf-8")
    page = browser.new_page()
    page.goto(copy_path.resolve().as_uri())
    page.wait_for_load_state()
    expect(page.locator("main")).to_have_text(
        "This copy cannot read its data. Open the latest address once with internet."
    )
    page.close()


def test_report_save_failure_keeps_line_and_actions(context):
    page, blocked = _open_page(
        context,
        f"#/community/{WADEYE}?report",
        """
        (() => {
          let value;
          Object.defineProperty(window, 'CrosscheckStore', {
            configurable: true,
            get: () => value,
            set: (next) => {
              value = next;
              if (value) value.saveReport = () => Promise.reject(new Error('quota'));
            },
          });
        })();
        """,
    )
    page.locator(".report-form__status", has_text="Slow").click()
    page.locator(".report-form__save").click()
    expect(page.locator("p.report-error[role=alert]")).to_have_text(
        "Could not save this report on this phone. You can still copy or send this line."
    )
    expect(page.locator(".report-line")).to_be_visible()
    assert blocked == []
    page.close()


def test_copy_failure_is_announced_for_statement_and_report(context):
    page, blocked = _open_page(
        context,
        f"#/community/{WADEYE}?report",
        """
        Object.defineProperty(navigator, 'clipboard', {
          configurable: true,
          value: { writeText: () => Promise.reject(new Error('denied')) },
        });
        document.execCommand = () => false;
        """,
    )
    page.locator("details.share-fold > summary").click()
    page.locator("details.share-fold button.button--secondary").click()
    expect(page.locator("details.share-fold button.button--secondary")).to_have_text(
        "Copy failed. Select the text and copy it manually."
    )
    page.locator(".report-form__status", has_text="Slow").click()
    page.locator(".report-form__save").click()
    page.locator(".report-line__copy").click()
    expect(page.locator(".report-line__copy")).to_have_text(
        "Copy failed. Select the text and copy it manually."
    )
    assert blocked == []
    page.close()


def test_camera_failure_uses_plain_language(context):
    page, blocked = _open_page(
        context,
        "#/share",
        """
        Object.defineProperty(navigator, 'mediaDevices', {
          configurable: true,
          value: { getUserMedia: () => Promise.reject(
            Object.assign(new Error(), {name: 'NotAllowedError'})
          ) },
        });
        """,
    )
    page.locator("details.transfer-fold > summary").click()
    page.get_by_role("button", name="Receive", exact=True).click()
    expect(page.locator(".transfer__status")).to_have_text(
        "We couldn't use the camera. Allow camera access in your browser, then try again."
    )
    assert blocked == []
    page.close()


def test_valid_update_save_failure_is_distinguished(context):
    page, blocked = _open_page(
        context,
        "#/share",
        """
        (() => {
          let value;
          Object.defineProperty(window, 'CrosscheckStore', {
            configurable: true,
            get: () => value,
            set: (next) => {
              value = next;
              if (value) value.save = () => Promise.reject(new Error('quota'));
            },
          });
        })();
        """,
    )
    page.locator("details.transfer-fold > summary").click()
    page.get_by_role("button", name="Receive", exact=True).click()
    result = page.evaluate(
        """
        async () => {
          const text = await window.CrosscheckTransfer.testPayloadText();
          const built = await window.CrosscheckTransfer.encoder(text);
          const receiver = window.CrosscheckTransfer.receiver();
          for (let index = 0; index < built.k; index += 1) receiver.push(built.frameAt(index));
          await window.CrosscheckTransfer.testReceiveComplete(receiver.bytes());
          return true;
        }
        """
    )
    assert result is True
    expect(page.locator(".transfer__status")).to_have_text(
        "The update is valid, but this phone could not save it. Try again."
    )
    assert blocked == []
    page.close()


def test_location_failure_suggests_search(context):
    page, blocked = _open_page(
        context,
        f"#/community/{WADEYE}",
        """
        Object.defineProperty(navigator, 'geolocation', {
          configurable: true,
          value: { getCurrentPosition: (_success, failure) => failure({code: 1}) },
        });
        """,
    )
    page.locator("button.locate-button").click()
    expect(page.locator(".locate-status")).to_have_text(
        "We couldn't use your location. Search for a community instead."
    )
    assert blocked == []
    page.close()


def test_labels_do_not_intersect_at_supported_widths(context):
    for viewport in ({"width": 412, "height": 915}, {"width": 768, "height": 1024}):
        page = context.new_page()
        page.set_viewport_size(viewport)
        page.goto(f"{DIST_INDEX}#/map")
        page.wait_for_load_state()
        page.wait_for_timeout(150)
        collisions = page.evaluate(
            """
            () => {
              const labels = [...document.querySelectorAll('.map__label')].filter((el) => {
                const box = el.getBoundingClientRect();
                const style = getComputedStyle(el);
                return !el.hidden && style.display !== 'none' && style.visibility !== 'hidden'
                  && box.width > 0 && box.height > 0;
              });
              const boxes = labels.map((el) => el.getBoundingClientRect());
              return boxes.some((one, i) => boxes.slice(i + 1).some((other) =>
                one.left < other.right && one.right > other.left
                && one.top < other.bottom && one.bottom > other.top));
            }
            """
        )
        assert collisions is False, viewport
        page.close()
