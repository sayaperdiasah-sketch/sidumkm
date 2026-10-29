/* SIDUMKM - offline sederhana: halaman inti + aset statis di-cache */
const CACHE = "sidumkm-v1";
const INTI = ["/dashboard", "/keuangan", "/static/css/app.css", "/static/css/stempel.css",
              "/static/js/buku.js", "/static/js/catat.js", "/static/js/rupiah.js",
              "/static/manifest.webmanifest", "/static/img/icon.svg"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(INTI)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((k) =>
    Promise.all(k.filter((n) => n !== CACHE).map((n) => caches.delete(n)))
  ).then(() => self.clients.claim()));
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || !req.url.startsWith(self.location.origin)) return;
  const html = req.mode === "navigate";
  e.respondWith(
    fetch(req)
      .then((res) => {
        const salin = res.clone();
        caches.open(CACHE).then((c) => c.put(req, salin));
        return res;
      })
      .catch(() => caches.match(req).then((ada) =>
        ada || (html ? caches.match("/dashboard") : Response.error())))
  );
});
