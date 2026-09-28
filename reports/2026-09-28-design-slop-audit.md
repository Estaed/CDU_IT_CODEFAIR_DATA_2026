# Design audit: what read as template output, and what changed (2026-09-28)

Tarik asked for the Tarik Base design to replace the original look (light by default, dark on
a toggle, the original kept) and for anything that reads as AI "slop" to be named, researched
and fixed. This file is the record. The original look is at the git tag `design-original` with
screenshots in `design/original/shots/`; the new one is in `design/shots/`.

## Sources

S1 was read directly on 2026-09-28 (raw SKILL.md). The rest were collected by a research
sub-agent the same day and are cited as it reported them; open them before quoting one.

- **S1** Anthropic, `frontend-design` skill, github.com/anthropics/skills (skills/frontend-design/SKILL.md).
  Names five default looks: warm cream (near `#F4F1EA`) with a high-contrast serif and a
  terracotta accent (near `#D97757`); near-black with one bright acid-green or vermilion accent;
  broadsheet hairlines with zero radius; the SaaS card kit ("content chopped into identical
  rounded cards, one border-radius on everything"); template chrome (tracked all-caps eyebrows,
  middle-dot meta strings, `WORD — fragment` labels, tinted near-black for black, "a monospace
  face for small data labels", `→` on buttons). Also: "All traits are legitimate for some
  briefs … Where the brief pins down a visual direction, follow it exactly."
- **S4** Adrian Krebs, "Scoring Show HN submissions for AI design patterns", 2026-04-20
  (adriankrebs.ch/blog/design-slop): icon-topped identical cards are the most frequent pattern.
- **S8** NN/g, "Visual indicators to differentiate items in a list", 2016: colour plus shape.
- **S9** NN/g, "Accordions on desktop", 2023; **S12** GOV.UK Design System, Details: do not
  fold what most readers need.
- **S11** GOV.UK task list; **S13** Agriculture Design System (AGDS-based) status badge: plain
  status in dense lists, colour only where action is needed.
- **S14–S17** Datawrapper (Lisa Charlotte Muth) on colour, colour-blind readers, tables and
  maps: grey by default and colour for what matters; do not draw rank as size.
- **S18** Stephen Few, "Common pitfalls in dashboard design", 2006: numbers need a comparison.

## Findings in the original app, and what was done

| # | What read as template | Source | Done |
|---|---|---|---|
| 1 | Numbers in a mono face inside sentences ("All `4` sources", "`495  KB`") | S1 template chrome | Numbers now take the sentence's own face with tabular figures; mono is kept only for the report line a person copies or pastes |
| 2 | A "Works offline" pill in the top bar that looks tappable | S1, S4 pill badge | Now quiet caption text; the words stay (a smoke test reads them) |
| 3 | "▶ Why" fold repeated on each of 96 Fix first rows | S9, S12 | The one-sentence reason is shown under each row; no fold |
| 4 | Twenty red tinted "Fails" pills stacked down Fix first | S11, S13, S18 | Dense lists carry glyph + word only; the outlined pill stays on the four community answers |
| 5 | Verdict pills with fill, outline and coloured text at once | S13 | Outline and word in the status colour, no fill |
| 6 | Browser triangles in three sizes on nine different folds | consistency | One chevron marker after the words on every fold, turning when open |
| 7 | "Report here" button beside a bare "▶ Share" fold title | consistency | Share reads as the second button of the pair |
| 8 | Search placeholder cut to "Search 96 communiti…" by a wide button | defect | Location button in the label size; the whole placeholder shows at 360 |
| 9 | All 96 map points in one ink colour, rank shown only by size | S14 | Top ten in the accent, 11–30 ink, the rest grey |
| 10 | Pill chips and a pill segmented control; one radius everywhere | S1 card kit | Radius by role: 12 buttons and controls, 16 cards, 8 chips, pills only for status |
| 11 | `●` and `◐` drawn at half size by Android's fallback font (seen on the emulator, Chrome) | device check | The verdict glyphs are drawn in CSS with the map's own point geometry; the characters stay in the markup |
| 12 | A two-line underlined accent link, "Check the evidence · Priority #30 of 96 · …" | consistency | A plain row with a chevron into Fix first; same words |

Checked on 2026-09-28 at 360 × 780 and 390 × 844 in headless Chromium, both themes, and on the
Android emulator (Chrome, 1080 × 2400): toggle, stored choice across a reload, browser bar
colour following the theme. The full gate stayed green after every pass.

## Named, not changed (each needs Tarik's call)

- **The 2×2 icon-topped service cards** on the community screen are the single strongest
  template tell left (S4, S1 card kit). Blueprint fixes them since Task-53 ("individual
  two-column cards whose static icons identify the service"), so they stay. Recommendation:
  four hairline rows, each `service · glyph + word · one-line reason`, no card chrome.
- **Point size by rank** on the map (Task-48 in Blueprint). S16 warns rank drawn as size reads
  as a quantity. Recommendation: one point size, rank as the number on the top ten only.
- **Map labels that collide with points** (Woodycupaldiya, Orrtipa-Thurra at zoom 1): the
  label placement is in `declutter`, not in the theme; a pass that avoids points is app code.
- **Middle-dot meta strings** ("Major · Top End · 2,259 people", the footer, the build line):
  S1 template chrome, mild. Copy is PRD-bound; left as written.
- **Tarik Base itself**: its dark mode (graphite with one vermilion accent) is S1's second
  default look, and a serif display over a sans body is half of S1's first. Mitigations in
  place: light is the default, the canvas is neutral (`#F4F4F5`, not cream), the accent is
  saturated ember, not clay `#D97757`, and the serif is used only for the brand, the home
  question and a community's name. S1 also says a pinned brief wins, and Tarik Base is the
  pinned brief here. Worth a look in the base language, not in this app. (Superseded the same
  evening by round 2 below.)

## Round 2, the same evening: Tarik's second pass

Tarik kept the 2×2 cards (so that item above is closed), asked for the page to breathe ("like
everything was stuffed into a Word document"), for black and orange that feel original, for a
better map idea, and for eight concrete fixes. Three research sub-agents read the web the same
day; their sources are cited as they reported them (S1 was read directly, the NT colours were
checked directly on nt.gov.au and pmc.gov.au).

**Why the pages felt crammed.** `design/screens/screens.css` gives every `.section` a
full-width hairline and 12 px above and below it, so the space between groups equalled the
space inside them. Refactoring UI ("start with too much white space", fewer borders), NN/g
(proximity 2020, common region 2020, cards vs lists 2016), Apple HIG (grouped lists), Material 3
("use full-width dividers sparingly"), GOV.UK (section breaks are space; details only for what
some users need) and the NHS App (stacked card links, expanders matching cards) agree on: space
between groups, containers rather than lines, inset dividers between rows. **Done:** no
full-width rule in the scrolling body; a 4 / 12 / 24–32 rhythm; the community's five folds and
lines as one grouped card of rows; community reports as its own card; Fix first and the map's
list as grouped lists; the first-screen budget at 360 × 780 still holds (actions row ends at
748, 724 and 748 for the three test communities).

**Why black and orange read generic, and the fix.** Tarik Base's light greys are Tailwind's zinc
scale verbatim (`#F4F4F5`, `#E4E4E7`, `#71717A`, `#18181B`) with orange-700, green-700 and
amber-700; its dark mode is S1's "near-black with a single vermilion accent"; the ember accent
sat between Crosscheck's amber and red verdicts. Braun, Teenage Engineering and the Bloomberg
Terminal show that no hex is ownable, but a system is: orange with one job, a chosen neutral, a
signature. The subject has its own palette: ochre, black and white are the Northern Territory's
official colours since 17 February 1964 (flag ochre PMS 159). **Decided by Tarik:** Crosscheck
ships "Territory" (ochre only on the primary action and the brand's tick, gold for Degraded,
sans headings, flag black in dark; `design/deviations.md`); Tarik Base itself moves to an
"Instrument" v4 (a chosen housing grey, orange as a lamp) after the submission, as its own job.

**The map.** Sources: Matthew Ericson (NYT, "when maps shouldn't be maps", 2011), Datawrapper
(no zoom on purpose, mobile locator maps, crop plus inset, cartograms), ABC News equal-hex
electorate maps (2022, 2025), NPR hex tile maps (2015). The strongest alternative was regional
small multiples; Tarik chose instead to add detail and a heat surface from the data already in
the pack. **Done:** the carriers' own 4G claims (ACCC MIR 2025, three layers already in the
pack) drawn under every lens as one faint ochre surface that deepens where carriers overlap,
explained in the legend; rank numbers now scale with their discs (they drifted out when
zoomed); the ± buttons are smaller; "Tap a community." is a hint, not a field-like box.
Later the same evening (Tarik left the rest to Eko): every dot is one size except the numbered
top-ten discs, the tier told by ink or grey (S16: rank drawn as size reads as a quantity); the
label placer now also counts the dots a name would cover and takes the position that covers
fewest, among those that already cleared other labels and the top-ten discs (two dense spots,
Woodycupaldiya and Orrtipa-Thurra, still touch a dot, masked by the label's halo). The report's
Figure 2 was redrawn in the same language (ochre claims, ink numbered top ten, greys, one dot
size) and Figure 1 in the Territory verdict colours; both were swapped into the Word report,
whose ten pages and page breaks are unchanged except one line moving from page 7 to page 8.

**Other fixes in round 2.** Report here gets Share's chevron and becomes the screen's one
primary action; the verdict badges of a card row share one baseline; Filter by action is one
ordered list with a check and a count per action instead of wrapped chips; the hard offset
shadow of Tarik Base's feature card is not used (Impeccable bans it outside a neobrutalist
world, and every card here is peer data).
