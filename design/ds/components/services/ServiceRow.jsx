import React, { useState } from 'react';
import { Figures } from '../core/Figures.jsx';
import { SourceLine } from '../core/SourceLine.jsx';
import { VerdictBadge } from '../core/VerdictBadge.jsx';
export function ServiceRow({ service, verdict = 'nodata', reason, sources = [], path, defaultExpanded = false, children }) {
  const [open, setOpen] = useState(defaultExpanded);
  const [pressed, setPressed] = useState(false);
  return (
    <div style={{ borderBottom: 'var(--size-hairline) solid var(--border-hairline)' }}>
      <button type="button" aria-expanded={open} onClick={() => setOpen(!open)}
        onPointerDown={() => setPressed(true)} onPointerUp={() => setPressed(false)} onPointerLeave={() => setPressed(false)}
        style={{ display: 'block', width: '100%', textAlign: 'left', minHeight: 'var(--size-touch)', padding: 'var(--space-sm) var(--space-md)', background: pressed ? 'var(--surface-block)' : 'var(--surface-page)', cursor: 'pointer' }}>
        <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-sm)' }}>
          <span style={{ font: 'var(--text-title-sm)', color: 'var(--text-heading)' }}>{service}</span>
          <VerdictBadge verdict={verdict} />
        </span>
        {reason ? <span style={{ display: 'block', font: 'var(--text-body-sm)', color: 'var(--text-body)', marginTop: 'var(--space-xxs)', textWrap: 'pretty' }}><Figures text={reason} size="sm" /></span> : null}
      </button>
      {open ? (
        <div style={{ background: 'var(--surface-soft)', padding: 'var(--space-sm) var(--space-md)', display: 'grid', gap: 'var(--space-xxs)' }}>
          {sources.length ? sources.map((s, i) => <SourceLine key={i} label={s.label} source={s.source} date={s.date} />) : <SourceLine label="Sources:" />}
          {path ? <span style={{ font: 'var(--text-caption)', color: 'var(--text-secondary)' }}><Figures text={path} size="xs" /></span> : null}
        </div>
      ) : null}
      {children}
    </div>
  );
}
