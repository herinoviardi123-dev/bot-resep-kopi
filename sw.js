/* ══════════════════════════════════════════════
   HEY KOPI — Service Worker v1.0
   Netlify: https://boisterous-cucurucho-2a78f0.netlify.app
══════════════════════════════════════════════ */

const CACHE_NAME = 'heykopi-v32';
const STATIC_CACHE = 'heykopi-static-v29';
const FONT_CACHE = 'heykopi-fonts-v29';

// Core files to cache immediately
const CORE_FILES = [
  '/',
  '/index.html',
  '/offline.html',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
];

// Google Fonts to cache
const FONT_URLS = [
  'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,400&family=Outfit:wght@200;300;400;500;600;700&display=swap',
];

// ── INSTALL ───────────────────────────────────
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Hey Kopi Service Worker...');
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE).then((cache) => {
        console.log('[SW] Caching core files');
        return cache.addAll(CORE_FILES).catch(err => {
          console.warn('[SW] Some core files failed to cache:', err);
        });
      }),
      caches.open(FONT_CACHE).then((cache) => {
        return cache.addAll(FONT_URLS).catch(err => {
          console.warn('[SW] Font cache failed:', err);
        });
      }),
    ]).then(() => {
      console.log('[SW] Install complete');
      return self.skipWaiting();
    })
  );
});

// ── ACTIVATE ──────────────────────────────────
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter(name => name !== STATIC_CACHE && name !== FONT_CACHE && name !== CACHE_NAME)
          .map(name => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => {
      console.log('[SW] Activated, claiming clients');
      return self.clients.claim();
    })
  );
});

// ── FETCH STRATEGY ────────────────────────────
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') return;

  // Skip chrome-extension and non-http
  if (!request.url.startsWith('http')) return;

  // Skip Telegram WebApp SDK calls
  if (url.hostname === 'telegram.org') return;

  // Skip OneSignal
  if (url.hostname.includes('onesignal')) return;

  // Skip analytics/external APIs
  if (url.hostname.includes('google-analytics') || url.hostname.includes('googleapis.com')) return;

  // FONTS: Cache-first
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    event.respondWith(cacheFirst(request, FONT_CACHE));
    return;
  }

  // HTML pages: Network-first (get latest), fallback to cache
  if (request.headers.get('accept')?.includes('text/html') || url.pathname === '/' || url.pathname.endsWith('.html')) {
    event.respondWith(networkFirstHtml(request));
    return;
  }

  // Static assets: Cache-first
  event.respondWith(cacheFirst(request, STATIC_CACHE));
});

// ── STRATEGIES ────────────────────────────────
async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    return new Response('Offline — Hey Kopi', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

async function networkFirstHtml(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    // Try cached version first
    const cached = await caches.match(request)
      || await caches.match('/index.html')
      || await caches.match('/');
    if (cached) return cached;
    // Fallback to offline page
    const offline = await caches.match('/offline.html');
    if (offline) return offline;
    // Last resort inline offline response
    return new Response(`<!DOCTYPE html><html lang="id"><head><meta charset="UTF-8"><title>Hey Kopi — Offline</title>
      <meta name="viewport" content="width=device-width,initial-scale=1"><style>
      body{font-family:sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#f0ebe3;color:#4a3728;text-align:center;padding:20px}
      h1{color:#c49a6c;font-size:22px}button{margin-top:20px;padding:12px 28px;background:#c49a6c;color:#fff;border:none;border-radius:24px;font-size:14px;cursor:pointer}
      </style></head><body><div style="font-size:56px;margin-bottom:16px">☕</div>
      <h1>Hey Kopi</h1><p style="color:#9a8472;font-size:14px">Sedang offline. Sambungkan internet.</p>
      <button onclick="location.reload()">Coba Lagi</button></body></html>`,
      { status: 200, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
    );
  }
}

// ── PUSH NOTIFICATIONS (OneSignal backup) ─────
self.addEventListener('push', (event) => {
  const data = event.data?.json() || {};
  const title = data.title || 'Hey Kopi';
  const options = {
    body: data.body || 'Ada notifikasi baru dari Hey Kopi!',
    icon: '/icons/icon-192.png',
    badge: '/icons/icon-96.png',
    vibrate: [200, 100, 200],
    tag: 'heykopi-notif',
    data: { url: data.url || '/' },
    actions: [
      { action: 'open', title: 'Buka Aplikasi' },
      { action: 'dismiss', title: 'Tutup' }
    ]
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  if (event.action === 'dismiss') return;
  const url = event.notification.data?.url || '/';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url === url && 'focus' in client) return client.focus();
      }
      if (clients.openWindow) return clients.openWindow(url);
    })
  );
});

// ── BACKGROUND SYNC ───────────────────────────
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-logs') {
    console.log('[SW] Background sync: logs');
  }
});

console.log('[SW] Hey Kopi Service Worker loaded ☕');
