"""Catalogue public et membres entièrement fictifs, sans accès à Firebase."""
import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def slug(text):
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def catalogue_fixture():
    with (ROOT / "donnees/catalogue-films.csv").open() as stream:
        rows = list(csv.DictReader(stream, delimiter=";"))
    envs, mouvements, fiches, entries = {}, {}, {}, []
    for row in rows:
        fid = row["identifiant"]
        keywords = row["mots-clés"].split(", ")
        for key in keywords:
            envs[key] = {"id": key, "label": key, "sous": []}
        movement = slug(row["mouvement"])
        mouvements[movement] = {"id": movement, "label": row["mouvement"]}
        fiches[fid] = {"c": row["pays"], "k": keywords, "mv": movement,
                       "p": row["résumé"], "e": 7.3, "m": 0, "w": ""}
        entries.append({"id": fid, "t": row["titre"], "y": int(row["année"]),
                        "d": row["cinéaste"], "r": ""})
    # La fiche distante doit passer avant le complément, y compris les champs vides.
    fiches["1917-2019"].update(duree=121, av=[], th=[], fiab="")
    families = [{"id": fid, "label": label, "fond": "#FCE3CF", "bord": "#E79E6B",
                 "encre": "#602D00"} for fid, label in [
                    ("carnet", "Mon carnet"), ("themes", "Thèmes"),
                    ("playlists", "Playlists"), ("epoques", "Époques")]]
    docs = {}
    items = list(fiches.items())
    for number in range(6):
        docs[f"fiches-{number + 1}"] = {"fiches": dict(items[number::6])}
    docs["fiches-1"].update(familles=families, envies=list(envs.values()), mouvements=[
        {"id": "courants-test", "label": "Courants", "sous": list(mouvements.values())}])
    docs["s01-test"] = {"titre": "Le catalogue", "famille": "themes", "ordre": 1,
                        "films": entries}
    docs["s16-classement"] = {"titre": "Mes films notés", "famille": "carnet",
                              "auto": "classement", "ordre": 2, "films": []}
    docs["s18-mes-statistiques"] = {"titre": "Mes statistiques", "famille": "carnet",
                                   "auto": "stats", "ordre": 3, "films": []}
    docs["s00-pour-toi"] = {"titre": "Suggestions", "famille": "carnet", "films": []}
    for sid, label, fid in [("s22-nouveau-mer", "Mer", "abyss-1989"),
                             ("s28-un-seul-plan", "Filmés sans coupure", "birdman-2014")]:
        docs[sid] = {"titre": label, "famille": "themes", "ordre": 4,
                      "films": [entry for entry in entries if entry["id"] == fid]}
    seeds = ["shining-1980", "titanic-1997", "pulp-fiction-1994", "matrix-1999",
             "la-la-land-2016", "mulholland-drive-2001", "le-parrain-1972",
             "parasite-2019", "la-jetee-1962", "barbie-2023", "the-artist-2011",
             "la-planete-sauvage-1973", "playtime-1967", "the-father-2020"]
    rep = {fid: {"etat": "vu", "note10": [9.3, 8, 9, 7.5][i % 4]}
           for i, fid in enumerate(seeds)}
    rep["a-history-of-violence-2005"] = {"etat": "pas_vu", "note10": 0}
    profils = {
        "test-membre": {"pseudo": "Alix (test)", "pid": "m_test-membre", "rep": rep,
                         "liste": {}, "quiz": {"v": 1, "esthetique": 1, "sombre": 1}},
        "test-autre": {"pseudo": "Camille (test)", "pid": "m_test-autre", "liste": {},
                       "rep": {fid: {"etat": "vu", "note10": 8.7} for fid in seeds[::2]}}
    }
    return {"films": docs, "profils": profils}


