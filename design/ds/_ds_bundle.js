/* @ds-bundle: {"format":4,"namespace":"CrosscheckDesignSystem_469d70","components":[{"name":"AgreementHeadline","sourcePath":"components/community/AgreementHeadline.jsx"},{"name":"CommunityHeader","sourcePath":"components/community/CommunityHeader.jsx"},{"name":"KindChip","sourcePath":"components/community/PublisherRow.jsx"},{"name":"PublisherRow","sourcePath":"components/community/PublisherRow.jsx"},{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"Chip","sourcePath":"components/core/Chip.jsx"},{"name":"Figures","sourcePath":"components/core/Figures.jsx"},{"name":"SourceLine","sourcePath":"components/core/SourceLine.jsx"},{"name":"VERDICTS","sourcePath":"components/core/VerdictBadge.jsx"},{"name":"VerdictBadge","sourcePath":"components/core/VerdictBadge.jsx"},{"name":"MapLegend","sourcePath":"components/map/MapLegend.jsx"},{"name":"NtMap","sourcePath":"components/map/NtMap.jsx"},{"name":"FilterTabs","sourcePath":"components/navigation/FilterTabs.jsx"},{"name":"Footer","sourcePath":"components/navigation/Footer.jsx"},{"name":"OfflineChip","sourcePath":"components/navigation/TopBar.jsx"},{"name":"TopBar","sourcePath":"components/navigation/TopBar.jsx"},{"name":"ResultRow","sourcePath":"components/search/SearchInput.jsx"},{"name":"SearchInput","sourcePath":"components/search/SearchInput.jsx"},{"name":"AssumptionNote","sourcePath":"components/services/AssumptionNote.jsx"},{"name":"ServiceRow","sourcePath":"components/services/ServiceRow.jsx"},{"name":"QrCode","sourcePath":"components/share/QrCode.jsx"},{"name":"ShareCard","sourcePath":"components/share/ShareCard.jsx"}],"sourceHashes":{"components/community/AgreementHeadline.jsx":"b412ada1a05d","components/community/CommunityHeader.jsx":"b9bc5fbeb7e7","components/community/PublisherRow.jsx":"ec5f7f97b672","components/core/Button.jsx":"57e3d31ba362","components/core/Chip.jsx":"9c89b412d2e1","components/core/Figures.jsx":"aa510a745dbc","components/core/SourceLine.jsx":"769c5369b438","components/core/VerdictBadge.jsx":"489ce5cdb3f5","components/map/MapLegend.jsx":"91bac78bdb65","components/map/NtMap.jsx":"5b612875b01a","components/navigation/FilterTabs.jsx":"c4be8a2b2ca3","components/navigation/Footer.jsx":"fa555e44cfed","components/navigation/TopBar.jsx":"aa98b972a25f","components/search/SearchInput.jsx":"a7783ff03cb9","components/services/AssumptionNote.jsx":"5d782560e519","components/services/ServiceRow.jsx":"9b946f4aac10","components/share/QrCode.jsx":"a4f4740f57dd","components/share/ShareCard.jsx":"81942aee98b7","components/share/qr.js":"4ac17445f258"},"inlinedExternals":[],"unexposedExports":[{"name":"project","sourcePath":"components/map/NtMap.jsx"},{"name":"qrModules","sourcePath":"components/share/qr.js"}]} */

(() => {

const __ds_ns = (window.CrosscheckDesignSystem_469d70 = window.CrosscheckDesignSystem_469d70 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/community/AgreementHeadline.jsx
try { (() => {
function AgreementHeadline({
  covered = 0,
  total = 0,
  subject = 'sources say covered'
}) {
  const agree = total > 0 && (covered === total || covered === 0);
  return /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-md)',
      color: 'var(--text-heading)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-title-md)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-figure-lg)'
    }
  }, covered), " of ", /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-figure-lg)'
    }
  }, total), " ", subject), /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-caption)',
      color: 'var(--text-secondary)',
      marginTop: 'var(--space-xxs)'
    }
  }, total === 0 ? 'No source makes a claim here' : agree ? 'Sources agree' : 'Sources disagree'));
}
Object.assign(__ds_scope, { AgreementHeadline });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/community/AgreementHeadline.jsx", error: String((e && e.message) || e) }); }

