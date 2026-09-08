// ====================
// Service Worker - Cache ۋە Offline
// ====================

const CACHE_NAME = 'edraak-cache-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/manifest.json',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    'https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap'
];

// ====================
// 1. Install - Cache قۇرۇش
// ====================
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('📦 Cache ئېچىلدى');
                return cache.addAll(urlsToCache);
            })
            .catch(err => {
                console.error('❌ Cache خاتالىقى:', err);
            })
    );
    self.skipWaiting();
});

// ====================
// 2. Activate - كونا cache نى تازىلاش
// ====================
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

// ====================
// 3. Fetch - Cache دىن بېرىش (Network first, cache fallback)
// ====================
self.addEventListener('fetch', event => {
    // پەقەت GET تەلەپلىرىگە cache
    if (event.request.method !== 'GET') {
        return;
    }

    // API تەلەپلىرىنى cache قىلمايدۇ
    if (event.request.url.includes('/api/')) {
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then(response => {
                // Cache غا يېڭىلاش
                if (response.status === 200) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            })
            .catch(() => {
                // ئىنتېرنېت يوق بولسا، cache دىن ئېلىش
                return caches.match(event.request)
                    .then(response => {
                        if (response) {
                            console.log('📦 Cache دىن ئېلىندى:', event.request.url);
                            return response;
                        }
                        // Offline بەت
                        if (event.request.mode === 'navigate') {
                            return caches.match('/');
                        }
                    });
            })
    );
});