FIREBASE_JS = r"""
(function(){
  // Faux Firestore : collections, requêtes « where » (== et array-contains), écritures fusionnées, lots,
  // et règles simulées : les collections de window.__fixtureDeny refusent lectures et écritures
  // (par défaut, les nouvelles collections du 12 novembre, comme tant que les règles ne sont pas publiées).
  var data = window.__fixture, listeners = {}, serial = 0;
  var deny = window.__fixtureDeny || ['carnets', 'ajouts', 'commentairesPrives'];
  window.__fixtureWrites = [];
  function copy(x){ return x === undefined ? undefined : JSON.parse(JSON.stringify(x)); }
  function refused(){ return Promise.reject({ code:'permission-denied', message:'Missing or insufficient permissions.' }); }
  function sentinel(v){ return v && typeof v === 'object' && (v.deleted || v.__union || v.__remove); }
  // Appliquer une valeur, avec les marqueurs delete / arrayUnion / arrayRemove.
  function apply(target, key, v){
    if (v && v.deleted) { delete target[key]; return; }
    if (v && v.__union) { var a = Array.isArray(target[key]) ? target[key].slice() : []; v.__union.forEach(function(x){ if (a.indexOf(x) < 0) a.push(x); }); target[key] = a; return; }
    if (v && v.__remove) { target[key] = (Array.isArray(target[key]) ? target[key] : []).filter(function(x){ return v.__remove.indexOf(x) < 0; }); return; }
    target[key] = copy(v);
  }
  function merge(target, src){
    Object.keys(src).forEach(function(k){
      var v = src[k];
      if (v && typeof v === 'object' && !Array.isArray(v) && !sentinel(v)) { if (!target[k] || typeof target[k] !== 'object' || Array.isArray(target[k])) target[k] = {}; merge(target[k], v); }
      else apply(target, k, v);
    });
  }
  function clean(v){ // set() sans fusion : les marqueurs delete disparaissent
    if (!v || typeof v !== 'object' || Array.isArray(v)) return v;
    var o = {}; Object.keys(v).forEach(function(k){ var x = v[k]; if (x && x.deleted) return; if (x && x.__union) { o[k] = x.__union.slice(); return; } if (x && x.__remove) { o[k] = []; return; } o[k] = clean(x); }); return o;
  }
  function doc(name, id){ return { id:id, exists:!!(data[name] || {})[id], data:function(){ return copy((data[name] || {})[id] || {}); } }; }
  function match(x, f){
    var v = x[f[0]];
    if (f[1] === '==') return JSON.stringify(v) === JSON.stringify(f[2]);
    if (f[1] === 'array-contains') return Array.isArray(v) && v.indexOf(f[2]) >= 0;
    return true;
  }
  function snapshot(name, filters){
    var ids = Object.keys(data[name] || {}).filter(function(id){ return (filters || []).every(function(f){ return match(data[name][id], f); }); });
    return { docs:ids.map(function(id){ return doc(name,id); }), docChanges:function(){ return this.docs.map(function(d){ return {type:'added',doc:d}; }); } };
  }
  function emit(name){ (listeners[name] || []).forEach(function(l){ queueMicrotask(function(){ l.cb(snapshot(name, l.f)); }); }); }
  function write(name, id, fn, log){
    if (deny.indexOf(name) >= 0) return refused();
    window.__fixtureWrites.push(Object.assign({ collection:name, id:id }, log));
    data[name] = data[name] || {}; fn(); emit(name); return Promise.resolve();
  }
  function ref(name, id){
    id = id || ('test-document-' + ++serial);
    return { id:id, _n:name,
      get:function(){ return deny.indexOf(name) >= 0 ? refused() : Promise.resolve(doc(name,id)); },
      set:function(value, opt){ return write(name, id, function(){ if (opt && opt.merge) { data[name][id] = data[name][id] || {}; merge(data[name][id], value); } else data[name][id] = clean(copy(value)); }, { value:copy(value), merge:!!(opt && opt.merge) }); },
      update:function(field, value){
        // Comme Firestore : un objet, ou des paires « chemin, valeur » (plusieurs champs d'un coup). Refusé si le document n'existe pas.
        var args = arguments;
        if (deny.indexOf(name) < 0 && !(data[name] || {})[id]) return Promise.reject({ code:'not-found', message:'No document to update' });
        if (!(field && field.parts)) return write(name, id, function(){ var root = data[name][id]; Object.keys(field).forEach(function(k){ var p = k.split('.'), t = root; for (var i = 0; i < p.length - 1; i++) t = t[p[i]] = t[p[i]] || {}; apply(t, p[p.length - 1], field[k]); }); }, { field:field, value:value });
        return write(name, id, function(){
          var root = data[name][id];
          for (var k = 0; k < args.length; k += 2) {
            var f = args[k], v = args[k + 1], target = root, a = f.parts;
            for (var i = 0; i < a.length - 1; i++) target = target[a[i]] = target[a[i]] || {};
            apply(target, a[a.length - 1], v);
          }
        }, { field:field, value:value });
      },
      delete:function(){ return write(name, id, function(){ delete data[name][id]; }, { deleted:true }); }
    };
  }
  function query(name, filters){
    return {
      limit:function(){ return this; },
      where:function(a, op, b){ return query(name, filters.concat([[a, op, b]])); },
      onSnapshot:function(cb, err){
        if (deny.indexOf(name) >= 0) { queueMicrotask(function(){ if (err) err({ code:'permission-denied' }); }); return function(){}; }
        (listeners[name] = listeners[name] || []).push({ cb:cb, f:filters }); queueMicrotask(function(){ cb(snapshot(name, filters)); }); return function(){};
      },
      doc:function(id){ return ref(name, id); },
      add:function(v){ var r = ref(name); return r.set(v).then(function(){ return r; }); }
    };
  }
  function collection(name){ data[name] = data[name] || {}; return query(name, []); }
  function batch(){
    var ops = [];
    return { set:function(r, v, o){ ops.push(function(){ return r.set(v, o); }); }, update:function(r, v){ ops.push(function(){ return r.update(v); }); }, delete:function(r){ ops.push(function(){ return r.delete(); }); },
      commit:function(){ return ops.reduce(function(p, f){ return p.then(f); }, Promise.resolve()); } };
  }
  // Pour les tests : écrire comme le ferait un autre membre, sans passer par les règles (null efface).
  window.__fixturePut = function(name, id, v){ data[name] = data[name] || {}; if (v === null) delete data[name][id]; else data[name][id] = copy(v); emit(name); };
  var fs = { collection:collection, batch:batch, enablePersistence:function(){ return Promise.resolve(); } };
  var who = window.__fixtureUid || 'test-membre';
  var auth = { isSignInWithEmailLink:function(){ return false; }, onAuthStateChanged:function(cb){ queueMicrotask(function(){ cb({uid:who,email:'test@example.invalid',emailVerified:false}); }); return function(){}; } };
  function firestore(){ return fs; }
  firestore.FieldPath = function(){ this.parts=Array.prototype.slice.call(arguments); };
  firestore.FieldValue = {delete:function(){ return {deleted:true}; }, arrayUnion:function(){ return {__union:Array.prototype.slice.call(arguments)}; }, arrayRemove:function(){ return {__remove:Array.prototype.slice.call(arguments)}; }};
  window.firebase = {initializeApp:function(){},auth:function(){return auth;},firestore:firestore};
})();
"""