// components/core/Button.jsx
try { (() => {
const {
  useState
} = React;
function Button({
  variant = 'primary',
  disabled = false,
  fullWidth = false,
  onClick,
  children
}) {
  const [pressed, setPressed] = useState(false);
  const primary = variant === 'primary';
  const bg = disabled ? 'var(--action-disabled)' : primary ? pressed ? 'var(--action-primary-pressed)' : 'var(--action-primary)' : pressed ? 'var(--surface-block)' : 'var(--surface-page)';
  const color = disabled ? 'var(--text-secondary)' : primary ? 'var(--text-on-primary)' : 'var(--text-heading)';
  return /*#__PURE__*/React.createElement("button", {
    type: "button",
    disabled: disabled,
    onClick: onClick,
    onPointerDown: () => setPressed(true),
    onPointerUp: () => setPressed(false),
    onPointerLeave: () => setPressed(false),
    style: {
      font: 'var(--text-button)',
      height: 'var(--size-control)',
      minWidth: 'var(--size-touch)',
      padding: '0 20px',
      borderRadius: 'var(--radius-md)',
      border: primary || disabled ? 'var(--size-hairline) solid transparent' : 'var(--size-hairline) solid var(--border-hairline)',
      background: bg,
      color,
      width: fullWidth ? '100%' : undefined,
      cursor: disabled ? 'default' : 'pointer',
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center'
    }
  }, children);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/Chip.jsx
try { (() => {
const {
  useState
} = React;
function Chip({
  children,
  onClick,
  selected = false
}) {
  const [pressed, setPressed] = useState(false);
  const pill = /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      height: 'var(--size-chip)',
      padding: '0 var(--space-sm)',
      borderRadius: 'var(--radius-pill)',
      font: 'var(--text-label)',
      color: selected ? 'var(--text-on-primary)' : 'var(--text-body)',
      background: selected ? 'var(--action-primary)' : pressed ? 'var(--surface-pressed)' : 'var(--surface-block)',
      whiteSpace: 'nowrap'
    }
  }, children);
  if (!onClick) return pill;
  return /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: onClick,
    "aria-pressed": selected,
    onPointerDown: () => setPressed(true),
    onPointerUp: () => setPressed(false),
    onPointerLeave: () => setPressed(false),
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      minHeight: 'var(--size-touch)',
      cursor: 'pointer'
    }
  }, pill);
}
Object.assign(__ds_scope, { Chip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Chip.jsx", error: String((e && e.message) || e) }); }

// components/core/Figures.jsx
try { (() => {
// Renders prose with figures in monospace. Figures are marked with backticks: "Latency `665 ms` vs `100 ms` required".
function Figures({
  text = '',
  size = 'sm'
}) {
  const parts = String(text).split('`');
  return /*#__PURE__*/React.createElement(React.Fragment, null, parts.map((p, i) => i % 2 ? /*#__PURE__*/React.createElement("span", {
    key: i,
    style: {
      font: `var(--text-figure-${size})`,
      whiteSpace: 'nowrap'
    }
  }, p) : p));
}
Object.assign(__ds_scope, { Figures });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Figures.jsx", error: String((e && e.message) || e) }); }

// components/core/SourceLine.jsx
try { (() => {
function SourceLine({
  label,
  source,
  date
}) {
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      font: 'var(--text-caption)',
      color: 'var(--text-secondary)'
    }
  }, label ? /*#__PURE__*/React.createElement("span", null, label, " ") : null, source || 'Not recorded', date ? /*#__PURE__*/React.createElement(React.Fragment, null, " \xB7 ", /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-figure-xs)',
      whiteSpace: 'nowrap'
    }
  }, date)) : null);
}
Object.assign(__ds_scope, { SourceLine });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/SourceLine.jsx", error: String((e && e.message) || e) }); }

// components/community/CommunityHeader.jsx
try { (() => {
function CommunityHeader({
  name,
  region,
  type,
  population,
  populationSource = 'ABS 2021 SA1 via BushTel',
  populationDate,
  children
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-md)',
      borderBottom: 'var(--size-hairline) solid var(--border-hairline)',
      color: 'var(--text-heading)'
    }
  }, /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: 0,
      font: 'var(--text-title-lg)',
      letterSpacing: 'var(--tracking-title-lg)',
      textWrap: 'pretty'
    }
  }, name), /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-body-sm)',
      color: 'var(--text-body)',
      marginTop: 'var(--space-xxs)'
    }
  }, [region, type].filter(Boolean).join(' · ') || 'Region not recorded'), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 'var(--space-xs)',
      color: 'var(--text-heading)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-figure-md)'
    }
  }, typeof population === 'number' ? population.toLocaleString('en-AU') : 'Not recorded'), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-body-sm)',
      color: 'var(--text-body)'
    }
  }, " people")), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 'var(--space-xxs)'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.SourceLine, {
    source: populationSource,
    date: populationDate
  })), children ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 'var(--space-xs)',
      marginTop: 'var(--space-sm)'
    }
  }, children) : null);
}
Object.assign(__ds_scope, { CommunityHeader });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/community/CommunityHeader.jsx", error: String((e && e.message) || e) }); }

// components/community/PublisherRow.jsx
try { (() => {
const SAYS = {
  covered: 'Covered',
  'not-covered': 'Not covered',
  'not-recorded': 'Not recorded'
};
function KindChip({
  kind = 'listed'
}) {
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      height: 'var(--size-badge)',
      padding: '0 var(--space-xs)',
      borderRadius: 'var(--radius-xs)',
      font: 'var(--text-label)',
      color: 'var(--text-body)',
      background: 'var(--surface-block)',
      whiteSpace: 'nowrap'
    }
  }, kind);
}
function PublisherRow({
  publisher,
  kind = 'listed',
  saysCovered = 'not-recorded',
  detail,
  source,
  date
}) {
  const text = kind === 'predicted' && detail ? `${detail} (carrier prediction)` : detail;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-sm) var(--space-md)',
      borderBottom: 'var(--size-hairline) solid var(--border-hairline-soft)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-xs)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-title-sm)',
      color: 'var(--text-heading)',
      flex: '1 1 auto',
      minWidth: 0
    }
  }, publisher), /*#__PURE__*/React.createElement(KindChip, {
    kind: kind
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-label)',
      color: 'var(--text-heading)',
      whiteSpace: 'nowrap'
    }
  }, SAYS[saysCovered] || SAYS['not-recorded'])), text ? /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-caption)',
      color: 'var(--text-body)',
      marginTop: 'var(--space-xxs)'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Figures, {
    text: text,
    size: "xs"
  })) : null, /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 'var(--space-xxs)'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.SourceLine, {
    source: source,
    date: date
  })));
}
Object.assign(__ds_scope, { KindChip, PublisherRow });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/community/PublisherRow.jsx", error: String((e && e.message) || e) }); }

