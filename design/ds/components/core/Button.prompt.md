Button: the primary (near-black) or secondary (white, hairline) action; use one primary per screen and never colour a button.

```jsx
<Button fullWidth onClick={share}>Share this app</Button>
<Button variant="secondary" fullWidth onClick={save}>Save file</Button>
```

Props: `variant` 'primary' | 'secondary', `disabled`, `fullWidth`. States: default and pressed only. Labels in sentence case, no exclamation marks.
