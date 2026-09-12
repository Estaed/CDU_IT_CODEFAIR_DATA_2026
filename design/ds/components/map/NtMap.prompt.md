NtMap: the Map screen's inline SVG, a simplified NT outline with one point per community in the verdict colour and glyph shape; the selected point gets an ink ring and its name.

```jsx
<NtMap points={communities.map(c => ({ id: c.id, name: c.name, lon: c.lon, lat: c.lat, verdict: c.telehealth }))} selectedId={sel} onSelect={p => setSel(p.id)} />
<MapLegend counts={{ works: 1, degraded: 58, fails: 11, nodata: 26 }} />
```

Points are hit-tested at a 44px-class radius. `project(lon, lat)` is exported for overlays. The outline here is approximate; swap in the pipeline's when it exists.
