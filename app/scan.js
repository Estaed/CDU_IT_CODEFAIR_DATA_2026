"use strict";

// One QR reader adapter (Task-25, OQ15): Safari on iPhone has never shipped BarcodeDetector
// (broken since iOS 18), so this is the only place in the app that decides which reader runs.
// transfer.js and nearby.js call CrosscheckScan.reader().detect(video) and never touch
// BarcodeDetector or the vendored app/vendor/jsQR.js directly (the build test checks this).
// The camera itself is never touched here (layer rule 8): this file receives a <video> element
// already playing a stream and returns decoded strings, nothing more.
window.CrosscheckScan = (() => {
  // A plain number, not CSS (Execution Guide): the longer side of the frame handed to jsQR.
  const MAX_JSQR_SIDE = 720;

  const hasNative = () => "BarcodeDetector" in window;

  let nativeDetector = null;
  const getNativeDetector = () => {
    if (!nativeDetector) {
      nativeDetector = new window.BarcodeDetector({ formats: ["qr_code"] });
    }
    return nativeDetector;
  };

  // One reusable offscreen canvas for the jsQR path, resized only when the source frame's own
  // size changes, so repeat calls on the same video stream stay cheap.
  let canvas = null;
  let ctx = null;
  const sizeForJsqr = (sourceWidth, sourceHeight) => {
    const scale = Math.min(1, MAX_JSQR_SIDE / Math.max(sourceWidth, sourceHeight));
    return {
      width: Math.max(1, Math.round(sourceWidth * scale)),
      height: Math.max(1, Math.round(sourceHeight * scale)),
    };
  };

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
    const { width, height } = sizeForJsqr(sourceWidth, sourceHeight);
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
    }
    ctx.drawImage(video, 0, 0, width, height);
    const imageData = ctx.getImageData(0, 0, width, height);
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

  return { reader, decodeImageData, kind };
})();
