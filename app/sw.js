"use strict";

// Host-only (GitHub Pages): caches the page on install. dist/index.html never depends on this
// file; app.js registers it only over https. The cache name carries this build's own hash
// (scripts/build_app.py replaces __BUILD__), so a new build never serves a stale page from an
// old cache (Task-26: a phone that opened Pages once kept showing the first build forever).
const CACHE = "crosscheck-__BUILD__";
const FILES = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png",
  "./apple-touch-icon.png",
];

self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(FILES)));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key))))
      .then(() => self.clients.claim()),
  );
});

// The page itself, navigated to directly or opened as the app shell.
const isPageRequest = (request) =>
  request.mode === "navigate" || request.url.endsWith("/") || request.url.endsWith("/index.html");

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") {
    return;
  }
  if (isPageRequest(event.request)) {
    // Network first: today's build if the network answers, the last cached one otherwise.
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE).then((cache) => cache.put(event.request, copy));
          return response;
        })
        .catch(() => caches.match(event.request, { ignoreSearch: true })),
    );
    return;
  }
  event.respondWith(
    caches.match(event.request, { ignoreSearch: true }).then((hit) => hit || fetch(event.request)),
  );
});
