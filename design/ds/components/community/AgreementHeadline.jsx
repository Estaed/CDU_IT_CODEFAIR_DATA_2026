import React from 'react';
export function AgreementHeadline({ covered = 0, total = 0, subject = 'sources say covered' }) {
  const agree = total > 0 && (covered === total || covered === 0);
  return (
    <div style={{ padding: 'var(--space-md)', color: 'var(--text-heading)' }}>
      <div style={{ font: 'var(--text-title-md)' }}>
        <span style={{ font: 'var(--text-figure-lg)' }}>{covered}</span> of <span style={{ font: 'var(--text-figure-lg)' }}>{total}</span> {subject}
      </div>
      <div style={{ font: 'var(--text-caption)', color: 'var(--text-secondary)', marginTop: 'var(--space-xxs)' }}>{total === 0 ? 'No source makes a claim here' : agree ? 'Sources agree' : 'Sources disagree'}</div>
    </div>
  );
}
