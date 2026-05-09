const CACHE_NAME = 'goldtracker-v3';
const ASSETS = [
    '/dashboard/',
    '/static/css/main.css',
    '/static/js/dashboard.js',
    '/static/manifest.json'
];

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
    );
});

self.addEventListener('fetch', (e) => {
    e.respondWith(
        fetch(e.request).catch(() => caches.match(e.request))
    );
});
