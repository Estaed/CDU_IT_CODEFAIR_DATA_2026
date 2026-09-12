FilterTabs: a scrolling tab row for screen navigation (Community / Map / Share) or map filters; the selected tab is ink with a 2px ink rule.

```jsx
<FilterTabs tabs={[{id:'all',label:'All',count:96},{id:'mast',label:'Licensed mast, no coverage map',count:11}]} selected="mast" onSelect={setFilter} />
```

Tabs are 44px tall, sentence case, and scroll horizontally on overflow. Only one accent: the near-black rule.
