Chip: a 28px grey pill for services present ("Health centre", "Public WiFi Mon–Sat 8am–8pm"), fragility flags and colour-by choices.

```jsx
<Chip>Health centre</Chip>
<Chip selected onClick={() => setBy('failing')}>Services failing</Chip>
```

Tappable chips wrap the pill in a 44px-tall button. Never use verdict colour on a chip.
