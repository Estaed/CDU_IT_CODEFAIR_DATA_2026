PublisherRow: one line per source that makes a coverage claim, with the kind chip (predicted / licensed / listed / portal), the claim as words ("Covered", "Not covered", "Not recorded"), a detail line and the source line.

```jsx
<PublisherRow publisher="ACCC 2025" kind="predicted" saysCovered="covered" detail="Telstra 4G outdoor polygon" source="ACCC Mobile Infrastructure Report" date="2025-11-10" />
```

The claim is not a verdict, so it uses ink, not verdict colour. `KindChip` (same file) is exported separately.
