"""Browser tests for transfer by camera v4 (Task-37): the `CP` frame contract, the peeling
receiver's lossless and lossy-drop round trips, and the progress UI on both ends.

What travels is the **data pack, not the app**: the payload is the pack this copy is running
with, `layers` replaced by `[]`, gzipped at Show time. The receiver stores it through
store.js, which carries this copy's own map layers over the incoming empty ones. Headless
Chromium may lack BarcodeDetector and a camera (Blueprint), so every round trip below pushes
frame texts straight into CrosscheckTransfer.receiver() (or the mounted receive UI's
testPushFrame hook) instead of scanning.

The loss budgets are Blueprint's, and since 2026-09-17 they are read over a distribution: for
each of 10 / 50 / 70 % loss the median of twenty fixed seeds stays within 1.6 / 2.8 / 4.5 * K
pushed frames and the worst seed within 2.5 / 3.5 / 4.5 * K, every seed completing, and the
deterministic sources-0..19 scenario stays within 2.0 * K. The medians are the budgets
Task-36 measured at K 233 and they hold at v4's much smaller K, where the same overhead buys
far fewer frames; the worst-seed line is what one fixed seed used to hide."""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist" / "index.html"
DIST_INDEX = DIST.resolve().as_uri()

FRAME_RE = re.compile(r"^CP[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{6}[A-Za-z0-9+/]{1000}$")

# A small seeded PRNG (mulberry32), reused by the drop test below so the drop pattern is fixed
# run to run without pulling in a dependency for one test.
MULBERRY32_JS = """
(seed) => {
    let state = seed | 0;
    return () => {
        state |= 0; state = (state + 0x6D2B79F5) | 0;
        let t = Math.imul(state ^ (state >>> 15), 1 | state);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}
"""


@pytest.fixture
def context(browser):
    context = browser.new_context()
    yield context
    context.close()


def _open_page(context, hash_route: str = ""):
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


def _built_pack() -> dict:
    html = DIST.read_text(encoding="utf-8")
    match = re.search(r'<script type="application/json" id="pack">(.*?)</script>', html, re.S)
    return json.loads(match.group(1))


def test_frame_regex_matches_source_and_repair_frames(context):
    page, blocked, errors = _open_page(context, "#/share")

    result = page.evaluate(
        """
        async () => {
            const text = await window.CrosscheckTransfer.testPayloadText();
            const built = await window.CrosscheckTransfer.encoder(text);
            const texts = [];
            for (let i = 0; i < built.k; i++) texts.push(built.frameAt(i));
            for (let i = built.k; i < built.k + 20; i++) texts.push(built.frameAt(i));
            return { k: built.k, texts };
        }
        """
    )
    assert result["k"] >= 1
    for text in result["texts"]:
        assert FRAME_RE.match(text), text

    assert errors == []
    assert blocked == []
    page.close()


def test_round_trip_between_two_pages_is_the_pack_and_layers_are_carried_over(context):
    # The whole contract in one test: what one page's Show plays is the pack with `layers`
    # emptied; a second page reassembles it byte for byte, and after store.js accepts it the
    # stored pack holds this copy's own layers again -- the map is static geography and never
    # needs to cross the camera (Task-37).
    expected = _built_pack()
    sender, sender_blocked, sender_errors = _open_page(context, "#/share")
    frames = sender.evaluate(
        """
        async () => {
            const text = await window.CrosscheckTransfer.testPayloadText();
            const built = await window.CrosscheckTransfer.encoder(text);
            const texts = [];
            for (let i = 0; i < built.k; i++) texts.push(built.frameAt(i));
            return { k: built.k, texts };
        }
        """
    )
    sender.close()

    receiver, blocked, errors = _open_page(context, "#/share")
    result = receiver.evaluate(
        """
        async (texts) => {
            const rx = window.CrosscheckTransfer.receiver();
            let status;
            for (const text of texts) {
                status = rx.push(text);
            }
            if (!status.complete) {
                return { complete: false };
            }
            const text = await window.CrosscheckTransfer.inflate(rx.bytes());
            await window.CrosscheckTransfer.testReceiveComplete(rx.bytes());
            const stored = await window.CrosscheckStore.load();
            return { complete: true, received: JSON.parse(text), stored };
        }
        """,
        frames["texts"],
    )

    assert result["complete"], result
    assert result["received"] == {**expected, "layers": []}
    assert result["stored"]["layers"] == expected["layers"]
    assert result["stored"]["built"] == expected["built"]
    assert len(result["stored"]["communities"]) == 96

    status_el = receiver.locator(".transfer__status")
    expect(status_el).to_have_text("Received. Tap to use the new data.")
    expect(
        receiver.locator(".transfer__button", has_text="Use received data now")
    ).to_be_visible()

    assert sender_errors == []
    assert sender_blocked == []
    assert errors == []
    assert blocked == []
    receiver.close()


