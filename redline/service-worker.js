const CACHE_VERSION = "redline-shell-v1";
const RUNTIME_CACHE = "redline-runtime-v1";

const SHELL_FILES = [
  "./",
  "./index.html",
  "./redline.js",
  "./manifest.json",
  "../academy/assets/icons/favicon-32.png",
  "../academy/assets/icons/icon-192.png",
  "../academy/assets/icons/icon-512.png",
  "../academy/assets/icons/apple-touch-icon.png"
];

// Nur die Shell selbst (Icon-Font vom CDN) wird zwischengespeichert; Module bleiben Netzwerk-first.
const RUNTIME_ORIGINS = ["https://cdnjs.cloudflare.com"];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(cache => Promise.all(SHELL_FILES.map(path =>
        fetch(path).then(r => r.ok ? cache.put(path, r) : null).catch(() => null)
      )))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys
        .filter(key => key.startsWith("redline-") && key !== CACHE_VERSION && key !== RUNTIME_CACHE)
        .map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const sameOrigin = url.origin === self.location.origin;
  const shellPath = sameOrigin && (req.mode === "navigate" || SHELL_FILES.some(f => new URL(f, self.location).href === url.href));
  if (shellPath) {
    // Netzwerk zuerst, Cache als Offline-Fallback
    event.respondWith(
      fetch(req).then(res => {
        if (res.ok) { const copy = res.clone(); caches.open(CACHE_VERSION).then(c => c.put(req, copy)); }
        return res;
      }).catch(() => caches.match(req).then(hit => hit || caches.match("./index.html")))
    );
    return;
  }
  if (RUNTIME_ORIGINS.includes(url.origin)) {
    event.respondWith(
      caches.match(req).then(hit => hit || fetch(req).then(res => {
        if (res.ok || res.type === "opaque") { const copy = res.clone(); caches.open(RUNTIME_CACHE).then(c => c.put(req, copy)); }
        return res;
      }))
    );
  }
});
