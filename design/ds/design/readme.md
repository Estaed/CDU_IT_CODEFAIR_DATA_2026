# design/

Step 1 output of `brief.md`: the Crosscheck design system, adapted from the Cal.com design analysis in VoltAgent/awesome-design-md (MIT).

- `DESIGN.md`: the rulebook. Same section structure as the source, with Verdicts and Content rules as their own sections. `{token.refs}` throughout; hex only in the front matter.
- `tokens.json`: every colour, verdict, type, spacing, radius and size token.
- `styles.css`: imports `tokens/colors.css`, `tokens/typography.css`, `tokens/spacing.css` (CSS custom properties on `:root`) and `base.css` (focus ring, link colour, button reset).
- The full readme (context, source, index, content fundamentals, visual foundations, iconography) is the project root `readme.md`; component recreations are in `components/`.

Iconography: none. Fonts: system stack, no web fonts. Screens: step 2, not yet produced.
