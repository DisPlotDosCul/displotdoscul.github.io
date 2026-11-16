"""Cap Logement : télécharge les commerces d'Île-de-France depuis OpenStreetMap (Overpass)
et écrit logement/commerces.json, lu par l'onglet ★ Mois (plus de recherche en direct depuis le téléphone).
Format : {"maj": date, "s": [[lat, lon, type, nom, marque, halal, horaires], ...]}"""
import json, sys, time, urllib.parse, urllib.request, datetime

S, W, N, E = 48.40, 1.40, 49.20, 2.95
ROWS, COLS = 4, 4
FOOD = "supermarket|convenience|greengrocer|frozen_food|organic|health_food|butcher|deli|spices|general|food|bulk|variety_store|discount"
EP = ["https://overpass-api.de/api/interpreter", "https://maps.mail.ru/osm/tools/overpass/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]

def ask(q):
    data = urllib.parse.urlencode({"data": q}).encode()
    for tour in range(4):
        for u in EP:
            try:
                req = urllib.request.Request(u, data=data, headers={"User-Agent": "CapLogement/1.0 (displotdoscul.github.io)"})
                with urllib.request.urlopen(req, timeout=300) as r:
                    return json.load(r)
            except Exception as e:
                print("  échec", u, e, file=sys.stderr)
                time.sleep(10 * (tour + 1))
    raise SystemExit("Overpass injoignable")

out, seen = [], set()
for i in range(ROWS):
    for j in range(COLS):
        s = S + (N - S) * i / ROWS; n = S + (N - S) * (i + 1) / ROWS
        w = W + (E - W) * j / COLS; e = W + (E - W) * (j + 1) / COLS
        bb = f"{s},{w},{n},{e}"
        q = (f'[out:json][timeout:280];(nwr({bb})[shop~"^({FOOD})$"];nwr({bb})[amenity=marketplace];'
             f'nwr({bb})[shop=chemist][name~"^normal",i];nwr({bb})[bulk_purchase=only];nwr({bb})[organic=only][shop];'
             f'nwr({bb})[shop=herbalist];nwr({bb})[shop~"^(cosmetics|beauty|chemist|perfumery)$"][name~"aroma|centifolia|herbor|naturel|savon|karit|cosm.tique bio|z.ro ?d.chet|mademoiselle bio|cosmo ?naturel|comptoir|afro|exotic|beauty ?supply|huiles",i];);out center tags;')
        print("tuile", i, j, file=sys.stderr)
        for el in ask(q).get("elements", []):
            k = el["type"][0] + str(el["id"])
            if k in seen: continue
            seen.add(k)
            t = el.get("tags", {})
            lat = el.get("lat", el.get("center", {}).get("lat")); lon = el.get("lon", el.get("center", {}).get("lon"))
            if lat is None: continue
            ty = "marketplace" if t.get("amenity") == "marketplace" else t.get("shop", "")
            nm = (t.get("name", "") + " " + t.get("brand", "")).lower()
            if t.get("bulk_purchase") == "only": ty = "bulk"
            elif t.get("organic") == "only" and ty in ("supermarket", "convenience", "general", "food", "deli"): ty = "organic"
            if ty in ("herbalist", "cosmetics", "beauty", "perfumery") or (ty == "chemist" and not nm.startswith("normal")): ty = "diycos"
            halal = 1 if t.get("diet:halal") in ("yes", "only") else 0
            oh = t.get("opening_hours", "") if ty == "marketplace" else ""
            out.append([round(lat, 5), round(lon, 5), ty, t.get("name", ""), t.get("brand", "") or t.get("operator", ""), halal, oh])
        time.sleep(5)

if len(out) < 5000:
    raise SystemExit(f"Trop peu de commerces ({len(out)}) : données incomplètes, fichier non remplacé")
out.sort()
json.dump({"maj": datetime.date.today().isoformat(), "s": out}, open("logement/commerces.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(out), "commerces", file=sys.stderr)
