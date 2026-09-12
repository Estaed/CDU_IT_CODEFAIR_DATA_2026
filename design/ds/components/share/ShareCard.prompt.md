ShareCard: the whole Share screen in one hairline card, with the inline-SVG QR code, data-pack date and size in mono, primary "Share this app" and secondary "Save file" buttons, and the plain statement.

```jsx
<ShareCard qrText="https://example.org/crosscheck" packDate="2026-09-30" packSize="212 KB" appSize="810 KB" onShare={share} onSave={save} />
```

Keep the statement verbatim unless the PRD changes it; it says what the app does not do.
