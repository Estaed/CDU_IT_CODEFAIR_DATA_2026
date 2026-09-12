CommunityHeader: the top of the Community screen, with name at 22px, region and type, population in mono with its source line, and chips for what exists here.

```jsx
<CommunityHeader name="Wadeye" region="Top End" type="Major community" population={2259} populationDate="2026-06-26">
  <Chip>Health centre</Chip><Chip>School</Chip><Chip>Public WiFi Mon–Sat 8am–8pm</Chip>
</CommunityHeader>
```

What exists comes before what fails: put the services-present chips here, verdicts below.
