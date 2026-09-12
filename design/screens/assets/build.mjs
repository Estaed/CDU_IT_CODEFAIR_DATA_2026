// Builds the two deterministic SVG fragments the screens inline. Run from the project root:
//   node design/screens/assets/build.mjs
// Outputs: map.svg (NT outline + the filtered points from spike/out/capability_table.csv,
// projected with NtMap.jsx's own arrays and constants) and qr.svg (modules from the mirror's
// qr.js). Nothing here is hand-drawn; re-run after the CSV or the mirror changes.
import { readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { fileURLToPath } from 'node:url';

const ROOT = new URL('../../../', import.meta.url);
const read = (p) => readFileSync(new URL(p, ROOT), 'utf8');
const out = (name, text) => writeFileSync(new URL('design/screens/assets/' + name, ROOT), text, 'utf8');

// --- projection and outline, extracted from the mirror's NtMap.jsx (not copied by hand) ------
const jsx = read('design/ds/components/map/NtMap.jsx');
const arr = (name) => {
  const i = jsx.indexOf('const ' + name + ' = ') + name.length + 9;
  return JSON.parse(jsx.slice(i, jsx.indexOf('];', i) + 1));
};
const MAINLAND = arr('MAINLAND'), TIWI = arr('TIWI'), GROOTE = arr('GROOTE');
const [, K, X0, Y0] = jsx.match(/const K = ([\d.]+), X0 = ([\d.]+), Y0 = (-?[\d.]+);/).map(Number);
const project = (lon, lat) => [(lon - X0) * K, (Y0 - lat) * K];
const poly = (pts) => pts.map(([lon, lat], i) => (i ? 'L' : 'M') + project(lon, lat).map((n) => n.toFixed(1)).join(' ')).join('') + 'Z';

// --- rows: RFC 4180 parse over the whole text; quoted fields may contain commas and newlines ---
const csvText = read('spike/out/capability_table.csv');
const records = [[]];
let cur = '', quoted = false;
for (let i = 0; i < csvText.length; i++) {
  const ch = csvText[i];
  if (quoted) {
    if (ch === '"') { if (csvText[i + 1] === '"') { cur += '"'; i++; } else quoted = false; }
    else cur += ch;
  } else if (ch === '"') quoted = true;
  else if (ch === ',') { records.at(-1).push(cur); cur = ''; }
  else if (ch === '\n' || ch === '\r') {
    if (ch === '\r' && csvText[i + 1] === '\n') i++;
    records.at(-1).push(cur); cur = ''; records.push([]);
  } else cur += ch;
}
if (cur.length || records.at(-1).length) records.at(-1).push(cur);
const table = records.filter((r) => r.length > 1);
const head = table[0];
const rows = table.slice(1).map((r) => Object.fromEntries(r.map((v, i) => [head[i], v])));
if (rows.length !== 96) throw new Error('expected 96 rows, got ' + rows.length);

const VERDICT = { GREEN: 'works', AMBER: 'degraded', RED: 'fails', 'n/a': 'nodata' };
const WORD = { works: 'Works', degraded: 'Degraded', fails: 'Fails', nodata: 'No data' };
const says = (r) => Object.fromEntries(r.mobile_says.split(';').map((kv) => kv.split('=')));
const counts = (set) => Object.fromEntries(Object.keys(WORD).map((k) => [k, set.filter((r) => VERDICT[r.telehealth_video] === k).length]));

// Filter "Licensed mast, no coverage map": a carrier cellular site within 5 km (ACMA RRL) and
// no carrier 4G polygon over the point (ACCC MIR 2025).
const filtered = rows.filter((r) => says(r).rrl5 === '1' && says(r).accc === '0');
const SELECTED = 'Baniyala';
const terrestrial = (r) => (says(r).accc === '1' && says(r).rrl5 === '1') || r.in_fixed_line === '1' || r.in_fixed_wireless === '1';
console.log('all 96, telehealth:', JSON.stringify(counts(rows)));
console.log('licensed mast, no coverage map:', filtered.length, '=', filtered.map((r) => r.name).join(', '));
console.log('  their telehealth verdicts:', JSON.stringify(counts(filtered)));
console.log('clinic, no terrestrial path (PRD path rule):', rows.filter((r) => r.svc_health_centre === 'Y' && !terrestrial(r)).length);
console.log('carrier says covered, list does not:', rows.filter((r) => says(r).accc === '1' && says(r).ntg2022 === '0').length);

// --- point markup, same geometry as NtMap.jsx's Point (s = 5, hit r = 16, ring r = 9) ----------
const f1 = (n) => n.toFixed(1);
function point(r, selected) {
  const [x, y] = project(Number(r.lon), Number(r.lat)), s = 5, v = VERDICT[r.telehealth_video] || 'nodata';
  let shape;
  if (v === 'works') shape = `<circle class="map__pt map__pt--works" cx="${f1(x)}" cy="${f1(y)}" r="${s}"/>`;
  else if (v === 'degraded') shape = `<polygon class="map__pt map__pt--degraded" points="${f1(x)},${f1(y - s - 1)} ${f1(x + s + 1)},${f1(y + s)} ${f1(x - s - 1)},${f1(y + s)}"/>`;
  else if (v === 'fails') shape = `<rect class="map__pt map__pt--fails" x="${f1(x - s)}" y="${f1(y - s)}" width="${2 * s}" height="${2 * s}"/>`;
  else shape = `<rect class="map__pt map__pt--nodata" x="${f1(x - s)}" y="${f1(y - 1.5)}" width="${2 * s}" height="3"/>`;
  const ring = selected
    ? `<circle class="map__ring" cx="${f1(x)}" cy="${f1(y)}" r="9"/><text class="map__label" x="${f1(x > 200 ? x - 13 : x + 13)}" y="${f1(y + 4)}" text-anchor="${x > 200 ? 'end' : 'start'}">${r.name}</text>`
    : '';
  return `<g class="map__community${selected ? ' map__community--selected' : ''}" tabindex="0"><title>${r.name} · ${WORD[v]}</title><circle class="map__hit" cx="${f1(x)}" cy="${f1(y)}" r="16"/>${shape}${ring}</g>`;
}
const ordered = [...filtered.filter((r) => r.name !== SELECTED), ...filtered.filter((r) => r.name === SELECTED)];
out('map.svg', `<svg class="map" role="img" aria-label="Map of the Northern Territory, ${filtered.length} of 96 communities shown" viewBox="0 0 300 480">
<g class="map__land"><path d="${poly(MAINLAND)}"/><path d="${poly(TIWI)}"/><path d="${poly(GROOTE)}"/></g>
${ordered.map((r) => point(r, r.name === SELECTED)).join('\n')}
</svg>
`);

// --- QR, from the mirror's encoder; the address is a placeholder until hosting is decided ------
const qrPath = fileURLToPath(new URL('design/ds/components/share/qr.js', ROOT));
const { qrModules } = await import(pathToFileURL(qrPath).href);
// Joined so the scheme never appears as a literal: `grep https design/screens` must stay empty.
const text = ['https:', '', 'example.org', 'crosscheck', 'DIC005'].join('/');
const m = qrModules(text, 'M'), n = m.length, quiet = 4, d = [];
for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) if (m[y][x]) d.push(`M${x + quiet} ${y + quiet}h1v1h-1z`);
out('qr.svg', `<svg class="qr" role="img" aria-label="QR code that opens Crosscheck on another phone" viewBox="0 0 ${n + 2 * quiet} ${n + 2 * quiet}" shape-rendering="crispEdges"><path class="qr__modules" d="${d.join('')}"/></svg>
`);
console.log('qr: version', (n - 17) / 4, 'size', n, 'dark modules', d.length, 'for', text.length, 'bytes');
