import React from 'react';
export function OfflineChip({ offline = true }) {
  return <span style={{ display: 'inline-flex', alignItems: 'center', height: 'var(--size-chip)', padding: '0 var(--space-sm)', borderRadius: 'var(--radius-pill)', font: 'var(--text-label)', color: 'var(--text-body)', background: 'var(--surface-block)', whiteSpace: 'nowrap' }}>{offline ? 'Offline' : 'Online'}</span>;
}
export function TopBar({ title = 'Crosscheck', offline = true, sticky = true, children }) {
  return (
    <header style={{ position: sticky ? 'sticky' : 'static', top: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-sm)', height: 'var(--size-topbar)', padding: '0 var(--space-md)', background: 'var(--surface-page)', borderBottom: 'var(--size-hairline) solid var(--border-hairline)', color: 'var(--text-heading)' }}>
      <span style={{ font: 'var(--text-title-sm)' }}>{title}</span>
      {children ? <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>{children}</div> : null}
      <OfflineChip offline={offline} />
    </header>
  );
}
