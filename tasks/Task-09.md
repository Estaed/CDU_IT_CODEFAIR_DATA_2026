# Task-09: Share screen, QR, save-as-file, and the host-only PWA files

**Status: DONE** — verified 2026-09-15 (line added 2026-09-17; the verification was recorded in the commit and the Status section only)

> **Execution:** agent `claude-worker` · effort `high`
> *Why:* reference markup `design/screens/share.html`; QR produced at build by `qrcode` (Blueprint spike); criteria are Playwright assertions including an `expect_download`.

**Lane**
- OWNS: `app/app.js` (share renderer), `app/sw.js`, `app/manifest.webmanifest`, `scripts/build_app.py` (additive: QR SVG, sizes, sw/manifest copy), `tests/browser/test_share.py`, `tests/test_build.py` (additive)
- MUST NOT TOUCH: `pipeline/`, `design/`, `tests/browser/test_smoke.py`, `test_community.py`, `test_map.py`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-08

## Objective

Screen 3: the share card with the QR code for `APP_URL`, the data pack's date and size and the
app's size, "Share this app" through the Web Share API with a file fallback, "Save file" that
downloads the page itself, and the plain statement. Plus the two host-only files that make the
Pages copy installable without the HTML ever depending on them.

## Execution Guide

- `scripts/build_app.py`: generate the QR with `qrcode` (version fit, error level M, `border=4`)
  for `APP_URL` from `constants.md`, render it as the same single-path inline SVG as
  `design/screens/assets/qr.svg` (`<svg class="qr" role="img" viewBox="0 0 n n">` with
  `M{x} {y}h1v1h-1z` modules) and place it into the template as a `<template id="qr">`. Write
  `pack_bytes` and, after inlining, the final `app_bytes` into a `<meta name="crosscheck-sizes"
  content="pack=<n>;app=<n>">` (compute app size with the meta present by iterating once). Copy
  `app/sw.js` and `app/manifest.webmanifest` to `dist/`.
- `renderShare()` builds the `.share-card` per the reference: QR from `#qr`, meta lines with the
  pack `built` date and the two sizes in KB (integer division, `KB` unit as on the screen),
  source line `Crosscheck build · <built>`, the two buttons, the statement.
- "Share this app": if `navigator.share` exists and `navigator.canShare({files})` accepts an
  `File([outerHTML], "crosscheck.html", {type: "text/html"})`, share the file; otherwise share
  `{url: app_url}`; otherwise fall through to save. "Save file": create a Blob of
  `document.documentElement.outerHTML` prefixed with `<!DOCTYPE html>` and trigger a download
  named `crosscheck.html`.
- `app/sw.js`: cache-first for `./`, `./index.html`, `./manifest.webmanifest` on install; no
  network fetch except the first load. `app/manifest.webmanifest`: name `Crosscheck`, `display:
  standalone`, `start_url: ./`, no icons (DESIGN.md forbids images; note that install prompts
  without icons are browser-dependent and record it in the task report). Registration in
  `app.js` is guarded: only when `location.protocol` is `https:`, so `file://` never touches it.
- Footer as on the reference.

## Acceptance Criteria (DoD)

- [x] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [x] `tests/test_build.py`: the QR path in `dist/index.html` decodes back to `APP_URL` (use `qrcode`'s matrix for the same text and compare module for module, as `design/screens/README.md` did); the sizes meta matches the actual file sizes; `dist/sw.js` and `dist/manifest.webmanifest` exist.
- [x] `tests/browser/test_share.py` (marker `browser`): `#/share` renders one `.qr`, meta text containing the pack `built` date and both `KB` figures inside `.fig`, two `.button`; clicking `Save file` triggers a download (`page.expect_download`) whose content starts with `<!DOCTYPE html>` and contains `id="pack"` exactly once.
- [x] Over `file://`, `navigator.serviceWorker.register` is never called (assert by evaluating a flag `window.__swRegistered === undefined`).
- [x] Zero non-`file:` requests and no console errors on `#/share`.
- [x] `grep -nE "#[0-9a-fA-F]{3}|[0-9]px" app/app.css app/app.js` prints nothing.

## Status

DONE 2026-09-15 (otopilot, lane gate and main gate green at `b7c3234`; 7 build tests, 3 share browser tests). Bee notes: the build reads `APP_URL` from the pack (which reads `constants.md`), the QR and sizes meta are inserted by text at `</head>` and the pack marker because `app/index.html` was outside the lane, the manifest link is added by script over `https:` only, and nothing was exercised over `https:` since Pages is not enabled. Manifest has no icons (DESIGN.md), so the install prompt is browser-dependent. review-visual pending.
