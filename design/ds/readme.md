# Crosscheck design system

Design system for **Crosscheck**, an offline-first web app built for the CDU IT Code Fair 2026 Data Innovation Challenge (theme: Remote Connectivity), team DIC005. Written 2026-09-12 as step 1 of `uploads/brief.md`. Step 2 (the three screens) is not part of this folder.

## Context

Crosscheck puts four published claims about mobile coverage side by side for each of the 96 BushTel Major and Minor communities in the Northern Territory, computes the best available connection path, tests it against what each service present in the community requires (telehealth video, school video meeting, myGov and banking, voice and SMS), and shows where the sources disagree and who should act. It ships as one self-contained HTML page under 1 MB (data pack under 300 KB) that opens in flight mode and passes phone to phone by QR code. No server, no tiles, no fonts, no network.

Three screens: **Community** (search, header, what exists here, agreement headline and publisher rows, service verdicts with reasons, who does what), **Map** (NT outline with 96 points coloured and shaped by verdict, filter tabs, legend), **Share** (QR code, data-pack date and size, two buttons, plain statement).

Users: an NT Government (DCDD) analyst on a laptop in Darwin; a clinic nurse, teacher or council worker on a phone in the community; a judge on a phone in flight mode. Three of the four judges work for the department that would act on the output.

Ethics shape the design: the data is about First Nations communities. A community is never shown as a deficit; the unit of failure is the service and the path, with the responsible party named. Predicted is never presented as measured.

## Sources

- `uploads/PRD.md`: the product requirements (sections 2, 4.2, 5, 6, 7 drive this system).
- `uploads/brief.md`: the two-step design brief; this folder answers step 1.
- `uploads/DESIGN_CAL.md`: the starting rulebook, a public design analysis of cal.com from VoltAgent/awesome-design-md (MIT). Its proprietary identity (name, wordmark, Cal Sans, badge pastels, marketing components, dark surfaces) was removed; its neutral palette, near-black action, type scale, 4px spacing, radius scale, elevation table, responsive and touch rules, do's and don'ts and iteration guide were kept and adapted.
- No Figma, no codebase, no logo was provided. **There is no logo or wordmark**: wherever a mark would go, the name "Crosscheck" is set in plain type (`--text-title-sm`).

## Index

- `design/DESIGN.md`: the rulebook (front matter with every token, then Overview, Colors, Verdicts, Typography, Layout, Elevation, Shapes, Components, Content rules, Do's and don'ts, Responsive behaviour, Iteration guide, Known gaps, Attribution).
- `design/tokens.json`: every colour, verdict, type, spacing, radius and size token.
- `design/styles.css`: imports `design/tokens/colors.css`, `design/tokens/typography.css`, `design/tokens/spacing.css` and `design/base.css` (focus ring, link colour, button reset).
- `styles.css` (root): the compiler's entry point; imports `design/styles.css`.
- `design/readme.md`: short pointer for the app repo's `design/` folder.
- `guidelines/`: 18 specimen cards (Colors, Type, Spacing, Brand groups).
- `components/`: React primitives, one directory per concern, each with a card.
- `SKILL.md`: agent skill wrapper.
- `thumbnail.html`: homepage tile.

## Components

Built exactly to brief item 5, default and pressed states only. Namespace `CrosscheckDesignSystem_469d70`.

- `components/core/`: **Button** (primary, secondary, disabled), **Chip**, **VerdictBadge** (plus the `VERDICTS` table: word, glyph, shape), **Figures** (prose with mono figures), **SourceLine**.
- `components/navigation/`: **TopBar** with **OfflineChip**, **FilterTabs**, **Footer**.
- `components/search/`: **SearchInput** with **ResultRow**.
- `components/community/`: **CommunityHeader**, **AgreementHeadline**, **PublisherRow** with **KindChip**.
- `components/services/`: **ServiceRow** (collapsed, pressed, expanded with sources), **AssumptionNote**.
- `components/map/`: **NtMap** (inline SVG, verdict-shaped points, selected ring; exports `project`), **MapLegend**.
- `components/share/`: **ShareCard**, **QrCode** (inline SVG; `qr.js` is a small byte-mode encoder, versions 1–10, levels L/M).

Intentional additions beyond the brief's list: `Figures` and `SourceLine` (the brief's rules "every figure in mono" and "every value shows its source and date" needed a reusable primitive), `VerdictBadge` and `KindChip` (named in the brief as parts of rows), `QrCode` and `MapLegend` (named as parts of the share card and map).

No UI kit or screens exist yet; the brief defers them to step 2.

## Content fundamentals