// components/core/VerdictBadge.jsx
try { (() => {
const VERDICTS = {
  works: {
    word: 'Works',
    glyph: '●',
    shape: 'circle'
  },
  degraded: {
    word: 'Degraded',
    glyph: '▲',
    shape: 'triangle'
  },
  fails: {
    word: 'Fails',
    glyph: '■',
    shape: 'square'
  },
  nodata: {
    word: 'No data',
    glyph: '–',
    shape: 'dash'
  }
};
function VerdictBadge({
  verdict = 'nodata'
}) {
  const key = VERDICTS[verdict] ? verdict : 'nodata';
  const v = VERDICTS[key];
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 'var(--space-xxs)',
      height: 'var(--size-badge)',
      padding: '0 var(--space-xs)',
      borderRadius: 'var(--radius-xs)',
      font: 'var(--text-label)',
      color: `var(--verdict-${key}-text)`,
      background: `var(--verdict-${key}-fill)`,
      whiteSpace: 'nowrap'
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      fontSize: 11,
      lineHeight: 1
    }
  }, v.glyph), v.word);
}
Object.assign(__ds_scope, { VERDICTS, VerdictBadge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/VerdictBadge.jsx", error: String((e && e.message) || e) }); }

// components/map/MapLegend.jsx
try { (() => {
function MapLegend({
  counts = {},
  subject
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-sm) var(--space-md)',
      font: 'var(--text-caption)',
      color: 'var(--text-body)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 'var(--space-xxs) var(--space-md)'
    }
  }, Object.keys(__ds_scope.VERDICTS).map(k => /*#__PURE__*/React.createElement("span", {
    key: k,
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 'var(--space-xxs)',
      whiteSpace: 'nowrap'
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      color: `var(--verdict-${k}-text)`,
      fontSize: 11,
      lineHeight: 1,
      width: 12,
      textAlign: 'center'
    }
  }, __ds_scope.VERDICTS[k].glyph), __ds_scope.VERDICTS[k].word, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-figure-xs)'
    }
  }, typeof counts[k] === 'number' ? counts[k] : '–')))), subject ? /*#__PURE__*/React.createElement("div", {
    style: {
      color: 'var(--text-secondary)',
      marginTop: 'var(--space-xxs)'
    }
  }, subject) : null);
}
Object.assign(__ds_scope, { MapLegend });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/map/MapLegend.jsx", error: String((e && e.message) || e) }); }

