"""Browser tests for Report here (Task-35): the line format, the form that writes one, the
paste-in import and the evidence block. A fresh browser context per test keeps IndexedDB from
leaking between tests, since the file:// origin is shared (as tests/browser/test_update.py)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST_INDEX = (ROOT / "dist" / "index.html").resolve().as_uri()
PACK = ROOT / "data" / "out" / "data_pack.json"

SERVICE_NAMES = (
    "Telehealth video",
    "School video meeting",
    "myGov and banking",
    "Voice and SMS",
)
WADEYE = 426


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


def _synthetic_records() -> list[dict]:
    """Twenty canonical records, including the longest field values the format allows."""
    pack = _pack()
    ids = sorted(community["id"] for community in pack["communities"])
    widest_id = max(ids, key=lambda value: len(str(value)))
    statuses = ["works", "slow", "none"]
    carriers = ["telstra", "optus", "tpg", "other", None]
    types = ["4g", "3g", "2g", "slow-2g", None]

    records = [
        {
            "id": ids[index % len(ids)],
            "time": f"20260916{index % 24:02d}{(index * 7) % 60:02d}",
            "status": statuses[index % len(statuses)],
            "carrier": carriers[index % len(carriers)],
            "effectiveType": types[index % len(types)],
            "rtt": None if index % 4 == 0 else index * 37,
            "downlink": None if index % 5 == 0 else round(index * 1.5, 1),
            "lat": None if index % 3 == 0 else round(-25.58 + index * 0.5, 2),
            "lon": None if index % 3 == 0 else round(129.08 + index * 0.4, 2),
        }
        for index in range(19)
    ]
    # The longest line the format can produce: the widest id, the longest status, carrier and
    # effectiveType, six-digit rtt, four-digit downlink and a position in both hemispheres.
    records.append(
        {
            "id": widest_id,
            "time": "209912312359",
            "status": "works",
            "carrier": "telstra",
            "effectiveType": "slow-2g",
            "rtt": 999999,
            "downlink": 9999.9,
            "lat": -25.58,
            "lon": 137.85,
        }
    )
    return records


def test_format_parse_roundtrip_and_limit(context):
    page, blocked, errors = _open_page(context, f"#/community/{WADEYE}")
    records = _synthetic_records()

    results = page.evaluate(
        """(records) => records.map((record) => {
            const line = window.CrosscheckReport.format(record);
            return {
                line,
                bytes: new TextEncoder().encode(line).length,
                back: window.CrosscheckReport.parse(line),
            };
        })""",
        records,
    )

    assert len(results) == 20
    for record, result in zip(records, results, strict=True):
        assert result["line"].startswith("CR1|"), result["line"]
        assert result["bytes"] <= 200, result
        assert result["back"] == record

    assert errors == []
    assert blocked == []
    page.close()


def test_parse_rejects_malformed(context):
    page, blocked, errors = _open_page(context, f"#/community/{WADEYE}")
    good = f"CR1|{WADEYE}|202609161230|slow|telstra|4g|120|1.5|-14.24,129.52"
    unknown_id = 999999
    assert unknown_id not in {community["id"] for community in _pack()["communities"]}

    bad = [
        good.replace("CR1|", "CR2|", 1),  # wrong prefix
        "|".join(good.split("|")[:8]),  # 8 fields
        good.replace("|slow|", "|maybe|", 1),  # unknown status
        good.replace(f"|{WADEYE}|", f"|{unknown_id}|", 1),  # a community not in the pack
    ]

    verdicts = page.evaluate(
        "(lines) => lines.map((line) => window.CrosscheckReport.parse(line))",
        [good, *bad],
    )
    assert verdicts[0] is not None
    assert verdicts[1:] == [None, None, None, None]

    assert errors == []
    assert blocked == []
    page.close()


def _save_slow_report(page) -> str:
    """Tap Slow, leave the position box unticked, save, and return the stored line."""
    page.locator(".report-form__status", has_text="Slow").click()
    page.locator(".report-form__save").click()
    page.wait_for_selector(".report-line")
    return page.locator(".report-line").text_content()


def test_save_report_no_request(context):
    page, blocked, errors = _open_page(context, f"#/community/{WADEYE}?report")
    badges_before = page.locator(".verdict-badge").all_text_contents()

    line = _save_slow_report(page)

    assert len(line.encode("utf-8")) <= 200
    record = page.evaluate("(line) => window.CrosscheckReport.parse(line)", line)
    assert record["id"] == WADEYE
    assert record["status"] == "slow"
    assert record["carrier"] is None
    assert record["lat"] is None and record["lon"] is None

    stored = page.evaluate(f"() => window.CrosscheckStore.reportsFor({WADEYE})")
    assert stored == [line]
    assert page.locator(".report-line__sms").get_attribute("href").startswith("sms:?body=")
    assert page.locator("svg.report-line__qr").count() == 1
    assert page.locator(".verdict-badge").all_text_contents() == badges_before

    assert errors == []
    assert blocked == []
    page.close()


def test_second_page_import_counts(context):
    first, first_blocked, first_errors = _open_page(context, f"#/community/{WADEYE}?report")
    line = _save_slow_report(first)
    assert first_errors == []
    assert first_blocked == []
    first.close()

    page, blocked, errors = _open_page(context, f"#/community/{WADEYE}")
    page.locator(".reports-fold > summary").click()
    page.locator(".reports-fold__text").fill(f"{line}\nnot a report line\n")
    page.locator(".reports-import").click()

    result = page.locator(".reports-import__result")
    page.wait_for_function("() => document.querySelector('.reports-import__result').textContent")
    assert result.text_content() == "Added 1 of 2 lines"

    count_line = page.locator(".reports-line").text_content()
    assert re.fullmatch(
        r"Reports from here: 1 · 0 works, 1 slow, 0 no connection · latest "
        r"\d{1,2} [A-Z][a-z]{2} \d{4}",
        count_line,
    ), count_line

    assert errors == []
    assert blocked == []
    page.close()


def test_copy_evidence_text(context):
    page, blocked, errors = _open_page(context, f"#/community/{WADEYE}?report")
    line = _save_slow_report(page)

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

    community = next(c for c in _pack()["communities"] if c["id"] == WADEYE)
    assert community["name"] in copied
    for name in SERVICE_NAMES:
        assert f"{name}: " in copied, name
    assert line in copied
    assert copied.endswith(
        f"Crosscheck does not measure signal; reports are what people in "
        f"{community['name']} recorded on their own phones."
    )
    assert "`" not in copied

    assert errors == []
    assert blocked == []
    page.close()
