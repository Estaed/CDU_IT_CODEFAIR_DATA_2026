import React from 'react';
import { Figures } from '../core/Figures.jsx';
import { SourceLine } from '../core/SourceLine.jsx';
const SAYS = { covered: 'Covered', 'not-covered': 'Not covered', 'not-recorded': 'Not recorded' };
export function KindChip({ kind = 'listed' }) {
  return <span style={{ display: 'inline-flex', alignItems: 'center', height: 'var(--size-badge)', padding: '0 var(--space-xs)', borderRadius: 'var(--radius-xs)', font: 'var(--text-label)', color: 'var(--text-body)', background: 'var(--surface-block)', whiteSpace: 'nowrap' }}>{kind}</span>;
}
export function PublisherRow({ publisher, kind = 'listed', saysCovered = 'not-recorded', detail, source, date }) {
  const text = kind === 'predicted' && detail ? `${detail} (carrier prediction)` : detail;
  return (
    <div style={{ padding: 'var(--space-sm) var(--space-md)', borderBottom: 'var(--size-hairline) solid var(--border-hairline-soft)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>
        <span style={{ font: 'var(--text-title-sm)', color: 'var(--text-heading)', flex: '1 1 auto', minWidth: 0 }}>{publisher}</span>
        <KindChip kind={kind} />
        <span style={{ font: 'var(--text-label)', color: 'var(--text-heading)', whiteSpace: 'nowrap' }}>{SAYS[saysCovered] || SAYS['not-recorded']}</span>
      </div>
      {text ? <div style={{ font: 'var(--text-caption)', color: 'var(--text-body)', marginTop: 'var(--space-xxs)' }}><Figures text={text} size="xs" /></div> : null}
      <div style={{ marginTop: 'var(--space-xxs)' }}><SourceLine source={source} date={date} /></div>
    </div>
  );
}