// components/map/NtMap.jsx
try { (() => {
// Simplified NT outline (lon, lat). Replace with the pipeline's BushTel-derived outline when available.
const MAINLAND = [[129.0, -14.87], [129.6, -14.55], [129.7, -14.0], [130.0, -13.3], [130.3, -12.9], [130.8, -12.45], [131.1, -12.2], [131.5, -12.25], [132.0, -12.1], [132.5, -11.3], [132.9, -11.1], [133.0, -11.4], [133.5, -11.8], [134.2, -12.0], [135.0, -12.1], [136.0, -12.0], [136.6, -12.2], [136.9, -12.3], [136.6, -12.9], [136.2, -13.2], [135.9, -13.6], [136.0, -14.2], [135.7, -14.8], [136.0, -15.2], [136.6, -15.6], [137.1, -15.9], [137.8, -16.5], [138.0, -16.7], [138.0, -26.0], [129.0, -26.0]];
const TIWI = [[130.0, -11.8], [130.2, -11.3], [130.6, -11.3], [131.0, -11.2], [131.5, -11.4], [131.6, -11.8], [131.0, -11.9], [130.4, -11.9]];
const GROOTE = [[136.4, -13.7], [136.9, -13.7], [137.0, -14.2], [136.5, -14.2]];
const K = 30,
  X0 = 128.5,
  Y0 = -10.5;
function project(lon, lat) {
  return [(lon - X0) * K, (Y0 - lat) * K];
}
const poly = pts => pts.map(([lon, lat], i) => (i ? 'L' : 'M') + project(lon, lat).map(n => n.toFixed(1)).join(' ')).join('') + 'Z';
const COLOR = v => `var(--verdict-${v}-text)`;
function Point({
  p,
  selected,
  onSelect
}) {
  const [x, y] = project(p.lon, p.lat),
    s = 5,
    c = COLOR(p.verdict || 'nodata');
  let shape = null;
  if (p.verdict === 'works') shape = /*#__PURE__*/React.createElement("circle", {
    cx: x,
    cy: y,
    r: s,
    fill: c
  });else if (p.verdict === 'degraded') shape = /*#__PURE__*/React.createElement("polygon", {
    points: `${x},${y - s - 1} ${x + s + 1},${y + s} ${x - s - 1},${y + s}`,
    fill: c
  });else if (p.verdict === 'fails') shape = /*#__PURE__*/React.createElement("rect", {
    x: x - s,
    y: y - s,
    width: 2 * s,
    height: 2 * s,
    fill: c
  });else shape = /*#__PURE__*/React.createElement("rect", {
    x: x - s,
    y: y - 1.5,
    width: 2 * s,
    height: 3,
    fill: c
  });
  return /*#__PURE__*/React.createElement("g", {
    onClick: () => onSelect && onSelect(p),
    style: {
      cursor: onSelect ? 'pointer' : 'default'
    }
  }, /*#__PURE__*/React.createElement("title", null, `${p.name || 'Community'} · ${p.verdict || 'nodata'}`), /*#__PURE__*/React.createElement("circle", {
    cx: x,
    cy: y,
    r: 16,
    fill: "transparent"
  }), shape, selected ? /*#__PURE__*/React.createElement("circle", {
    cx: x,
    cy: y,
    r: 9,
    fill: "none",
    stroke: "var(--focus-ring)",
    strokeWidth: 2
  }) : null, selected && p.name ? /*#__PURE__*/React.createElement("text", {
    x: x > 200 ? x - 13 : x + 13,
    y: y + 4,
    textAnchor: x > 200 ? 'end' : 'start',
    style: {
      font: 'var(--text-label)',
      fill: 'var(--text-heading)'
    }
  }, p.name) : null);
}
function NtMap({
  points = [],
  selectedId,
  onSelect,
  label = 'Map of the Northern Territory'
}) {
  const sel = points.find(p => p.id === selectedId);
  return /*#__PURE__*/React.createElement("svg", {
    role: "img",
    "aria-label": label,
    viewBox: "0 0 300 480",
    style: {
      display: 'block',
      width: '100%',
      height: 'auto',
      background: 'var(--surface-page)'
    }
  }, /*#__PURE__*/React.createElement("g", {
    fill: "var(--map-land)",
    stroke: "var(--map-outline)",
    strokeWidth: "1",
    strokeLinejoin: "round",
    vectorEffect: "non-scaling-stroke"
  }, /*#__PURE__*/React.createElement("path", {
    d: poly(MAINLAND)
  }), /*#__PURE__*/React.createElement("path", {
    d: poly(TIWI)
  }), /*#__PURE__*/React.createElement("path", {
    d: poly(GROOTE)
  })), points.filter(p => p.id !== selectedId).map(p => /*#__PURE__*/React.createElement(Point, {
    key: p.id || p.name,
    p: p,
    onSelect: onSelect
  })), sel ? /*#__PURE__*/React.createElement(Point, {
    p: sel,
    selected: true,
    onSelect: onSelect
  }) : null);
}
Object.assign(__ds_scope, { project, NtMap });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/map/NtMap.jsx", error: String((e && e.message) || e) }); }

// components/navigation/FilterTabs.jsx
try { (() => {
const {
  useState
} = React;
function Tab({
  tab,
  selected,
  onSelect
}) {
  const [pressed, setPressed] = useState(false);
  return /*#__PURE__*/React.createElement("button", {
    type: "button",
    role: "tab",
    "aria-selected": selected,
    onClick: () => onSelect && onSelect(tab.id),
    onPointerDown: () => setPressed(true),
    onPointerUp: () => setPressed(false),
    onPointerLeave: () => setPressed(false),
    style: {
      font: 'var(--text-tab)',
      color: selected ? 'var(--tab-selected)' : 'var(--text-secondary)',
      padding: 'var(--space-sm) var(--space-md)',
      minHeight: 'var(--size-touch)',
      borderBottom: `var(--size-focus-ring) solid ${selected ? 'var(--tab-selected)' : 'transparent'}`,
      background: pressed ? 'var(--surface-block)' : 'transparent',
      whiteSpace: 'nowrap',
      cursor: 'pointer',
      flex: '0 0 auto'
    }
  }, tab.label, typeof tab.count === 'number' ? /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-figure-xs)',
      marginLeft: 'var(--space-xxs)'
    }
  }, tab.count) : null);
}
function FilterTabs({
  tabs = [],
  selected,
  onSelect,
  ariaLabel = 'Filters'
}) {
  return /*#__PURE__*/React.createElement("div", {
    role: "tablist",
    "aria-label": ariaLabel,
    style: {
      display: 'flex',
      overflowX: 'auto',
      borderBottom: 'var(--size-hairline) solid var(--border-hairline)',
      scrollbarWidth: 'none'
    }
  }, tabs.map(t => /*#__PURE__*/React.createElement(Tab, {
    key: t.id,
    tab: t,
    selected: t.id === selected,
    onSelect: onSelect
  })));
}
Object.assign(__ds_scope, { FilterTabs });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/FilterTabs.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Footer.jsx
try { (() => {
function Footer({
  attributions = [],
  team = 'CDU IT Code Fair 2026 · Data Innovation Challenge · Team DIC005',
  statement = 'Crosscheck does not measure signal.'
}) {
  return /*#__PURE__*/React.createElement("footer", {
    style: {
      borderTop: 'var(--size-hairline) solid var(--border-hairline)',
      padding: 'var(--space-lg) var(--space-md)',
      font: 'var(--text-caption)',
      color: 'var(--text-secondary)',
      display: 'grid',
      gap: 'var(--space-xs)'
    }
  }, attributions.map((a, i) => /*#__PURE__*/React.createElement("span", {
    key: i
  }, /*#__PURE__*/React.createElement(__ds_scope.Figures, {
    text: a,
    size: "xs"
  }))), /*#__PURE__*/React.createElement("span", {
    style: {
      marginTop: 'var(--space-xs)'
    }
  }, team), /*#__PURE__*/React.createElement("span", null, statement));
}
Object.assign(__ds_scope, { Footer });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Footer.jsx", error: String((e && e.message) || e) }); }

// components/navigation/TopBar.jsx
try { (() => {
function OfflineChip({
  offline = true
}) {
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      height: 'var(--size-chip)',
      padding: '0 var(--space-sm)',
      borderRadius: 'var(--radius-pill)',
      font: 'var(--text-label)',
      color: 'var(--text-body)',
      background: 'var(--surface-block)',
      whiteSpace: 'nowrap'
    }
  }, offline ? 'Offline' : 'Online');
}
function TopBar({
  title = 'Crosscheck',
  offline = true,
  sticky = true,
  children
}) {
  return /*#__PURE__*/React.createElement("header", {
    style: {
      position: sticky ? 'sticky' : 'static',
      top: 0,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: 'var(--space-sm)',
      height: 'var(--size-topbar)',
      padding: '0 var(--space-md)',
      background: 'var(--surface-page)',
      borderBottom: 'var(--size-hairline) solid var(--border-hairline)',
      color: 'var(--text-heading)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-title-sm)'
    }
  }, title), children ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-xs)'
    }
  }, children) : null, /*#__PURE__*/React.createElement(OfflineChip, {
    offline: offline
  }));
}
Object.assign(__ds_scope, { OfflineChip, TopBar });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/TopBar.jsx", error: String((e && e.message) || e) }); }

