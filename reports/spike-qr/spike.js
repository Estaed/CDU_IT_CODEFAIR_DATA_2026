"use strict";

// Transfer v3 experiment (Task-31, 2026-09-16). Four candidate frame geometries -- A one code,
// B four codes in a 2x2 grid, C three codes multiplexed into the R, G and B channels of one
// code-sized picture, D the grid of composites -- played by send.html and read by receive.html
// so Tarik can measure them on the S24 and the Mi 6. The winner is built into app/transfer.js
// by Task-36; nothing under app/ imports this file and nothing here imports app/transfer.js.
//
// The fountain code below is transfer.js's, copied on purpose (the spike must not import the
// app) with one deliberate change the task fixes: the repair degree comes from the robust
// soliton distribution (c = 0.1, delta = 0.5) rather than v2's uniform 6..12, because the v2
// degree was tuned against 10 % frame loss and a real phone loses half or more. The frame
// prefix is `CZ`, so a v2 (`CY`) receiver and this one can never mix frames.
window.Spike = (() => {
  const crosscheckQR = window.CrosscheckQR;
  const crosscheckScan = window.CrosscheckScan;

  const FRAME_PREFIX = "CZ";
  const BLOCK_BYTES = 750;
  const BLOCK_B64_CHARS = 1000; // 750 bytes, divisible by 3, base64s with no padding
  const MAX_INDEX = 0xffff; // 4 hex digits
  const QUIET_MODULES = 4; // the quiet zone every QR needs, in modules, inside its own cell
  const RATE_WINDOW_MS = 5000; // "per second over the last 5 seconds" on the receive page
  // 174,725 bytes: the gzipped size of the app on 2026-09-16, so K matches the real thing.
  const PAYLOAD_BYTES = 174725;
  const PAYLOAD_SEED = 0x5eed;
  // cells across the picture x codes per cell. A: one code. B: a 2x2 grid. C: three colour
  // channels of one code-sized picture. D: both.
  const SHAPE = {
    A: { cells: 1, channels: 1 },
    B: { cells: 4, channels: 1 },
    C: { cells: 1, channels: 3 },
    D: { cells: 4, channels: 3 },
  };
  const codesPerFrame = (candidate) => SHAPE[candidate].cells * SHAPE[candidate].channels;

  const FRAME_RE = new RegExp(
    `^${FRAME_PREFIX}([ABCD])([0-9a-f]{4})([0-9a-f]{4})([0-9a-f]{6})([A-Za-z0-9+/]{${BLOCK_B64_CHARS}})$`,
  );

  // --- bytes, base64, hex, hash ----------------------------------------------------------------

  const bytesToBase64 = (bytes) => {
    let binary = "";
    const step = 0x8000;
    for (let i = 0; i < bytes.length; i += step) {
      binary += String.fromCharCode(...bytes.subarray(i, i + step));
    }
    return btoa(binary);
  };

  const base64ToBytes = (text) => {
    const binary = atob(text);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  };

  const hex4 = (n) => n.toString(16).padStart(4, "0");
  const hex6 = (n) => n.toString(16).padStart(6, "0");

  // Both pages show the first 8 hex characters of SHA-256 over the payload, so a completed run
  // proves the received bytes are the sent bytes and not merely K blocks of something.
  const hash8 = async (bytes) => {
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    return [...new Uint8Array(digest)]
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("")
      .slice(0, 8);
  };

  // --- the fountain code -----------------------------------------------------------------------

  const xorshift32 = (seed) => {
    let x = seed >>> 0;
    return () => {
      x ^= x << 13;
      x >>>= 0;
      x ^= x >>> 17;
      x ^= x << 5;
      x >>>= 0;
      return x >>> 0;
    };
  };

  const nextFloat = (rand) => rand() / 4294967296; // uint32 -> [0, 1)

  // Robust soliton, c = 0.1, delta = 0.5: rho (the ideal soliton) plus tau (the extra weight
  // that keeps the decoder's ripple alive), normalised, kept as a cumulative table so one
  // uniform draw and a binary search give the degree. One table per K, built once.
  const SOLITON_C = 0.1;
  const SOLITON_DELTA = 0.5;
  const solitonCache = new Map();
  const solitonCumulative = (k) => {
    const cached = solitonCache.get(k);
    if (cached) {
      return cached;
    }
    const r = SOLITON_C * Math.log(k / SOLITON_DELTA) * Math.sqrt(k);
    const weight = new Float64Array(k + 1);
    for (let i = 1; i <= k; i++) {
      weight[i] = i === 1 ? 1 / k : 1 / (i * (i - 1));
    }
    const spike = Math.max(1, Math.floor(k / r));
    for (let i = 1; i < spike; i++) {
      weight[i] += r / (i * k);
    }
    if (spike <= k) {
      weight[spike] += (r * Math.log(r / SOLITON_DELTA)) / k;
    }
    let total = 0;
    for (let i = 1; i <= k; i++) {
      total += weight[i];
    }
    const cumulative = new Float64Array(k + 1);
    let running = 0;
    for (let i = 1; i <= k; i++) {
      running += weight[i] / total;
      cumulative[i] = running;
    }
    cumulative[k] = 1;
    solitonCache.set(k, cumulative);
    return cumulative;
  };

  const drawDegree = (rand, k) => {
    const cumulative = solitonCumulative(k);
    const u = nextFloat(rand);
    let low = 1;
    let high = k;
    while (low < high) {
      const mid = (low + high) >> 1;
      if (cumulative[mid] >= u) {
        high = mid;
      } else {
        low = mid + 1;
      }
    }
    return Math.max(1, Math.min(k, low));
  };

  // Fisher-Yates partial shuffle drawn from the same generator: `degree` distinct ids in [0, k).
  const drawDistinctIds = (rand, k, degree) => {
    const ids = new Array(k);
    for (let i = 0; i < k; i++) {
      ids[i] = i;
    }
    const count = Math.min(degree, k);
    for (let i = 0; i < count; i++) {
      const j = i + Math.floor(nextFloat(rand) * (k - i));
      const tmp = ids[i];
      ids[i] = ids[j];
      ids[j] = tmp;
    }
    return ids.slice(0, count);
  };

  // The only place either end derives a repair frame's block set: index and k in, block ids out.
  const blockIdsForIndex = (index, k) => {
    const seed = (index * 2654435761) >>> 0 || 1;
    const rand = xorshift32(seed);
    const degree = drawDegree(rand, k);
    return drawDistinctIds(rand, k, degree);
  };

  // The test payload both pages generate in-page, so no file and no network is involved.
  const makePayload = () => {
    const rand = xorshift32(PAYLOAD_SEED);
    const bytes = new Uint8Array(PAYLOAD_BYTES);
    for (let i = 0; i < PAYLOAD_BYTES; i++) {
      bytes[i] = rand() & 0xff;
    }
    return bytes;
  };

  const encoder = (payload, candidate) => {
    const length = payload.length;
    const k = Math.max(1, Math.ceil(length / BLOCK_BYTES));
    const sourceBlocks = [];
    for (let i = 0; i < k; i++) {
      const block = new Uint8Array(BLOCK_BYTES);
      block.set(payload.subarray(i * BLOCK_BYTES, Math.min((i + 1) * BLOCK_BYTES, length)));
      sourceBlocks.push(block);
    }
    const header = (index) => `${FRAME_PREFIX}${candidate}${hex4(index)}${hex4(k)}${hex6(length)}`;
    const frameAt = (index) => {
      if (index < k) {
        return `${header(index)}${bytesToBase64(sourceBlocks[index])}`;
      }
      const xored = new Uint8Array(BLOCK_BYTES);
      for (const id of blockIdsForIndex(index, k)) {
        const block = sourceBlocks[id];
        for (let b = 0; b < BLOCK_BYTES; b++) {
          xored[b] ^= block[b];
        }
      }
      return `${header(index)}${bytesToBase64(xored)}`;
    };
    return { k, length, frameAt };
  };

  // Send order, as today: one pass of the K source frames, then repair frames only.
  const createSequence = (k) => {
    let phase = "initial";
    let initialIndex = 0;
    let repairIndex = k;
    const next = () => {
      if (phase === "initial") {
        const index = initialIndex;
        initialIndex += 1;
        if (initialIndex >= k) {
          phase = "repair";
        }
        return index;
      }
      const index = repairIndex;
      repairIndex += 1;
      if (repairIndex >= MAX_INDEX) {
        repairIndex = k;
      }
      return index;
    };
    return { next };
  };

  // The peeling decoder of transfer.js, copied: order-insensitive, duplicates harmless.
  const receiver = (candidate) => {
    let k = null;
    let length = null;
    const known = new Map();
    const pending = [];
    const resolveQueue = [];

    const xorInto = (target, source) => {
      for (let i = 0; i < target.length; i++) {
        target[i] ^= source[i];
      }
    };

    const markKnown = (index, data) => {
      if (known.has(index)) {
        return;
      }
      known.set(index, data);
      resolveQueue.push(index);
    };

    const peel = () => {
      while (resolveQueue.length > 0) {
        const resolved = resolveQueue.pop();
        const data = known.get(resolved);
        for (let i = pending.length - 1; i >= 0; i--) {
          const edge = pending[i];
          if (!edge.ids.has(resolved)) {
            continue;
          }
          edge.ids.delete(resolved);
          xorInto(edge.data, data);
          if (edge.ids.size === 0) {
            pending.splice(i, 1);
          } else if (edge.ids.size === 1) {
            const [remaining] = edge.ids;
            pending.splice(i, 1);
            markKnown(remaining, edge.data);
          }
        }
      }
    };

    // Returns, besides the progress the app's receiver returns: whether this text was a frame
    // of this candidate at all (`accepted`, so the page can count decoded codes) and how many
    // blocks it resolved (`gained`, the new-blocks-per-second rate).
    const push = (text) => {
      const match = typeof text === "string" ? FRAME_RE.exec(text) : null;
      const accepted = match !== null && (!candidate || match[1] === candidate);
      const before = known.size;
      if (accepted) {
        const index = parseInt(match[2], 16);
        const frameK = parseInt(match[3], 16);
        const frameLength = parseInt(match[4], 16);
        if (k === null) {
          k = frameK;
          length = frameLength;
        }
        if (frameK === k && frameLength === length) {
          const data = base64ToBytes(match[5]);
          if (index < k) {
            markKnown(index, data);
          } else {
            const ids = new Set(blockIdsForIndex(index, k));
            const reduced = data;
            for (const id of [...ids]) {
              if (known.has(id)) {
                xorInto(reduced, known.get(id));
                ids.delete(id);
              }
            }
            if (ids.size === 1) {
              const [only] = ids;
              markKnown(only, reduced);
            } else if (ids.size > 1) {
              pending.push({ ids, data: reduced });
            }
          }
          peel();
        }
      }
      return {
        accepted,
        gained: known.size - before,
        complete: k !== null && known.size === k,
        known: known.size,
        total: k || 0,
      };
    };

    const bytes = () => {
      if (k === null || known.size !== k) {
        return null;
      }
      const out = new Uint8Array(k * BLOCK_BYTES);
      for (let i = 0; i < k; i++) {
        out.set(known.get(i), i * BLOCK_BYTES);
      }
      return out.slice(0, length);
    };

    return { push, bytes };
  };

  // --- drawing: one code, a 2x2 grid, a colour composite, or both ------------------------------

  // A QR laid out in its own square cell: quiet zone included, integer module scale, centred.
  const cellLayout = (size, side) => {
    const total = size + QUIET_MODULES * 2;
    const scale = Math.max(1, Math.floor(side / total));
    const drawn = total * scale;
    return { total, scale, drawn, pad: Math.floor((side - drawn) / 2) };
  };

  // One cell's picture as ImageData at module resolution. `results` is one code (plain) or three
  // (colour). A module dark in channel c makes that component 0 and light makes it 255, so a
  // module dark in all three is black -- and the finder and timing patterns, identical in all
  // three codes because all three are the same version, stay black and locatable by any reader.
  // Their masks may differ, which colours only the format-information modules; every reader
  // reads those from its own channel's picture after the split, never from the composite.
  const cellImageData = (results, total) => {
    const pixels = new Uint8ClampedArray(total * total * 4);
    pixels.fill(255);
    for (let channel = 0; channel < results.length; channel++) {
      const { size, modules } = results[channel];
      for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
          if (!modules[y * size + x]) {
            continue;
          }
          const at = ((y + QUIET_MODULES) * total + (x + QUIET_MODULES)) * 4;
          if (results.length === 1) {
            pixels[at] = 0;
            pixels[at + 1] = 0;
            pixels[at + 2] = 0;
          } else {
            pixels[at + channel] = 0;
          }
        }
      }
    }
    return new ImageData(pixels, total, total);
  };

  // One scratch canvas, reused: a frame draws up to four cells and a phone plays ten frames a
  // second, so allocating one canvas per cell would be the loop's largest cost.
  let scratch = null;
  const scratchCanvas = (total) => {
    if (!scratch) {
      scratch = document.createElement("canvas");
    }
    if (scratch.width !== total) {
      scratch.width = total;
      scratch.height = total;
    }
    return scratch;
  };

  // `results` is one flat array of cells x channels codes, cell-major, drawn into the square of
  // side `side` with its top-left corner at (x, y).
  const drawFrame = (ctx, candidate, results, x, y, side) => {
    const { cells, channels } = SHAPE[candidate];
    const across = cells === 4 ? 2 : 1;
    const cellSide = Math.floor(side / across);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(x, y, side, side);
    ctx.imageSmoothingEnabled = false;
    for (let cell = 0; cell < cells; cell++) {
      const group = results.slice(cell * channels, cell * channels + channels);
      const { total, drawn, pad } = cellLayout(group[0].size, cellSide);
      const source = scratchCanvas(total);
      source.getContext("2d").putImageData(cellImageData(group, total), 0, 0);
      const cx = x + (cell % across) * cellSide + pad;
      const cy = y + Math.floor(cell / across) * cellSide + pad;
      ctx.drawImage(source, cx, cy, drawn, drawn);
    }
  };

  // --- reading back: quadrants, channel split ---------------------------------------------------

  const subImage = (imageData, sx, sy, side) => {
    const out = new Uint8ClampedArray(side * side * 4);
    for (let row = 0; row < side; row++) {
      const from = ((sy + row) * imageData.width + sx) * 4;
      out.set(imageData.data.subarray(from, from + side * 4), row * side * 4);
    }
    return new ImageData(out, side, side);
  };

  const quadrants = (imageData) => {
    const half = Math.floor(Math.min(imageData.width, imageData.height) / 2);
    return [
      subImage(imageData, 0, 0, half),
      subImage(imageData, half, 0, half),
      subImage(imageData, 0, half, half),
      subImage(imageData, half, half, half),
    ];
  };

  // Each of R, G and B stretched to the range of its own darkest and lightest 1 % of pixels and
  // written as a grey RGBA image, so each channel's code reads as an ordinary black-on-white QR
  // whatever the camera did to the white balance. Crosstalk between channels is what the
  // experiment measures; this stretch is the only compensation the receiver applies.
  const CLIP_FRACTION = 0.01;
  const splitChannels = (imageData) => {
    const { data, width, height } = imageData;
    const count = width * height;
    const cut = Math.max(1, Math.floor(count * CLIP_FRACTION));
    const out = [];
    for (let channel = 0; channel < 3; channel++) {
      const histogram = new Uint32Array(256);
      for (let i = 0; i < count; i++) {
        histogram[data[i * 4 + channel]] += 1;
      }
      let low = 0;
      let seen = 0;
      while (low < 255 && seen + histogram[low] < cut) {
        seen += histogram[low];
        low += 1;
      }
      let high = 255;
      seen = 0;
      while (high > 0 && seen + histogram[high] < cut) {
        seen += histogram[high];
        high -= 1;
      }
      if (high <= low) {
        low = 0;
        high = 255;
      }
      const span = high - low;
      const grey = new Uint8ClampedArray(count * 4);
      for (let i = 0; i < count; i++) {
        const stretched = Math.round(((data[i * 4 + channel] - low) * 255) / span);
        grey[i * 4] = stretched;
        grey[i * 4 + 1] = stretched;
        grey[i * 4 + 2] = stretched;
        grey[i * 4 + 3] = 255;
      }
      out.push(new ImageData(grey, width, height));
    }
    return out;
  };

  // One camera picture -> the list of code-sized pictures this candidate expects.
  const explode = (candidate, imageData) => {
    const { cells, channels } = SHAPE[candidate];
    const pieces = cells === 4 ? quadrants(imageData) : [imageData];
    if (channels === 1) {
      return pieces;
    }
    const out = [];
    for (const piece of pieces) {
      out.push(...splitChannels(piece));
    }
    return out;
  };

  // --- readers ---------------------------------------------------------------------------------

  // The reader choice is CrosscheckScan's: the native BarcodeDetector where the browser has one,
  // else the vendored jsQR. jsQR runs in a Web Worker built from a Blob of its own inlined
  // source text, so a decode never blocks the frame callback and the page still requests
  // nothing. The native path stays on the main thread, as in the app.
  const readerKind = () => crosscheckScan.kind();

  const WORKER_TAIL = `
self.onmessage = (event) => {
  const { id, data, width, height } = event.data;
  const pixels = new Uint8ClampedArray(data);
  const code = self.jsQR(pixels, width, height, { inversionAttempts: "dontInvert" });
  self.postMessage({ id, text: code ? code.data : null });
};
`;

  let worker = null;
  const workerJobs = new Map();
  let nextJobId = 1;
  const jsqrWorker = () => {
    if (worker) {
      return worker;
    }
    const source = document.getElementById("jsqr-src").textContent + WORKER_TAIL;
    const url = URL.createObjectURL(new Blob([source], { type: "text/javascript" }));
    worker = new Worker(url);
    URL.revokeObjectURL(url);
    worker.onmessage = (event) => {
      const resolve = workerJobs.get(event.data.id);
      if (resolve) {
        workerJobs.delete(event.data.id);
        resolve(event.data.text);
      }
    };
    return worker;
  };

  const decodeInWorker = (imageData) =>
    new Promise((resolve) => {
      const id = nextJobId;
      nextJobId += 1;
      const copy = new Uint8ClampedArray(imageData.data);
      workerJobs.set(id, resolve);
      jsqrWorker().postMessage(
        { id, data: copy.buffer, width: imageData.width, height: imageData.height },
        [copy.buffer],
      );
    });

  let nativeDetector = null;
  const detectNative = async (imageData) => {
    if (!nativeDetector) {
      nativeDetector = new window.BarcodeDetector({ formats: ["qr_code"] });
    }
    const canvas = document.createElement("canvas");
    canvas.width = imageData.width;
    canvas.height = imageData.height;
    canvas.getContext("2d").putImageData(imageData, 0, 0);
    const codes = await nativeDetector.detect(canvas);
    return codes.map((code) => code.rawValue);
  };

  // One code-sized picture in, the texts found in it out. The native detector may find several
  // codes in one picture; jsQR finds at most one.
  const decodePiece = async (imageData) => {
    if (readerKind() === "native") {
      return detectNative(imageData);
    }
    const text = await decodeInWorker(imageData);
    return text === null ? [] : [text];
  };

  // The main-thread jsQR path of scan.js, for the no-camera loopback checks.
  const decodeImageData = (imageData) => crosscheckScan.decodeImageData(imageData);

  // --- pages ------------------------------------------------------------------------------------

  const el = (tag, attrs, ...children) => {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs || {})) {
      if (value !== null && value !== undefined) {
        node.setAttribute(key, value);
      }
    }
    for (const child of children) {
      if (child === null || child === undefined) {
        continue;
      }
      node.appendChild(child instanceof Node ? child : document.createTextNode(String(child)));
    }
    return node;
  };

  const chooser = (id, label, values, initial) => {
    const node = el("select", { id, class: "spike-select" });
    for (const value of values) {
      node.appendChild(el("option", { value: String(value) }, String(value)));
    }
    node.value = String(initial);
    return { field: el("label", { class: "spike-label" }, label, node), node };
  };

  const holdScreen = async () => {
    try {
      return navigator.wakeLock ? await navigator.wakeLock.request("screen") : null;
    } catch (error) {
      return null;
    }
  };

  const mountSend = (root) => {
    const candidate = chooser("candidate", "Candidate", ["A", "B", "C", "D"], "A");
    const hold = chooser("hold", "Hold (display refreshes)", [4, 6, 8], 6);
    const startButton = el("button", { type: "button", class: "spike-button" }, "Start");
    const fullButton = el("button", { type: "button", class: "spike-button" }, "Fullscreen");
    const counter = el("p", { class: "spike-counter" }, "not started");
    const canvas = el("canvas", { class: "spike-canvas" });
    const stage = el("div", { class: "spike-stage" }, canvas);

    let payload = null;
    let payloadHash = "";
    let letter = "A";
    let built = null;
    let sequence = null;
    let playing = false;
    let refreshes = 0;
    let framesShown = 0;
    let startedAt = 0;
    let wakeLock = null;
    const ready = [];

    const prepare = () => {
      const group = [];
      for (let i = 0; i < codesPerFrame(letter); i++) {
        group.push(crosscheckQR.encode(built.frameAt(sequence.next()), "L"));
      }
      ready.push(group);
    };

    const fit = () => {
      const side = Math.min(stage.clientWidth, stage.clientHeight) || 512;
      const pixels = Math.floor(side * (window.devicePixelRatio || 1));
      if (canvas.width !== pixels) {
        canvas.width = pixels;
        canvas.height = pixels;
      }
      canvas.style.width = `${side}px`;
      canvas.style.height = `${side}px`;
    };

    const paint = () => {
      fit();
      if (ready.length === 0) {
        prepare();
      }
      drawFrame(canvas.getContext("2d"), letter, ready.shift(), 0, 0, canvas.width);
      framesShown += 1;
      const seconds = ((performance.now() - startedAt) / 1000).toFixed(1);
      counter.textContent = `frames ${framesShown} · ${seconds} s · K ${built.k} · payload ${payloadHash}`;
      if (ready.length === 0) {
        prepare(); // encode the next frame right after a draw, not at the next deadline
      }
    };

    const loop = () => {
      if (!playing) {
        return;
      }
      if (refreshes === 0) {
        paint();
      }
      refreshes = (refreshes + 1) % Number(hold.node.value);
      requestAnimationFrame(loop);
    };

    const stop = () => {
      playing = false;
      startButton.textContent = "Start";
      if (wakeLock) {
        wakeLock.release().catch(() => {});
        wakeLock = null;
      }
    };

    startButton.addEventListener("click", async () => {
      if (playing) {
        stop();
        return;
      }
      if (!payload) {
        payload = makePayload();
        payloadHash = await hash8(payload);
      }
      letter = candidate.node.value;
      built = encoder(payload, letter);
      sequence = createSequence(built.k);
      ready.length = 0;
      framesShown = 0;
      refreshes = 0;
      startedAt = performance.now();
      playing = true;
      startButton.textContent = "Stop";
      wakeLock = await holdScreen();
      loop();
    });

    fullButton.addEventListener("click", () => {
      if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen().catch(() => {});
      }
    });

    root.appendChild(
      el(
        "div",
        { class: "spike-controls" },
        el("h1", { class: "spike-title" }, "Transfer v3 spike — send"),
        candidate.field,
        hold.field,
        startButton,
        fullButton,
        counter,
        el(
          "p",
          { class: "spike-note" },
          "Landscape and fullscreen give the codes the most pixels. Start the receiver first.",
        ),
      ),
    );
    root.appendChild(stage);
  };

  const mountReceive = (root) => {
    const candidate = chooser("candidate", "Candidate (must match the sender)", ["A", "B", "C", "D"], "A");
    const hold = chooser("hold", "Hold the sender is using", [4, 6, 8], 6);
    const phone = el("input", { id: "phone", class: "spike-input", value: "phone" });
    const startButton = el("button", { type: "button", class: "spike-button" }, "Start");
    const copyButton = el("button", { type: "button", class: "spike-button" }, "Copy runs");
    const kindLine = el("p", { class: "spike-counter" }, `reader: ${readerKind()}`);
    const counter = el("p", { class: "spike-counter" }, "not started");
    const rates = el("p", { class: "spike-counter" }, "");
    const video = el("video", { class: "spike-video", autoplay: "", playsinline: "", muted: "" });
    const log = el("pre", { class: "spike-log" });

    let stream = null;
    let untune = null;
    let scanning = false;
    let busy = false;
    let active = null;
    let letter = "A";
    let framesSeen = 0;
    let codesDecoded = 0;
    let newBlocks = 0;
    let firstDecodeAt = 0;
    const decodeStamps = [];
    const blockStamps = [];
    let canvas = null;
    let ctx = null;

    // Loss cannot be computed across two phones (this page never learns how many frames the
    // sender has shown), so the rate over a 5-second window stands in for it.
    const rate = (stamps, now) => {
      while (stamps.length > 0 && now - stamps[0] > RATE_WINDOW_MS) {
        stamps.shift();
      }
      return (stamps.length * 1000) / RATE_WINDOW_MS;
    };

    const stopStream = () => {
      if (untune) {
        untune();
        untune = null;
      }
      if (stream) {
        for (const track of stream.getTracks()) {
          track.stop();
        }
        stream = null;
      }
    };

    const show = (status) => {
      const now = performance.now();
      const seconds = firstDecodeAt ? (now - firstDecodeAt) / 1000 : 0;
      counter.textContent =
        `frames ${framesSeen} · codes ${codesDecoded} · new blocks ${newBlocks} · ` +
        `${status.known} of ${status.total} · ${seconds.toFixed(1)} s`;
      rates.textContent =
        `last 5 s: ${rate(decodeStamps, now).toFixed(1)} codes/s · ` +
        `${rate(blockStamps, now).toFixed(1)} new blocks/s`;
      return seconds;
    };

    const finish = async (seconds) => {
      scanning = false;
      stopStream();
      startButton.textContent = "Start";
      const digest = await hash8(active.bytes());
      counter.textContent = `DONE ${seconds.toFixed(1)} ${digest}`;
      if (navigator.vibrate) {
        navigator.vibrate(400);
      }
      const line = [
        letter,
        hold.node.value,
        phone.value || "phone",
        readerKind(),
        seconds.toFixed(1),
        framesSeen,
        codesDecoded,
      ].join(",");
      log.textContent += `${line}\n`;
    };

    const handle = async () => {
      const width = video.videoWidth;
      const height = video.videoHeight;
      if (!width || !height) {
        return;
      }
      const { sx, sy, side, outSide } = crosscheckScan.cropRect(width, height);
      if (!canvas) {
        canvas = document.createElement("canvas");
        ctx = canvas.getContext("2d", { willReadFrequently: true });
      }
      if (canvas.width !== outSide) {
        canvas.width = outSide;
        canvas.height = outSide;
      }
      ctx.drawImage(video, sx, sy, side, side, 0, 0, outSide, outSide);
      let status = { known: 0, total: 0, complete: false };
      for (const piece of explode(letter, ctx.getImageData(0, 0, outSide, outSide))) {
        for (const text of await decodePiece(piece)) {
          const result = active.push(text);
          if (!result.accepted) {
            continue;
          }
          const now = performance.now();
          codesDecoded += 1;
          decodeStamps.push(now);
          if (!firstDecodeAt) {
            firstDecodeAt = now;
          }
          for (let i = 0; i < result.gained; i++) {
            blockStamps.push(now);
          }
          newBlocks += result.gained;
          status = result;
        }
      }
      const seconds = show(status);
      if (status.complete) {
        await finish(seconds);
      }
    };

    // One camera frame in flight at a time: a frame that arrives while the last one is being
    // decoded is dropped, which is what a phone does anyway and what the measurement assumes.
    const tick = async () => {
      if (!scanning) {
        return;
      }
      framesSeen += 1;
      if (!busy) {
        busy = true;
        try {
          await handle();
        } catch (error) {
          // A single failed decode is noise, not a fault; keep scanning.
        }
        busy = false;
      }
      schedule();
    };

    function schedule() {
      if (!scanning) {
        return;
      }
      if (video.requestVideoFrameCallback) {
        video.requestVideoFrameCallback(() => tick());
      } else {
        requestAnimationFrame(() => tick());
      }
    }

    startButton.addEventListener("click", async () => {
      if (scanning) {
        scanning = false;
        stopStream();
        startButton.textContent = "Start";
        return;
      }
      letter = candidate.node.value;
      active = receiver(letter);
      framesSeen = 0;
      codesDecoded = 0;
      newBlocks = 0;
      firstDecodeAt = 0;
      decodeStamps.length = 0;
      blockStamps.length = 0;
      try {
        stream = await navigator.mediaDevices.getUserMedia(crosscheckScan.constraints());
      } catch (error) {
        counter.textContent = `no camera (${error && error.name}, ${location.protocol})`;
        return;
      }
      video.srcObject = stream;
      untune = crosscheckScan.tune(stream, video);
      scanning = true;
      startButton.textContent = "Stop";
      schedule();
    });

    // The Clipboard API is not available on a file:// page, and this one is opened both ways.
    copyButton.addEventListener("click", () => {
      const range = document.createRange();
      range.selectNodeContents(log);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      document.execCommand("copy");
    });

    root.appendChild(
      el(
        "div",
        { class: "spike-controls" },
        el("h1", { class: "spike-title" }, "Transfer v3 spike — receive"),
        candidate.field,
        hold.field,
        el("label", { class: "spike-label" }, "Phone", phone),
        startButton,
        kindLine,
        counter,
        rates,
      ),
    );
    root.appendChild(video);
    root.appendChild(
      el(
        "div",
        { class: "spike-controls" },
        el("p", { class: "spike-note" }, "candidate,hold,phone,reader,seconds,frames_seen,codes_decoded"),
        copyButton,
        log,
      ),
    );
  };

  const mount = (page, root) => {
    if (page === "send") {
      mountSend(root);
    } else {
      mountReceive(root);
    }
  };

  return {
    FRAME_PREFIX,
    BLOCK_BYTES,
    PAYLOAD_BYTES,
    SHAPE,
    codesPerFrame,
    xorshift32,
    blockIdsForIndex,
    makePayload,
    hash8,
    encoder,
    receiver,
    createSequence,
    cellLayout,
    drawFrame,
    quadrants,
    splitChannels,
    explode,
    decodeImageData,
    decodePiece,
    readerKind,
    mount,
  };
})();

(() => {
  const start = () =>
    window.Spike.mount(document.body.dataset.page, document.getElementById("app"));
  if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
