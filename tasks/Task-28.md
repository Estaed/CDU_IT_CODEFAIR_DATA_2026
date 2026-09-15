# Task-28: Install as a real home-screen app (tactics from the Calisthenics app)

> **Execution:** agent `claude-worker` · effort `medium` · plan mode **no**
> *Why:* head tags, a manifest and three generated icons; every criterion is a static check on `dist/` plus the existing smoke test. Whether a phone offers "Install" is Tarik's manual check.

**Lane**
- OWNS: `app/index.html` (the `<head>` only), `app/manifest.webmanifest`, `app/sw.js` (the precache file list only), `scripts/build_app.py` (the host-files step only: manifest templating and icon drawing), `tests/test_build.py` (the manifest assertions in `test_host_files_copied`, and appended tests), `tests/browser/test_smoke.py` (append only)
- MUST NOT TOUCH: `app/app.js`, `app/store.js`, `app/transfer.js`, `app/nearby.js` (Task-24, running beside this task), `app/app.css`, `app/qr.js`, `app/layers.css`, `pipeline/`, `scripts/gate.py`, `design/`
- GATE: `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` from the project root
- DEPENDS ON: Task-26

## Objective

Tarik's Calisthenics app (`estaed.github.io/Calisthenics-App`) installs on a phone as a real app;
Crosscheck does not, measured 2026-09-15: `app/index.html` has no `<link rel="manifest">`, the
manifest has no icons and no colours, and there are no Apple home-screen tags. Chrome therefore
offers only a bookmark-style shortcut and iPhone shows a screenshot as the icon. After this task
the Pages address installs as a standalone app with a Crosscheck icon on Android and iPhone.

What the Calisthenics app does that is taken here: manifest link, `theme-color`, manifest icons
at 192 and 512 pixels, `display: standalone`, `apple-mobile-web-app-capable`,
`apple-mobile-web-app-title`, a precached manifest in the service worker. What is not taken: its
service-worker unregister-and-re-register on every load and its `?v=` query (Task-26's build-hash
cache already updates the page), and its Turkish app name.

## Execution Guide

- **Head tags** in `app/index.html`: `<link rel="manifest" href="manifest.webmanifest">`,
  `<meta name="theme-color" content="__THEME_COLOR__">`, `<link rel="icon" type="image/png"
  sizes="192x192" href="icon-192.png">`, `<link rel="apple-touch-icon" href="apple-touch-icon.png">`,
  `<meta name="mobile-web-app-capable" content="yes">`, `<meta name="apple-mobile-web-app-capable"
  content="yes">`, `<meta name="apple-mobile-web-app-title" content="Crosscheck">`,
  `<meta name="apple-mobile-web-app-status-bar-style" content="default">`, and `viewport-fit=cover`
  added to the existing viewport meta.
- **Manifest** `app/manifest.webmanifest`: `id` and `start_url` and `scope` `./`, `name` and
  `short_name` `Crosscheck`, a one-line `description`, `display` `standalone`, `theme_color` and
  `background_color` `__THEME_COLOR__`, `icons`: `icon-192.png` and `icon-512.png` each listed twice,
  once with `purpose` `any` and once with `purpose` `maskable`.
- **Build** (`scripts/build_app.py`, host-files step): read `--color-canvas`, `--color-ink` and
  `--color-on-primary` from `design/ds/design/tokens/colors.css` (parse the custom property, never
  retype the hex); replace `__THEME_COLOR__` with `--color-canvas` in `dist/index.html` and in
  `dist/manifest.webmanifest`; draw with Pillow (12.3.0, installed through matplotlib, already in
  `uv.lock`) `dist/icon-192.png`, `dist/icon-512.png` and `dist/apple-touch-icon.png` (180 by 180, RGB,
  no alpha): a full-bleed `--color-ink` square with one bold check mark in `--color-on-primary`,
  drawn as a thick polyline with round ends, kept inside the central 60 percent so a maskable crop
  never cuts it. Draw at 4 times the size and downsample with `LANCZOS` for clean edges. Keep the
  PNG bytes deterministic (no timestamp chunks).
- **Service worker** `app/sw.js`: add `./manifest.webmanifest`, `./icon-192.png`, `./icon-512.png`
  and `./apple-touch-icon.png` to the precache list. Nothing else in `sw.js` changes.
- `dist/index.html` must still work from `file://` with no console error: the links point at files
  that sit next to it in `dist/`.

## Acceptance Criteria (DoD)

- [ ] `PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py` exits 0.
- [ ] `tests/test_build.py`: `dist/index.html` contains the manifest link, the apple-touch-icon link, `apple-mobile-web-app-capable` and a `theme-color` meta whose content equals `--color-canvas` parsed from the tokens; no `__THEME_COLOR__` remains in `dist/index.html` or `dist/manifest.webmanifest`; the dist manifest parses with `name` `Crosscheck`, `start_url` `./`, `display` `standalone`, both colours equal to `--color-canvas`, and icons 192 and 512 each present with purpose `any` and with purpose `maskable`; every icon `src` exists in `dist/` and Pillow reads its size as declared; `apple-touch-icon.png` is 180 by 180 in mode `RGB`; the centre pixel of `icon-512.png` differs from its corner pixel and the corner pixel equals `--color-ink`; building twice gives byte-identical icons; `dist/sw.js` lists the manifest and the three icons.
- [ ] `tests/browser/test_smoke.py` (appended): `dist/index.html` over `file://` still records zero non-`file:` requests and no console errors, and `document.querySelector('link[rel="manifest"]')` is present.
- [ ] Not gated, Tarik's manual check on the Pages address after deploy: Chrome on the S24 offers "Install app" and the installed icon opens without an address bar; on an iPhone, Share then Add to Home Screen shows the Crosscheck icon and opens full screen.

## Status

Not started.
