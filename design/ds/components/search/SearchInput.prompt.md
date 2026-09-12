SearchInput: the 44px search field with hairline border (ink border on focus) and a list of ResultRow beneath it, each showing name, matched alias, region and population.

```jsx
<SearchInput value={q} onChange={setQ} results={matches} onSelect={openCommunity} />
```

`ResultRow` (same file) is exported for custom lists. Results carry `{ id, name, aliases, region, population }`; missing values render "Not recorded".
