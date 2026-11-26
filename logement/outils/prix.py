#!/usr/bin/env python3
"""Indice de prix des magasins d'Île-de-France, à partir d'Open Prices (Open Food Facts, licence ODbL).

Méthode : pour chaque produit (code-barres) relevé dans au moins 2 enseignes d'Île-de-France sur les 18 derniers mois,
on compare le prix de chaque magasin au prix médian du produit (prix hors promotion, relevé le plus récent par magasin).
Indice d'un magasin ou d'une enseigne = moyenne géométrique de ces écarts.
Échelle : 100 = moyenne des grandes enseignes classiques (Carrefour, Carrefour Market, Intermarché, Super U, Auchan).
Un magasin n'a son propre indice qu'avec au moins MIN_MAG produits comparables ; il est alors rapproché de son enseigne
quand il a peu de produits (moyenne pondérée, poids K de l'enseigne).
Écrit logement/prix.json.
"""
import json, math, sys, time, urllib.request, urllib.parse, datetime, os, re
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

API = "https://prices.openfoodfacts.org/api/v1"
BOX = (48.1, 49.25, 1.45, 3.56)  # Île-de-France (lat min, lat max, lon min, lon max)
MOIS = 18
MIN_ENS, MIN_MAG, K = 100, 20, 40
# Enseignes sans code-barres comparables (marques propres) : repère national Radin Malin, 18 nov. 2026 (écart à Lidl), recalé sur E.Leclerc
REPERES = {"Lidl": 0.0, "Aldi": 0.6}
RM_LECLERC = 2.8
REF = ["Carrefour", "Carrefour Market", "Intermarché", "Système U", "Auchan"]
UA = {"User-Agent": "CapLogement/1.0 (displotdoscul.github.io)"}

# Nom d'enseigne → nom utilisé par le calculateur (mêmes noms que BRANDS dans calculateur.html)
ENS = [(r"lidl", "Lidl"), (r"aldi", "Aldi"), (r"netto", "Netto"), (r"leader ?price", "Leader Price"), (r"grand ?frais", "Grand Frais"),
       (r"leclerc", "E.Leclerc"), (r"carrefour ?(city|express|contact)", "Carrefour City"), (r"carrefour ?market", "Carrefour Market"),
       (r"carrefour", "Carrefour"), (r"intermarch[ée] ?express", "Intermarché Express"), (r"intermarch", "Intermarché"),
       (r"super ?u|hyper ?u|u express|\bu\b", "Système U"), (r"auchan", "Auchan"), (r"casino|spar|vival", "Casino"),
       (r"monop", "Monoprix"), (r"franprix", "Franprix"), (r"g ?20", "G20"), (r"coccinelle|coccimarket", "Coccinelle"),
       (r"picard", "Picard"), (r"naturalia", "Naturalia"), (r"biocoop", "Biocoop"), (r"la vie claire", "La Vie Claire"),
       (r"bio c.?bon", "Bio c' Bon"), (r"paris ?store|tang", "Supermarché asiatique"), (r"cora", "Cora"), (r"match", "Match"),
       (r"la grande [ée]picerie", "La Grande Épicerie"), (r"diagonal", "Diagonal")]

def get(path, **q):
    u = f"{API}/{path}?" + urllib.parse.urlencode(q)
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90) as r:
                return json.load(r)
        except Exception as e:
            if k == 4: raise
            time.sleep(3 * (k + 1))

def ens_of(l):
    s = " ".join(x for x in [l.get("osm_brand"), l.get("osm_name")] if x).lower()
    for rx, n in ENS:
        if re.search(rx, s): return n
    return None

