# Design brief — what Claude Design was asked, in two steps

Written 2026-09-12. Step 1 produces the design system; step 2, run only after step 1's files are
on disk, produces the three screens. Both prompts are pasted verbatim into Claude Design with
`design/DESIGN_CAL.md` and `docs/PRD.md` attached.

---

## Step 1 — design system (paste as the first message, attach DESIGN_CAL.md and PRD.md)

You are producing the design system for **Crosscheck**, an offline-first web app for the CDU IT
Code Fair 2026 Data Innovation Challenge. Read the attached `docs/PRD.md` first (sections 2, 4.2,
5, 6, 7 matter most), then the attached `DESIGN_CAL.md`, a public design analysis of cal.com from
the MIT-licensed VoltAgent/awesome-design-md collection.

**What Crosscheck is.** For each of 96 remote Northern Territory communities it shows: which
services exist there (clinic, school, store, public WiFi and its hours), whether the community's
connectivity can support each service (a verdict: Works / Degraded / Fails / No data, each with
the number that fails and the number required, and the source and date of both), what four
published sources claim about mobile coverage and whether they agree, and who should act. It is
a single self-contained HTML page that works in flight mode, is shared phone-to-phone by QR code,
and must stay under 1 MB including its data. Three screens: Community, Map, Share. Users: an NT
Government analyst on a laptop, a clinic nurse or council worker on a phone in the community, a
judge on a phone in flight mode. Three of the four judges work for the NT Government department
that would act on the output.

**Use DESIGN_CAL.md as the starting rulebook, with these changes:**

1. **Strip proprietary identity.** Remove the Cal.com name, wordmark, logo and every reference to
   Cal.com pages or products. Remove **Cal Sans** entirely (it is licensed to Cal.com); do not
   substitute another display face. Remove the badge pastels (orange / pink / violet / emerald),
   the avatar rules, the product-mockup, testimonial, pricing-tier and hero components, the dark
   featured tier and the marketing section rhythm. Keep everything else that is a rule rather than
   a brand: the neutral palette, near-black primary action, the type scale and weights, the 4px
   spacing scale, the radius scale, the elevation table, the responsive and touch-target rules,
   the do's and don'ts, the iteration guide.
2. **Fonts are the system stack, no web fonts.** The app is offline and byte-budgeted, so there
   is no `@font-face`, no Google Fonts link, no vendored woff2 and no icon font. Sans:
   `system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`. Mono for
   every figure (latency, distance, population, dates):
   `ui-monospace, "SF Mono", Menlo, Consolas, monospace`. Weights available are 400 and 600 only;
   design the hierarchy with size and weight 600, never 700. State this in the typography section
   as a rule with the reason.
3. **Colour has one job: the verdict.** Define four verdict tokens with a text colour, a soft fill,
   a Unicode glyph and a word — Works (green, ●), Degraded (amber, ▲), Fails (red, ■), No data
   (grey, –). Amber must be a dark ochre readable on white in sunlight, not a yellow. Every
   verdict is shown with glyph + word + colour; colour alone is forbidden. Green, amber and red
   may not appear anywhere that is not a verdict (no green buttons, no red headings). The one
   accent for links, the primary button, focus rings and the selected tab is the near-black
   primary from the source; there is no second accent.
4. **Phone-first, dense, sunlight.** Design at 360px wide, one column, content max width 640px
   centred on larger screens; no breakpoint changes information order. Touch targets 44px.
   Hairlines and surface change carry hierarchy; drop the drop shadows, gradients, blur and
   transparency. A community's verdict list must fit a 640px-tall viewport without scrolling.
5. **Add the components Crosscheck needs**, each with token references, default and pressed
   states only: top bar with an offline indicator chip; search input with result rows; community
   header with a source line; service row (service name, reason sentence with monospace figures,
   verdict badge; expands to show sources); publisher row (publisher, kind chip: predicted /
   licensed / listed / portal, says-covered badge, detail, date); agreement headline ("3 of 4
   sources say covered"); assumption note (grey block, 3px amber left rule, for verdicts that rest
   on a stated assumption); chip; filter tabs; inline-SVG map with 96 points using the verdict
   colours and glyph shapes, selected point ring, legend below the map; share card with QR code
   as inline SVG, data-pack date and size, two buttons; footer with attribution lines.
