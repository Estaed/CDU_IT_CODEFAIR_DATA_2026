"use strict";

// Transfer by camera (Task-18): plays this build's own bytes as a loop of QR frames on one
// phone and reads them back with the camera on another, no network, no file (CLAUDE.md Part 2,
// "Entry points: Transfer by camera"). The camera is touched only here (layer rule 8).
window.CrosscheckTransfer = (() => {
  // Bracket access: qr.js's own declaration is the only place the dotted global reference may
  // appear as text (tests/test_build.py counts it once to check qr.js is inlined only there).
  const crosscheckQR = window.CrosscheckQR;

  const FRAME_PREFIX = "CX";
  const CHUNK_CHARS = 1000;
  const SHOW_INTERVAL_MS = 125; // ~8 fps, setTimeout-driven so the rate is the same on every phone
  const SCAN_INTERVAL_MS = 100; // ~10 fps
  const FRAME_RE = /^CX([0-9a-f]{4})([0-9a-f]{4})([A-Za-z0-9+/=]{1,1000})$/;

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

  // Payload -> frame texts: gzip the page's own bytes, base64 the result (every reader in
  // scan.js hands back a string, not bytes), then split into chunks of up to 1,000 base64
  // characters.
  const frames = async (html) => {
    const bytes = new TextEncoder().encode(html);
    const gzipped = await gzip(bytes);
    const b64 = bytesToBase64(gzipped);
    const count = Math.max(1, Math.ceil(b64.length / CHUNK_CHARS));
    const out = [];
    for (let i = 0; i < count; i++) {
      const chunk = b64.slice(i * CHUNK_CHARS, (i + 1) * CHUNK_CHARS);
      out.push(`${FRAME_PREFIX}${hex4(i)}${hex4(count)}${chunk}`);
    }
    return out;
  };

  // Order-insensitive, duplicates ignored: a Map keyed by frame index. Base64-decodes only once
  // every frame up to the declared count has arrived.
  const reassemble = (frameTexts) => {
    const parts = new Map();
    let total = 0;
    for (const text of frameTexts) {
      const match = typeof text === "string" ? FRAME_RE.exec(text) : null;
      if (!match) {
        continue;
      }
      const index = parseInt(match[1], 16);
      total = parseInt(match[2], 16);
      if (!parts.has(index)) {
        parts.set(index, match[3]);
      }
    }
    const received = parts.size;
    const complete = total > 0 && received === total;
    let bytes = null;
    if (complete) {
      let b64 = "";
      for (let i = 0; i < total; i++) {
        b64 += parts.get(i);
      }
      bytes = base64ToBytes(b64);
    }
    return { complete, received, total, bytes };
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

  // The whole running app, looped as QR frames. Encoded once per Show click, then the loop only
  // swaps a path string, which keeps it cheap on every repeat.
  const buildShow = (getPageHtml) => {
    const button = el("button", { type: "button", class: "transfer__button" }, "Show");
    const stage = el("div", { class: "transfer__stage", hidden: "" });
    const path = svg("path", {});
    const svgEl = svg("svg", { class: "transfer__svg", viewBox: "0 0 1 1" });
    svgEl.appendChild(path);
    const counter = el("div", { class: "transfer__counter" });
    stage.appendChild(svgEl);
    stage.appendChild(counter);

    let renderedFrames = null;
    let index = 0;
    let timer = null;
    let playing = false;

    const step = () => {
      const result = renderedFrames[index];
      svgEl.setAttribute("viewBox", `0 0 ${result.size} ${result.size}`);
      path.setAttribute("d", crosscheckQR.toSvgPath(result));
      counter.textContent = `frame ${index + 1} of ${renderedFrames.length}`;
      index = (index + 1) % renderedFrames.length;
      timer = setTimeout(step, SHOW_INTERVAL_MS);
    };

    const stop = () => {
      if (timer !== null) {
        clearTimeout(timer);
        timer = null;
      }
      playing = false;
      button.textContent = "Show";
    };

    button.addEventListener("click", async () => {
      if (playing) {
        stop();
        return;
      }
      playing = true;
      button.textContent = "Stop";
      const frameTexts = await frames(getPageHtml());
      if (!playing) {
        return; // Stopped again while the page was being encoded.
      }
      renderedFrames = frameTexts.map((text) => crosscheckQR.encode(text, "L"));
      index = 0;
      stage.hidden = false;
      step();
    });

    return { el: el("div", { class: "transfer__section" }, button, stage), stop };
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
    const counter = el("div", { class: "transfer__status", hidden: "" });
    const openButton = el(
      "button",
      { type: "button", class: "transfer__button", hidden: "" },
      "Open received app",
    );
    // Task-24: kept in the browser's own storage (store.js) so the installed app updates in
    // place on the next start; the download button stays for the phone-to-phone file handoff.
    const useReceivedButton = el(
      "button",
      { type: "button", class: "transfer__button", hidden: "" },
      "Use received pack now",
    );
    const downloadLink = el(
      "a",
      { class: "transfer__button", download: "crosscheck.html", hidden: "" },
      "Download crosscheck.html",
    );

    let stream = null;
    let scanTimer = null;
    let scanning = false;
    let receivedTexts = new Set();
    let receivedUrl = null;

    const revokeReceivedUrl = () => {
      if (receivedUrl) {
        URL.revokeObjectURL(receivedUrl);
        receivedUrl = null;
      }
    };

    const resetReceived = () => {
      receivedTexts = new Set();
      counter.hidden = true;
      counter.textContent = "";
      openButton.hidden = true;
      useReceivedButton.hidden = true;
      downloadLink.hidden = true;
      revokeReceivedUrl();
    };

    const stopStream = () => {
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

    const finish = async (bytes) => {
      stop();
      const html = await inflate(bytes);
      // Parsed, not a substring search: this file's own source text must not contain the
      // literal markup it is checking for (tests/test_build.py counts that markup once).
      const parsed = new DOMParser().parseFromString(html, "text/html");
      const looksLikeCrosscheck =
        parsed.documentElement.tagName === "HTML" && parsed.getElementById("pack") !== null;
      if (!looksLikeCrosscheck) {
        counter.hidden = false;
        counter.textContent = "That did not look like Crosscheck; try again.";
        return;
      }
      const blob = new Blob([html], { type: "text/html" });
      revokeReceivedUrl();
      receivedUrl = URL.createObjectURL(blob);
      openButton.hidden = false;
      downloadLink.hidden = false;
      downloadLink.setAttribute("href", receivedUrl);
      counter.hidden = false;
      counter.textContent = "Received the app.";
      // Task-24: the received page's own pack, kept for next start if it validates (store.js
      // rejects anything with a different pack_version or community count on its own).
      const packEl = parsed.getElementById("pack");
      if (packEl && window.CrosscheckStore) {
        try {
          const result = await window.CrosscheckStore.save(packEl.textContent);
          useReceivedButton.hidden = !result || !result.built;
        } catch (error) {
          // Storage is optional; Open and Download still work without it.
        }
      }
    };

    const scan = async () => {
      if (!scanning) {
        return;
      }
      try {
        const values = await window.CrosscheckScan.reader().detect(video);
        for (const value of values) {
          if (typeof value === "string" && value.startsWith(FRAME_PREFIX)) {
            receivedTexts.add(value);
          }
        }
        const partial = reassemble([...receivedTexts]);
        if (partial.total > 0) {
          counter.hidden = false;
          counter.textContent = `received ${partial.received} of ${partial.total}`;
        }
        if (partial.complete) {
          await finish(partial.bytes);
          return;
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
      stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      video.srcObject = stream;
      video.hidden = false;
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

    openButton.addEventListener("click", () => {
      if (receivedUrl) {
        window.open(receivedUrl);
      }
    });

    useReceivedButton.addEventListener("click", () => {
      location.reload();
    });

    return {
      el: el(
        "div",
        { class: "transfer__section" },
        button,
        readerKind,
        note,
        video,
        counter,
        openButton,
        useReceivedButton,
        downloadLink,
      ),
      stop,
      finish,
    };
  };

  let currentStop = null;
  let listenerAdded = false;
  let mountedReceiveFinish = null;

  // Builds the Show and Receive controls into container, replacing any previous ones and
  // stopping their timers and camera track first. getPageHtml is app.js's own pageHtml, the
  // same bytes Save file writes, so Show always plays the running app.
  const mount = (container, getPageHtml) => {
    if (currentStop) {
      currentStop();
      currentStop = null;
    }
    const show = buildShow(getPageHtml);
    const receive = buildReceive();
    mountedReceiveFinish = receive.finish;
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

  return { frames, reassemble, inflate, mount, testReceiveComplete };
})();
