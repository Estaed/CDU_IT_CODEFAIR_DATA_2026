import React, { useState } from 'react';
export function ResultRow({ result, onSelect, query = '' }) {
  const [pressed, setPressed] = useState(false);
  const alias = query && result.aliases ? result.aliases.find((a) => a.toLowerCase().includes(query.toLowerCase())) : null;
  return (
    <button type="button" onClick={() => onSelect && onSelect(result)}
      onPointerDown={() => setPressed(true)} onPointerUp={() => setPressed(false)} onPointerLeave={() => setPressed(false)}
      style={{ display: 'block', width: '100%', textAlign: 'left', minHeight: 'var(--size-touch)', padding: 'var(--space-sm) var(--space-md)', borderBottom: 'var(--size-hairline) solid var(--border-hairline-soft)', background: pressed ? 'var(--surface-block)' : 'var(--surface-page)', cursor: 'pointer' }}>
      <span style={{ display: 'block', font: 'var(--text-body-md)', color: 'var(--text-heading)' }}>
        {result.name}{alias ? <span style={{ font: 'var(--text-caption)', color: 'var(--text-secondary)' }}> also {alias}</span> : null}
      </span>
      <span style={{ display: 'block', font: 'var(--text-caption)', color: 'var(--text-secondary)' }}>
        {result.region || 'Region not recorded'} · <span style={{ font: 'var(--text-figure-xs)' }}>{typeof result.population === 'number' ? result.population.toLocaleString('en-AU') : 'Not recorded'}</span> people
      </span>
    </button>
  );
}
export function SearchInput({ value = '', onChange, placeholder = 'Search 96 communities', results = [], onSelect, label = 'Search communities' }) {
  const [focused, setFocused] = useState(false);
  return (
    <div>
      <input type="search" value={value} aria-label={label} placeholder={placeholder} autoComplete="off"
        onChange={(e) => onChange && onChange(e.target.value)} onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
        style={{ display: 'block', width: '100%', boxSizing: 'border-box', height: 'var(--size-control)', padding: '0 var(--space-sm)', font: 'var(--text-body-md)', color: 'var(--text-heading)', background: 'var(--surface-page)', border: `var(--size-hairline) solid ${focused ? 'var(--text-heading)' : 'var(--border-hairline)'}`, borderRadius: 'var(--radius-md)', appearance: 'none', WebkitAppearance: 'none' }} />
      {results.length ? (
        <div role="listbox" style={{ marginTop: 'var(--space-xs)', border: 'var(--size-hairline) solid var(--border-hairline)', borderRadius: 'var(--radius-sm)', overflow: 'hidden' }}>
          {results.map((r) => <ResultRow key={r.id || r.name} result={r} onSelect={onSelect} query={value} />)}
        </div>
      ) : null}
    </div>
  );
}
