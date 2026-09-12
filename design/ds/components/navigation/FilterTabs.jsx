import React, { useState } from 'react';
function Tab({ tab, selected, onSelect }) {
  const [pressed, setPressed] = useState(false);
  return (
    <button type="button" role="tab" aria-selected={selected} onClick={() => onSelect && onSelect(tab.id)}
      onPointerDown={() => setPressed(true)} onPointerUp={() => setPressed(false)} onPointerLeave={() => setPressed(false)}
      style={{ font: 'var(--text-tab)', color: selected ? 'var(--tab-selected)' : 'var(--text-secondary)', padding: 'var(--space-sm) var(--space-md)', minHeight: 'var(--size-touch)', borderBottom: `var(--size-focus-ring) solid ${selected ? 'var(--tab-selected)' : 'transparent'}`, background: pressed ? 'var(--surface-block)' : 'transparent', whiteSpace: 'nowrap', cursor: 'pointer', flex: '0 0 auto' }}>
      {tab.label}{typeof tab.count === 'number' ? <span style={{ font: 'var(--text-figure-xs)', marginLeft: 'var(--space-xxs)' }}>{tab.count}</span> : null}
    </button>
  );
}
export function FilterTabs({ tabs = [], selected, onSelect, ariaLabel = 'Filters' }) {
  return (
    <div role="tablist" aria-label={ariaLabel} style={{ display: 'flex', overflowX: 'auto', borderBottom: 'var(--size-hairline) solid var(--border-hairline)', scrollbarWidth: 'none' }}>
      {tabs.map((t) => <Tab key={t.id} tab={t} selected={t.id === selected} onSelect={onSelect} />)}
    </div>
  );
}
