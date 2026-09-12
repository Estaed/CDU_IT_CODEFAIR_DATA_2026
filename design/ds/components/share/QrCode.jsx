import React, { useMemo } from 'react';
import { qrModules } from './qr.js';
// Inline-SVG QR code: ink modules on canvas, 4-module quiet zone, one <path> so the DOM stays small.
export function QrCode({ text = '', modules, level = 'M', size = 'var(--size-qr)', label = 'QR code' }) {
  const m = useMemo(() => modules || (text ? qrModules(text, level) : null), [text, modules, level]);
  if (!m) return null;
  const n = m.length, q = 4, d = [];
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) if (m[y][x]) d.push(`M${x + q} ${y + q}h1v1h-1z`);
  return (
    <svg role="img" aria-label={label} viewBox={`0 0 ${n + 2 * q} ${n + 2 * q}`} width={size} height={size} shapeRendering="crispEdges" style={{ display: 'block', background: 'var(--surface-page)' }}>
      <path d={d.join('')} fill="var(--text-heading)" />
    </svg>
  );
}
