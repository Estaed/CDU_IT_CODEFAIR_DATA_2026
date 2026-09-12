// Minimal QR encoder: byte mode, versions 1–10, EC level L or M, mask 0. Returns a boolean matrix (true = dark).
const TABLE = {
  L: { data: [19, 34, 55, 80, 108, 136, 156, 194, 232, 274], ec: [7, 10, 15, 20, 26, 18, 20, 24, 30, 18], blocks: [1, 1, 1, 1, 1, 2, 2, 2, 2, 4] },
  M: { data: [16, 28, 44, 64, 86, 108, 124, 154, 182, 216], ec: [10, 16, 26, 18, 24, 16, 18, 22, 22, 26], blocks: [1, 1, 1, 2, 2, 4, 4, 4, 5, 5] },
};
const ECBITS = { L: 1, M: 0 };
const VERSION_BITS = [0, 0, 0, 0, 0, 0, 0, 0x07c94, 0x085bc, 0x09a99, 0x0a4d3];
const ALIGN = [[], [], [6, 18], [6, 22], [6, 26], [6, 30], [6, 34], [6, 22, 38], [6, 24, 42], [6, 26, 46], [6, 28, 50]];

function gfMul(a, b) { let r = 0; while (b) { if (b & 1) r ^= a; a <<= 1; if (a & 0x100) a ^= 0x11d; b >>= 1; } return r; }
function rsGenerator(n) {
  let g = [1], root = 1;
  for (let i = 0; i < n; i++) {
    const ng = new Array(g.length + 1).fill(0);
    for (let j = 0; j < g.length; j++) { ng[j] ^= g[j]; ng[j + 1] ^= gfMul(g[j], root); }
    g = ng; root = gfMul(root, 2);
  }
  return g;
}
function rsEncode(data, n) {
  const g = rsGenerator(n), res = new Array(n).fill(0);
  for (const b of data) { const f = b ^ res.shift(); res.push(0); for (let j = 0; j < n; j++) res[j] ^= gfMul(g[j + 1], f); }
  return res;
}
function utf8(text) { return Array.from(new TextEncoder().encode(text)); }
function formatBits(level) {
  const data = (ECBITS[level] << 3) | 0; // mask 0
  let r = data << 10;
  for (let i = 14; i >= 10; i--) if ((r >> i) & 1) r ^= 0x537 << (i - 10);
  return ((data << 10) | r) ^ 0x5412;
}

export function qrModules(text, level = 'M') {
  const bytes = utf8(text), t = TABLE[level] || TABLE.M;
  let v = 0;
  for (let i = 1; i <= 10; i++) { const cc = i < 10 ? 8 : 16; if (t.data[i - 1] * 8 >= 4 + cc + bytes.length * 8) { v = i; break; } }
  if (!v) throw new Error('qr: text too long for versions 1-10');
  const cap = t.data[v - 1] * 8, cc = v < 10 ? 8 : 16, bits = [];
  const push = (val, n) => { for (let i = n - 1; i >= 0; i--) bits.push((val >> i) & 1); };
  push(4, 4); push(bytes.length, cc); bytes.forEach((b) => push(b, 8));
  push(0, Math.min(4, cap - bits.length));
  while (bits.length % 8) bits.push(0);
  for (let p = 0xec; bits.length < cap; p ^= 0xec ^ 0x11) push(p, 8);
  const data = []; for (let i = 0; i < bits.length; i += 8) data.push(parseInt(bits.slice(i, i + 8).join(''), 2));
  // blocks
  const nb = t.blocks[v - 1], ec = t.ec[v - 1], short = Math.floor(data.length / nb), longCount = data.length % nb;
  const blocks = [], ecs = []; let off = 0;
  for (let b = 0; b < nb; b++) { const len = short + (b >= nb - longCount ? 1 : 0); const d = data.slice(off, off + len); off += len; blocks.push(d); ecs.push(rsEncode(d, ec)); }
  const out = [];
  for (let i = 0; i <= short; i++) for (const d of blocks) if (i < d.length) out.push(d[i]);
  for (let i = 0; i < ec; i++) for (const e of ecs) out.push(e[i]);
  // matrix
  const size = 17 + 4 * v;
  const m = Array.from({ length: size }, () => new Array(size).fill(false));
  const fn = Array.from({ length: size }, () => new Array(size).fill(false));
  const set = (x, y, dark) => { if (x >= 0 && y >= 0 && x < size && y < size) { m[y][x] = dark; fn[y][x] = true; } };
  const finder = (cx, cy) => { for (let dy = -4; dy <= 4; dy++) for (let dx = -4; dx <= 4; dx++) { const d = Math.max(Math.abs(dx), Math.abs(dy)); set(cx + dx, cy + dy, d !== 2 && d !== 4); } };
  finder(3, 3); finder(size - 4, 3); finder(3, size - 4);
  for (let i = 0; i < size; i++) { if (!fn[6][i]) set(i, 6, i % 2 === 0); if (!fn[i][6]) set(6, i, i % 2 === 0); }
  const al = ALIGN[v], last = al.length - 1;
  al.forEach((a, i) => al.forEach((b, j) => {
    if ((i === 0 && j === 0) || (i === 0 && j === last) || (i === last && j === 0)) return;
    for (let dy = -2; dy <= 2; dy++) for (let dx = -2; dx <= 2; dx++) set(a + dx, b + dy, Math.max(Math.abs(dx), Math.abs(dy)) !== 1);
  }));
  const drawFormat = () => {
    const f = formatBits(level), bit = (i) => ((f >> i) & 1) === 1;
    for (let i = 0; i <= 5; i++) set(8, i, bit(i));
    set(8, 7, bit(6)); set(8, 8, bit(7)); set(7, 8, bit(8));
    for (let i = 9; i < 15; i++) set(14 - i, 8, bit(i));
    for (let i = 0; i < 8; i++) set(size - 1 - i, 8, bit(i));
    for (let i = 8; i < 15; i++) set(8, size - 15 + i, bit(i));
    set(8, size - 8, true);
  };
  drawFormat();
  if (v >= 7) { const vb = VERSION_BITS[v]; for (let i = 0; i < 18; i++) { const bit = ((vb >> i) & 1) === 1, a = size - 11 + (i % 3), b = Math.floor(i / 3); set(a, b, bit); set(b, a, bit); } }
  // data placement
  let i = 0; const total = out.length * 8;
  for (let right = size - 1; right >= 1; right -= 2) {
    if (right === 6) right = 5;
    for (let vert = 0; vert < size; vert++) for (let j = 0; j < 2; j++) {
      const x = right - j, upward = ((right + 1) & 2) === 0, y = upward ? size - 1 - vert : vert;
      if (!fn[y][x] && i < total) { m[y][x] = ((out[i >> 3] >> (7 - (i & 7))) & 1) === 1; i++; }
    }
  }
  // mask 0
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) if (!fn[y][x] && (x + y) % 2 === 0) m[y][x] = !m[y][x];
  return m;
}
