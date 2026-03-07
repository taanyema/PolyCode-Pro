const CACHE_NAME = 'polycode-v1';
const assets = ['/', '/static/style.css', '/static/script.js', '/static/logo_polycode.png'];

self.addEventListener('install', evt => {
    evt.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            cache.addAll(assets);
        })
    );
});

self.addEventListener('fetch', evt => {
    evt.respondWith(
        caches.match(evt.request).then(res => {
            return res || fetch(evt.request);
        })
    );
});