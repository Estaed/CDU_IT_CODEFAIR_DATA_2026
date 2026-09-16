# Task-13: Send as SMS, copy statement and the freshness line

> **Execution:** agent `claude-worker` · effort `high`
> *Why:* render-only work on Screen 1 with strings already in the pack; criteria are Playwright assertions on text and on the `sms:` href.

**Lane**
- OWNS: `app/app.js` (statement builder, two buttons, freshness line), `tests/browser/test_statement.py`
- MUST NOT TOUCH: `pipeline/`, `scripts/`, `design/`, `app/app.css`, other files under `tests/browser/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-12

## Objective

A community can state its own situation in one message: a short text for SMS (works where only
voice and SMS work, including satellite-to-mobile SMS) and a longer plain-language statement
for the clipboard, both assembled from pack strings. Plus one line saying how old the oldest
source is. PRD §4.2 additions, 2026-09-15.

## Execution Guide

- `statementShort(community, pack)`: `<name>: Telehealth video FAILS (<reason>) · School video
  DEGRADED · myGov WORKS · Voice/SMS WORKS. Crosscheck, data <pack.built>.` Verdict words from
  the pack in upper case; the reason only for the first non-works service; target under 300
  characters, never cut a word. `statementLong(...)`: one paragraph: population and source,
  how many of how many sources say covered, best path, each service with verdict and reason,
  the oldest source line, and "Every figure is from a published source; the app measures
  nothing." No template string carries a figure or a threshold: all from the pack.
- Buttons under "What the connection allows", reusing `.button` / `.button--secondary`:
  **Send as SMS** is an `<a class="button" href="sms:?body=<encoded short text>">` (no number;
  the phone asks). **Copy statement** writes the long text with `navigator.clipboard.writeText`
  and falls back to selecting a hidden `<textarea>`; the button label reads "Copied" for two
  seconds. No network, no new element type outside the screens' vocabulary.
- Freshness line in the header block, reusing the `.source-line` style: `Oldest source: <source
  name> · <date>` from `community.freshness` and the `sources` table.
- `#/community/<id>` stays the route; nothing else on the screen moves.

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [x] `tests/browser/test_statement.py` (marker `browser`): on `#/community/9` the SMS link's href starts with `sms:?body=` and, decoded, contains the community name, one of `FAILS`/`DEGRADED`/`WORKS`, and the pack date; the decoded text is under 300 characters for all 96 communities (evaluate the builder in the page over the pack); the long statement, read back from the clipboard (grant `clipboard-read` and `clipboard-write`), contains `sources say covered` and the oldest-source date; the freshness line is present with a date.
- [x] Zero non-`file:` requests and no console errors.
- [x] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js` prints nothing; `grep -nE "[0-9]+ ?ms|Mbps" app/app.js` prints nothing (no figure lives in a template).

## Status

DONE 2026-09-15 (otopilot, lane gate and main gate green at `467f0eb`; 5 browser tests). Bee notes: the fallback textarea uses an inline `position: fixed; opacity: 0`; `window.__statement` exposes the builders for the test; the `·` separator makes the SMS UCS-2 (about 3 segments), a `-` would halve the segment count on prepaid plans, left as specified for Tarik to decide. review-visual pending for the button placement.
