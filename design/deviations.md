# Crosscheck on Tarik Base: project layer and deliberate breaks

Since 2026-09-28 (Tarik's decisions) the app wears Tarik Base's shapes, spacing, states and
toggle, in a palette of its own: **Territory**, the Northern Territory's official colours
(ochre, black and white since 17 February 1964; flag ochre PMS 159, nt.gov.au). `app/theme.css`
re-points the design system's tokens, light by default and dark on the toggle in the top bar; the
component rules a token swap cannot reach sit at the end of `app/app.css`. The look before that
day is kept at the git tag `design-original` and in `design/original/`. The research behind every
choice is in `reports/2026-09-28-design-slop-audit.md`; the palettes that were compared are in
`design/directions/`.

## Project layer

- **Accent:** NT ochre, `#CB6015` light (black text on it, 4.6:1) and `#E07A2E` dark (black
  text, 7.0:1). It marks the one primary action on a screen and the brand's tick, nothing else:
  not map points, chips, links or the current tab. In light mode it is never text (4.0:1).
- **Neutrals:** canvas `#F4F4F4`, cards `#FFFFFF`, ink `#141414` in light; flag black `#000000`,
  cards `#151515`, ink `#EDEDED` in dark.
- **Verdicts:** Works green, Fails red, and Degraded **gold** (`#7A5C00` / `#E8C547`), moved off
  amber so it never reads as the ochre accent beside it.
- **Type:** one sans, the phone's own, heavy and tight for names; numbers in the same face with
  tabular figures; mono only for the report line a person copies or pastes.
- **Map:** the carriers' 4G claims as one faint ochre surface under every lens (the pack's three
  coverage layers drawn once more, overlapping, so shade deepens where more carriers claim); in
  dark mode the surface is a light grey, because faint ochre on black reads as brown. Every dot
  is one size except the numbered top-ten discs; the tier is told by ink or grey.
- **Report figures:** `docs/report/figures/` draw in the same palette and the same map language.
- **Illustration tier:** none. **App icon:** the double check in ink on the light canvas.

## Breaks from Tarik Base

| Rule in Tarik Base | What Crosscheck does | Why |
|---|---|---|
| Ember accent `#D4400A` / `#FF5A1F` on the action, the tab, the key number and links | NT ochre on the primary action and the brand's tick only | Ember sat between the amber and red verdicts; ochre is the subject's own colour and has one job (Braun's rule, research round 2) |
| Neutral zinc greys (`#F4F4F5`, `#18181B` …) | `#F4F4F4` / `#141414` light, flag black `#000000` dark | Tarik Base's greys are Tailwind's zinc scale verbatim, the template default; the dark mode was Anthropic's "near-black with one vermilion accent" |
| Serif for display (Newsreader) | The system sans, bold | No web font can ship, so the serif was a different fallback face on every phone; serif display over sans is half of Anthropic's first default look |
| Mono for numbers | Numbers in the sans with tabular figures; mono only for the copied report line | "A monospace face for small data labels" is template chrome in Anthropic's list, and a mono digit inside a sentence read as a glitch |
| Status pill everywhere | Outlined pill on the four community answers; glyph and word only in dense lists | Twenty stacked red pills made the list shout |
| Feature card with a 4 px hard offset shadow | Not used | A hard offset shadow belongs to a neobrutalist world (Impeccable); every card here is peer data |
| Dark first, follow the system setting | Light by default whatever the phone says; dark on the toggle, remembered | Tarik's call: judges and field staff read it outdoors |
| No pure white in dark mode | QR codes on a white tile with black modules in both modes | Cameras and jsQR read dark on light reliably; an inverted code often fails |
| Inputs: surface-2, no border at rest | A `hairline-strong` border on a card-white field | A borderless field on the canvas has no visible edge |
| Caption 12 px | 13 px | Source lines are read outdoors on small phones |

Carrier toggles under "Highlight and layers" keep the carriers' own colours from `app/layers.css`;
people recognise carriers by them.

Screenshots of every screen in both modes: `design/shots/` (build with `scripts/build_app.py`,
then `.venv/Scripts/python design/shots.py design/shots`).
