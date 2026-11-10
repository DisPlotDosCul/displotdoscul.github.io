"""Cap Logement : chiffre et déchiffre les espaces privés (logement/espaces/<espace>.json).

Chaque espace est chiffré en AES-GCM (Advanced Encryption Standard, mode Galois/Counter) avec une clé
dérivée de la clé de maintenance par PBKDF2 (Password-Based Key Derivation Function 2, SHA-256,
310 000 tours, sel « cap-logement:<espace> »). La page logement/index.html lit la même clé dans Firestore,
où seules la propriétaire de l'espace et l'administratrice peuvent la lire.

La clé de maintenance n'est jamais écrite dans le dépôt : on la passe par la variable CAP_CLE.
Les sources en clair restent hors du dépôt (dossier de travail).

  CAP_CLE=... python3 outils/cap_logement.py dechiffrer <dossier_de_travail>
  CAP_CLE=... python3 outils/cap_logement.py chiffrer   <dossier_de_travail>

Dossier de travail : <espace>/carte.html, annonces.html, bondy.html… (une page par onglet) et calc.json.
"""
import base64, hashlib, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ESPACES = ["licia", "cloche", "violette"]
ICI = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.join(ICI, "..", "logement", "espaces")


def cle(maitre, espace):
    return hashlib.pbkdf2_hmac("sha256", maitre.encode(), ("cap-logement:" + espace).encode(), 310000, 32)


def chiffrer(maitre, travail):
    os.makedirs(DEPOT, exist_ok=True)
    for e in ESPACES:
        d = os.path.join(travail, e)
        if not os.path.isdir(d):
            continue
        b = {"pages": {}}
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if f.endswith(".html"):
                b["pages"][f[:-5]] = open(p, encoding="utf-8").read()
            elif f == "calc.json":
                b["calc"] = json.load(open(p, encoding="utf-8"))
        iv = os.urandom(12)
        data = AESGCM(cle(maitre, e)).encrypt(iv, json.dumps(b, ensure_ascii=False).encode(), None)
        json.dump({"v": 1, "i": base64.b64encode(iv).decode(), "d": base64.b64encode(data).decode()},
                  open(os.path.join(DEPOT, e + ".json"), "w"))
        print("chiffré", e, sorted(b["pages"]), "calc" if "calc" in b else "")


def dechiffrer(maitre, travail):
    for e in ESPACES:
        p = os.path.join(DEPOT, e + ".json")
        if not os.path.exists(p):
            continue
        j = json.load(open(p))
        b = json.loads(AESGCM(cle(maitre, e)).decrypt(base64.b64decode(j["i"]), base64.b64decode(j["d"]), None))
        d = os.path.join(travail, e)
        os.makedirs(d, exist_ok=True)
        for k, html in b["pages"].items():
            open(os.path.join(d, k + ".html"), "w", encoding="utf-8").write(html)
        if "calc" in b:
            json.dump(b["calc"], open(os.path.join(d, "calc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("déchiffré", e, sorted(b["pages"]))


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("chiffrer", "dechiffrer") or not os.environ.get("CAP_CLE"):
        sys.exit(__doc__)
    {"chiffrer": chiffrer, "dechiffrer": dechiffrer}[sys.argv[1]](os.environ["CAP_CLE"], sys.argv[2])
