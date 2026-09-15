"use strict";

// Received-pack storage (Task-24): a pack that arrives by light (transfer.js) or nearby chat
// (nearby.js) is kept here, so the installed app uses it on every later start with no network
// (CLAUDE.md Part 2, "Pack header" seam; Tarik's decision 2026-09-15: "update atsın"). IndexedDB
// only; no network word appears in this file (layer rule 7).
window.CrosscheckStore = (() => {
  const DB_NAME = "crosscheck";
  const STORE_NAME = "pack";
  const RECORD_KEY = "pack";
  const REQUIRED_COMMUNITY_COUNT = 96;

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
        request = indexedDB.open(DB_NAME, 1);
      } catch (error) {
        reject(error);
        return;
      }
      request.addEventListener("upgradeneeded", () => {
        request.result.createObjectStore(STORE_NAME);
      });
      request.addEventListener("success", () => resolve(request.result));
      request.addEventListener("error", () => reject(request.error));
      request.addEventListener("blocked", () => reject(new Error("IndexedDB blocked")));
    });

  // Runs one transaction; fn receives the object store and may return an IDBRequest, whose
  // result becomes this promise's resolved value once the transaction completes.
  const runTx = (mode, fn) =>
    openDb().then(
      (db) =>
        new Promise((resolve, reject) => {
          const tx = db.transaction(STORE_NAME, mode);
          const store = tx.objectStore(STORE_NAME);
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

  // Rejects a pack whose pack_version differs from the built-in one or whose community count
  // is not 96; never stores anything else. Never throws: a refusal (bad shape, bad IndexedDB)
  // resolves with {built: null} rather than an error on screen.
  const save = async (packJson) => {
    let candidate;
    try {
      candidate = JSON.parse(packJson);
    } catch (error) {
      return { built: null };
    }
    const communityCount = Array.isArray(candidate.communities) ? candidate.communities.length : -1;
    if (
      candidate.pack_version !== builtInPack().pack_version ||
      communityCount !== REQUIRED_COMMUNITY_COUNT
    ) {
      return { built: null };
    }
    try {
      await runTx("readwrite", (store) => store.put({ json: packJson, built: candidate.built }, RECORD_KEY));
    } catch (error) {
      warnOnce(error);
      return { built: null };
    }
    return { built: candidate.built };
  };

  const load = async () => {
    let record;
    try {
      record = await runTx("readonly", (store) => store.get(RECORD_KEY));
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
      await runTx("readwrite", (store) => store.delete(RECORD_KEY));
    } catch (error) {
      warnOnce(error);
    }
  };

  return { save, load, clear };
})();
