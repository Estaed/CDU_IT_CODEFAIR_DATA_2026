# Task-35: Report here — the community's own evidence, on the phone, shared by choice

> **Execution:** agent `claude-worker` (opus) · effort `high` · plan mode **no**
> *Why:* 2026-09-16. A new file with a byte-exact line format, IndexedDB and a privacy
> contract: a wrong output is expensive to notice, so Opus. The "how" is below. Codex is at
> 100 %.

> **Lane:** OWNS `app/report.js` (new), `app/store.js` (a `reports` object store beside the
> pack), in `app/app.js` only the `Report here` button's handler, the `?report` query, the
> `Reports from here` line, the `Add reports` fold and the `Copy evidence` button (all inside
> the community render), `app/app.css` (report rules), `scripts/build_app.py` (insert
> `report.js` before `app.js`), `tests/browser/test_report.py` (new), `tests/test_build.py`
> (order and the layer-rule greps), this file · MUST NOT TOUCH the map functions, `transfer.js`,
> `scan.js`, `pipeline/`, `design/`, the pack · GATE `PYTHONUTF8=1 .venv/Scripts/python
> scripts/gate.py` · DEPENDS ON Task-34

## Why

PRD §1: "a community cannot prove its own situation". Every source in the pack is a
publisher's claim; the community's own word is missing, and the open measurement sets are
empty here (Ookla: 11 of 50 communities with zero tests in 4.5 years, `reports/2026-09-12-
arena-measured.md`). Report here is the deferred D2 done with no network: the person says
what their phone is doing, the browser adds what it already knows, the record stays on the
phone and travels only by choice, as one line the mesh text's channels already carry.

## Contract

1. **The line** (CLAUDE.md Part 2, seam "Report line"):
   `CR1|<bushtel_id>|<yyyymmddhhmm UTC>|<status>|<carrier>|<effectiveType>|<rtt>|<downlink>|<lat>,<lon>`
   with `status` in `works|slow|none`, `carrier` in `telstra|optus|tpg|other|-`, the three
   connection fields from `navigator.connection` when present else `-` (rtt an integer of
   ms, downlink with one decimal), position rounded to two decimals or `-`. ASCII only, at most
   200 bytes. `window.CrosscheckReport.format(record)` and `.parse(line)` are inverses;
   `parse` returns `null` for any line that does not match exactly (wrong prefix, wrong field
   count, unknown status, a community id not in the pack).
2. **The form.** `Report here` (Task-34's stub) opens `div.report-form` under the actions:
   three `button.report-form__status` (`Works`, `Slow`, `No connection`), a carrier row of
   five chips (`Telstra`, `Optus`, `TPG`, `Other`, `Don't know`), a checkbox
   `label.report-form__location` reading `Include my position (about 1 km)` unchecked by
   default, and `button.report-form__save` reading `Save report`. Save is disabled until a
   status is chosen. On save: read `navigator.connection` if present; if the checkbox is
   checked ask `navigator.geolocation.getCurrentPosition` once (refused or timed out after
   8 s: position `-`, no error shown); store; show the line in `pre.report-line` with
   `button.report-line__copy`, `a.report-line__sms` (`sms:?body=<encoded line>`) and one
   static QR of the line (`CrosscheckQR`, level M) in `svg.report-line__qr`.
3. **Storage.** `CrosscheckStore` gains `saveReport(line)`, `reportsFor(bushtelId)` and
   `importReports(text)` (one line per row, keeps well-formed `CR1` lines, drops the rest,
   deduplicates on the whole line, returns the count kept). Reports live in an object store
   `reports` keyed on the line, in the same database as the pack; the pack's own validation is
   untouched.
4. **The count line.** Under the sources fold, `p.reports-line` reading
   `Reports from here: <n>` followed, when `n > 0`, by ` · <w> works, <s> slow, <z> no connection · latest <d Mon yyyy>`.
   `n = 0` reads `Reports from here: none yet`. No `.verdict-badge` text on the page changes
   when reports exist: `grep -n "verdict" app/report.js` prints nothing.
5. **Add reports.** `details.reports-fold` (`summary` `Add reports`) with a `textarea` and
   `button.reports-import` reading `Add`; after Add, the count line updates and
   `p.reports-import__result` reads `Added <k> of <m> lines`.
6. **Copy evidence.** `button.evidence-button` reading `Copy evidence` writes to the clipboard
   one plain-text block: the community name and id, one line per service `<name>: <verdict
   word> — <reason> (<source>, <date>)`, one line per publisher line, then every stored
   report as its line, then the sentence `Crosscheck does not measure signal; reports are what
   people in <name> recorded on their own phones.` Assembled from pack strings and stored
   lines only.
7. **Privacy.** Nothing is sent. `tests/test_build.py`'s layer-rule grep for runtime requests
   includes `report.js`; `getUserMedia` is not in `report.js`; `navigator.geolocation` appears
   only inside the save handler and only behind the checkbox.
8. **Build order.** `vendor/jsQR.js`, `qr.js`, `scan.js`, `transfer.js`, `store.js`,
   `report.js`, `app.js`.

## Tests (`tests/browser/test_report.py`, marker `browser`)

`test_format_parse_roundtrip_and_limit` (twenty synthetic records including the longest
possible fields: every line ≤ 200 bytes UTF-8, parse(format(r)) equals r);
`test_parse_rejects_malformed` (wrong prefix, 8 fields, unknown status, unknown id);
`test_save_report_no_request` (Wadeye, status Slow, no position: the line appears, IndexedDB
holds it, the abort-counting fixture saw zero non-`file:` requests, every `.verdict-badge`
text equals what it was before); `test_second_page_import_counts` (a second page in the same
fixture browser, `Add reports` with that line plus one junk line: `Added 1 of 2 lines`,
`Reports from here: 1 · 0 works, 1 slow, 0 no connection · latest ...`); `test_copy_evidence_text`
(clipboard stubbed by `page.evaluate`: the block contains the four service names, every
stored line and the closing sentence).

## Out of the gate

The real-phone `sms:` handoff and the QR read by a camera app (Tarik's checklist); wording.

## Status

Status: TODO
