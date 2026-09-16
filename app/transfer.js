"use strict";

// Transfer by camera (Task-18; frame contract v4, Task-37, 2026-09-16 evening): plays the data
// pack as a loop of QR frames on one phone and reads it back with the camera on another, no
// network, no pairing (CLAUDE.md Part 2, "Entry points: Transfer by camera"). The camera is
// touched only here (layer rule 8).
//
// What travels is the **data pack, not the app**. The receiving phone must already have
// Crosscheck -- a phone with only its camera app cannot reassemble frames -- so the camera was
// never an install path; what it is, is the one pairing-free channel between an Android and an
// iPhone with no network. The payload is therefore the inlined pack with `layers` replaced by
// `[]` (the map layers are static geography and the receiver keeps its own), about 18 KB
// gzipped instead of 72, and the loop finishes in seconds.
//
// The rest of the contract is v3's, measured on the S24 in Task-31:
//
//   * the repair degree comes from the robust soliton distribution (c = 0.1, delta = 0.5)
//     instead of v2's uniform 6..12, which was tuned against 10 % frame loss while a real phone
//     loses half or more;
//   * the sender changes the code inside requestAnimationFrame and holds it for 16 refreshes
//     (3.75 frames a second at 60 Hz) -- slower is faster, because fewer captured frames
//     straddle a change. The reader keeps the main-thread setTimeout loop, which round one
//     proved faster on a phone than a worker or requestVideoFrameCallback.
//
// The fountain code: `K` source blocks of 750 bytes plus an unbounded stream of repair blocks,
// each the XOR of a set of source blocks a receiver can recompute from the frame's own index
// alone. A missed frame is repaired by any later frame instead of waiting for its own turn in
// the next loop. `CX` (v1), `CY` (v2) and `CZ` (v3) frames are ignored (FRAME_RE only matches
// `CP`), so a receiver never mixes two contracts.
window.CrosscheckTransfer = (() => {
  // Bracket access: qr.js's own declaration is the only place the dotted global reference may
  // appear as text (tests/test_build.py counts it once to check qr.js is inlined only there).
  const crosscheckQR = window.CrosscheckQR;

  const FRAME_PREFIX = "CP";
  const BLOCK_BYTES = 750;
  const BLOCK_B64_CHARS = 1000; // 750 bytes, divisible by 3, base64s with no padding
  const MAX_INDEX = 0xffff; // 4 hex digits
  // Display refreshes one code is held for: 16 at 60 Hz is 3.75 frames a second, the rate the
  // Task-31 phone trial measured fastest end to end (see the header).
  const HOLD_REFRESHES = 16;
  const SCAN_INTERVAL_MS = 100; // ~10 fps
  const FRAME_RE = new RegExp(
    `^${FRAME_PREFIX}([0-9a-f]{4})([0-9a-f]{4})([0-9a-f]{6})([A-Za-z0-9+/]{${BLOCK_B64_CHARS}})$`,
  );

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
    const reader = stream.getReader();
    for (;;) {
      const { value, done } = await reader.read();
      if (done) {
        break;
      }
      chunks.push(value);
    }
    return concatBytes(chunks);
  };

  const gzip = (bytes) => pump(new Blob([bytes]).stream().pipeThrough(new CompressionStream("gzip")));

  const gunzip = (bytes) => pump(new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip")));

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

  // --- Repair block selection: xorshift32 seeded from the frame index alone, so both ends -----
  // derive the same block set from the index with no side channel.

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

  // Degree: the robust soliton distribution, c = 0.1, delta = 0.5 -- rho (the ideal soliton)
  // plus tau (the extra weight that keeps the decoder's ripple alive), normalised and kept as a
  // cumulative table so one uniform draw and a binary search give the degree. One table per K,
  // built once. v2's uniform 6..12 draw was tuned against 10 % frame loss; a real phone reading
  // a screen loses half or more, and the soliton's low-degree frames are what restart a stalled
  // peel (Task-31, measured on the S24: v2 stalled near block 110, v3 completed in 27.6 s).
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

  // Fisher-Yates partial shuffle drawn from the same generator: `degree` distinct ids in
  // [0, k), deterministic given the generator's state.
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

  // --- Encoder: the payload -> K source blocks, any frame on demand ----------------------------

  // Payload -> encoder: a string is text and is gzipped here (the pack JSON, and what every
  // test passes); a Uint8Array is already the gzipped payload. Either way the payload is split
  // into K blocks of 750 bytes (the last zero-padded), and frameAt(index) then builds a source
  // frame (index < k) or a repair frame (index >= k) on demand, so the sender can play an
  // unbounded repair stream without precomputing it.
  const encoder = async (source) => {
    const payload =
      typeof source === "string" ? await gzip(new TextEncoder().encode(source)) : source;
    const length = payload.length;
    const k = Math.max(1, Math.ceil(length / BLOCK_BYTES));
    const sourceBlocks = [];
    for (let i = 0; i < k; i++) {
      const block = new Uint8Array(BLOCK_BYTES);
      block.set(payload.subarray(i * BLOCK_BYTES, Math.min((i + 1) * BLOCK_BYTES, length)));
      sourceBlocks.push(block);
    }
    const header = (index) => `${FRAME_PREFIX}${hex4(index)}${hex4(k)}${hex6(length)}`;
    const frameAt = (index) => {
      if (index < k) {
        return `${header(index)}${bytesToBase64(sourceBlocks[index])}`;
      }
      const ids = blockIdsForIndex(index, k);
      const xored = new Uint8Array(BLOCK_BYTES);
      for (const id of ids) {
        const block = sourceBlocks[id];
        for (let b = 0; b < BLOCK_BYTES; b++) {
          xored[b] ^= block[b];
        }
      }
      return `${header(index)}${bytesToBase64(xored)}`;
    };
    return { k, length, frameAt };
  };

  // The send order (Execution Guide, revised 2026-09-15 -- see tasks/Task-27.md Status): one
  // pass of the K source frames, then repair frames only (K, K+1, ...), wrapping the repair
  // index before it would overflow its 4 hex digits. No cycling source resend: the swept
  // alternative measured better loss recovery within the DoD's frame budget at the app's real
  // K than resending known-good sources ever did. `pass` counts full laps through the repair
  // index space (1 for the initial source pass, +1 every time the repair index wraps back to
  // K), shown on the sending screen so a phone that starts late can tell frames keep coming.
  const createSequence = (k) => {
    let pass = 1;
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
        return { index, pass };
      }
      const index = repairIndex;
      repairIndex += 1;
      if (repairIndex >= MAX_INDEX) {
        repairIndex = k;
        pass += 1;
      }
      return { index, pass };
    };

    return { next };
  };

  // --- Receiver: a peeling decoder over pushed frame texts --------------------------------------

  // Order-insensitive, duplicates and repeats harmless: source frames are known outright; a
  // repair frame is reduced by XOR-ing out every block already known, and when only one unknown
  // block is left in a repair frame (now or after a later block resolves it), that block becomes
  // known and every other pending repair frame is reduced again (peeling).
  const receiver = () => {
    let k = null;
    let length = null;
    const known = new Map(); // index -> Uint8Array(BLOCK_BYTES)
    const pending = []; // { ids: Set<number>, data: Uint8Array }
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

    const push = (text) => {
      const match = typeof text === "string" ? FRAME_RE.exec(text) : null;
      if (match) {
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
      return { complete: k !== null && known.size === k, known: known.size, total: k || 0 };
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

  const inflate = async (bytes) => {
    const inflated = await gunzip(bytes);
    return new TextDecoder().decode(inflated);
  };

  // --- Show and Receive controls, appended to the share screen (app.js: renderShare) --------

  const el = (tag, attrs, ...children) => {
    const node = document.createElement(tag);
    if (attrs) {
      for (const [key, value] of Object.entries(attrs)) {
        if (value !== null && value !== undefined) {
          node.setAttribute(key, value);
        }
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

  // The HTML parser places <svg> and <path> in the SVG namespace; reading it back keeps a
  // namespace URL literal out of this file (layer rule 7 forbids one).
  const SVG_NS = (() => {
    const template = document.createElement("template");
    template.innerHTML = "<svg><path></path></svg>";
    return template.content.firstChild.namespaceURI;
  })();

  const svg = (tag, attrs) => {
    const node = document.createElementNS(SVG_NS, tag);
    for (const [key, value] of Object.entries(attrs || {})) {
      node.setAttribute(key, value);
    }
    return node;
  };

  // --- What the camera carries -----------------------------------------------------------------

  // The text the camera carries: the pack this copy is currently running with -- the stored one
  // if a received pack replaced the inline one, the inline one otherwise (store.js keeps that
  // one definition) -- with `layers` emptied. Read at Show time, not at load: the pack a phone
  // holds may be newer than the build it is running, and that newer pack is exactly what the
  // next phone wants.
  const packText = async () => {
    const inline = JSON.parse(document.getElementById("pack").textContent);
    const current = window.CrosscheckStore ? await window.CrosscheckStore.effective() : inline;
    return JSON.stringify({ ...current, layers: [] });
  };

  // The pack, looped as QR frames. Encoded once per Show click, then the loop only swaps a path
  // string, which keeps it cheap on every repeat. Every index (source or repair) is sent exactly
  // once per lap of the send order, so there is nothing worth caching between steps -- each
  // frame is QR-encoded fresh.
  const buildShow = () => {
    const button = el("button", { type: "button", class: "transfer__button" }, "Show");
    const stage = el("div", { class: "transfer__stage", hidden: "" });
    const path = svg("path", {});
    const svgEl = svg("svg", { class: "transfer__svg", viewBox: "0 0 1 1" });
    svgEl.appendChild(path);
    const counter = el("div", { class: "transfer__counter" });
    const note = el(
      "p",
      { class: "transfer__note" },
      "Keep showing until the other phone says Received.",
    );
    stage.appendChild(svgEl);
    stage.appendChild(counter);
    stage.appendChild(note);

    let built = null;
    let sequence = null;
    let rafId = null;
    let refreshes = 0;
    let playing = false;
    let frameCount = 0;
    // Task-30: the showing phone must not dim mid-transfer; best effort where Wake Lock exists.
    let wakeLock = null;
    const holdScreen = async () => {
      try {
        wakeLock = navigator.wakeLock ? await navigator.wakeLock.request("screen") : null;
      } catch (error) {
        wakeLock = null;
      }
    };
    const releaseScreen = () => {
      if (wakeLock) {
        wakeLock.release().catch(() => {});
        wakeLock = null;
      }
    };

    const paint = () => {
      const { index, pass } = sequence.next();
      frameCount += 1;
      const result = crosscheckQR.encode(built.frameAt(index), "L");
      svgEl.setAttribute("viewBox", `0 0 ${result.size} ${result.size}`);
      path.setAttribute("d", crosscheckQR.toSvgPath(result));
      counter.textContent = `frame ${frameCount}, pass ${pass}`;
    };

    // The code changes inside requestAnimationFrame and is held for HOLD_REFRESHES refreshes, so
    // a change never lands mid-repaint and the reading phone gets several whole camera frames of
    // each code. A setTimeout at the same nominal rate was measured slower on the S24 (Task-31).
    const loop = () => {
      if (!playing) {
        return;
      }
      if (refreshes === 0) {
        paint();
      }
      refreshes = (refreshes + 1) % HOLD_REFRESHES;
      rafId = requestAnimationFrame(loop);
    };

    const stop = () => {
      if (rafId !== null) {
        cancelAnimationFrame(rafId);
        rafId = null;
      }
      playing = false;
      releaseScreen();
      button.textContent = "Show";
    };

    button.addEventListener("click", async () => {
      if (playing) {
        stop();
        return;
      }
      playing = true;
      button.textContent = "Stop";
      holdScreen();
      built = await encoder(await packText());
      if (!playing) {
        return; // Stopped again while the page was being encoded.
      }
      sequence = createSequence(built.k);
      frameCount = 0;
      refreshes = 0;
      stage.hidden = false;
      loop();
    });

    return {
      el: el(
        "div",
        { class: "transfer__section" },
        el("h2", { class: "transfer__title" }, "Send the latest data by camera"),
        el(
          "p",
          { class: "transfer__note" },
          "No internet, no pairing. The other phone needs Crosscheck installed; it taps Receive and points its camera at the moving code.",
        ),
        button,
        stage,
      ),
      stop,
    };
  };

  // Reads the frames back with the camera and reassembles, inflates and offers the result.
  const buildReceive = () => {
    const button = el("button", { type: "button", class: "transfer__button" }, "Receive");
    // Task-25: which reader is running, so a phone test says jsQR ran without opening devtools.
    const readerKind = el(
      "p",
      { class: "transfer__reader" },
      `reader: ${window.CrosscheckScan.kind()}`,
    );
    const note = el("p", { class: "transfer__note", hidden: "" });
    const video = el("video", {
      class: "transfer__video",
      autoplay: "",
      playsinline: "",
      muted: "",
      hidden: "",
    });
    const progress = el("progress", { class: "transfer__progress", hidden: "" });
    const counter = el("div", { class: "transfer__status", hidden: "" });
    // Task-24: the received pack is kept in the browser's own storage (store.js) and used on
    // every later start. Since Task-37 there is no page to open and no file to download: what
    // arrived is data for the copy already running here.
    const useReceivedButton = el(
      "button",
      { type: "button", class: "transfer__button", hidden: "" },
      "Use received data now",
    );

    let stream = null;
    let untune = null;
    let scanTimer = null;
    let scanning = false;
    let currentReceiver = null;

    const resetReceived = () => {
      currentReceiver = receiver();
      progress.hidden = true;
      progress.removeAttribute("value");
      progress.removeAttribute("max");
      counter.hidden = true;
      counter.textContent = "";
      useReceivedButton.hidden = true;
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
      video.hidden = true;
    };

    const stop = () => {
      if (scanTimer !== null) {
        clearTimeout(scanTimer);
        scanTimer = null;
      }
      scanning = false;
      stopStream();
      button.textContent = "Receive";
    };

    // Every block known: inflate, check it parses, and hand it to store.js, which owns what a
    // pack must be (pack_version, 96 communities) and carries this copy's map layers over the
    // incoming empty ones. Three outcomes, three sentences: stored, too old, or not a pack.
    const finish = async (bytes) => {
      stop();
      const text = await inflate(bytes);
      try {
        JSON.parse(text);
      } catch (error) {
        counter.hidden = false;
        counter.textContent = "That did not look like Crosscheck data; try again";
        return;
      }
      let result = null;
      try {
        result = window.CrosscheckStore ? await window.CrosscheckStore.save(text) : null;
      } catch (error) {
        result = null; // Storage is optional; the refusal below is what the screen says.
      }
      counter.hidden = false;
      if (result && result.built) {
        counter.textContent = "Received. Tap to use the new data.";
        useReceivedButton.hidden = false;
        if (navigator.vibrate) {
          navigator.vibrate(200);
        }
        return;
      }
      counter.textContent =
        result && result.reason === "pack_version"
          ? "This copy is too old for that data; open the address once with the internet"
          : "That did not look like Crosscheck data; try again";
    };

    // One frame text in, progress UI updated, finish() called once every block is known. Shared
    // by the real scan loop below and by testPushFrame (no camera in the browser test).
    const pushFrame = async (text) => {
      const status = currentReceiver.push(text);
      if (status.total > 0) {
        progress.hidden = false;
        progress.setAttribute("max", String(status.total));
        progress.setAttribute("value", String(status.known));
        counter.hidden = false;
        counter.textContent = `${status.known} of ${status.total} blocks`;
      }
      if (status.complete) {
        await finish(currentReceiver.bytes());
      }
      return status;
    };

    const scan = async () => {
      if (!scanning) {
        return;
      }
      try {
        const values = await window.CrosscheckScan.reader().detect(video);
        for (const value of values) {
          if (typeof value === "string") {
            const status = await pushFrame(value);
            if (status.complete) {
              return;
            }
          }
        }
      } catch (error) {
        // One failed detect() call (decode noise on a single frame) is not fatal; keep scanning.
      }
      if (scanning) {
        scanTimer = setTimeout(scan, SCAN_INTERVAL_MS);
      }
    };

    const start = async () => {
      resetReceived();
      stream = await navigator.mediaDevices.getUserMedia(window.CrosscheckScan.constraints());
      video.srcObject = stream;
      video.hidden = false;
      untune = window.CrosscheckScan.tune(stream, video);
      scanning = true;
      button.textContent = "Stop";
      scan();
    };

    button.addEventListener("click", () => {
      if (scanning || stream) {
        stop();
        return;
      }
      if (!navigator.mediaDevices) {
        note.hidden = false;
        note.textContent = "This browser cannot use the camera.";
        return;
      }
      note.hidden = true;
      start().catch((error) => {
        stop();
        counter.hidden = false;
        const why = error && error.name ? ` (${error.name}, ${location.protocol})` : "";
        counter.textContent = `Could not access the camera${why}.`;
      });
    });

    useReceivedButton.addEventListener("click", () => {
      location.reload();
    });

    resetReceived();

    return {
      el: el(
        "div",
        { class: "transfer__section" },
        el("h2", { class: "transfer__title" }, "Receive new data by camera"),
        el(
          "p",
          { class: "transfer__note" },
          "Point this camera at the other phone's moving code. Your copy keeps working while it arrives.",
        ),
        button,
        readerKind,
        note,
        video,
        progress,
        counter,
        useReceivedButton,
      ),
      stop,
      finish,
      pushFrame: (text) => pushFrame(text),
    };
  };

  let currentStop = null;
  let listenerAdded = false;
  let mountedReceiveFinish = null;
  let mountedReceivePush = null;

  // Builds the Show and Receive controls into container, replacing any previous ones and
  // stopping their timers and camera track first. app.js still passes its own pageHtml as the
  // second argument (that file is not this task's to change); since Task-37 what Show plays is
  // the pack, not the page, so the argument is ignored.
  const mount = (container) => {
    if (currentStop) {
      currentStop();
      currentStop = null;
    }
    const show = buildShow();
    const receive = buildReceive();
    mountedReceiveFinish = receive.finish;
    mountedReceivePush = receive.pushFrame;
    container.textContent = "";
    container.appendChild(show.el);
    container.appendChild(receive.el);
    currentStop = () => {
      show.stop();
      receive.stop();
    };
    if (!listenerAdded) {
      listenerAdded = true;
      window.addEventListener("hashchange", () => {
        if (currentStop) {
          currentStop();
          currentStop = null;
        }
      });
    }
  };

  // Exposed for the browser test, which has no camera: drives the same completion path the
  // scan loop calls once the camera has read every frame (Task-24 DoD).
  const testReceiveComplete = (bytes) => mountedReceiveFinish(bytes);

  // Exposed for the browser test: pushes one frame text through the currently mounted receiver
  // and its progress UI, exactly as the scan loop would (Task-27 DoD).
  const testPushFrame = (text) => mountedReceivePush(text);

  // Exposed for the browser test: the exact text Show would encode, so the round trip is run
  // against the payload the sender really plays rather than one the test rebuilds (Task-37).
  const testPayloadText = () => packText();

  return {
    encoder,
    receiver,
    createSequence,
    inflate,
    mount,
    testReceiveComplete,
    testPushFrame,
    testPayloadText,
  };
})();
