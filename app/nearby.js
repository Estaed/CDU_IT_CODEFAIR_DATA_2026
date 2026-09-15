"use strict";

// Nearby chat over the phone's own Wi-Fi (Task-19): two phones exchange an SDP offer/answer as
// QR codes, then talk directly over a WebRTC data channel; no server, no STUN, no TURN
// (CLAUDE.md Part 2, "Entry points: Nearby chat"; reports/spike-webrtc-hotspot/ is the working
// reference for the calls below). The camera is touched only here and in transfer.js (layer
// rule 8); CrosscheckTransfer exposes no reusable scanner, so buildScanButton below is its own
// ~30-line copy of the same shape as transfer.js's buildReceive scan loop.
window.CrosscheckNearby = (() => {
  const ICE_GATHER_TIMEOUT_MS = 3000;
  const SCAN_INTERVAL_MS = 100;

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

  const deflate = (bytes) =>
    pump(new Blob([bytes]).stream().pipeThrough(new CompressionStream("deflate-raw")));

  const inflateBytes = (bytes) =>
    pump(new Blob([bytes]).stream().pipeThrough(new DecompressionStream("deflate-raw")));

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

  // Offer/answer text (Execution Guide): the full SDP JSON, deflated and base64-encoded.
  const encodeSdp = async (description) => {
    const json = JSON.stringify({ type: description.type, sdp: description.sdp });
    const deflated = await deflate(new TextEncoder().encode(json));
    return bytesToBase64(deflated);
  };

  const decodeSdp = async (text) => {
    const inflated = await inflateBytes(base64ToBytes(text));
    return JSON.parse(new TextDecoder().decode(inflated));
  };

  const waitForIceGatheringComplete = (peer) =>
    new Promise((resolve) => {
      if (peer.iceGatheringState === "complete") {
        resolve();
        return;
      }
      let done = false;
      const timer = setTimeout(() => {
        if (!done) {
          done = true;
          resolve();
        }
      }, ICE_GATHER_TIMEOUT_MS);
      peer.addEventListener("icegatheringstatechange", function onChange() {
        if (peer.iceGatheringState === "complete" && !done) {
          done = true;
          clearTimeout(timer);
          peer.removeEventListener("icegatheringstatechange", onChange);
          resolve();
        }
      });
    });

  // Chrome rejects a single RTCDataChannel message over its negotiated max-message-size
  // (measured 2026-09-15: the ~450 KB pack fails whole; "pack-data" from the Execution Guide
  // is one logical message but many wire messages, {t:"pack-chunk", i, n, part}, chosen well
  // under any browser's limit; onEvent still sees one "pack" event with the full text).
  const PACK_CHUNK_CHARS = 16000;

  let pc = null;
  let dc = null;
  let handler = null;
  let packChunks = null;
  // Camera scanners started by buildScanButton register their own stop() here, so close()
  // (called on every hashchange) stops every open stream, not only the peer connection.
  const activeScans = new Set();

  const emit = (event) => {
    if (handler) {
      handler(event);
    }
  };

  // One handler at a time: the screen that owns #/nearby re-registers on every mount, which
  // is also how the previous screen's listener is dropped (CLAUDE.md Part 2, layer rule 4).
  const onEvent = (fn) => {
    handler = fn;
  };

  const wireDataChannel = () => {
    dc.addEventListener("open", () => emit({ type: "state", state: "open" }));
    dc.addEventListener("close", () => emit({ type: "state", state: "closed" }));
    dc.addEventListener("error", () => emit({ type: "error" }));
    dc.addEventListener("message", (event) => {
      let message;
      try {
        message = JSON.parse(event.data);
      } catch (error) {
        return; // Not one of ours; ignored rather than crashing the channel.
      }
      if (message.t === "msg") {
        emit({ type: "msg", who: "peer", text: message.text });
      } else if (message.t === "pack") {
        const json = document.getElementById("pack").textContent;
        const n = Math.max(1, Math.ceil(json.length / PACK_CHUNK_CHARS));
        for (let i = 0; i < n; i++) {
          const part = json.slice(i * PACK_CHUNK_CHARS, (i + 1) * PACK_CHUNK_CHARS);
          dc.send(JSON.stringify({ t: "pack-chunk", i, n, part }));
        }
      } else if (message.t === "pack-chunk") {
        if (!packChunks || packChunks.length !== message.n) {
          packChunks = new Array(message.n).fill(null);
        }
        packChunks[message.i] = message.part;
        if (packChunks.every((part) => part !== null)) {
          const json = packChunks.join("");
          packChunks = null;
          // Task-24: kept for next start if it validates (store.js checks pack_version and the
          // community count on its own); the event fires only after the save settles, so a
          // listener that reacts to it can rely on the store already holding this pack.
          (async () => {
            if (window.CrosscheckStore) {
              try {
                await window.CrosscheckStore.save(json);
              } catch (error) {
                // Storage is optional; the chat and the pack event still work without it.
              }
            }
            emit({ type: "pack", json });
          })();
        }
      }
    });
  };

  const start = async () => {
    pc = new RTCPeerConnection({ iceServers: [] });
    dc = pc.createDataChannel("chat");
    wireDataChannel();
    await pc.setLocalDescription(await pc.createOffer());
    await waitForIceGatheringComplete(pc);
    return encodeSdp(pc.localDescription);
  };

  const accept = async (offerText) => {
    const offer = await decodeSdp(offerText);
    pc = new RTCPeerConnection({ iceServers: [] });
    pc.addEventListener("datachannel", (event) => {
      dc = event.channel;
      wireDataChannel();
    });
    await pc.setRemoteDescription(offer);
    await pc.setLocalDescription(await pc.createAnswer());
    await waitForIceGatheringComplete(pc);
    return encodeSdp(pc.localDescription);
  };

  const finish = async (answerText) => {
    const answer = await decodeSdp(answerText);
    await pc.setRemoteDescription(answer);
  };

  const send = (text) => {
    if (!dc || dc.readyState !== "open") {
      return;
    }
    dc.send(JSON.stringify({ t: "msg", text }));
    emit({ type: "msg", who: "me", text });
  };

  const requestPack = () => {
    if (!dc || dc.readyState !== "open") {
      return;
    }
    dc.send(JSON.stringify({ t: "pack" }));
  };

  const close = () => {
    for (const stop of [...activeScans]) {
      stop();
    }
    if (dc) {
      dc.close();
      dc = null;
    }
    if (pc) {
      pc.close();
      pc = null;
    }
    packChunks = null;
    emit({ type: "state", state: "closed" });
  };

  window.addEventListener("hashchange", close);

  // Reads one QR code from the camera, then stops itself. Every stream this starts is tracked
  // in activeScans so a route change (hashchange -> close()) always stops it (layer rule 8).
  const buildScanButton = (label, onCode) => {
    const wrap = document.createElement("div");
    wrap.className = "nearby__scanner";
    const button = document.createElement("button");
    button.type = "button";
    button.className = "nearby__button";
    button.textContent = label;
    const video = document.createElement("video");
    video.className = "nearby__video";
    video.autoplay = true;
    video.playsInline = true;
    video.muted = true;
    video.hidden = true;
    wrap.append(button, video);

    let stream = null;
    let timer = null;
    let detector = null;

    const stop = () => {
      if (timer !== null) {
        clearTimeout(timer);
        timer = null;
      }
      if (stream) {
        for (const track of stream.getTracks()) {
          track.stop();
        }
        stream = null;
      }
      video.hidden = true;
      button.textContent = label;
      activeScans.delete(stop);
    };

    const tick = async () => {
      if (!stream) {
        return;
      }
      try {
        const codes = await detector.detect(video);
        if (codes.length > 0) {
          const text = codes[0].rawValue;
          stop();
          onCode(text);
          return;
        }
      } catch (error) {
        // One failed detect() call (decode noise on a single frame) is not fatal; keep scanning.
      }
      if (stream) {
        timer = setTimeout(tick, SCAN_INTERVAL_MS);
      }
    };

    button.addEventListener("click", async () => {
      if (stream) {
        stop();
        return;
      }
      if (!("BarcodeDetector" in window)) {
        button.disabled = true;
        button.title = "This browser cannot scan QR codes with the camera.";
        return;
      }
      detector = detector || new window.BarcodeDetector({ formats: ["qr_code"] });
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      } catch (error) {
        return;
      }
      activeScans.add(stop);
      video.srcObject = stream;
      video.hidden = false;
      button.textContent = "Stop";
      tick();
    });

    return { el: wrap, stop };
  };

  return { start, accept, finish, send, requestPack, close, onEvent, buildScanButton };
})();