6. **Content rules, in the document.** Sentence case everywhere. No emoji, no icons, no
   exclamation marks. No deficit language: never "vulnerable", "disadvantaged", "at-risk",
   "underserved"; describe the service and the path, not categories of people. Every value that
   came from somewhere shows its source and date beneath it. Empty reads "Not recorded"; an
   unverified value reads "Unverified". Predicted coverage is always labelled as a carrier
   prediction. A community screen shows what exists there before what fails.

**Deliver into `design/`:** `DESIGN.md` (same section structure as the source, adapted as above,
with the verdict table and the content rules as their own sections and an attribution line to
VoltAgent/awesome-design-md, MIT), `tokens.json` (every colour, type, spacing, radius, size token),
`styles.css` importing `tokens/colors.css`, `tokens/typography.css`, `tokens/spacing.css` as CSS
custom properties, and `readme.md` (context, source, index, content fundamentals, visual
foundations, iconography = none). **Do not generate screens or HTML mockups in this step.** Use
`{token.refs}` everywhere in DESIGN.md, never inline hex outside the front matter.

---

## Step 2 — the three screens (paste after step 1's files exist; attach DESIGN.md, tokens.json, PRD.md)

Using `design/DESIGN.md` and `design/tokens.json` exactly, produce the three Crosscheck screens
described in `docs/PRD.md` §4.2, at 360×780 and 768×1024, as static HTML+CSS files under
`design/screens/` (`community.html`, `map.html`, `share.html`) that use only the system font
stack and inline SVG, plus one `README.md` listing per screen every element and the token it uses.

Fill them with **real rows from the PRD's spike data**, not lorem ipsum:

- **Community — Wadeye** (population 2,259; Top End; health centre, school, two stores, police,
  public WiFi Mon–Sat 8am–8pm near the council office, STAND site; road unsealed past the Daly
  River crossing, Dry Season only). Best path: satellite (NBN satellite residual) with Telstra 4G
  predicted. Verdicts: Telehealth video — Degraded (latency 665 ms measured on satellite vs 100 ms
  required, source ACCC MBA 2024-12-05; could work over Telstra 4G if latency is under 100 ms, no
  measurement exists here → assumption note). School video meeting — Degraded. myGov and
  banking — Works. Voice and SMS — Works (Telstra). Publishers: ACCC 2025 Telstra 4G outdoor
  polygon — covered (predicted, 2025-11-10); NT Government 2022 list — covered, macro cell,
  Telstra (listed, 2022-07-04); ACMA licence register — Telstra site at 0.06 km, "74 Perdjert
  Street WADEYE" (licensed, 2026-09-12); BushTel mobile phone row — yes, links to Telstra's map
  (portal, 2026-06-26). Agreement: 4 of 4. Fragility: fibre backhaul (2019 list), wet-season road
  cut. Who does what: carrier — publish measured latency for this site; DCDD — confirm the clinic's
  enterprise link technology.
- **Map** — the NT outline with 96 points coloured by "services failing"; filter tab "Licensed
  mast, no coverage map" selected, showing 11 points; legend: Works 1 · Degraded 58 · Fails 11 ·
  No data 26 for telehealth. Selected point: Baniyala (population 138, East Arnhem; 19 m Telstra
  mast 0.17 km away, licensed; no carrier polygon; not on the 2022 list; telehealth Fails).
- **Share** — data pack dated 2026-09-30, 212 KB, app 810 KB; QR code; buttons "Share this app"
  and "Save file"; the plain statement: "Crosscheck shows what published sources say about a
  community's connectivity and what that allows. It does not measure signal. Every value shows its
  source and date."

Rules: nothing in the screens may use a colour, size or radius that is not a token; no
placeholder text; no images; no external requests; each HTML file must open from disk with no
network and render the same. Report the byte size of each file.
