QrCode: the phone-to-phone handoff graphic, an inline SVG with ink modules on white and a 4-module quiet zone; no image, no network.

```jsx
<QrCode text="https://example.org/crosscheck" />
```

Encodes byte mode up to version 10 (about 270 bytes at level L). Pass `modules` if the pipeline pre-encodes the code.
