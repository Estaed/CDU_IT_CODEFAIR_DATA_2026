import React from 'react';
// Renders prose with figures in monospace. Figures are marked with backticks: "Latency `665 ms` vs `100 ms` required".
export function Figures({ text = '', size = 'sm' }) {
  const parts = String(text).split('`');
  return <>{parts.map((p, i) => (i % 2 ? <span key={i} style={{ font: `var(--text-figure-${size})`, whiteSpace: 'nowrap' }}>{p}</span> : p))}</>;
}
