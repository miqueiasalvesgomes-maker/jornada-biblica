// Service Worker para PWA - Jornada Bíblica 365 (v3.1)
// Network-First para documentos, scripts e estilos garantindo atualização instantânea no Render
const CACHE_NAME = 'jb365-cache-v3.1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/style.css?v=3.1',
  '/app.js?v=3.1',
  '/manifest.json'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch(err => {
        console.warn('Falha parcial no pre-cache inicial:', err);
      });
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => {
          console.log('[SW] Removendo cache antigo:', key);
          return caches.delete(key);
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const requestUrl = new URL(event.request.url);

  // 1. Chamadas de API SEMPRE vão para a rede (nunca cachear para não dessincronizar multi-usuário)
  if (requestUrl.pathname.startsWith('/api/')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // 2. Capas de livros (imagens estáticas): Stale-While-Revalidate para performance rápida
  if (requestUrl.pathname.includes('/covers/') || requestUrl.pathname.includes('/img/')) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        const fetchPromise = fetch(event.request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const clone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return networkResponse;
        }).catch(() => cachedResponse);
        return cachedResponse || fetchPromise;
      })
    );
    return;
  }

  // 3. Documentos (HTML), scripts (JS) e estilos (CSS): NETWORK-FIRST
  // Garante que qualquer atualização enviada ao Render apareça imediatamente
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && event.request.method === 'GET') {
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return networkResponse;
      })
      .catch(() => {
        // Se offline ou sem conexão, recorre ao cache local
        return caches.match(event.request).then((cached) => {
          if (cached) return cached;
          if (event.request.mode === 'navigate') {
            return caches.match('/index.html') || caches.match('/');
          }
          return new Response('Sem conexão', { status: 503, statusText: 'Offline' });
        });
      })
  );
});

// Listener para forçar limpeza quando solicitado pela interface
self.addEventListener('message', (event) => {
  if (event.data && event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }
  if (event.data && event.data.action === 'clearCache') {
    caches.keys().then((keys) => {
      keys.forEach((key) => caches.delete(key));
    });
  }
});
