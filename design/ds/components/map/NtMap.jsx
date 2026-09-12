import React from 'react';
// Simplified NT outline (lon, lat). Replace with the pipeline's BushTel-derived outline when available.
const MAINLAND = [[129.0, -14.87], [129.6, -14.55], [129.7, -14.0], [130.0, -13.3], [130.3, -12.9], [130.8, -12.45], [131.1, -12.2], [131.5, -12.25], [132.0, -12.1], [132.5, -11.3], [132.9, -11.1], [133.0, -11.4], [133.5, -11.8], [134.2, -12.0], [135.0, -12.1], [136.0, -12.0], [136.6, -12.2], [136.9, -12.3], [136.6, -12.9], [136.2, -13.2], [135.9, -13.6], [136.0, -14.2], [135.7, -14.8], [136.0, -15.2], [136.6, -15.6], [137.1, -15.9], [137.8, -16.5], [138.0, -16.7], [138.0, -26.0], [129.0, -26.0]];
const TIWI = [[130.0, -11.8], [130.2, -11.3], [130.6, -11.3], [131.0, -11.2], [131.5, -11.4], [131.6, -11.8], [131.0, -11.9], [130.4, -11.9]];
const GROOTE = [[136.4, -13.7], [136.9, -13.7], [137.0, -14.2], [136.5, -14.2]];
const K = 30, X0 = 128.5, Y0 = -10.5;
export function project(lon, lat) { return [(lon - X0) * K, (Y0 - lat) * K]; }
const poly = (pts) => pts.map(([lon, lat], i) => (i ? 'L' : 'M') + project(lon, lat).map((n) => n.toFixed(1)).join(' ')).join('') + 'Z';
const COLOR = (v) => `var(--verdict-${v}-text)`;
function Point({ p, selected, onSelect }) {
  const [x, y] = project(p.lon, p.lat), s = 5, c = COLOR(p.verdict || 'nodata');
  let shape = null;
  if (p.verdict === 'works') shape = <circle cx={x} cy={y} r={s} fill={c} />;
  else if (p.verdict === 'degraded') shape = <polygon points={`${x},${y - s - 1} ${x + s + 1},${y + s} ${x - s - 1},${y + s}`} fill={c} />;
  else if (p.verdict === 'fails') shape = <rect x={x - s} y={y - s} width={2 * s} height={2 * s} fill={c} />;
  else shape = <rect x={x - s} y={y - 1.5} width={2 * s} height={3} fill={c} />;
  return (
    <g onClick={() => onSelect && onSelect(p)} style={{ cursor: onSelect ? 'pointer' : 'default' }}>
      <title>{`${p.name || 'Community'} · ${p.verdict || 'nodata'}`}</title>
      <circle cx={x} cy={y} r={16} fill="transparent" />
      {shape}
      {selected ? <circle cx={x} cy={y} r={9} fill="none" stroke="var(--focus-ring)" strokeWidth={2} /> : null}
      {selected && p.name ? <text x={x > 200 ? x - 13 : x + 13} y={y + 4} textAnchor={x > 200 ? 'end' : 'start'} style={{ font: 'var(--text-label)', fill: 'var(--text-heading)' }}>{p.name}</text> : null}
    </g>
  );
}
export function NtMap({ points = [], selectedId, onSelect, label = 'Map of the Northern Territory' }) {
  const sel = points.find((p) => p.id === selectedId);
  return (
    <svg role="img" aria-label={label} viewBox="0 0 300 480" style={{ display: 'block', width: '100%', height: 'auto', background: 'var(--surface-page)' }}>
      <g fill="var(--map-land)" stroke="var(--map-outline)" strokeWidth="1" strokeLinejoin="round" vectorEffect="non-scaling-stroke">
        <path d={poly(MAINLAND)} /><path d={poly(TIWI)} /><path d={poly(GROOTE)} />
      </g>
      {points.filter((p) => p.id !== selectedId).map((p) => <Point key={p.id || p.name} p={p} onSelect={onSelect} />)}
      {sel ? <Point p={sel} selected onSelect={onSelect} /> : null}
    </svg>
  );
}
