# Tarik Base on Crosscheck: deliberate breaks

Branch `tarik-base`, 2026-09-28. The theme is `design/tarik-base/theme.css`, loaded last by
`scripts/build_app.py`; it only re-points the design system's custom properties and restyles a few
components. Behaviour, markup and every test are unchanged (`tests/test_build.py` and
`tests/browser/`: 148 passed).

| Rule in Tarik Base | What Crosscheck does | Why |
|---|---|---|
| Manrope, Newsreader, JetBrains Mono | Named first in the stacks, but the app ships no font files; it falls back to Segoe UI / system-ui, a system serif (Palatino, Georgia) and Consolas / ui-monospace | The app must work offline in one file under 1 MiB; it is already at ~1.0 MB, so embedding three font families does not fit |
| Dark is the default | Dark by default, light when the phone asks for light (`prefers-color-scheme`) | No in-app toggle exists; the OS setting is the switch |
| No pure white in dark mode | QR codes sit on a white tile with black modules in both modes | Phone cameras and jsQR read dark-on-light reliably; an inverted QR often fails, and QR transfer is a core feature |
| Chart colours for data | Carrier coverage layers keep the carriers' own colours (Telstra blue, Optus teal, TPG purple) from `app/layers.css` | People recognise carriers by those colours |
| Status colours are status only | Verdict badges use success / warning / danger for Works / Degraded / Fails | That is their meaning; no other use of the status colours was added |

Screenshots of every screen in both modes: `design/tarik-base/shots/` (rebuild with
`uv run python scripts/build_app.py`, then `uv run python design/tarik-base/shots.py`).
