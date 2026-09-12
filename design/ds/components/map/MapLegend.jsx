import React from 'react';
import { VERDICTS } from '../core/VerdictBadge.jsx';
export function MapLegend({ counts = {}, subject }) {
  return (
    <div style={{ padding: 'var(--space-sm) var(--space-md)', font: 'var(--text-caption)', color: 'var(--text-body)' }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-xxs) var(--space-md)' }}>
        {Object.keys(VERDICTS).map((k) => (
          <span key={k} style={{ display: 'inline-flex', alignItems: 'center', gap: 'var(--space-xxs)', whiteSpace: 'nowrap' }}>
            <span aria-hidden="true" style={{ color: `var(--verdict-${k}-text)`, fontSize: 11, lineHeight: 1, width: 12, textAlign: 'center' }}>{VERDICTS[k].glyph}</span>
            {VERDICTS[k].word}
            <span style={{ font: 'var(--text-figure-xs)' }}>{typeof counts[k] === 'number' ? counts[k] : '–'}</span>
          </span>
        ))}
      </div>
      {subject ? <div style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-xxs)' }}>{subject}</div> : null}
    </div>
  );
}