// components/search/SearchInput.jsx
try { (() => {
const {
  useState
} = React;
function ResultRow({
  result,
  onSelect,
  query = ''
}) {
  const [pressed, setPressed] = useState(false);
  const alias = query && result.aliases ? result.aliases.find(a => a.toLowerCase().includes(query.toLowerCase())) : null;
  return /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: () => onSelect && onSelect(result),
    onPointerDown: () => setPressed(true),
    onPointerUp: () => setPressed(false),
    onPointerLeave: () => setPressed(false),
    style: {
      display: 'block',
      width: '100%',
      textAlign: 'left',
      minHeight: 'var(--size-touch)',
      padding: 'var(--space-sm) var(--space-md)',
      borderBottom: 'var(--size-hairline) solid var(--border-hairline-soft)',
      background: pressed ? 'var(--surface-block)' : 'var(--surface-page)',
      cursor: 'pointer'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      font: 'var(--text-body-md)',
      color: 'var(--text-heading)'
    }
  }, result.name, alias ? /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-caption)',
      color: 'var(--text-secondary)'
    }
  }, " also ", alias) : null), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      font: 'var(--text-caption)',
      color: 'var(--text-secondary)'
    }
  }, result.region || 'Region not recorded', " \xB7 ", /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-figure-xs)'
    }
  }, typeof result.population === 'number' ? result.population.toLocaleString('en-AU') : 'Not recorded'), " people"));
}
function SearchInput({
  value = '',
  onChange,
  placeholder = 'Search 96 communities',
  results = [],
  onSelect,
  label = 'Search communities'
}) {
  const [focused, setFocused] = useState(false);
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("input", {
    type: "search",
    value: value,
    "aria-label": label,
    placeholder: placeholder,
    autoComplete: "off",
    onChange: e => onChange && onChange(e.target.value),
    onFocus: () => setFocused(true),
    onBlur: () => setFocused(false),
    style: {
      display: 'block',
      width: '100%',
      boxSizing: 'border-box',
      height: 'var(--size-control)',
      padding: '0 var(--space-sm)',
      font: 'var(--text-body-md)',
      color: 'var(--text-heading)',
      background: 'var(--surface-page)',
      border: `var(--size-hairline) solid ${focused ? 'var(--text-heading)' : 'var(--border-hairline)'}`,
      borderRadius: 'var(--radius-md)',
      appearance: 'none',
      WebkitAppearance: 'none'
    }
  }), results.length ? /*#__PURE__*/React.createElement("div", {
    role: "listbox",
    style: {
      marginTop: 'var(--space-xs)',
      border: 'var(--size-hairline) solid var(--border-hairline)',
      borderRadius: 'var(--radius-sm)',
      overflow: 'hidden'
    }
  }, results.map(r => /*#__PURE__*/React.createElement(ResultRow, {
    key: r.id || r.name,
    result: r,
    onSelect: onSelect,
    query: value
  }))) : null);
}
Object.assign(__ds_scope, { ResultRow, SearchInput });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/search/SearchInput.jsx", error: String((e && e.message) || e) }); }

