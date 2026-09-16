"use strict";

// Transfer v3 experiment (Task-31, round two, 2026-09-16). Round one built four frame
// geometries and none of them completed on a phone: the wall is the phone's decode rate on
// version-23 codes, and round one's reader path (requestVideoFrameCallback, jsQR in a worker)
// was slower than the one the app already ships. So round two changes exactly two things and
// copies everything else from app/transfer.js:
//
//   * fewer blocks -- the payload is the lite copy of the built app (no jsQR, no map layers),
//     built by build.py and inlined here, so K is the product's own K and not a proxy's;
//   * fewer frames a second -- one code per frame, changed inside requestAnimationFrame and
//     held for 12 refreshes (5 fps) by default, so the phone gets several camera frames per
//     code instead of racing one.
//
// The reader is the v2 app's loop, copied not redesigned: setTimeout every 100 ms on the main
// thread calling CrosscheckScan.reader().detect(video). No worker, no requestVideoFrameCallback.
//
// The fountain code is transfer.js's with the one change round one kept: the repair degree comes
// from the robust soliton distribution (c = 0.1, delta = 0.5) rather than v2's uniform 6..12,
// because the v2 degree was tuned against 10 % frame loss and a real phone loses half or more.
// The frame prefix is `CZ`, so a v2 (`CY`) receiver and this one can never mix frames.
//
// Nothing under app/ imports this file and nothing here imports app/transfer.js: the encoder,
// the receiver and the loops are copied on purpose, so a change here can never reach the app.
window.Spike = (() => {
  const crosscheckQR = window.CrosscheckQR;
  const crosscheckScan = window.CrosscheckScan;
  const payloadConstant = window.SpikePayload;

  const FRAME_PREFIX = "CZ";
  const BLOCK_BYTES = 750;
  const BLOCK_B64_CHARS = 1000; // 750 bytes, divisible by 3, base64s with no padding
  const MAX_INDEX = 0xffff; // 4 hex digits
  const SCAN_INTERVAL_MS = 100; // the app's v2 receive loop, copied
  const RATE_WINDOW_MS = 5000; // "per second over the last 5 seconds" on the receive page
  const HOLDS = [12, 8, 16]; // display refreshes per code; 12 is 5 fps at 60 Hz and the default
  const FRAME_RE = new RegExp(
    `^${FRAME_PREFIX}([0-9a-f]{4})([0-9a-f]{4})([0-9a-f]{6})([A-Za-z0-9+/]{${BLOCK_B64_CHARS}})$`,
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

  // The full SHA-256 of the gzipped payload. build.py wrote the sender's value into the page,
  // so the receive page can prove the bytes it reassembled are the bytes that were sent rather
  // than merely K blocks of something.
  const sha256Hex = async (bytes) => {
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
  };

  // The payload: the gzipped lite copy inlined by build.py. Decoded once, on first use.
  let payloadBytes = null;
  const payload = () => {
    if (payloadBytes === null) {
      payloadBytes = base64ToBytes(payloadConstant.b64);
    }
    return payloadBytes;
  };

  const payloadHash8 = () => payloadConstant.sha256.slice(0, 8);

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

  const encoder = (bytes) => {
    const length = bytes.length;
    const k = Math.max(1, Math.ceil(length / BLOCK_BYTES));
    const sourceBlocks = [];
    for (let i = 0; i < k; i++) {
      const block = new Uint8Array(BLOCK_BYTES);
      block.set(bytes.subarray(i * BLOCK_BYTES, Math.min((i + 1) * BLOCK_BYTES, length)));
      sourceBlocks.push(block);
    }
    const header = (index) => `${FRAME_PREFIX}${hex4(index)}${hex4(k)}${hex6(length)}`;
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

  // Send order, as the app's: one pass of the K source frames, then repair frames only.
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
  const receiver = () => {
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

    // Returns, besides the progress the app's receiver returns: whether this text was one of
    // our frames at all (`accepted`, so the page can count decoded codes) and how many blocks
    // it resolved (`gained`, the new-blocks-per-second rate).
    const push = (text) => {
      const match = typeof text === "string" ? FRAME_RE.exec(text) : null;
      const accepted = match !== null;
      const before = known.size;
      if (accepted) {
        const index = parseInt(match[1], 16);
        const frameK = parseInt(match[2], 16);
        const frameLength = parseInt(match[3], 16);
        if (k === null) {
          k = frameK;
          length = frameLength;
        }
        if (frameK === k && frameLength === length) {
          const data = base64ToBytes(match[4]);
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

  // --- inflate ----------------------------------------------------------------------------------

  const concatBytes = (chunks) => {
    const total = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
    const out = new Uint8Array(total);
    let offset = 0;
    for (const chunk of chunks) {
      out.set(chunk, offset);
      offset += chunk.length;
    }
    return out;
  };

  const pump = async (stream) => {
    const chunks = [];
    const streamReader = stream.getReader();
    for (;;) {
      const { value, done } = await streamReader.read();
      if (done) {
        break;
      }
      chunks.push(value);
    }
    return concatBytes(chunks);
  };

  const gunzip = (bytes) =>
    pump(new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip")));

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

  // The SVG is cloned from the template in page.html: the app draws the frame as one path in an
  // SVG element and this page must draw it the same way, but the namespace URL and the closing
  // tags cannot be written inside this inlined script.
  const frameSvg = () =>
    document.getElementById("frame-proto").content.firstElementChild.cloneNode(true);

  const holdScreen = async () => {
    try {
      return navigator.wakeLock ? await navigator.wakeLock.request("screen") : null;
    } catch (error) {
      return null;
    }
  };

  const readerKind = () => crosscheckScan.kind();

  const mountSend = (root) => {
    const hold = chooser("hold", "Hold (display refreshes)", HOLDS, HOLDS[0]);
    const startButton = el("button", { type: "button", class: "spike-button" }, "Start");
    const fullButton = el("button", { type: "button", class: "spike-button" }, "Fullscreen");
    const counter = el("p", { class: "spike-counter" }, "not started");
    const svgEl = frameSvg();
    const path = svgEl.firstElementChild;
    const stage = el("div", { class: "spike-stage" }, svgEl);

    let built = null;
    let sequence = null;
    let playing = false;
    let refreshes = 0;
    let framesShown = 0;
    let startedAt = 0;
    let wakeLock = null;

    // The app's own two lines: encode the frame, swap the viewBox and the path.
    const paint = () => {
      const result = crosscheckQR.encode(built.frameAt(sequence.next()), "L");
      svgEl.setAttribute("viewBox", `0 0 ${result.size} ${result.size}`);
      path.setAttribute("d", crosscheckQR.toSvgPath(result));
      framesShown += 1;
      const seconds = ((performance.now() - startedAt) / 1000).toFixed(1);
      counter.textContent =
        `frames ${framesShown} · ${seconds} s · K ${built.k} · ` +
        `${payloadConstant.gzippedBytes} bytes · payload ${payloadHash8()}`;
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
      built = encoder(payload());
      sequence = createSequence(built.k);
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
        hold.field,
        startButton,
        fullButton,
        counter,
        el(
          "p",
          { class: "spike-note" },
          "Fullscreen gives the code the most pixels. Start the receiver first.",
        ),
      ),
    );
    root.appendChild(stage);
  };

  const mountReceive = (root) => {
    const hold = chooser("hold", "Hold the sender is using", HOLDS, HOLDS[0]);
    const phone = el("input", { id: "phone", class: "spike-input", value: "phone" });
    const startButton = el("button", { type: "button", class: "spike-button" }, "Start");
    const copyButton = el("button", { type: "button", class: "spike-button" }, "Copy runs");
    const openButton = el(
      "button",
      { type: "button", class: "spike-button", hidden: "" },
      "Open lite copy",
    );
    const kindLine = el(
      "p",
      { class: "spike-counter" },
      `reader: ${readerKind()} · expecting ${payloadConstant.gzippedBytes} bytes · payload ${payloadHash8()}`,
    );
    const counter = el("p", { class: "spike-counter" }, "not started");
    const rates = el("p", { class: "spike-counter" }, "");
    const video = el("video", { class: "spike-video", autoplay: "", playsinline: "", muted: "" });
    const log = el("pre", { class: "spike-log" });

    let stream = null;
    let untune = null;
    let scanning = false;
    let scanTimer = null;
    let active = null;
    let framesRead = 0;
    let codesDecoded = 0;
    let newBlocks = 0;
    let firstDecodeAt = 0;
    let receivedUrl = null;
    // The last progress the receiver reported, kept across ticks: most ticks decode nothing and
    // the counter must not fall back to "0 of 0" between codes.
    let lastStatus = { known: 0, total: 0, complete: false };
    const decodeStamps = [];

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

    const stop = () => {
      if (scanTimer !== null) {
        clearTimeout(scanTimer);
        scanTimer = null;
      }
      scanning = false;
      stopStream();
      startButton.textContent = "Start";
    };

    const show = (status) => {
      const now = performance.now();
      const seconds = firstDecodeAt ? (now - firstDecodeAt) / 1000 : 0;
      counter.textContent =
        `frames ${framesRead} · codes ${codesDecoded} · new blocks ${newBlocks} · ` +
        `${status.known} of ${status.total} · ${seconds.toFixed(1)} s`;
      rates.textContent = `last 5 s: ${rate(decodeStamps, now).toFixed(1)} codes/s`;
      return seconds;
    };

    // Complete: check the hash against the constant build.py wrote, record the run, and offer
    // the inflated page so Tarik can see that what arrived actually runs.
    const finish = async (seconds) => {
      stop();
      const bytes = active.bytes();
      const digest = await sha256Hex(bytes);
      if (digest !== payloadConstant.sha256) {
        counter.textContent = `complete but the hash differs: ${digest.slice(0, 8)}`;
        return;
      }
      counter.textContent = `DONE ${seconds.toFixed(1)} s · ${digest.slice(0, 8)}`;
      if (navigator.vibrate) {
        navigator.vibrate(400);
      }
      const line = [
        hold.node.value,
        phone.value || "phone",
        readerKind(),
        seconds.toFixed(1),
        framesRead,
        codesDecoded,
      ].join(",");
      log.textContent += `${line}\n`;
      const html = await gunzip(bytes);
      if (receivedUrl) {
        URL.revokeObjectURL(receivedUrl);
      }
      receivedUrl = URL.createObjectURL(new Blob([html], { type: "text/html" }));
      openButton.hidden = false;
    };

    const record = (text) => {
      const result = active.push(text);
      if (!result.accepted) {
        return null;
      }
      const now = performance.now();
      codesDecoded += 1;
      decodeStamps.push(now);
      if (!firstDecodeAt) {
        firstDecodeAt = now;
      }
      newBlocks += result.gained;
      return result;
    };

    // The v2 app's receive loop, copied: one detect() call every 100 ms on the main thread.
    const scan = async () => {
      if (!scanning) {
        return;
      }
      framesRead += 1;
      try {
        const values = await crosscheckScan.reader().detect(video);
        for (const value of values) {
          if (typeof value === "string") {
            const result = record(value);
            if (result) {
              lastStatus = result;
            }
          }
        }
      } catch (error) {
        // One failed detect() call (decode noise on a single frame) is not fatal; keep scanning.
      }
      const seconds = show(lastStatus);
      if (lastStatus.complete) {
        await finish(seconds);
        return;
      }
      if (scanning) {
        scanTimer = setTimeout(scan, SCAN_INTERVAL_MS);
      }
    };

    startButton.addEventListener("click", async () => {
      if (scanning || stream) {
        stop();
        return;
      }
      active = receiver();
      framesRead = 0;
      codesDecoded = 0;
      newBlocks = 0;
      firstDecodeAt = 0;
      decodeStamps.length = 0;
      lastStatus = { known: 0, total: 0, complete: false };
      openButton.hidden = true;
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
      scan();
    });

    openButton.addEventListener("click", () => {
      if (receivedUrl) {
        window.open(receivedUrl);
      }
    });

    // Round one's copy failed on the phone. The Clipboard API needs the click it is called in,
    // so it is called first and directly; if it rejects (a file:// page has no clipboard), the
    // log text is selected instead so a long-press copies it.
    copyButton.addEventListener("click", () => {
      const selectLog = () => {
        const range = document.createRange();
        range.selectNodeContents(log);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
      };
      try {
        navigator.clipboard.writeText(log.textContent).catch(selectLog);
      } catch (error) {
        selectLog();
      }
    });

    root.appendChild(
      el(
        "div",
        { class: "spike-controls" },
        el("h1", { class: "spike-title" }, "Transfer v3 spike — receive"),
        hold.field,
        el("label", { class: "spike-label" }, "Phone", phone),
        startButton,
        openButton,
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
        el("p", { class: "spike-note" }, "hold,phone,reader,seconds,frames_read,codes_decoded"),
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
    HOLDS,
    xorshift32,
    blockIdsForIndex,
    payload,
    sha256Hex,
    encoder,
    receiver,
    createSequence,
    gunzip,
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
