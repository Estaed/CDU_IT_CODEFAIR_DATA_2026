TopBar: the sticky 56px header with the app title and an offline indicator chip; put screen navigation in FilterTabs beneath it rather than in the bar.

```jsx
<TopBar title="Crosscheck" offline={!navigator.onLine} />
```

`OfflineChip` (same file) can be used alone. No icons, no colour cue: the chip reads "Offline" or "Online".
