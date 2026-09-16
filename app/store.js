"use strict";

// Received-pack storage (Task-24): a pack that arrives by light (transfer.js) is kept here,
// so the installed app uses it on every later start with no network
// (CLAUDE.md Part 2, "Pack header" seam; Tarik's decision 2026-09-15: "update atsın"). IndexedDB
// only; no network word appears in this file (layer rule 7).
window.CrosscheckStore = (() => {
  const DB_NAME = "crosscheck";
  const STORE_NAME = "pack";
  const RECORD_KEY = "pack";
  const REQUIRED_COMMUNITY_COUNT = 96;
  // Task-35: the reports a person recorded on this phone, one object store beside the pack in
  // the same database, each row keyed on its own line so storing the same line twice is one
  // row. Version 2 because the store is new; the pack's own record and its validation are
  // untouched by the upgrade.
  const REPORTS_STORE = "reports";
  const DB_VERSION = 2;

  // Read fresh every call rather than cached at module load: the built-in pack is the one
  // truth a candidate is checked against, regardless of what is currently rendered.
  const builtInPack = () => JSON.parse(document.getElementById("pack").textContent);

  let warned = false;
  const warnOnce = (error) => {
    if (!warned) {
      warned = true;
      console.warn("CrosscheckStore: IndexedDB unavailable, no stored pack", error);
    }
  };

  const openDb = () =>
    new Promise((resolve, reject) => {
      let request;
      try {
        request = indexedDB.open(DB_NAME, DB_VERSION);
      } catch (error) {
        reject(error);
        return;
      }
      request.addEventListener("upgradeneeded", () => {
        const db = request.result;
        for (const name of [STORE_NAME, REPORTS_STORE]) {
          if (!db.objectStoreNames.contains(name)) {
            db.createObjectStore(name);
          }
        }
      });
      request.addEventListener("success", () => resolve(request.result));
      request.addEventListener("error", () => reject(request.error));
      request.addEventListener("blocked", () => reject(new Error("IndexedDB blocked")));
    });

  // Runs one transaction; fn receives the object store and may return an IDBRequest, whose
  // result becomes this promise's resolved value once the transaction completes.
  const runTx = (storeName, mode, fn) =>
    openDb().then(
      (db) =>
        new Promise((resolve, reject) => {
          const tx = db.transaction(storeName, mode);
          const store = tx.objectStore(storeName);
          let result;
          const request = fn(store);
          if (request && typeof request.addEventListener === "function") {
            request.addEventListener("success", () => {
              result = request.result;
            });
          }
          tx.addEventListener("complete", () => {
            db.close();
            resolve(result);
          });
          tx.addEventListener("error", () => {
            db.close();
            reject(tx.error);
          });
          tx.addEventListener("abort", () => {
            db.close();
            reject(tx.error);
          });
        }),
    );

  // The pack this copy is actually running with: the stored one when it is newer than the
  // built-in one (the same test app.js applies at startup), the built-in one otherwise. One
  // definition, read by save() below for the layers carry-over and by transfer.js for what the
  // camera plays (Task-37).
  const effective = async () => {
    let stored = null;
    try {
      stored = await load();
    } catch (error) {
      stored = null;
    }
    const builtIn = builtInPack();
    if (stored && typeof stored.built === "string" && stored.built > builtIn.built) {
      return stored;
    }
    return builtIn;
  };

  // Rejects a pack whose pack_version differs from the built-in one or whose community count
  // is not 96; never stores anything else. Never throws: a refusal (bad shape, bad IndexedDB)
  // resolves with {built: null} rather than an error on screen. A refusal on pack_version says
  // so in `reason`, because that is the one case the receiving screen explains (Task-37).
  //
  // Carry-over (Task-37): the camera carries the pack with `layers` emptied -- the map layers
  // are static geography, about 24 times the size of everything else, and the receiving phone
  // already has them. An incoming empty `layers` therefore means "keep yours", not "I have
  // none", so the effective pack's layers are written into the stored record.
  const save = async (packJson) => {
    let candidate;
    try {
      candidate = JSON.parse(packJson);
    } catch (error) {
      return { built: null };
    }
    const communityCount = Array.isArray(candidate.communities) ? candidate.communities.length : -1;
    if (candidate.pack_version !== builtInPack().pack_version) {
      return { built: null, reason: "pack_version" };
    }
    if (communityCount !== REQUIRED_COMMUNITY_COUNT) {
      return { built: null };
    }
    let json = packJson;
    if (Array.isArray(candidate.layers) && candidate.layers.length === 0) {
      const current = await effective();
      if (
        current.pack_version === candidate.pack_version &&
        Array.isArray(current.layers) &&
        current.layers.length > 0
      ) {
        candidate.layers = current.layers;
        json = JSON.stringify(candidate);
      }
    }
    try {
      await runTx(STORE_NAME, "readwrite", (store) =>
        store.put({ json, built: candidate.built }, RECORD_KEY),
      );
    } catch (error) {
      warnOnce(error);
      return { built: null };
    }
    return { built: candidate.built };
  };

  const load = async () => {
    let record;
    try {
      record = await runTx(STORE_NAME, "readonly", (store) => store.get(RECORD_KEY));
    } catch (error) {
      warnOnce(error);
      return null;
    }
    if (!record) {
      return null;
    }
    try {
      return JSON.parse(record.json);
    } catch (error) {
      return null;
    }
  };

  const clear = async () => {
    try {
      await runTx(STORE_NAME, "readwrite", (store) => store.delete(RECORD_KEY));
    } catch (error) {
      warnOnce(error);
    }
  };

  // --- reports (Task-35) ---------------------------------------------------------------------
  // "Well-formed" has one definition, window.CrosscheckReport.parse, and it lives in report.js
  // beside the line format itself. report.js is inlined after this file (build_app.JS_FILES),
  // so the global is read at call time, never at definition time.

  const saveReport = async (line) => {
    try {
      await runTx(REPORTS_STORE, "readwrite", (store) => store.put(line, line));
    } catch (error) {
      warnOnce(error);
      return false;
    }
    return true;
  };

  const allReports = async () => {
    try {
      const lines = await runTx(REPORTS_STORE, "readonly", (store) => store.getAll());
      return Array.isArray(lines) ? lines : [];
    } catch (error) {
      warnOnce(error);
      return [];
    }
  };

  // Every stored line for one community, oldest first; a row that no longer parses (a line
  // written by a later format) is left out rather than shown half-read.
  const reportsFor = async (bushtelId) => {
    const parsed = (await allReports())
      .map((line) => ({ line, record: window.CrosscheckReport.parse(line) }))
      .filter((entry) => entry.record && entry.record.id === bushtelId);
    parsed.sort((a, b) => (a.record.time < b.record.time ? -1 : 1));
    return parsed.map((entry) => entry.line);
  };

  // One line per row: keeps the well-formed CR1 lines, drops the rest, and counts a line
  // repeated in the text once. Returns how many were kept; a line already stored is written
  // again over its own key, so the store never holds two copies of one line.
  const importReports = async (text) => {
    const kept = [];
    const seen = new Set();
    for (const raw of String(text).split("\n")) {
      const line = raw.trim();
      if (!line || seen.has(line) || !window.CrosscheckReport.parse(line)) {
        continue;
      }
      seen.add(line);
      kept.push(line);
    }
    if (kept.length) {
      try {
        await runTx(REPORTS_STORE, "readwrite", (store) => {
          let request;
          for (const line of kept) {
            request = store.put(line, line);
          }
          return request;
        });
      } catch (error) {
        warnOnce(error);
        return 0;
      }
    }
    return kept.length;
  };

  return { save, load, effective, clear, saveReport, reportsFor, importReports };
})();
