Figures: renders a sentence with each backtick-marked figure in the monospace stack, so latency, distance, population, dates and sizes never sit in the sans face.

```jsx
<p style={{ font: 'var(--text-body-sm)' }}><Figures text="Latency `665 ms` on satellite vs `100 ms` required" /></p>
```

`size` picks the mono size to match the surrounding sans: xs (13), sm (14), md (16), lg (22). Figures do not wrap mid-value.
