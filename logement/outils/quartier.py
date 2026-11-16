"""Cap Logement : télécharge les lieux de vie de quartier d'Île-de-France depuis OpenStreetMap (Overpass)
et écrit logement/quartier.json, lu par l'onglet ★ Mois (bloc « Style de vie »).
Format : {"maj": date, "c": {code: libellé}, "s": [[lat, lon, code, nom], ...]} (nom vide pour cafés, bars, restaurants)."""
import json, sys, time, re, urllib.parse, urllib.request, datetime

S, W, N, E = 48.40, 1.40, 49.20, 2.95
ROWS, COLS = 6, 6
EP = ["https://overpass-api.de/api/interpreter", "https://maps.mail.ru/osm/tools/overpass/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]
LOWGYM = re.compile(r"basic.?fit|on ?air|fitness ?park|keep ?cool|l.?orange ?bleue|neoness|cmg", re.I)
CHEAPWEAR = re.compile(r"primark|kiabi|tati\b|g[ée]mo|la halle|zeeman|takko|action", re.I)
SOLID = re.compile(r"solidaire|restos? du c|secours|croix.rouge|emma[üu]s|banque alimentaire|linkee|agoraé|agorae", re.I)

def ask(q):
    data = urllib.parse.urlencode({"data": q}).encode()
    for tour in range(4):
        for u in EP:
            try:
                req = urllib.request.Request(u, data=data, headers={"User-Agent": "CapLogement/1.0 (displotdoscul.github.io)"})
                with urllib.request.urlopen(req, timeout=200) as r:
                    return json.load(r)
            except Exception as e:
                print("  échec", u, e, file=sys.stderr)
                time.sleep(10 * (tour + 1))
    raise SystemExit("Overpass injoignable")

def code(t):
    a, s, l, n = t.get("amenity", ""), t.get("shop", ""), t.get("leisure", ""), t.get("name", "")
    sp = t.get("sport", "")
    full = " ".join([n, t.get("brand", ""), t.get("operator", "")])
    if SOLID.search(full) or t.get("social_facility") == "food_bank": return "sol"
    if a == "restaurant": return "cro" if re.search(r"crous|resto ?u\b|restaurant universitaire", full, re.I) else "res"
    if a == "fast_food": return "fas"
    if a == "cafe": return "caf"
    if a in ("bar", "pub"): return "bar"
    if a == "pharmacy": return "pha"
    if a == "library": return "bib"
    if a == "cinema": return "cin"
    if a in ("theatre", "arts_centre"): return "the"
    if a == "post_office": return "pos"
    if a == "doctors": return "med"
    if a == "dancing_school" or l == "dance" or "yoga" in sp: return "dan"
    if s in ("bakery", "pastry"): return "bou"
    if s == "laundry": return "lav"
    if s == "books": return "lib"
    if s == "cheese": return "fro"
    if s == "seafood": return "poi"
    if s == "wine": return "cav"
    if s == "florist": return "fle"
    if s in ("second_hand", "charity"): return "fri"
    if s in ("doityourself", "hardware"): return "bri"
    if s == "herbalist": return "her"
    if s in ("tobacco", "newsagent"): return "tab"
    if s == "clothes": return "hab" if CHEAPWEAR.search(full) else None
    if s == "sports": return "dec" if re.search(r"decathlon", full, re.I) else None
    if "climbing" in sp: return "esc"
    if "swimming" in sp or l == "swimming_pool": return "pis"
    if l in ("fitness_centre", "sports_centre"): return "spl" if LOWGYM.search(full) else "spo"
    if l == "park": return "par"
    if l == "garden": return "jar"
    return None

LAB = {"bou": "Boulangerie", "pha": "Pharmacie", "caf": "Café", "bar": "Bar", "res": "Restaurant", "fas": "Restauration rapide",
       "cro": "Resto U (CROUS)", "lav": "Laverie", "lib": "Librairie", "bib": "Bibliothèque", "fro": "Fromagerie", "poi": "Poissonnerie",
       "cav": "Caviste", "fle": "Fleuriste", "fri": "Friperie, ressourcerie", "bri": "Bricolage", "her": "Herboristerie", "tab": "Tabac, presse",
       "hab": "Vêtements pas chers", "dec": "Decathlon", "sol": "Aide alimentaire, épicerie solidaire", "esc": "Escalade", "pis": "Piscine",
       "spo": "Salle de sport", "spl": "Salle de sport low-cost", "dan": "Danse, yoga", "par": "Parc", "jar": "Jardin partagé",
       "cin": "Cinéma", "the": "Théâtre, lieu culturel", "pos": "Poste", "med": "Médecin"}
NONAME = {"caf", "bar", "res", "fas"}

out, seen = [], set()
for i in range(ROWS):
    for j in range(COLS):
        s = S + (N - S) * i / ROWS; n = S + (N - S) * (i + 1) / ROWS
        w = W + (E - W) * j / COLS; e = W + (E - W) * (j + 1) / COLS
        bb = f"{s},{w},{n},{e}"
        q = (f'[out:json][timeout:170];('
             f'nwr({bb})[amenity~"^(restaurant|fast_food|cafe|bar|pub|pharmacy|library|cinema|theatre|arts_centre|post_office|doctors|dancing_school)$"];'
             f'nwr({bb})[shop~"^(bakery|pastry|laundry|books|cheese|seafood|wine|florist|second_hand|charity|doityourself|hardware|herbalist|tobacco|newsagent)$"];'
             f'nwr({bb})[shop=clothes][name~"primark|kiabi|tati|gémo|gemo|la halle|zeeman|takko",i];'
             f'nwr({bb})[shop=sports][name~"decathlon",i];'
             f'nwr({bb})[amenity=social_facility][social_facility=food_bank];'
             f'nwr({bb})[leisure~"^(fitness_centre|dance)$"];'
             f'nwr({bb})[leisure=sports_centre][sport~"swimming|climbing|yoga|fitness"];'
             f'nwr({bb})[leisure=swimming_pool][name][access!~"private|customers|no"];'
             f'nwr({bb})[leisure=park][name];'
             f'nwr({bb})[leisure=garden]["garden:type"=community];'
             f');out center tags;')
        print("tuile", i, j, file=sys.stderr)
        for el in ask(q).get("elements", []):
            k = el["type"][0] + str(el["id"])
            if k in seen: continue
            seen.add(k)
            t = el.get("tags", {})
            lat = el.get("lat", el.get("center", {}).get("lat")); lon = el.get("lon", el.get("center", {}).get("lon"))
            if lat is None: continue
            c = code(t)
            if not c: continue
            nm = "" if c in NONAME else t.get("name", "")[:40]
            out.append([round(lat, 4), round(lon, 4), c, nm])
        time.sleep(5)

if len(out) < 20000:
    raise SystemExit(f"Trop peu de lieux ({len(out)}) : données incomplètes, fichier non remplacé")
out.sort()
json.dump({"maj": datetime.date.today().isoformat(), "c": LAB, "s": out}, open("logement/quartier.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(out), "lieux", file=sys.stderr)
