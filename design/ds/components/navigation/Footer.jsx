import React from 'react';
import { Figures } from '../core/Figures.jsx';
export function Footer({ attributions = [], team = 'CDU IT Code Fair 2026 · Data Innovation Challenge · Team DIC005', statement = 'Crosscheck does not measure signal.' }) {
  return (
    <footer style={{ borderTop: 'var(--size-hairline) solid var(--border-hairline)', padding: 'var(--space-lg) var(--space-md)', font: 'var(--text-caption)', color: 'var(--text-secondary)', display: 'grid', gap: 'var(--space-xs)' }}>
      {attributions.map((a, i) => <span key={i}><Figures text={a} size="xs" /></span>)}
      <span style={{ marginTop: 'var(--space-xs)' }}>{team}</span>
      <span>{statement}</span>
    </footer>
  );
}