// components/services/AssumptionNote.jsx
try { (() => {
function AssumptionNote({
  children,
  text,
  label = 'Assumption'
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      margin: '0 var(--space-md) var(--space-sm)',
      padding: 'var(--space-sm) var(--space-md)',
      background: 'var(--surface-block)',
      borderLeft: 'var(--size-rule) solid var(--verdict-degraded-text)',
      borderRadius: 'var(--radius-xs)',
      font: 'var(--text-body-sm)',
      color: 'var(--text-body)',
      textWrap: 'pretty'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-label)',
      color: 'var(--text-heading)'
    }
  }, label, " "), text ? /*#__PURE__*/React.createElement(__ds_scope.Figures, {
    text: text,
    size: "sm"
  }) : children);
}
Object.assign(__ds_scope, { AssumptionNote });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/services/AssumptionNote.jsx", error: String((e && e.message) || e) }); }

// components/services/ServiceRow.jsx
try { (() => {
const {
  useState
} = React;
function ServiceRow({
  service,
  verdict = 'nodata',
  reason,
  sources = [],
  path,
  defaultExpanded = false,
  children
}) {
  const [open, setOpen] = useState(defaultExpanded);
  const [pressed, setPressed] = useState(false);
  return /*#__PURE__*/React.createElement("div", {
    style: {
      borderBottom: 'var(--size-hairline) solid var(--border-hairline)'
    }
  }, /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-expanded": open,
    onClick: () => setOpen(!open),
    onPointerDown: () => setPressed(true),
    onPointerUp: () => setPressed(false),
    onPointerLeave: () => setPressed(false),
    style: {
      display: 'block',
      width: '100%',
      textAlign: 'left',
      minHeight: 'var(--size-touch)',
      padding: 'var(--space-sm) var(--space-md)',
      background: pressed ? 'var(--surface-block)' : 'var(--surface-page)',
      cursor: 'pointer'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: 'var(--space-sm)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-title-sm)',
      color: 'var(--text-heading)'
    }
  }, service), /*#__PURE__*/React.createElement(__ds_scope.VerdictBadge, {
    verdict: verdict
  })), reason ? /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      font: 'var(--text-body-sm)',
      color: 'var(--text-body)',
      marginTop: 'var(--space-xxs)',
      textWrap: 'pretty'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Figures, {
    text: reason,
    size: "sm"
  })) : null), open ? /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-soft)',
      padding: 'var(--space-sm) var(--space-md)',
      display: 'grid',
      gap: 'var(--space-xxs)'
    }
  }, sources.length ? sources.map((s, i) => /*#__PURE__*/React.createElement(__ds_scope.SourceLine, {
    key: i,
    label: s.label,
    source: s.source,
    date: s.date
  })) : /*#__PURE__*/React.createElement(__ds_scope.SourceLine, {
    label: "Sources:"
  }), path ? /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-caption)',
      color: 'var(--text-secondary)'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Figures, {
    text: path,
    size: "xs"
  })) : null) : null, children);
}
Object.assign(__ds_scope, { ServiceRow });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/services/ServiceRow.jsx", error: String((e && e.message) || e) }); }