# Tarik's decision, 2026-09-17: a loss budget is a distribution, not one seed. Over the twenty
# fixed seeds below, the MEDIAN frames-needed ratio must sit inside Blueprint's 1.6 / 2.8 / 4.5 x K
# and the WORST seed inside 2.5 / 3.5 / 4.5 x K, and every seed must complete. One seed was
# never a property of the decoder: at K 24 three of these twenty already needed more than
# 1.6 x K at 10 % loss, and one block more of pack (K 25) moved the fixed seed from 1.29 to
# 2.20 x K. The twenty runs share one page evaluation; twenty page loads for one assertion is
# the slow way round.
SEEDS = [20260915 + s * 7919 for s in range(20)]


@pytest.mark.parametrize(
    ("loss", "median_budget", "worst_budget"),
    [(0.1, 1.6, 2.5), (0.5, 2.8, 3.5), (0.7, 4.5, 4.5)],
    ids=["loss10", "loss50", "loss70"],
)
def test_seeded_drop_completes_within_budget(context, loss, median_budget, worst_budget):
    # Three losses, not one: a phone reading a screen loses half the frames or more, which is
    # what v2's uniform 6..12 degree was never tuned for and the robust soliton is.
    page, blocked, errors = _open_page(context, "#/share")

    result = page.evaluate(
        f"""
        async (seeds) => {{
            const text = await window.CrosscheckTransfer.testPayloadText();
            const built = await window.CrosscheckTransfer.encoder(text);
            const mulberry32 = {MULBERRY32_JS};
            const runs = [];
            for (const seed of seeds) {{
                const seq = window.CrosscheckTransfer.createSequence(built.k);
                const rand = mulberry32(seed);
                const rx = window.CrosscheckTransfer.receiver();
                // Far more room than the worst budget, so a run that does not complete is the
                // decoder's answer and never the cap's.
                const cap = built.k * 8;
                let pushed = 0;
                let offered = 0;
                const maxOffered = Math.ceil(cap / (1 - {loss})) * 4;
                let status = {{ complete: false, known: 0, total: built.k }};
                while (!status.complete && pushed < cap && offered < maxOffered) {{
                    const {{ index }} = seq.next();
                    offered += 1;
                    if (rand() < {loss}) {{
                        continue; // dropped, as if the camera missed this frame
                    }}
                    status = rx.push(built.frameAt(index));
                    pushed += 1;
                }}
                if (!status.complete) {{
                    runs.push({{ seed, complete: false, ratio: null, same: false }});
                    continue;
                }}
                const out = await window.CrosscheckTransfer.inflate(rx.bytes());
                runs.push({{
                    seed,
                    complete: true,
                    ratio: pushed / built.k,
                    same: out === text,
                }});
            }}
            return {{ k: built.k, runs }};
        }}
        """,
        SEEDS,
    )

    runs = result["runs"]
    k = result["k"]
    never = [run["seed"] for run in runs if not run["complete"]]
    assert never == [], f"k {k}: seeds that never completed within {k * 8} frames: {never}"
    wrong = [run["seed"] for run in runs if not run["same"]]
    assert wrong == [], f"k {k}: runs that completed but inflated to other bytes: {wrong}"

    ratios = sorted(run["ratio"] for run in runs)
    median = statistics.median(ratios)
    worst = ratios[-1]
    observed = (
        f"{int(loss * 100)} % loss, k {k}, {len(ratios)} seeds: "
        f"median {median:.2f} x K, worst {worst:.2f} x K"
    )
    print(observed)
    assert median <= median_budget, f"{observed}; median budget {median_budget} x K"
    assert worst <= worst_budget, f"{observed}; worst-seed budget {worst_budget} x K"

    assert errors == []
    assert blocked == []
    page.close()


