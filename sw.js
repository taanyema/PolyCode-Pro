const CACHE_NAME = 'polycode-v1';
// On ajoute /static/ devant le logo pour que le navigateur le trouve vraiment
const assets = [
  '/', 
  '/index.html', 
  '/static/style.css', 
  '/static/script.js', 
  '/static/logo_polycode.png'
];

self.addEventListener('install', evt => {
    evt.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            // Cette ligne va maintenant fonctionner car tous les fichiers existent
            return cache.addAll(assets);
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