// components/share/qr.js
try { (() => {
// Minimal QR encoder: byte mode, versions 1–10, EC level L or M, mask 0. Returns a boolean matrix (true = dark).
const TABLE = {
  L: {
    data: [19, 34, 55, 80, 108, 136, 156, 194, 232, 274],
    ec: [7, 10, 15, 20, 26, 18, 20, 24, 30, 18],
    blocks: [1, 1, 1, 1, 1, 2, 2, 2, 2, 4]
  },
  M: {
    data: [16, 28, 44, 64, 86, 108, 124, 154, 182, 216],
    ec: [10, 16, 26, 18, 24, 16, 18, 22, 22, 26],
    blocks: [1, 1, 1, 2, 2, 4, 4, 4, 5, 5]
  }
};
const ECBITS = {
  L: 1,
  M: 0
};
const VERSION_BITS = [0, 0, 0, 0, 0, 0, 0, 0x07c94, 0x085bc, 0x09a99, 0x0a4d3];
const ALIGN = [[], [], [6, 18], [6, 22], [6, 26], [6, 30], [6, 34], [6, 22, 38], [6, 24, 42], [6, 26, 46], [6, 28, 50]];
function gfMul(a, b) {
  let r = 0;
  while (b) {
    if (b & 1) r ^= a;
    a <<= 1;
    if (a & 0x100) a ^= 0x11d;
    b >>= 1;
  }
  return r;
}
function rsGenerator(n) {
  let g = [1],
    root = 1;
  for (let i = 0; i < n; i++) {
    const ng = new Array(g.length + 1).fill(0);
    for (let j = 0; j < g.length; j++) {
      ng[j] ^= g[j];
      ng[j + 1] ^= gfMul(g[j], root);
    }
    g = ng;
    root = gfMul(root, 2);
  }
  return g;
}
function rsEncode(data, n) {
  const g = rsGenerator(n),
    res = new Array(n).fill(0);
  for (const b of data) {
    const f = b ^ res.shift();
    res.push(0);
    for (let j = 0; j < n; j++) res[j] ^= gfMul(g[j + 1], f);
  }
  return res;
}
function utf8(text) {
  return Array.from(new TextEncoder().encode(text));
}
function formatBits(level) {
  const data = ECBITS[level] << 3 | 0; // mask 0
  let r = data << 10;
  for (let i = 14; i >= 10; i--) if (r >> i & 1) r ^= 0x537 << i - 10;
  return (data << 10 | r) ^ 0x5412;
}
function qrModules(text, level = 'M') {
  const bytes = utf8(text),
    t = TABLE[level] || TABLE.M;
  let v = 0;
  for (let i = 1; i <= 10; i++) {
    const cc = i < 10 ? 8 : 16;
    if (t.data[i - 1] * 8 >= 4 + cc + bytes.length * 8) {
      v = i;
      break;
    }
  }
  if (!v) throw new Error('qr: text too long for versions 1-10');
  const cap = t.data[v - 1] * 8,
    cc = v < 10 ? 8 : 16,
    bits = [];
  const push = (val, n) => {
    for (let i = n - 1; i >= 0; i--) bits.push(val >> i & 1);
  };
  push(4, 4);
  push(bytes.length, cc);
  bytes.forEach(b => push(b, 8));
  push(0, Math.min(4, cap - bits.length));
  while (bits.length % 8) bits.push(0);
  for (let p = 0xec; bits.length < cap; p ^= 0xec ^ 0x11) push(p, 8);
  const data = [];
  for (let i = 0; i < bits.length; i += 8) data.push(parseInt(bits.slice(i, i + 8).join(''), 2));
  // blocks
  const nb = t.blocks[v - 1],
    ec = t.ec[v - 1],
    short = Math.floor(data.length / nb),
    longCount = data.length % nb;
  const blocks = [],
    ecs = [];
  let off = 0;
  for (let b = 0; b < nb; b++) {
    const len = short + (b >= nb - longCount ? 1 : 0);
    const d = data.slice(off, off + len);
    off += len;
    blocks.push(d);
    ecs.push(rsEncode(d, ec));
  }
  const out = [];
  for (let i = 0; i <= short; i++) for (const d of blocks) if (i < d.length) out.push(d[i]);
  for (let i = 0; i < ec; i++) for (const e of ecs) out.push(e[i]);
  // matrix
  const size = 17 + 4 * v;
  const m = Array.from({
    length: size
  }, () => new Array(size).fill(false));
  const fn = Array.from({
    length: size
  }, () => new Array(size).fill(false));
  const set = (x, y, dark) => {
    if (x >= 0 && y >= 0 && x < size && y < size) {
      m[y][x] = dark;
      fn[y][x] = true;
    }
  };
  const finder = (cx, cy) => {
    for (let dy = -4; dy <= 4; dy++) for (let dx = -4; dx <= 4; dx++) {
      const d = Math.max(Math.abs(dx), Math.abs(dy));
      set(cx + dx, cy + dy, d !== 2 && d !== 4);
    }
  };
  finder(3, 3);
  finder(size - 4, 3);
  finder(3, size - 4);
  for (let i = 0; i < size; i++) {
    if (!fn[6][i]) set(i, 6, i % 2 === 0);
    if (!fn[i][6]) set(6, i, i % 2 === 0);
  }
  const al = ALIGN[v],
    last = al.length - 1;
  al.forEach((a, i) => al.forEach((b, j) => {
    if (i === 0 && j === 0 || i === 0 && j === last || i === last && j === 0) return;
    for (let dy = -2; dy <= 2; dy++) for (let dx = -2; dx <= 2; dx++) set(a + dx, b + dy, Math.max(Math.abs(dx), Math.abs(dy)) !== 1);
  }));
  const drawFormat = () => {
    const f = formatBits(level),
      bit = i => (f >> i & 1) === 1;
    for (let i = 0; i <= 5; i++) set(8, i, bit(i));
    set(8, 7, bit(6));
    set(8, 8, bit(7));
    set(7, 8, bit(8));
    for (let i = 9; i < 15; i++) set(14 - i, 8, bit(i));
    for (let i = 0; i < 8; i++) set(size - 1 - i, 8, bit(i));
    for (let i = 8; i < 15; i++) set(8, size - 15 + i, bit(i));
    set(8, size - 8, true);
  };
  drawFormat();
  if (v >= 7) {
    const vb = VERSION_BITS[v];
    for (let i = 0; i < 18; i++) {
      const bit = (vb >> i & 1) === 1,
        a = size - 11 + i % 3,
        b = Math.floor(i / 3);
      set(a, b, bit);
      set(b, a, bit);
    }
  }
  // data placement
  let i = 0;
  const total = out.length * 8;
  for (let right = size - 1; right >= 1; right -= 2) {
    if (right === 6) right = 5;
    for (let vert = 0; vert < size; vert++) for (let j = 0; j < 2; j++) {
      const x = right - j,
        upward = (right + 1 & 2) === 0,
        y = upward ? size - 1 - vert : vert;
      if (!fn[y][x] && i < total) {
        m[y][x] = (out[i >> 3] >> 7 - (i & 7) & 1) === 1;
        i++;
      }
    }
  }
  // mask 0
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) if (!fn[y][x] && (x + y) % 2 === 0) m[y][x] = !m[y][x];
  return m;
}
Object.assign(__ds_scope, { qrModules });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/share/qr.js", error: String((e && e.message) || e) }); }

// components/share/QrCode.jsx
try { (() => {
const {
  useMemo
} = React;
// Inline-SVG QR code: ink modules on canvas, 4-module quiet zone, one <path> so the DOM stays small.
function QrCode({
  text = '',
  modules,
  level = 'M',
  size = 'var(--size-qr)',
  label = 'QR code'
}) {
  const m = useMemo(() => modules || (text ? __ds_scope.qrModules(text, level) : null), [text, modules, level]);
  if (!m) return null;
  const n = m.length,
    q = 4,
    d = [];
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) if (m[y][x]) d.push(`M${x + q} ${y + q}h1v1h-1z`);
  return /*#__PURE__*/React.createElement("svg", {
    role: "img",
    "aria-label": label,
    viewBox: `0 0 ${n + 2 * q} ${n + 2 * q}`,
    width: size,
    height: size,
    shapeRendering: "crispEdges",
    style: {
      display: 'block',
      background: 'var(--surface-page)'
    }
  }, /*#__PURE__*/React.createElement("path", {
    d: d.join(''),
    fill: "var(--text-heading)"
  }));
}
Object.assign(__ds_scope, { QrCode });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/share/QrCode.jsx", error: String((e && e.message) || e) }); }

// components/share/ShareCard.jsx
try { (() => {
function ShareCard({
  qrText,
  qrModules,
  packDate,
  packSize,
  appSize,
  buildSource = 'Crosscheck build',
  onShare,
  onSave,
  shareLabel = 'Share this app',
  saveLabel = 'Save file',
  statement = "Crosscheck shows what published sources say about a community's connectivity and what that allows. It does not measure signal. Every value shows its source and date."
}) {
  const fig = {
    font: 'var(--text-figure-sm)',
    whiteSpace: 'nowrap'
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-page)',
      border: 'var(--size-hairline) solid var(--border-hairline)',
      borderRadius: 'var(--radius-lg)',
      padding: 'var(--space-lg)',
      display: 'grid',
      gap: 'var(--space-md)',
      color: 'var(--text-body)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'center'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.QrCode, {
    text: qrText,
    modules: qrModules,
    label: "QR code that opens Crosscheck on another phone"
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-body-sm)',
      display: 'grid',
      gap: 'var(--space-xxs)'
    }
  }, /*#__PURE__*/React.createElement("div", null, "Data pack ", /*#__PURE__*/React.createElement("span", {
    style: fig
  }, packDate || 'Not recorded'), packSize ? /*#__PURE__*/React.createElement(React.Fragment, null, " \xB7 ", /*#__PURE__*/React.createElement("span", {
    style: fig
  }, packSize)) : null), appSize ? /*#__PURE__*/React.createElement("div", null, "App ", /*#__PURE__*/React.createElement("span", {
    style: fig
  }, appSize)) : null, /*#__PURE__*/React.createElement(__ds_scope.SourceLine, {
    source: buildSource,
    date: packDate
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-xs)'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Button, {
    fullWidth: true,
    onClick: onShare
  }, shareLabel), /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "secondary",
    fullWidth: true,
    onClick: onSave
  }, saveLabel)), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: 'var(--text-body-sm)',
      textWrap: 'pretty'
    }
  }, statement));
}
Object.assign(__ds_scope, { ShareCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/share/ShareCard.jsx", error: String((e && e.message) || e) }); }

__ds_ns.AgreementHeadline = __ds_scope.AgreementHeadline;

__ds_ns.CommunityHeader = __ds_scope.CommunityHeader;

__ds_ns.KindChip = __ds_scope.KindChip;

__ds_ns.PublisherRow = __ds_scope.PublisherRow;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Chip = __ds_scope.Chip;

__ds_ns.Figures = __ds_scope.Figures;

__ds_ns.SourceLine = __ds_scope.SourceLine;

__ds_ns.VERDICTS = __ds_scope.VERDICTS;

__ds_ns.VerdictBadge = __ds_scope.VerdictBadge;

__ds_ns.MapLegend = __ds_scope.MapLegend;

__ds_ns.NtMap = __ds_scope.NtMap;

__ds_ns.FilterTabs = __ds_scope.FilterTabs;

__ds_ns.Footer = __ds_scope.Footer;

__ds_ns.OfflineChip = __ds_scope.OfflineChip;

__ds_ns.TopBar = __ds_scope.TopBar;

__ds_ns.ResultRow = __ds_scope.ResultRow;

__ds_ns.SearchInput = __ds_scope.SearchInput;

__ds_ns.AssumptionNote = __ds_scope.AssumptionNote;

__ds_ns.ServiceRow = __ds_scope.ServiceRow;

__ds_ns.QrCode = __ds_scope.QrCode;

__ds_ns.ShareCard = __ds_scope.ShareCard;

})();
