import React from 'react';
export const VERDICTS = {
  works: { word: 'Works', glyph: '●', shape: 'circle' },
  degraded: { word: 'Degraded', glyph: '▲', shape: 'triangle' },
  fails: { word: 'Fails', glyph: '■', shape: 'square' },
  nodata: { word: 'No data', glyph: '–', shape: 'dash' },
};
export function VerdictBadge({ verdict = 'nodata' }) {
  const key = VERDICTS[verdict] ? verdict : 'nodata';
  const v = VERDICTS[key];
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 'var(--space-xxs)', height: 'var(--size-badge)', padding: '0 var(--space-xs)', borderRadius: 'var(--radius-xs)', font: 'var(--text-label)', color: `var(--verdict-${key}-text)`, background: `var(--verdict-${key}-fill)`, whiteSpace: 'nowrap' }}>
      <span aria-hidden="true" style={{ fontSize: 11, lineHeight: 1 }}>{v.glyph}</span>{v.word}
    </span>
  );
}
