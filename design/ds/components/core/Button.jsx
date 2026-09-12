import React, { useState } from 'react';
export function Button({ variant = 'primary', disabled = false, fullWidth = false, onClick, children }) {
  const [pressed, setPressed] = useState(false);
  const primary = variant === 'primary';
  const bg = disabled ? 'var(--action-disabled)' : primary ? (pressed ? 'var(--action-primary-pressed)' : 'var(--action-primary)') : (pressed ? 'var(--surface-block)' : 'var(--surface-page)');
  const color = disabled ? 'var(--text-secondary)' : primary ? 'var(--text-on-primary)' : 'var(--text-heading)';
  return (
    <button type="button" disabled={disabled} onClick={onClick}
      onPointerDown={() => setPressed(true)} onPointerUp={() => setPressed(false)} onPointerLeave={() => setPressed(false)}
      style={{ font: 'var(--text-button)', height: 'var(--size-control)', minWidth: 'var(--size-touch)', padding: '0 20px', borderRadius: 'var(--radius-md)', border: primary || disabled ? 'var(--size-hairline) solid transparent' : 'var(--size-hairline) solid var(--border-hairline)', background: bg, color, width: fullWidth ? '100%' : undefined, cursor: disabled ? 'default' : 'pointer', display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>
      {children}
    </button>
  );
}
