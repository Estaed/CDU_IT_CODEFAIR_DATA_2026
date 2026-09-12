ServiceRow: a 44px-minimum row with the service name, the verdict badge at right and the reason sentence (figures in mono) beneath; tap to expand a grey panel listing each figure's source and date and the path rule.

```jsx
<ServiceRow service="Telehealth video" verdict="degraded" reason="Latency `665 ms` on satellite vs `100 ms` required"
  sources={[{label:'Failing figure:',source:'ACCC MBA',date:'2024-12-05'},{label:'Required figure:',source:'healthdirect',date:'2025-03-14'}]}
  path="Best path: satellite (NBN residual) · rule `v1`">
  <AssumptionNote>Could work over Telstra 4G if latency is under `100 ms`. No measurement exists here.</AssumptionNote>
</ServiceRow>
```

Keep the collapsed list of all services inside a 640px-tall viewport.