def main(out):
    locs, p = [], 1
    while True:
        d = get("locations", size=100, page=p); locs += d["items"]
        if p >= d["pages"]: break
        p += 1
    idf = {l["id"]: l for l in locs if l.get("osm_lat") and BOX[0] < l["osm_lat"] < BOX[1] and BOX[2] < l["osm_lon"] < BOX[3]
           and l.get("price_count") and l.get("type", "OSM") == "OSM"}
    since = (datetime.date.today() - datetime.timedelta(days=30 * MOIS)).isoformat()
    last = {}  # (loc, produit) -> (date, prix)
    def fetch(lid):
        out, p = [], 1
        while True:
            d = get("prices", location_id=lid, date__gte=since, type="PRODUCT", size=100, page=p)
            out += d["items"]
            if p >= d["pages"]: return lid, out
            p += 1
    with ThreadPoolExecutor(8) as ex:
        res_l = list(ex.map(fetch, list(idf)))
    for lid, items in res_l:
            for x in items:
                if x.get("currency") not in (None, "EUR") or x.get("price_is_discounted") or not x.get("product_code") or not x.get("price"): continue
                pr = x["price"]
                if x.get("price_per") == "KILOGRAM" or pr <= 0: continue
                k = (lid, x["product_code"])
                if k not in last or x["date"] > last[k][0]: last[k] = (x["date"], pr)
    by_prod = defaultdict(list)
    for (lid, pc), (dt, pr) in last.items():
        e = ens_of(idf[lid])
        if e: by_prod[pc].append((lid, e, pr))
    ratios = defaultdict(list)  # lid -> log-écarts
    for pc, L in by_prod.items():
        if len({e for _, e, _ in L}) < 2: continue
        v = sorted(pr for _, _, pr in L); m = v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2
        for lid, e, pr in L:
            r = math.log(pr / m)
            if abs(r) < math.log(3): ratios[lid].append(r)
    ens_r = defaultdict(list)
    for lid, R in ratios.items(): ens_r[ens_of(idf[lid])] += R
    gm = lambda R: math.exp(sum(R) / len(R))
    ref = [gm(ens_r[e]) for e in REF if len(ens_r[e]) >= MIN_ENS]
    if not ref: sys.exit("pas assez de données pour l'échelle")
    base = math.exp(sum(math.log(x) for x in ref) / len(ref))
    E = {e: {"i": round(100 * gm(R) / base, 1), "n": len(R), "mag": sum(1 for lid in ratios if ens_of(idf[lid]) == e)}
         for e, R in ens_r.items() if len(R) >= MIN_ENS}
    if "E.Leclerc" in E:
        for e, g in REPERES.items():
            if e not in E: E[e] = {"i": round(E["E.Leclerc"]["i"] * (1 + g / 100) / (1 + RM_LECLERC / 100), 1), "n": 0, "mag": 0, "rep": "Radin Malin, nov. 2026"}
    M = {}
    for lid, R in ratios.items():
        if len(R) < MIN_MAG: continue
        l = idf[lid]; e = ens_of(l); s = 100 * gm(R) / base
        if e in E: s = (len(R) * s + K * E[e]["i"]) / (len(R) + K)
        key = {"NODE": "n", "WAY": "w", "RELATION": "r"}.get(l.get("osm_type"), "?") + str(l["osm_id"])
        M[key] = {"i": round(s, 1), "n": len(R), "e": e, "nom": l.get("osm_name") or e, "lat": round(l["osm_lat"], 5), "lon": round(l["osm_lon"], 5)}
    res = {"maj": datetime.date.today().isoformat(), "source": "Open Prices (Open Food Facts), licence ODbL",
           "methode": f"produits identiques, prix hors promo, {MOIS} derniers mois, 100 = moyenne {', '.join(REF)}",
           "prix": len(last), "enseignes": dict(sorted(E.items(), key=lambda x: x[1]["i"])), "magasins": M}
    json.dump(res, open(out, "w"), ensure_ascii=False, separators=(",", ":"))
    print(len(idf), "magasins IDF ·", len(last), "prix ·", len(E), "enseignes ·", len(M), "magasins avec indice")
    for e, v in res["enseignes"].items(): print(f"{v['i']:6.1f}  {e}  ({v['n']} comparaisons, {v['mag']} magasins)")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "prix.json"))
