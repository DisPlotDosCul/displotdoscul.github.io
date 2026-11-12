// Cap Logement, appli installable : toujours la version en ligne d'abord ; la copie gardée sert seulement hors connexion.
var CACHE = "caplogement-v2";
var CORE = ["./", "calculateur.html", "annonces.html", "licia.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/icon-180.png", "icons/icon-32.png"];
self.addEventListener("install", function(e){
  e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(CORE); }).catch(function(){}).then(function(){ return self.skipWaiting(); }));
});
self.addEventListener("activate", function(e){
  e.waitUntil(caches.keys().then(function(keys){ return Promise.all(keys.filter(function(k){ return k !== CACHE; }).map(function(k){ return caches.delete(k); })); }).then(function(){ return self.clients.claim(); }));
});
self.addEventListener("fetch", function(e){
  var r = e.request, u = new URL(r.url);
  if (r.method !== "GET" || u.origin !== self.location.origin || u.pathname.indexOf("/logement/") !== 0) return;
  e.respondWith(fetch(r.url, { cache: "no-cache", credentials: "same-origin" }).then(function(res){
    if (res && res.ok) { var copy = res.clone(); caches.open(CACHE).then(function(c){ c.put(r, copy); }); }
    return res;
  }).catch(function(){ return caches.match(r, { ignoreSearch: true }).then(function(m){ return m || caches.match("./"); }); }));
});
