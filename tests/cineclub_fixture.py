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
  var data = window.__fixture, listeners = {}, serial = 0;
  window.__fixtureWrites = [];
  function copy(x){ return JSON.parse(JSON.stringify(x)); }
  function doc(name, id){ return { id:id, exists:!!(data[name] || {})[id], data:function(){ return copy((data[name] || {})[id] || {}); } }; }
  function snapshot(name){ return { docs:Object.keys(data[name] || {}).map(function(id){ return doc(name,id); }), docChanges:function(){ return this.docs.map(function(d){ return {type:'added',doc:d}; }); } }; }
  function emit(name){ (listeners[name] || []).forEach(function(cb){ queueMicrotask(function(){ cb(snapshot(name)); }); }); }
  function collection(name){
    data[name] = data[name] || {};
    return {
      limit:function(){ return this; }, where:function(){ return this; },
      onSnapshot:function(cb){ (listeners[name] = listeners[name] || []).push(cb); queueMicrotask(function(){ cb(snapshot(name)); }); return function(){}; },
      doc:function(id){
        id = id || ('test-document-' + ++serial);
        var api = { id:id, get:function(){ return Promise.resolve(doc(name,id)); },
          set:function(value){ window.__fixtureWrites.push({collection:name,id:id,value:copy(value)}); data[name][id]=copy(value); emit(name); return Promise.resolve(); },
          update:function(field,value){
            window.__fixtureWrites.push({collection:name,id:id,field:field,value:value});
            var target=data[name][id] = data[name][id] || {};
            if(field && field.parts){ var a=field.parts; for(var i=0;i<a.length-1;i++) target=target[a[i]] = target[a[i]] || {}; if(value && value.deleted) delete target[a[a.length-1]]; else target[a[a.length-1]]=copy(value); }
            else Object.assign(target,copy(field)); emit(name); return Promise.resolve();
          },
          delete:function(){ window.__fixtureWrites.push({collection:name,id:id,deleted:true}); delete data[name][id]; emit(name); return Promise.resolve(); }
        }; return api;
      }
    };
  }
  var fs = { collection:collection, enablePersistence:function(){ return Promise.resolve(); } };
  var auth = { isSignInWithEmailLink:function(){ return false; }, onAuthStateChanged:function(cb){ queueMicrotask(function(){ cb({uid:'test-membre',email:'test@example.invalid',emailVerified:false}); }); return function(){}; } };
  function firestore(){ return fs; }
  firestore.FieldPath = function(){ this.parts=Array.prototype.slice.call(arguments); };
  firestore.FieldValue = {delete:function(){ return {deleted:true}; }, arrayUnion:function(){ return Array.prototype.slice.call(arguments); }};
  window.firebase = {initializeApp:function(){},auth:function(){return auth;},firestore:firestore};
})();
"""


def install_routes(context, fixture=None, complements=None):
    """Remplacer tous les accès réseau avant de charger la page."""
    fixture = fixture or catalogue_fixture()
    context.add_init_script("window.__fixture = " + json.dumps(fixture) + ";")
    context.add_init_script("localStorage.setItem('ccUid','test-membre');localStorage.setItem('carnetIntroV1','1');")
    unexpected = []

    def route(request_route):
        url = request_route.request.url
        if url.startswith("https://cineclub.test/"):
            if url.endswith("complements.json"):
                body = json.dumps(complements) if complements is not None else (ROOT / "carnet-de-films/complements.json").read_text()
                request_route.fulfill(content_type="application/json", body=body)
            else:
                request_route.fulfill(content_type="text/html", path=ROOT / "carnet-de-films/index.html")
        elif "firebase-app-compat.js" in url:
            request_route.fulfill(content_type="application/javascript", body=FIREBASE_JS)
        elif "firebase-" in url and ".js" in url:
            request_route.fulfill(content_type="application/javascript", body="")
        elif "fonts.googleapis.com" in url:
            request_route.fulfill(content_type="text/css", body="")
        else:
            unexpected.append(url)
            request_route.abort()

    context.route("**/*", route)
    return unexpected
