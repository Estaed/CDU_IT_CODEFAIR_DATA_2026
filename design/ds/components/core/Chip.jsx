import React, { useState } from 'react';
export function Chip({ children, onClick, selected = false }) {
  const [pressed, setPressed] = useState(false);
  const pill = (
    <span style={{ display: 'inline-flex', alignItems: 'center', height: 'var(--size-chip)', padding: '0 var(--space-sm)', borderRadius: 'var(--radius-pill)', font: 'var(--text-label)', color: selected ? 'var(--text-on-primary)' : 'var(--text-body)', background: selected ? 'var(--action-primary)' : pressed ? 'var(--surface-pressed)' : 'var(--surface-block)', whiteSpace: 'nowrap' }}>{children}</span>
  );
  if (!onClick) return pill;
  return (
    <button type="button" onClick={onClick} aria-pressed={selected}
      onPointerDown={() => setPressed(true)} onPointerUp={() => setPressed(false)} onPointerLeave={() => setPressed(false)}
      style={{ display: 'inline-flex', alignItems: 'center', minHeight: 'var(--size-touch)', cursor: 'pointer' }}>{pill}</button>
  );
}
