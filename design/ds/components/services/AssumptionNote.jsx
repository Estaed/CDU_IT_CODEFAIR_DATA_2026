import React from 'react';
import { Figures } from '../core/Figures.jsx';
export function AssumptionNote({ children, text, label = 'Assumption' }) {
  return (
    <div style={{ margin: '0 var(--space-md) var(--space-sm)', padding: 'var(--space-sm) var(--space-md)', background: 'var(--surface-block)', borderLeft: 'var(--size-rule) solid var(--verdict-degraded-text)', borderRadius: 'var(--radius-xs)', font: 'var(--text-body-sm)', color: 'var(--text-body)', textWrap: 'pretty' }}>
      <span style={{ font: 'var(--text-label)', color: 'var(--text-heading)' }}>{label} </span>
      {text ? <Figures text={text} size="sm" /> : children}
    </div>
  );
}
