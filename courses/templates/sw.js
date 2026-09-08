// ====================
// Service Worker - Cache ۋە Offline
// ====================

const CACHE_NAME = 'edraak-cache-v2';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/main.js',
    '/manifest.json',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png'
];

// Install - Cache قۇرۇش
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('📦 Cache ئېچىلدى');
                return cache.addAll(urlsToCache).catch(err => {
                    console.log('⚠️ بەزى ھۆججەتلەر cache قىلىنمىدى:', err);
                });
            })
    );
    self.skipWaiting();
});

// Activate - كونا cache نى تازىلاش
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('🗑️ كونا cache ئۆچۈرۈلدى:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch - Network first, cache fallback
self.addEventListener('fetch', event => {
    // پەقەت GET تەلەپلىرىگە
    if (event.request.method !== 'GET') {
        return;
    }

    // POST تەلەپلىرىنى cache قىلمايدۇ (form submit)
    if (event.request.url.includes('/admin/') ||
        event.request.url.includes('/login/') ||
        event.request.url.includes('/logout/')) {
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then(response => {
                if (response.status === 200 && response.type === 'basic') {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            })
            .catch(() => {
                return caches.match(event.request)
                    .then(response => {
                        if (response) {
                            return response;
                        }
                        if (event.request.mode === 'navigate') {
                            return caches.match('/');
                        }
                    });
            })
    );
});