def test_sources_0_to_19_never_delivered_still_completes(context):
    # 2.0 * K (Tarik's decision, 2026-09-17; 1.75 until then). No randomness at all here: the
    # omission is fixed and createSequence is deterministic, so this is one value and not a
    # distribution. Twenty source blocks that never arrive must be rebuilt from repairs.
    page, blocked, errors = _open_page(context, "#/share")
    budget = 2.0

    result = page.evaluate(
        """
        async () => {
            const text = await window.CrosscheckTransfer.testPayloadText();
            const built = await window.CrosscheckTransfer.encoder(text);
            if (built.k <= 20) {
                return { skip: true, k: built.k };
            }
            const seq = window.CrosscheckTransfer.createSequence(built.k);
            const rx = window.CrosscheckTransfer.receiver();
            const cap = built.k * 8;
            let pushed = 0;
            let offered = 0;
            const maxOffered = cap * 4;
            let status = { complete: false, known: 0, total: built.k };
            while (!status.complete && pushed < cap && offered < maxOffered) {
                const { index } = seq.next();
                offered += 1;
                if (index < 20) {
                    continue; // never delivered, no other loss
                }
                status = rx.push(built.frameAt(index));
                pushed += 1;
            }
            if (!status.complete) {
                return { complete: false, pushed, k: built.k };
            }
            const out = await window.CrosscheckTransfer.inflate(rx.bytes());
            return { complete: true, pushed, k: built.k, same: out === text };
        }
        """
    )

    assert not result.get("skip"), f"the payload is too small for this test (k {result['k']})"
    assert result["complete"], result
    ratio = result["pushed"] / result["k"]
    observed = f"sources 0..19 dropped, k {result['k']}: {ratio:.2f} x K (deterministic)"
    print(observed)
    assert ratio <= budget, f"{observed}; budget {budget} x K"
    assert result["same"]

    assert errors == []
    assert blocked == []
    page.close()


@pytest.mark.parametrize("prefix", ["CY", "CZ"], ids=["v2", "v3"])
def test_older_contract_frames_are_ignored(context, prefix):
    # A v2 or v3 sender's frame is well-formed in every way except its prefix, and a v4
    # receiver must not mix contracts -- what a repair index means is not the same across
    # them, so peeling them together would decode to nothing. `known` stays at 0. (A v1 `CX`
    # frame is not even the right shape and never matched.)
    page, blocked, errors = _open_page(context, "#/share")

    status = page.evaluate(
        """
        (prefix) => {
            const rx = window.CrosscheckTransfer.receiver();
            const header = `${prefix}${"0".repeat(4)}${"0061"}${"0002ee"}`;
            return rx.push(`${header}${"A".repeat(1000)}`);
        }
        """,
        prefix,
    )
    assert status == {"complete": False, "known": 0, "total": 0}

    assert errors == []
    assert blocked == []
    page.close()


def test_transfer_texts_and_no_open_or_download_buttons(context):
    # Task-37's texts, and the two buttons that went with the withdrawn "the app travels"
    # story: there is no page to open and no file to download on this screen any more.
    page, blocked, errors = _open_page(context, "#/share")

    transfer = page.locator(".transfer")
    titles = transfer.locator(".transfer__title")
    expect(titles).to_have_text(["Send the latest data by camera", "Receive new data by camera"])

    sections = transfer.locator(".transfer__section")
    expect(sections.nth(0).locator(".transfer__note").first).to_have_text(
        "No internet, no pairing. The other phone needs Crosscheck installed; it taps Receive "
        "and points its camera at the moving code."
    )
    expect(sections.nth(1).locator(".transfer__note").first).to_have_text(
        "Point this camera at the other phone's moving code. Your copy keeps working while it "
        "arrives."
    )

    labels = page.locator(".transfer__button").all_text_contents()
    assert [label for label in labels if "Open" in label or "Download" in label] == []
    assert "Complete this copy" not in labels

    assert errors == []
    assert blocked == []
    page.close()


