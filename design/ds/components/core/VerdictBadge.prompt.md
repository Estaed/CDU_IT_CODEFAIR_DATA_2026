VerdictBadge: shows a service verdict as glyph + word + colour; use it wherever a verdict appears and nowhere else.

```jsx
<VerdictBadge verdict="degraded" />   // ▲ Degraded, ochre on soft ochre
```

`verdict`: 'works' | 'degraded' | 'fails' | 'nodata'. Colour alone or glyph alone is forbidden; the component always renders all three. `VERDICTS` (same file) exposes word, glyph and map shape per key.
