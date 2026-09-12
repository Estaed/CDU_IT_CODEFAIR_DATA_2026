import React from 'react';
export function SourceLine({ label, source, date }) {
  return (
    <span style={{ display: 'block', font: 'var(--text-caption)', color: 'var(--text-secondary)' }}>
      {label ? <span>{label} </span> : null}
      {source || 'Not recorded'}
      {date ? <> · <span style={{ font: 'var(--text-figure-xs)', whiteSpace: 'nowrap' }}>{date}</span></> : null}
    </span>
  );
}
