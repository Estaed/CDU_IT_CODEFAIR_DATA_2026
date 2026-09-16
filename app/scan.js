"use strict";

// One QR reader adapter (Task-25, OQ15): Safari on iPhone has never shipped BarcodeDetector
// (broken since iOS 18), so this is the only place in the app that decides which reader runs.
// transfer.js calls CrosscheckScan.reader().detect(video) and never touches
// BarcodeDetector or the vendored app/vendor/jsQR.js directly (the build test checks this).
// This file never opens the camera (layer rule 8): transfer.js opens the stream
// with constraints() and hands it to tune(), which only adjusts focus and zoom on that stream
// (Task-30), and detect() receives a <video> already playing it.
window.CrosscheckScan = (() => {
  // A plain number, not CSS: the longest side of the square handed to jsQR.
  const MAX_JSQR_SIDE = 1024;
  // After a tap-to-focus the camera returns to continuous focus once this has passed.
  const REFOCUS_MS = 2500;

  const hasNative = () => "BarcodeDetector" in window;

  // Task-30: the camera's default is often 640x480, where a transfer frame's modules are two or
  // three pixels wide; ask for more and let the browser pick the nearest it has.
  const constraints = () => ({
    audio: false,
    video: { facingMode: "environment", width: { ideal: 1920 }, height: { ideal: 1080 } },
  });

  // The centred square of the frame: the reader is told to hold the code in the middle, and
  // cropping instead of shrinking the whole frame keeps each module several pixels wide.
  const cropRect = (width, height) => {
    const side = Math.min(width, height);
    return {
      sx: Math.floor((width - side) / 2),
      sy: Math.floor((height - side) / 2),
      side,
      outSide: Math.min(side, MAX_JSQR_SIDE),
    };
  };

  let nativeDetector = null;
  const getNativeDetector = () => {
    if (!nativeDetector) {
      nativeDetector = new window.BarcodeDetector({ formats: ["qr_code"] });
    }
    return nativeDetector;
  };

  // One reusable offscreen canvas for the jsQR path, resized only when the crop size changes.
  let canvas = null;
  let ctx = null;

  // The jsQR path alone, exposed for tests that have no camera and draw their own image data.
  const decodeImageData = (imageData) => {
    const code = window.jsQR(imageData.data, imageData.width, imageData.height, {
      inversionAttempts: "dontInvert",
    });
    return code ? code.data : null;
  };

  const detectWithJsqr = (video) => {
    const sourceWidth = video.videoWidth || video.width || 0;
    const sourceHeight = video.videoHeight || video.height || 0;
    if (!sourceWidth || !sourceHeight) {
      return [];
    }
    if (!canvas) {
      canvas = document.createElement("canvas");
      ctx = canvas.getContext("2d", { willReadFrequently: true });
    }
    const { sx, sy, side, outSide } = cropRect(sourceWidth, sourceHeight);
    if (canvas.width !== outSide || canvas.height !== outSide) {
      canvas.width = outSide;
      canvas.height = outSide;
    }
    ctx.drawImage(video, sx, sy, side, side, 0, 0, outSide, outSide);
    const imageData = ctx.getImageData(0, 0, outSide, outSide);
    const text = decodeImageData(imageData);
    return text === null ? [] : [text];
  };

  const nativeReader = {
    detect: async (video) => {
      const codes = await getNativeDetector().detect(video);
      return codes.map((code) => code.rawValue);
    },
  };

  const jsqrReader = {
    detect: async (video) => detectWithJsqr(video),
  };

  const reader = () => (hasNative() ? nativeReader : jsqrReader);

  const kind = () => (hasNative() ? "native" : "jsqr");

  // Task-30: continuous focus where the track has it, tap the picture to focus there, and a zoom
  // slider where the track can zoom (step back from a phone screen, then zoom in, is what gets a
  // close code in focus). Every call is best effort: a browser that ignores a constraint still
  // scans. Returns the undo, which the caller runs when it stops the stream.
  const tune = (stream, video) => {
    const [track] = stream.getVideoTracks();
    if (!track) {
      return () => {};
    }
    const caps = typeof track.getCapabilities === "function" ? track.getCapabilities() : {};
    const focusModes = caps.focusMode || [];
    const apply = (set) => track.applyConstraints({ advanced: [set] }).catch(() => {});
    if (focusModes.includes("continuous")) {
      apply({ focusMode: "continuous" });
    }

    const added = [];
    const hint = document.createElement("p");
    hint.className = "scan-hint";
    hint.textContent = "Hold the code in the middle of the picture. Tap the picture to focus.";
    added.push(hint);

    const zoom = caps.zoom;
    if (zoom && zoom.max > zoom.min) {
      const label = document.createElement("label");
      label.className = "scan-zoom";
      const slider = document.createElement("input");
      slider.type = "range";
      slider.min = String(zoom.min);
      slider.max = String(zoom.max);
      slider.step = String(zoom.step || 0.1);
      const settings = typeof track.getSettings === "function" ? track.getSettings() : {};
      slider.value = String(settings.zoom || zoom.min);
      slider.addEventListener("input", () => apply({ zoom: Number(slider.value) }));
      label.append("Zoom", slider);
      added.push(label);
    }
    video.after(...added);

    let refocusTimer = null;
    const onTap = async (event) => {
      const rect = video.getBoundingClientRect();
      const x = Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width));
      const y = Math.min(1, Math.max(0, (event.clientY - rect.top) / rect.height));
      await apply({ pointsOfInterest: [{ x, y }] });
      if (focusModes.includes("single-shot")) {
        await apply({ focusMode: "single-shot" });
      } else if (focusModes.includes("manual") && focusModes.includes("continuous")) {
        // Leaving continuous and returning makes many cameras run a fresh focus sweep.
        await apply({ focusMode: "manual" });
        await apply({ focusMode: "continuous" });
      }
      clearTimeout(refocusTimer);
      if (focusModes.includes("continuous")) {
        refocusTimer = setTimeout(() => apply({ focusMode: "continuous" }), REFOCUS_MS);
      }
    };
    video.addEventListener("click", onTap);

    return () => {
      clearTimeout(refocusTimer);
      video.removeEventListener("click", onTap);
      for (const node of added) {
        node.remove();
      }
    };
  };

  return { reader, decodeImageData, kind, constraints, cropRect, tune };
})();
