import React from 'react';
import { SourceLine } from '../core/SourceLine.jsx';
export function CommunityHeader({ name, region, type, population, populationSource = 'ABS 2021 SA1 via BushTel', populationDate, children }) {
  return (
    <div style={{ padding: 'var(--space-md)', borderBottom: 'var(--size-hairline) solid var(--border-hairline)', color: 'var(--text-heading)' }}>
      <h1 style={{ margin: 0, font: 'var(--text-title-lg)', letterSpacing: 'var(--tracking-title-lg)', textWrap: 'pretty' }}>{name}</h1>
      <div style={{ font: 'var(--text-body-sm)', color: 'var(--text-body)', marginTop: 'var(--space-xxs)' }}>{[region, type].filter(Boolean).join(' · ') || 'Region not recorded'}</div>
      <div style={{ marginTop: 'var(--space-xs)', color: 'var(--text-heading)' }}>
        <span style={{ font: 'var(--text-figure-md)' }}>{typeof population === 'number' ? population.toLocaleString('en-AU') : 'Not recorded'}</span>
        <span style={{ font: 'var(--text-body-sm)', color: 'var(--text-body)' }}> people</span>
      </div>
      <div style={{ marginTop: 'var(--space-xxs)' }}><SourceLine source={populationSource} date={populationDate} /></div>
      {children ? <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-xs)', marginTop: 'var(--space-sm)' }}>{children}</div> : null}
    </div>
  );
}