- **Voice:** matter-of-fact, third person about the data, second person only in instructions ("Search 96 communities"). No persuasion, no praise, no reassurance. No metadiscourse.
- **Casing:** sentence case everywhere, including buttons, tabs, chips and badges. "Share this app", not "Share This App".
- **Punctuation:** no exclamation marks. Middle dot (·) separates source and date. ISO dates `2026-09-30`. Figures keep units and published precision: `665 ms`, `0.06 km`, `2,259`.
- **Emoji and icons:** none. The four verdict glyphs (● ▲ ■ –) are the only symbols and always sit beside their word.
- **Deficit language:** never "vulnerable", "disadvantaged", "at-risk", "underserved". Describe the service and the path: "Telehealth video fails on satellite here", not "this community lacks access".
- **Provenance:** every value that came from somewhere shows its source and date beneath it (SourceLine), or one tap away (ServiceRow expanded).
- **Gaps:** empty reads "Not recorded"; unverified reads "Unverified". Never blank, "N/A" or "unknown".
- **Predicted:** always labelled "carrier prediction" in words next to the kind chip.
- **Order:** what exists here (services, WiFi hours, licensed mast) before what fails.
- **Addressees:** who does what names them: "Carrier: publish measured latency for this site." "DCDD: confirm the clinic's enterprise link technology."
- **Honesty line:** "Crosscheck does not measure signal." appears in the footer and on the share card.

Examples of on-brand copy: "3 of 4 sources say covered", "Latency 665 ms on satellite vs 100 ms required", "Assumption: could work over Telstra 4G if latency is under 100 ms. No measurement exists here.", "Licensed mast, no coverage map".

## Visual foundations

- **Colour:** white canvas `#ffffff`, near-black ink and primary `#111111`, body `#374151`, muted `#6b7280`, hairline `#e5e7eb`, grey blocks `#f5f5f5` / `#f8f9fa`. One accent: the near-black, for the primary button, links, focus rings, selected tab and selected map point. Chromatic colour exists only as verdicts: Works green `#157a3a` on `#e6f4ea`, Degraded ochre `#8a5a00` on `#f6ead0`, Fails red `#b42318` on `#fbe4e0`, No data grey `#596270` on `#f3f4f6`. All text colours reach 4.5:1 on white and on their fill. No dark surfaces anywhere.
- **Type:** system sans stack for words, system mono stack for every figure. Weights 400 and 600 only; largest size 22px (community name, agreement count). No display face, no web fonts, no letter-spacing except -0.3px at 22px.
- **Spacing:** 4px base; 4 / 8 / 12 / 16 / 24 / 32 / 48. Rows are 12 × 16 padded; value-to-source gap 4; sections 24 apart and marked by a hairline.
- **Layout:** one column, designed at 360px, content max 640px centred on wider screens, 16px screen padding. No breakpoint changes information order; a laptop sees the phone layout with wide margins. The collapsed verdict list fits a 640px-tall viewport.
- **Backgrounds:** flat white. No images, no illustrations, no patterns, no gradients. The map (inline SVG outline with land `#f8f9fa`) and the QR code are the only graphics.
- **Depth:** hairlines (1px `#e5e7eb`, 1px `#f3f4f6` inside bounded sections), flat grey blocks, and the 3px ochre left rule on the assumption note. No drop shadows, no blur, no transparency.
- **Corners:** 4px badges and chips of the kind sort, 6px result list, 8px buttons and input, 12px share card, pill for chips. Map points are geometric shapes, not rounded boxes.
- **Cards:** the share card is the only card: white, 1px hairline, 12px radius, 24px padding. Everything else is rows separated by hairlines.
- **Hover:** not designed. Default and pressed only.
- **Press:** primary button darkens to `#242424`; rows, tabs and secondary buttons fill `#f5f5f5`; chips fill `#e5e7eb`. No scale, no shadow change.
- **Focus:** 2px solid ink outline, 2px offset, on every focusable element (`:focus-visible` in `design/base.css`).
- **Animation:** none. Expansion of a service row is an instant state change.
- **Touch:** 44px minimum on every button, tab, row, tappable chip and map point; inputs and buttons are 44px tall; top bar 56px.
- **Imagery:** none. Real community names are used; no photos, no stock, no invented places.

## Iconography

None. No icon font, no SVG icon set, no PNG icons, no emoji. Wherever an icon would normally go, the word goes instead ("Offline", "Search 96 communities", "Share this app"). The only symbols are the four verdict glyphs, always paired with their word, and their geometric counterparts as map point shapes. The two inline-SVG graphics (map outline, QR code) are data, not decoration.

## Attribution

Adapted from the Cal.com design analysis in VoltAgent/awesome-design-md, MIT licence.
