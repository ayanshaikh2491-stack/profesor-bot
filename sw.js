// Professor App — Service Worker for offline + install
const CACHE = 'professor-v1';
const FILES = ['/','/index.html','/manifest.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)));
  self.skipWaiting();
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request).catch(() => new Response('Offline',{status:503})))
  );
});