def open_more(page):
    """Express, Boussole, Dérive et Ciel sont rangés derrière « Autres façons de choisir » (12 novembre)."""
    page.wait_for_selector("#ccMoreB")
    if page.locator("#ccMore").is_hidden():
        page.locator("#ccMoreB").click()


def install_routes(context, fixture=None, complements=None):
    """Remplacer tous les accès réseau avant de charger la page."""
    fixture = fixture or catalogue_fixture()
    context.add_init_script("window.__fixture = " + json.dumps(fixture) + ";")
    context.add_init_script("localStorage.setItem('ccUid','test-membre');localStorage.setItem('carnetIntroV1','1');localStorage.setItem('ccGuideV1-test-membre','1');")
    unexpected = []

    def route(request_route):
        url = request_route.request.url
        if url.startswith("https://cineclub.test/"):
            local = ROOT / url.split("?")[0].replace("https://cineclub.test/", "")
            if "/i18n/" in url and local.suffix == ".json" and local.is_file():
                # Traductions de l'interface (choix de la langue).
                request_route.fulfill(content_type="application/json", path=local)
            elif local.suffix in (".js", ".webmanifest", ".png") and local.is_file():
                # Appli installable : service worker, manifeste et icônes.
                types = {".js": "application/javascript", ".webmanifest": "application/manifest+json", ".png": "image/png"}
                request_route.fulfill(content_type=types[local.suffix], path=local)
            elif url.endswith("complements.json"):
                body = json.dumps(complements) if complements is not None else (ROOT / "carnet-de-films/complements.json").read_text()
                request_route.fulfill(content_type="application/json", body=body)
            else:
                request_route.fulfill(content_type="text/html", path=ROOT / "carnet-de-films/index.html")
        elif "firebase-app-compat.js" in url:
            request_route.fulfill(content_type="application/javascript", body=FIREBASE_JS)
        elif "firebase-" in url and ".js" in url:
            request_route.fulfill(content_type="application/javascript", body="")
        elif "api.themoviedb.org" in url:
            # Images et affiches : TMDB fictif, sans résultat.
            request_route.fulfill(content_type="application/json", body='{"results":[]}')
        elif "fonts.googleapis.com" in url:
            request_route.fulfill(content_type="text/css", body="")
        else:
            unexpected.append(url)
            request_route.abort()

    context.route("**/*", route)
    return unexpected
