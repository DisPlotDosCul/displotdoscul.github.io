// Ciné-club, appli installable : la page et ses fichiers restent disponibles sans réseau.
// Toujours la version en ligne d'abord (les mises à jour arrivent tout de suite) ; la copie gardée sert seulement hors connexion.
// Les données (Firebase) et les images de films ne passent pas par ici.
var CACHE = "cineclub-v2";
var CORE = ["./", "complements.json", "manifest.webmanifest", "icones/icone-192.png", "icones/icone-512.png", "icones/apple-touch-icon.png", "icones/favicon-48.png"];
self.addEventListener("install", function(e){
  e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(CORE); }).catch(function(){}).then(function(){ return self.skipWaiting(); }));
});
self.addEventListener("activate", function(e){
  e.waitUntil(caches.keys().then(function(keys){ return Promise.all(keys.filter(function(k){ return k !== CACHE; }).map(function(k){ return caches.delete(k); })); }).then(function(){ return self.clients.claim(); }));
});
self.addEventListener("fetch", function(e){
  var r = e.request, u = new URL(r.url);
  if (r.method !== "GET" || u.origin !== self.location.origin || u.pathname.indexOf("/carnet-de-films/") !== 0) return;
  var page = r.mode === "navigate";
  var key = page ? new Request("./") : r;
  // « no-cache » : le navigateur redemande toujours au serveur si le fichier a changé (sinon GitHub le garde 10 minutes).
  var get = page || /\.(json|webmanifest|js)$/.test(u.pathname) ? fetch(r.url, { cache:"no-cache", credentials:"same-origin" }) : fetch(r);
  e.respondWith(get.then(function(res){
    if (res && res.ok && !u.searchParams.has("apiKey")) { var copy = res.clone(); caches.open(CACHE).then(function(c){ c.put(key, copy); }); }
    return res;
  }).catch(function(){
    return caches.match(key, { ignoreSearch:true }).then(function(m){ return m || (page ? caches.match("./") : Response.error()); });
  }));
});
