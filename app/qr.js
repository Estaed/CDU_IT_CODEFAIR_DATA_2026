"use strict";

// A runtime QR encoder, byte mode only, levels L and M: the transfer frames (Task-18) need
// to encode bytes the phone only knows at runtime, which the build-time Python QR
// (scripts/build_app.py: qr_svg) cannot do.
// Ported from the Python `qrcode` package (main.py: best_fit, best_mask_pattern, makeImpl;
// util.py: lost_point, mask functions, create_data, create_bytes; base.py: RS_BLOCK_TABLE,
// rs_blocks) so the two encoders agree module for module (CLAUDE.md Part 2, layer rule 7).
window.CrosscheckQR = (() => {
  const MODE_8BIT_BYTE = 4;
  const LEVEL_BITS = { L: 1, M: 0 };

  // Reed-Solomon over GF(256), the field this format's generator polynomials use.
  const EXP_TABLE = new Array(256);
  const LOG_TABLE = new Array(256);
  for (let i = 0; i < 8; i++) EXP_TABLE[i] = 1 << i;
  for (let i = 8; i < 256; i++) {
    EXP_TABLE[i] = EXP_TABLE[i - 4] ^ EXP_TABLE[i - 5] ^ EXP_TABLE[i - 6] ^ EXP_TABLE[i - 8];
  }
  for (let i = 0; i < 255; i++) LOG_TABLE[EXP_TABLE[i]] = i;

  const glog = (n) => {
    if (n < 1) throw new Error(`glog(${n})`);
    return LOG_TABLE[n];
  };
  const gexp = (n) => EXP_TABLE[((n % 255) + 255) % 255];

  // A polynomial over GF(256), most-significant coefficient first, matching qrcode/base.py.
  class Poly {
    constructor(num, shift) {
      if (num.length === 0) throw new Error("empty polynomial");
      let offset = 0;
      while (offset < num.length && num[offset] === 0) offset += 1;
      const start = offset < num.length ? offset : num.length - 1;
      this.num = num.slice(start).concat(new Array(shift).fill(0));
    }

    get(i) {
      return this.num[i];
    }

    get size() {
      return this.num.length;
    }

    mul(other) {
      const out = new Array(this.size + other.size - 1).fill(0);
      for (let i = 0; i < this.size; i++) {
        for (let j = 0; j < other.size; j++) {
          out[i + j] ^= gexp(glog(this.num[i]) + glog(other.num[j]));
        }
      }
      return new Poly(out, 0);
    }

    mod(other) {
      const difference = this.size - other.size;
      if (difference < 0) return this;
      const ratio = glog(this.num[0]) - glog(other.num[0]);
      const out = new Array(other.size);
      for (let i = 0; i < other.size; i++) {
        out[i] = this.num[i] ^ gexp(glog(other.num[i]) + ratio);
      }
      if (difference) {
        for (let i = other.size; i < this.size; i++) out.push(this.num[i]);
      }
      return new Poly(out, 0).mod(other);
    }
  }

  // Data codeword counts per block, levels L and M only, one row per version 1..40, groups
  // of (block count, total codewords, data codewords). Values copied from qrcode/base.py:
  // RS_BLOCK_TABLE, the L and M columns; they are data, not code.
  const RS_BLOCKS = {
    L: [
      [1, 26, 19], [1, 44, 34], [1, 70, 55], [1, 100, 80], [1, 134, 108], [2, 86, 68],
      [2, 98, 78], [2, 121, 97], [2, 146, 116], [2, 86, 68, 2, 87, 69], [4, 101, 81],
      [2, 116, 92, 2, 117, 93], [4, 133, 107], [3, 145, 115, 1, 146, 116],
      [5, 109, 87, 1, 110, 88], [5, 122, 98, 1, 123, 99], [1, 135, 107, 5, 136, 108],
      [5, 150, 120, 1, 151, 121], [3, 141, 113, 4, 142, 114], [3, 135, 107, 5, 136, 108],
      [4, 144, 116, 4, 145, 117], [2, 139, 111, 7, 140, 112], [4, 151, 121, 5, 152, 122],
      [6, 147, 117, 4, 148, 118], [8, 132, 106, 4, 133, 107], [10, 142, 114, 2, 143, 115],
      [8, 152, 122, 4, 153, 123], [3, 147, 117, 10, 148, 118], [7, 146, 116, 7, 147, 117],
      [5, 145, 115, 10, 146, 116], [13, 145, 115, 3, 146, 116], [17, 145, 115],
      [17, 145, 115, 1, 146, 116], [13, 145, 115, 6, 146, 116], [12, 151, 121, 7, 152, 122],
      [6, 151, 121, 14, 152, 122], [17, 152, 122, 4, 153, 123], [4, 152, 122, 18, 153, 123],
      [20, 147, 117, 4, 148, 118], [19, 148, 118, 6, 149, 119],
    ],
    M: [
      [1, 26, 16], [1, 44, 28], [1, 70, 44], [2, 50, 32], [2, 67, 43], [4, 43, 27],
      [4, 49, 31], [2, 60, 38, 2, 61, 39], [3, 58, 36, 2, 59, 37], [4, 69, 43, 1, 70, 44],
      [1, 80, 50, 4, 81, 51], [6, 58, 36, 2, 59, 37], [8, 59, 37, 1, 60, 38],
      [4, 64, 40, 5, 65, 41], [5, 65, 41, 5, 66, 42], [7, 73, 45, 3, 74, 46],
      [10, 74, 46, 1, 75, 47], [9, 69, 43, 4, 70, 44], [3, 70, 44, 11, 71, 45],
      [3, 67, 41, 13, 68, 42], [17, 68, 42], [17, 74, 46], [4, 75, 47, 14, 76, 48],
      [6, 73, 45, 14, 74, 46], [8, 75, 47, 13, 76, 48], [19, 74, 46, 4, 75, 47],
      [22, 73, 45, 3, 74, 46], [3, 73, 45, 23, 74, 46], [21, 73, 45, 7, 74, 46],
      [19, 75, 47, 10, 76, 48], [2, 74, 46, 29, 75, 47], [10, 74, 46, 23, 75, 47],
      [14, 74, 46, 21, 75, 47], [14, 74, 46, 23, 75, 47], [12, 75, 47, 26, 76, 48],
      [6, 75, 47, 34, 76, 48], [29, 74, 46, 14, 75, 47], [13, 74, 46, 32, 75, 47],
      [40, 75, 47, 7, 76, 48], [18, 75, 47, 31, 76, 48],
    ],
  };

  // Alignment pattern centre positions per version, versions 1..40. Copied from
  // qrcode/util.py: PATTERN_POSITION_TABLE; data, not code.
  const PATTERN_POSITION_TABLE = [
    [], [6, 18], [6, 22], [6, 26], [6, 30], [6, 34], [6, 22, 38], [6, 24, 42], [6, 26, 46],
    [6, 28, 50], [6, 30, 54], [6, 32, 58], [6, 34, 62], [6, 26, 46, 66], [6, 26, 48, 70],
    [6, 26, 50, 74], [6, 30, 54, 78], [6, 30, 56, 82], [6, 30, 58, 86], [6, 34, 62, 90],
    [6, 28, 50, 72, 94], [6, 26, 50, 74, 98], [6, 30, 54, 78, 102], [6, 28, 54, 80, 106],
    [6, 32, 58, 84, 110], [6, 30, 58, 86, 114], [6, 34, 62, 90, 118],
    [6, 26, 50, 74, 98, 122], [6, 30, 54, 78, 102, 126], [6, 26, 52, 78, 104, 130],
    [6, 30, 56, 82, 108, 134], [6, 34, 60, 86, 112, 138], [6, 30, 58, 86, 114, 142],
    [6, 34, 62, 90, 118, 146], [6, 30, 54, 78, 102, 126, 150], [6, 24, 50, 76, 102, 128, 154],
    [6, 28, 54, 80, 106, 132, 158], [6, 32, 58, 84, 110, 136, 162],
    [6, 26, 54, 82, 110, 138, 166], [6, 30, 58, 86, 114, 142, 170],
  ];

  const G15 = (1 << 10) | (1 << 8) | (1 << 5) | (1 << 4) | (1 << 2) | (1 << 1) | (1 << 0);
  const G18 =
    (1 << 12) | (1 << 11) | (1 << 10) | (1 << 9) | (1 << 8) | (1 << 5) | (1 << 2) | (1 << 0);
  const G15_MASK = (1 << 14) | (1 << 12) | (1 << 10) | (1 << 4) | (1 << 1);

  const bchDigit = (data) => {
    let digit = 0;
    while (data !== 0) {
      digit += 1;
      data >>>= 1;
    }
    return digit;
  };

  const bchTypeInfo = (data) => {
    let d = data << 10;
    while (bchDigit(d) - bchDigit(G15) >= 0) d ^= G15 << (bchDigit(d) - bchDigit(G15));
    return ((data << 10) | d) ^ G15_MASK;
  };

  const bchTypeNumber = (data) => {
    let d = data << 12;
    while (bchDigit(d) - bchDigit(G18) >= 0) d ^= G18 << (bchDigit(d) - bchDigit(G18));
    return (data << 12) | d;
  };

  const maskFunc = (pattern) => {
    switch (pattern) {
      case 0:
        return (i, j) => (i + j) % 2 === 0;
      case 1:
        return (i) => i % 2 === 0;
      case 2:
        return (i, j) => j % 3 === 0;
      case 3:
        return (i, j) => (i + j) % 3 === 0;
      case 4:
        return (i, j) => (Math.floor(i / 2) + Math.floor(j / 3)) % 2 === 0;
      case 5:
        return (i, j) => ((i * j) % 2) + ((i * j) % 3) === 0;
      case 6:
        return (i, j) => (((i * j) % 2) + ((i * j) % 3)) % 2 === 0;
      case 7:
        return (i, j) => (((i * j) % 3) + ((i + j) % 2)) % 2 === 0;
      default:
        throw new Error(`bad mask pattern: ${pattern}`);
    }
  };

  const charCountBits = (version) => (version < 10 ? 8 : 16);

  const rsBlocks = (version, level) => {
    const flat = RS_BLOCKS[level][version - 1];
    const blocks = [];
    for (let i = 0; i < flat.length; i += 3) {
      const [count, totalCount, dataCount] = [flat[i], flat[i + 1], flat[i + 2]];
      for (let k = 0; k < count; k++) blocks.push({ totalCount, dataCount });
    }
    return blocks;
  };

  const bitLimitForVersion = (version, level) =>
    rsBlocks(version, level).reduce((sum, b) => sum + b.dataCount * 8, 0);

  const bestVersion = (byteLength, level) => {
    for (let version = 1; version <= 40; version++) {
      const needed = 4 + charCountBits(version) + byteLength * 8;
      if (needed <= bitLimitForVersion(version, level)) return version;
    }
    throw new Error("data too large for a QR code");
  };

  // A bit-packed byte buffer, most-significant bit first, matching qrcode/util.py: BitBuffer.
  class BitBuffer {
    constructor() {
      this.bytes = [];
      this.length = 0;
    }

    put(num, len) {
      for (let i = 0; i < len; i++) this.putBit(((num >> (len - i - 1)) & 1) === 1);
    }

    putBit(bit) {
      const index = Math.floor(this.length / 8);
      if (this.bytes.length <= index) this.bytes.push(0);
      if (bit) this.bytes[index] |= 0x80 >> (this.length % 8);
      this.length += 1;
    }
  }

  const PAD0 = 0xec;
  const PAD1 = 0x11;

  const createBytes = (buffer, blocks) => {
    let offset = 0;
    let maxDc = 0;
    let maxEc = 0;
    const dcData = [];
    const ecData = [];
    for (const block of blocks) {
      const dcCount = block.dataCount;
      const ecCount = block.totalCount - dcCount;
      maxDc = Math.max(maxDc, dcCount);
      maxEc = Math.max(maxEc, ecCount);
      const currentDc = [];
      for (let i = 0; i < dcCount; i++) currentDc.push(buffer.bytes[i + offset] & 0xff);
      offset += dcCount;

      let rsPoly = new Poly([1], 0);
      for (let i = 0; i < ecCount; i++) rsPoly = rsPoly.mul(new Poly([1, gexp(i)], 0));
      const rawPoly = new Poly(currentDc, rsPoly.size - 1);
      const modPoly = rawPoly.mod(rsPoly);
      const currentEc = [];
      const modOffset = modPoly.size - ecCount;
      for (let i = 0; i < ecCount; i++) {
        const modIndex = i + modOffset;
        currentEc.push(modIndex >= 0 ? modPoly.get(modIndex) : 0);
      }
      dcData.push(currentDc);
      ecData.push(currentEc);
    }
    const data = [];
    for (let i = 0; i < maxDc; i++) {
      for (const dc of dcData) if (i < dc.length) data.push(dc[i]);
    }
    for (let i = 0; i < maxEc; i++) {
      for (const ec of ecData) if (i < ec.length) data.push(ec[i]);
    }
    return data;
  };

  const createData = (version, level, bytes) => {
    const buffer = new BitBuffer();
    buffer.put(MODE_8BIT_BYTE, 4);
    buffer.put(bytes.length, charCountBits(version));
    for (let i = 0; i < bytes.length; i++) buffer.put(bytes[i], 8);

    const blocks = rsBlocks(version, level);
    const bitLimit = blocks.reduce((sum, b) => sum + b.dataCount * 8, 0);
    if (buffer.length > bitLimit) throw new Error("data overflow for the chosen version");
    for (let i = 0; i < Math.min(bitLimit - buffer.length, 4); i++) buffer.putBit(false);
    const delimit = buffer.length % 8;
    if (delimit) {
      for (let i = 0; i < 8 - delimit; i++) buffer.putBit(false);
    }
    const bytesToFill = (bitLimit - buffer.length) / 8;
    for (let i = 0; i < bytesToFill; i++) buffer.put(i % 2 === 0 ? PAD0 : PAD1, 8);
    return createBytes(buffer, blocks);
  };

  // Function patterns: probe squares, alignment squares, timing strip. Independent of the
  // mask and the data, matching qrcode/main.py: setup_position_probe_pattern and friends.
  const setupPositionProbePattern = (modules, count, row, col) => {
    for (let r = -1; r < 8; r++) {
      if (row + r <= -1 || count <= row + r) continue;
      for (let c = -1; c < 8; c++) {
        if (col + c <= -1 || count <= col + c) continue;
        const dark =
          (r >= 0 && r <= 6 && (c === 0 || c === 6)) ||
          (c >= 0 && c <= 6 && (r === 0 || r === 6)) ||
          (r >= 2 && r <= 4 && c >= 2 && c <= 4);
        modules[row + r][col + c] = dark;
      }
    }
  };

  const setupTimingPattern = (modules, count) => {
    for (let r = 8; r < count - 8; r++) {
      if (modules[r][6] !== null) continue;
      modules[r][6] = r % 2 === 0;
    }
    for (let c = 8; c < count - 8; c++) {
      if (modules[6][c] !== null) continue;
      modules[6][c] = c % 2 === 0;
    }
  };

  const setupPositionAdjustPattern = (modules, count, version) => {
    const pos = PATTERN_POSITION_TABLE[version - 1];
    for (let i = 0; i < pos.length; i++) {
      const row = pos[i];
      for (let j = 0; j < pos.length; j++) {
        const col = pos[j];
        if (modules[row][col] !== null) continue;
        for (let r = -2; r <= 2; r++) {
          for (let c = -2; c <= 2; c++) {
            const dark = r === -2 || r === 2 || c === -2 || c === 2 || (r === 0 && c === 0);
            modules[row + r][col + c] = dark;
          }
        }
      }
    }
  };

  const setupTypeNumber = (modules, count, version, test) => {
    const bits = bchTypeNumber(version);
    for (let i = 0; i < 18; i++) {
      const mod = !test && (((bits >> i) & 1) === 1);
      modules[Math.floor(i / 3)][(i % 3) + count - 8 - 3] = mod;
    }
    for (let i = 0; i < 18; i++) {
      const mod = !test && (((bits >> i) & 1) === 1);
      modules[(i % 3) + count - 8 - 3][Math.floor(i / 3)] = mod;
    }
  };

  const setupTypeInfo = (modules, count, test, maskPattern, levelBits) => {
    const data = (levelBits << 3) | maskPattern;
    const bits = bchTypeInfo(data);
    for (let i = 0; i < 15; i++) {
      const mod = !test && (((bits >> i) & 1) === 1);
      if (i < 6) modules[i][8] = mod;
      else if (i < 8) modules[i + 1][8] = mod;
      else modules[count - 15 + i][8] = mod;
    }
    for (let i = 0; i < 15; i++) {
      const mod = !test && (((bits >> i) & 1) === 1);
      if (i < 8) modules[8][count - i - 1] = mod;
      else if (i < 9) modules[8][15 - i - 1 + 1] = mod;
      else modules[8][15 - i - 1] = mod;
    }
    modules[count - 8][8] = !test;
  };

  const mapData = (modules, count, data, maskFn) => {
    let inc = -1;
    let row = count - 1;
    let bitIndex = 7;
    let byteIndex = 0;
    const dataLen = data.length;
    // colBase steps -2 from a fixed sequence (count-1, count-3, ...), independent of the
    // col<=6 adjustment below: mutating the loop counter itself, as qrcode/main.py's Python
    // `for col in range(...)` cannot (range is precomputed), would desync every column after
    // the timing strip at column 6.
    for (let colBase = count - 1; colBase > 0; colBase -= 2) {
      const col = colBase <= 6 ? colBase - 1 : colBase;
      const colRange = [col, col - 1];
      for (;;) {
        for (const c of colRange) {
          if (modules[row][c] === null) {
            let dark = byteIndex < dataLen && ((data[byteIndex] >> bitIndex) & 1) === 1;
            if (maskFn(row, c)) dark = !dark;
            modules[row][c] = dark;
            bitIndex -= 1;
            if (bitIndex === -1) {
              byteIndex += 1;
              bitIndex = 7;
            }
          }
        }
        row += inc;
        if (row < 0 || count <= row) {
          row -= inc;
          inc = -inc;
          break;
        }
      }
    }
  };

  // The four ISO/IEC 18004 penalty rules. Levels 2 and 3 are written as plain nested scans
  // rather than qrcode's Horspool-style skip-ahead: the skip only ever advances past
  // positions the skipped-over check has already proven cannot score, so the total is the
  // same either way, just slower to compute for the module counts this encoder ever sees.
  const lostPointLevel1 = (modules, count) => {
    let lost = 0;
    const container = new Array(count + 1).fill(0);
    for (let row = 0; row < count; row++) {
      const thisRow = modules[row];
      let prevColor = thisRow[0];
      let length = 0;
      for (let col = 0; col < count; col++) {
        if (thisRow[col] === prevColor) {
          length += 1;
        } else {
          if (length >= 5) container[length] += 1;
          length = 1;
          prevColor = thisRow[col];
        }
      }
      if (length >= 5) container[length] += 1;
    }
    for (let col = 0; col < count; col++) {
      let prevColor = modules[0][col];
      let length = 0;
      for (let row = 0; row < count; row++) {
        if (modules[row][col] === prevColor) {
          length += 1;
        } else {
          if (length >= 5) container[length] += 1;
          length = 1;
          prevColor = modules[row][col];
        }
      }
      if (length >= 5) container[length] += 1;
    }
    for (let len = 5; len <= count; len++) lost += container[len] * (len - 2);
    return lost;
  };

  const lostPointLevel2 = (modules, count) => {
    let lost = 0;
    for (let row = 0; row < count - 1; row++) {
      for (let col = 0; col < count - 1; col++) {
        const a = modules[row][col];
        if (a === modules[row][col + 1] && a === modules[row + 1][col] && a === modules[row + 1][col + 1]) {
          lost += 3;
        }
      }
    }
    return lost;
  };

  const finderLike = (get) =>
    !get(1) &&
    get(4) &&
    !get(5) &&
    get(6) &&
    !get(9) &&
    ((get(0) && get(2) && get(3) && !get(7) && !get(8) && !get(10)) ||
      (!get(0) && !get(2) && !get(3) && get(7) && get(8) && get(10)));

  const lostPointLevel3 = (modules, count) => {
    let lost = 0;
    for (let row = 0; row < count; row++) {
      const thisRow = modules[row];
      for (let col = 0; col <= count - 11; col++) {
        if (finderLike((k) => thisRow[col + k])) lost += 40;
      }
    }
    for (let col = 0; col < count; col++) {
      for (let row = 0; row <= count - 11; row++) {
        if (finderLike((k) => modules[row + k][col])) lost += 40;
      }
    }
    return lost;
  };

  const lostPointLevel4 = (modules, count) => {
    let dark = 0;
    for (let r = 0; r < count; r++) {
      for (let c = 0; c < count; c++) if (modules[r][c]) dark += 1;
    }
    const percent = dark / (count * count);
    return Math.floor(Math.abs(percent * 100 - 50) / 5) * 10;
  };

  const lostPoint = (modules, count) =>
    lostPointLevel1(modules, count) +
    lostPointLevel2(modules, count) +
    lostPointLevel3(modules, count) +
    lostPointLevel4(modules, count);

  const buildMatrix = (version, level, codewords) => {
    const count = version * 4 + 17;
    const levelBits = LEVEL_BITS[level];

    const scaffold = () => {
      const modules = [];
      for (let r = 0; r < count; r++) modules.push(new Array(count).fill(null));
      setupPositionProbePattern(modules, count, 0, 0);
      setupPositionProbePattern(modules, count, count - 7, 0);
      setupPositionProbePattern(modules, count, 0, count - 7);
      setupPositionAdjustPattern(modules, count, version);
      setupTimingPattern(modules, count);
      return modules;
    };

    const fillFormatInfo = (modules, test, maskPattern) => {
      setupTypeInfo(modules, count, test, maskPattern, levelBits);
      if (version >= 7) setupTypeNumber(modules, count, version, test);
    };

    let bestPattern = 0;
    let bestScore = 0;
    for (let pattern = 0; pattern < 8; pattern++) {
      const modules = scaffold();
      fillFormatInfo(modules, true, pattern);
      mapData(modules, count, codewords, maskFunc(pattern));
      const score = lostPoint(modules, count);
      if (pattern === 0 || score < bestScore) {
        bestScore = score;
        bestPattern = pattern;
      }
    }

    const finalModules = scaffold();
    fillFormatInfo(finalModules, false, bestPattern);
    mapData(finalModules, count, codewords, maskFunc(bestPattern));
    return finalModules;
  };

  const encode = (data, level) => {
    if (level !== "L" && level !== "M") throw new Error('level must be "L" or "M"');
    const bytes = data instanceof Uint8Array ? data : new TextEncoder().encode(String(data));
    const version = bestVersion(bytes.length, level);
    const codewords = createData(version, level, bytes);
    const matrix = buildMatrix(version, level, codewords);
    const size = matrix.length;
    const modules = new Uint8Array(size * size);
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) modules[y * size + x] = matrix[y][x] ? 1 : 0;
    }
    return { version, size, modules };
  };

  // The same one-path markup as scripts/build_app.py: qr_svg, one M-h-v-h-z per dark module.
  const toSvgPath = (result) => {
    const { size, modules } = result;
    let path = "";
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        if (modules[y * size + x]) path += `M${x} ${y}h1v1h-1z`;
      }
    }
    return path;
  };

  return { encode, toSvgPath };
})();
