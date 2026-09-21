# Task-51: Defects from the 2026-09-22 audit, and the last map label rule

**Status: DONE** — verified 2026-09-22 (main loop: gate green, 212 unit + 117 browser, HTML 982,131 bytes. Attempt 1 omitted row F14, caught by Task-52's independently written test; attempt 2 was that one line. Eye review of the map at 360 and 412 wide: no two labels overlap.)

> **Execution:** agent `codex` (small tier) · effort `high`
> *Why:* 2026-09-22. Eighteen small, fully specified fixes with exact strings across four app
> files; machine-checkable through Task-52's tests. The eye check afterwards is the main loop's.

**Lane**
- OWNS: `app/app.js`, `app/app.css`, `app/report.js`, `app/transfer.js`, this file
- MUST NOT TOUCH: `tests/` (Task-52), `pipeline/`, `data/`, `app/index.html`, `app/store.js`, `app/qr.js`, `app/scan.js`, `app/vendor/`, `design/ds/`, `CLAUDE.md`, `docs/`
- GATE: from the project root, `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` (on a Windows temp-folder permission error rerun the two pytest steps with `--basetemp=.pytest_tmp` and delete it)
- DEPENDS ON: Task-48

## Objective

`reports/2026-09-22-audit.md` is a read-only audit of the built app against the fifth batch's
goal (a non-technical person understands the app in ten seconds; the analyst can act on it).
The main loop accepted the findings below as defects. Nothing here is a feature: no new
screen, control, pack field or route.

## Execution Guide

Read the audit file for each finding's evidence and location (line numbers may have moved).
Guidance, not a script, except the **fixed** strings, which Task-52 asserts exactly. Layer
rules still bind: tokens only in CSS (no hex, no `px` literal), no request, no `innerHTML`
with pack strings, `grep -n "verdict" app/report.js` prints nothing.

| Audit ID | What to do | **Fixed** string or attribute |
|---|---|---|
| F1 | `report.js`: catch a failed `saveReport`; still render the generated line with its Copy / SMS / QR; re-enable the button | `Could not save this report on this phone. You can still copy or send this line.` in `p.report-error[role=alert]` |
| F2 | every copy path (`app.js` `copyText` callers, `report.js`): use the result; on failure the button reads the failure text for 4 s instead of `Copied` | `Copy failed. Select the text and copy it manually.` |
| F3 | `transfer.js`: no error name or protocol in the visible text (keep them in a `title` attribute for debugging) | `We couldn't use the camera. Allow camera access in your browser, then try again.` |
| F4 | `transfer.js`: a save failure after a valid decode is not "not Crosscheck data" | `The update is valid, but this phone could not save it. Try again.` |
| F5 | community search with no match | `No communities match that search.` in `p.results__empty` |
| F7 | every `g.map__community`: `role="link"`, `tabindex="0"`, Enter and Space activate it like a tap, and `aria-label` | `{name}, fix first #{rank} of {count}` |
| F8 | one `h1.visually-hidden` as the first child of `main` on three screens (add the `.visually-hidden` rule to `app.css` if no such class exists in the inlined CSS) | `What to fix first` · `Map` · `Share` |
| F9 | `report.js`: status and carrier groups become `fieldset` with `legend` | `Status` · `Carrier (optional)` |
| F10 | chips, region chips, lens options, `Reset view`: `min-height` from the touch-size token (find it in `design/ds/design/tokens/spacing.css`; if none exists use `2.75em` and say so) | rendered height at least 44 px |
| F11 + main loop | label rule, final form: a community or town label is hidden unless, at the current view, its box overlaps **no other visible label** (towns included) **and no tier-1 marker other than the gap to its own**, and its own marker is the nearest tier-1 marker to the label's centre. Town labels win over community labels; the selected community's label wins over everything. Recompute on every view-box change and on resize. Must hold at 360, 412 and 768 px widths | no two visible label boxes intersect |
| F12 | Sources lens legend | `Drive test found no signal inside claimed coverage` · `Sources disagree on mobile coverage` · `Sources agree on mobile coverage` |
| F13 | the map's service `select` options read as the community rows do, capitalised | `See a doctor by video` · `Join a school lesson by video` · `Use myGov and banking` · `Call and text` |
| F14 | the path note inside the service rows' detail; the statement and evidence texts keep `Best available path` | `The best connection this community can get: ` |
| F15 (app part only) | the Fix first screen's intro line; intervention words and addressees come from the pack and do not change | `{n} communities, ordered by where action is needed first. Method and weights are in the report.` |
| F18 | under the legend, only while a filter or region is active | `Faded points are outside this highlight.` in `p.map-legend__note` |
| F19 | geolocation refused or unavailable | `We couldn't use your location. Search for a community instead.` |
| F20 | unknown `pack_version` at load | `This copy cannot read its data. Open the latest address once with internet.` |

Not accepted, do not do: F6 (tab semantics; every test keys on `[role=tab]`, logged under
Later), the intervention wording and `DCDD` in F15, F16, F17.

## Acceptance Criteria

- [ ] Every **fixed** string and attribute above is present exactly; the old strings they replace are gone from the four files (`grep` each).
- [ ] `grep -n "verdict" app/report.js` prints nothing; layer-rule greps 5 and 7 print nothing.
- [ ] The community screen's actions row is still inside 780 px at 360 wide; the map legend's bottom edge is still inside 780 px on `#/map` at 360 × 780.
- [ ] Gate: lint, unit, build and sizes green. Browser tests red **only** because a string in this table moved are listed in the report, not fixed; anything else red is yours.
- [ ] Nothing under `tests/` edited.
