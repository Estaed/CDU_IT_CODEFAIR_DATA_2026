# Tarik Base on Crosscheck: project layer and deliberate breaks

Since 2026-09-28 (Tarik's decision) the app wears Tarik Base (TarikOS
`.brain/skills/tasarim/references/DESIGN.md`): `app/theme.css` re-points the design system's
tokens, light by default and dark on the toggle in the top bar; the component rules a token swap
cannot reach sit at the end of `app/app.css`. The design before that day is kept at the git tag
`design-original` and in `design/original/` (screenshots and how to rebuild it).

## Project layer

- **Accent:** the base ember orange, unchanged (`#D4400A` light, `#FF5A1F` dark).
- **Display face:** the phone's own serif (see the first break below).
- **Illustration tier:** none. Real data carries every screen; the map is the only picture.
- **App icon:** the brand mark's double check in ink on the light canvas, drawn at build.

## Breaks from the base

| Rule in Tarik Base | What Crosscheck does | Why |
|---|---|---|
| Manrope, Newsreader, JetBrains Mono | The phone's own faces: system sans, system serif (`ui-serif`, Iowan Old Style, Palatino, Georgia, Noto Serif), system mono; body weight 400, not 500 | The app works offline in one file under 1 MiB with no web fonts (Blueprint); 500 does not exist in every system sans, so it would render as 400 on one phone and 500 on another |
| Mono for numbers | Numbers take the face and size of their sentence with tabular figures; mono only for the report line a person copies or pastes | Anthropic's frontend-design skill lists "a monospace face for small data labels" as template chrome, and a mono digit inside a sentence read as a glitch here (`reports/2026-09-28-design-slop-audit.md`) |
| Status pill everywhere | Outlined pill on the four community answers; glyph and word only in dense lists (Fix first) | Twenty stacked red pills made the list shout; plain status in dense lists is the civic design systems' pattern (same report) |
| Dark first, follow the system setting | Light by default whatever the phone says; dark only when the person taps the toggle, remembered on that phone | Tarik's call, 2026-09-28: judges and field staff read it outdoors |
| No pure white in dark mode | QR codes sit on a white tile with black modules in both modes | Phone cameras and jsQR read dark on light reliably; an inverted code often fails, and QR transfer is a core feature |
| Chart colours for data | Carrier coverage layers keep the carriers' own colours from `app/layers.css` | People recognise carriers by those colours |
| Status colours are status only | Works, Degraded and Fails use success, warning and danger, as outlined pills with a glyph and a word | That is their meaning; colour is never the only signal |
| Inputs: surface-2 fill, no border at rest | Inputs keep a `hairline-strong` border on a surface-1 fill | A borderless `#EFEFF1` field on a `#F4F4F5` canvas has no visible edge |
| Caption 12 px | Captions stay 13 px (the design system's size) | Source lines are read outdoors on small phones |
| Feature card with a hard offset shadow | Not used | Every card on these screens is peer data; none is the one feature |

Screenshots of every screen in both modes: `design/shots/` (build with
`scripts/build_app.py`, then `.venv/Scripts/python design/shots.py design/shots`).
