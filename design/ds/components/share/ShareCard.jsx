import React from 'react';
import { Button } from '../core/Button.jsx';
import { SourceLine } from '../core/SourceLine.jsx';
import { QrCode } from './QrCode.jsx';
export function ShareCard({ qrText, qrModules, packDate, packSize, appSize, buildSource = 'Crosscheck build', onShare, onSave, shareLabel = 'Share this app', saveLabel = 'Save file', statement = "Crosscheck shows what published sources say about a community's connectivity and what that allows. It does not measure signal. Every value shows its source and date." }) {
  const fig = { font: 'var(--text-figure-sm)', whiteSpace: 'nowrap' };
  return (
    <div style={{ background: 'var(--surface-page)', border: 'var(--size-hairline) solid var(--border-hairline)', borderRadius: 'var(--radius-lg)', padding: 'var(--space-lg)', display: 'grid', gap: 'var(--space-md)', color: 'var(--text-body)' }}>
      <div style={{ display: 'flex', justifyContent: 'center' }}><QrCode text={qrText} modules={qrModules} label="QR code that opens Crosscheck on another phone" /></div>
      <div style={{ font: 'var(--text-body-sm)', display: 'grid', gap: 'var(--space-xxs)' }}>
        <div>Data pack <span style={fig}>{packDate || 'Not recorded'}</span>{packSize ? <> · <span style={fig}>{packSize}</span></> : null}</div>
        {appSize ? <div>App <span style={fig}>{appSize}</span></div> : null}
        <SourceLine source={buildSource} date={packDate} />
      </div>
      <div style={{ display: 'grid', gap: 'var(--space-xs)' }}>
        <Button fullWidth onClick={onShare}>{shareLabel}</Button>
        <Button variant="secondary" fullWidth onClick={onSave}>{saveLabel}</Button>
      </div>
      <p style={{ margin: 0, font: 'var(--text-body-sm)', textWrap: 'pretty' }}>{statement}</p>
    </div>
  );
}