def test_receive_controls_and_show_stage_hidden_before_use(context):
    # Task-26: buildReceive() already set the `hidden` attribute on these elements, but
    # .transfer__button and .transfer__stage each set their own `display` as normal-author CSS,
    # which outranks the UA stylesheet's [hidden]{display:none} in the cascade regardless of
    # specificity -- so `hidden` had no visual effect until app.css added [hidden] overrides.
    page, blocked, errors = _open_page(context, "#/share")

    stage = page.locator(".transfer__stage")
    use_received = page.locator("button.transfer__button", has_text="Use received data now")
    progress = page.locator(".transfer__progress")

    expect(stage).to_be_hidden()
    expect(use_received).to_be_hidden()
    expect(progress).to_be_hidden()

    show_button = page.locator(".transfer").get_by_role("button", name="Show", exact=True)
    show_button.click()
    expect(stage).to_be_visible()

    assert errors == []
    assert blocked == []
    page.close()


def test_show_and_stop_controls_report_frame_and_pass(context):
    page, blocked, errors = _open_page(context, "#/share")

    transfer = page.locator(".transfer")
    expect(transfer).to_have_count(1)
    show_button = transfer.get_by_role("button", name="Show", exact=True)
    receive_button = transfer.get_by_role("button", name="Receive", exact=True)
    expect(show_button).to_have_count(1)
    expect(receive_button).to_have_count(1)

    show_button.click()
    expect(transfer.locator("svg")).to_have_count(1)
    counter = transfer.locator(".transfer__counter")
    expect(counter).to_have_text(re.compile(r"frame \d+"), timeout=10_000)
    expect(counter).to_have_text(re.compile(r"pass \d+"))

    note = transfer.locator(".transfer__stage .transfer__note")
    expect(note).to_have_text("Keep showing until the other phone says Received.")

    stop_button = transfer.get_by_role("button", name="Stop", exact=True)
    expect(stop_button).to_have_count(1)
    stop_button.click()

    frozen = counter.text_content()
    page.wait_for_timeout(500)
    assert counter.text_content() == frozen

    assert errors == []
    assert blocked == []
    page.close()


def test_receiving_screen_progress_and_received_message(context):
    page, blocked, errors = _open_page(context, "#/share")

    push_result = page.evaluate(
        """
        async () => {
            const text = await window.CrosscheckTransfer.testPayloadText();
            const built = await window.CrosscheckTransfer.encoder(text);
            let status;
            for (let i = 0; i < built.k; i++) {
                status = await window.CrosscheckTransfer.testPushFrame(built.frameAt(i));
            }
            return { k: built.k, status };
        }
        """
    )
    assert push_result["status"]["complete"]

    progress = page.locator(".transfer__progress")
    expect(progress).to_be_visible()
    progress_value = page.evaluate("() => document.querySelector('.transfer__progress').value")
    progress_max = page.evaluate("() => document.querySelector('.transfer__progress').max")
    assert progress_value == progress_max == push_result["k"]

    status_el = page.locator(".transfer__status")
    expect(status_el).to_have_text("Received. Tap to use the new data.")

    assert errors == []
    assert blocked == []
    page.close()


def test_transfer_module_has_no_network_literals():
    # CLAUDE.md Blueprint, layer rule 7: this file writes down no address and no transport. The
    # request count itself is asserted app-wide in tests/test_build.py, which is the one place
    # the token appears, so the grep behind the rule reads clean everywhere else.
    source = (ROOT / "app" / "transfer.js").read_text(encoding="utf-8")
    for token in ("XMLHttpRequest", "WebSocket", "EventSource", "http://", "https://"):
        assert token not in source
