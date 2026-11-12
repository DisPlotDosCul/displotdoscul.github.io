"""Confidentialité (12 novembre) : carnets déplacés dans « carnets », quatre modes, réglage élément par élément,
amis (demande acceptée des deux côtés), commentaires réservés aux proches, films ajoutés par les membres,
chacun sa playlist, fusion des anciennes playlists. Le faux Firestore suit les filtres des requêtes, comme les règles."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from cineclub_fixture import catalogue_fixture, install_routes, open_more


def fixture():
    f = catalogue_fixture()
    # Un membre déjà passé aux carnets, qui ne montre ses notes qu'à ses amis (dont ne fait pas partie test-membre).
    f["profils"]["test-prive"] = {"pseudo": "Dominique (test)", "pid": "m_test-prive", "carnet": 1, "vis": "prive", "amis": ["test-autre"]}
    f["carnets"] = {
        "test-prive__rep": {"uid": "test-prive", "part": "rep", "vis": "amis", "lect": ["test-autre"], "data": {"matrix-1999": {"etat": "vu", "note10": 9}}},
        "test-prive__stats": {"uid": "test-prive", "part": "stats", "vis": "tous", "lect": [], "data": {"vus": 42, "notes": 30, "moy": 7.4, "pasFinis": 1}},
    }
    f["films"]["pl-arthur"] = {"auto": "conseils", "famille": "playlists", "films": [], "ordre": 0.71, "prenom": "arthur", "titre": "Arthur"}
    f["conseils"] = {"arthur__shining-1980": {"prenom": "arthur", "film": "shining-1980", "ajout": "2026-01-01T00:00:00Z", "mot": "", "uid": "admin"}}
    return f


def open_page(browser, deny, change=None):
    context = browser.new_context(service_workers="block", viewport={"width": 390, "height": 820}, has_touch=True, is_mobile=True)
    context.add_init_script("window.__fixtureDeny = " + json.dumps(deny) + ";")
    unexpected = install_routes(context, fixture=(change or (lambda f: f))(fixture()))
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto("https://cineclub.test/carnet-de-films/", wait_until="networkidle")
    page.wait_for_function("window.CC && CC.me && CC.filmInfo && CC.filmInfo('matrix-1999')")
    if page.locator("#introX").is_visible():
        page.locator("#introX").click()
    return context, page, errors, unexpected


def run():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None, args=["--no-sandbox"])

        # 1. Règles pas encore publiées : tout reste dans le profil, le réglage est grisé et le dit.
        context, page, errors, unexpected = open_page(browser, ["carnets", "ajouts", "commentairesPrives"])
        assert page.evaluate("!__fixture.profils['test-membre'].carnet && !!__fixture.profils['test-membre'].rep['shining-1980']")
        page.locator("#ccMe").click()
        priv = page.locator("#ccPriv")
        priv.wait_for()
        assert "Pas encore disponible" in priv.inner_text()
        assert page.locator('#ccPriv [data-pmode="prive"]').is_disabled()
        assert not errors, errors
        assert not unexpected, unexpected
        context.close()

        # 2. Règles publiées : mes données passent dans « carnets », en public par défaut.
        context, page, errors, unexpected = open_page(browser, [])
        page.wait_for_function("__fixture.profils['test-membre'].carnet === 1")
        page.wait_for_function("(__fixture.carnets['test-membre__rep'] || {}).vis === 'tous'")
        assert page.evaluate("!('rep' in __fixture.profils['test-membre']) && !!__fixture.carnets['test-membre__rep'].data['shining-1980']")
        assert page.evaluate("__fixture.carnets['test-membre__quiz'].data.sombre === 1 && __fixture.carnets['test-membre__reglages'].vis === 'moi'")
        page.wait_for_function("(__fixture.carnets['test-membre__stats'] || {}).data && __fixture.carnets['test-membre__stats'].data.vus >= 1")
        # Une réponse va maintenant dans mon document « carnets ».
        open_more(page)
        page.locator("#ccXp").click()
        first = page.locator("#xpBody .xp-card").get_attribute("data-film")
        page.locator('#xpBody [data-xp="9"]').click()
        page.wait_for_function("id => ((__fixture.carnets['test-membre__rep'].data || {})[id] || {}).note10 === 9", arg=first)
        assert page.evaluate("!__fixture.profils['test-membre'].rep")
        page.keyboard.press("Escape")

        # Un carnet privé : cadenas et chiffres partagés, pas de notes, pas d'ouverture du carnet.
        page.locator("#ccMbr").click()
        row = page.locator('#msheet [data-msel="test-prive"]')
        row.wait_for()
        assert "42 vus" in row.inner_text(), row.inner_text()
        row.click()
        body = page.locator("#msheetBody").inner_text()
        assert "ne partage pas avec toi ses notes" in body and "42 films vus" in body, body
        assert page.locator("#msheet [data-mview]").count() == 0

        # Demande d'ami, acceptée de l'autre côté.
        page.locator('#msheet [data-msel=""]').click()
        page.locator('#msheet [data-msel="test-autre"]').click()
        page.locator('#msheet [data-amidem="test-autre"]').click()
        page.wait_for_function("Object.values(__fixture.messages || {}).some(m => m.type === 'ami-dem' && m.from === 'test-membre' && m.to === 'test-autre')")
        page.locator("#msheet .ami-b").get_by_text("Demande envoyée").wait_for()
        page.evaluate("""() => { __fixturePut('profils', 'test-autre', Object.assign({}, __fixture.profils['test-autre'], { amis:['test-membre'] }));
          __fixturePut('messages', 'ok1', { from:'test-autre', to:'test-membre', type:'ami-ok', mot:'', ajout:new Date().toISOString() }); }""")
        page.wait_for_function("(__fixture.profils['test-membre'].amis || []).includes('test-autre') && __fixture.messages.ok1.lu === true")
        page.locator("#msheet .ami-b").get_by_text("Vous êtes amis").wait_for()
        page.locator("#msheet [data-ccclose]").first.click()

        # Une demande reçue arrive en haut de « Pour moi » ; accepter l'ajoute et prévient l'autre.
        page.evaluate("__fixturePut('messages', 'dem1', { from:'test-prive', to:'test-membre', type:'ami-dem', mot:'', ajout:new Date().toISOString() })")
        page.locator("#ccMbr").click()
        page.locator('#msheet [data-ctab="pourmoi"]').click()
        page.locator("#msheet .cthread").get_by_text("te demande en ami").wait_for()
        page.locator('#msheet [data-amiok="test-prive"]').first.click()
        page.wait_for_function("(__fixture.profils['test-membre'].amis || []).includes('test-prive') && Object.values(__fixture.messages).some(m => m.type === 'ami-ok' && m.from === 'test-membre' && m.to === 'test-prive') && __fixture.messages.dem1.lu === true")
        page.locator("#msheet [data-ccclose]").first.click()
        page.evaluate("__fixturePut('profils', 'test-prive', Object.assign({}, __fixture.profils['test-prive'], { amis:['test-autre', 'test-membre'] }))")

        # Mode privé : mes documents ne sont plus lisibles que par mes amis.
        page.locator("#ccMe").click()
        page.locator('#ccPriv [data-pmode="prive"]').click()
        page.wait_for_function("__fixture.profils['test-membre'].vis === 'prive' && __fixture.profils['test-membre'].recoit === 'amis'")
        page.wait_for_function("JSON.stringify(__fixture.carnets['test-membre__rep'].lect) === '[\"test-autre\",\"test-prive\"]' && __fixture.carnets['test-membre__rep'].vis === 'amis'")
        assert page.evaluate("__fixture.carnets['test-membre__liste'].vis === 'amis'")

        # Mode personnalisé : liste visible par tous, commentaires pour mes proches seulement.
        page.locator('#ccPriv [data-pmode="perso"]').click()
        page.locator('#ccPriv [data-pvoir="liste"]').wait_for()
        assert page.locator("#ccPriv [data-pvoir]").count() == 9
        page.locator('#ccPriv [data-pvoir="liste"]').select_option("tous")
        page.wait_for_function("__fixture.carnets['test-membre__liste'].vis === 'tous'")
        page.locator('#ccPriv [data-pvoir="rep"]').select_option("moi")
        page.wait_for_function("__fixture.carnets['test-membre__rep'].vis === 'moi' && __fixture.carnets['test-membre__rep'].lect.length === 0")
        page.locator('#ccPriv [data-pvoir="com"]').select_option("proches")
        page.locator('#ccPriv [data-proche="test-autre"]').check()
        page.wait_for_function("JSON.stringify(((__fixture.carnets['test-membre__reglages'].data || {}).proches) || []) === '[\"test-autre\"]'")
        page.locator('#ccPriv [data-pvoir="recoit"]').select_option("moi")
        page.wait_for_function("__fixture.profils['test-membre'].recoit === 'moi'")
        page.locator("#lsheet").screenshot(path=str(Path(__file__).resolve().parent.parent / "docs/captures/cineclub-confidentialite.png"))
        page.keyboard.press("Escape")

        # Un commentaire écrit maintenant part dans « commentairesPrives », lu par mes proches.
        page.locator("#q").fill("Shining")
        card = '#main .film[data-id="shining-1980"]'
        page.locator(card).first.wait_for()
        page.locator(card + ' button:has-text("💬")').first.click()
        page.locator(card + " .c-in").first.fill("Pour mes proches seulement")
        page.locator(card + " [data-cok]").first.click()
        page.wait_for_function("Object.values(__fixture.commentairesPrives || {}).some(c => c.texte === 'Pour mes proches seulement' && c.vis === 'proches' && c.lect[0] === 'test-autre')")
        page.wait_for_function("s => [...document.querySelectorAll(s + ' .cmt')].some(c => c.textContent.includes('Pour mes proches seulement'))", arg=card)
        # Retour à tout le monde : le commentaire rejoint les commentaires publics.
        page.locator("#ccMe").click()
        page.locator('#ccPriv [data-pvoir="com"]').select_option("tous")
        page.wait_for_function("Object.values(__fixture.commentaires || {}).some(c => c.texte === 'Pour mes proches seulement') && !Object.values(__fixture.commentairesPrives || {}).some(c => c.texte === 'Pour mes proches seulement')", timeout=15000)
        page.keyboard.press("Escape")

        # Film ajouté par un membre : directement dans la base, visible par tous.
        page.locator("#q").fill("Un film imaginaire du test")
        page.locator("[data-addq]").first.click()
        page.locator("form[data-addform] [name=annee]").fill("2021")
        page.locator("form[data-addform] [name=indices]").fill("Un détail")
        page.locator("form[data-addform] button[type=submit]").click()
        page.wait_for_function("(__fixture.ajouts || {})['un-film-imaginaire-du-test-2021'] && __fixture.ajouts['un-film-imaginaire-du-test-2021'].uid === 'test-membre'")
        page.wait_for_function("window.CC && CC.filmInfo && CC.filmInfo('un-film-imaginaire-du-test-2021')")
        assert not page.evaluate("Object.keys(__fixture.propositions || {}).length")

        # Ma playlist : elle s'ouvre depuis Mon compte ; un film absent de la base y entre directement.
        page.locator("#q").fill("")
        page.locator("#ccMe").click()
        page.locator("#ccPriv").wait_for()
        page.locator("#lsheet [data-myplay]").click()
        sec = "#sec-pl-m_test-membre"
        page.locator(sec).wait_for()
        assert "Ta playlist est vide" in page.locator(sec).inner_text()
        page.locator(sec + " [data-plopen]").click()
        page.locator(sec + " form[data-plform] [name=titre]").fill("Un second film du test")
        page.locator(sec + " form[data-plform] [name=annee]").fill("2019")
        page.locator(sec + " form[data-plform] button[type=submit]").click()
        page.wait_for_function("!!(__fixture.ajouts || {})['un-second-film-du-test-2019'] && !!(__fixture.conseils || {})['m_test-membre__un-second-film-du-test-2019']")
        page.locator(sec + ' .film[data-id="un-second-film-du-test-2019"]').wait_for()
        # La playlist d'un autre : pas de bouton pour y ajouter un film.
        page.evaluate("CC.plOpen('pl-arthur')")
        page.locator("#sec-pl-arthur").wait_for()
        assert page.locator("#sec-pl-arthur [data-plopen]").count() == 0

        # Bulle : plus rien n'est lisible par les autres.
        page.locator("#ccMe").click()
        page.locator('#ccPriv [data-pmode="bulle"]').click()
        page.wait_for_function("__fixture.profils['test-membre'].bulle === true && __fixture.carnets['test-membre__liste'].vis === 'moi' && __fixture.carnets['test-membre__stats'].vis === 'moi'")
        page.locator('#ccPriv [data-pmode="public"]').click()
        page.wait_for_function("__fixture.profils['test-membre'].bulle === false && __fixture.carnets['test-membre__rep'].vis === 'tous'")
        page.keyboard.press("Escape")

        # Fusion des anciennes playlists : un compte « Arthur » est relié à la playlist d'Arthur, ses films suivent.
        page.evaluate("""() => { __fixturePut('profils', 'test-arthur', { pseudo:'Arthur', pid:'m_test-arthur', slug:'m_test-arthur' });
          __fixturePut('conseils', 'm_test-arthur__matrix-1999', { prenom:'m_test-arthur', film:'matrix-1999', ajout:'2026-02-01T00:00:00Z', mot:'top', uid:'test-arthur' }); }""")
        page.evaluate("() => { CC.admin = true; CC.autoLink(); }")
        page.wait_for_function("__fixture.profils['test-arthur'].pid === 'arthur'")
        page.wait_for_function("!!(__fixture.conseils || {})['arthur__matrix-1999'] && !__fixture.conseils['m_test-arthur__matrix-1999']")
        assert page.evaluate("__fixture.conseils['arthur__matrix-1999'].mot") == "top"
        assert not errors, errors
        assert not unexpected, unexpected
        context.close()

        # 3. Un onglet resté ouvert avec l'ancienne version a réécrit une réponse dans le profil : elle rejoint le carnet.
        def stray(f):
            p = f["profils"]["test-membre"]
            f["carnets"]["test-membre__rep"] = {"uid": "test-membre", "part": "rep", "vis": "tous", "lect": [], "data": p.pop("rep")}
            f["carnets"]["test-membre__liste"] = {"uid": "test-membre", "part": "liste", "vis": "tous", "lect": [], "data": p.pop("liste")}
            f["carnets"]["test-membre__quiz"] = {"uid": "test-membre", "part": "quiz", "vis": "tous", "lect": [], "data": p.pop("quiz")}
            p["carnet"] = 1
            p["rep"] = {"cube-1997": {"etat": "vu", "note10": 6, "titre": "Cube"}}
            return f
        context, page, errors, unexpected = open_page(browser, [], stray)
        page.wait_for_function("!('rep' in __fixture.profils['test-membre']) && (__fixture.carnets['test-membre__rep'].data['cube-1997'] || {}).note10 === 6 && !!__fixture.carnets['test-membre__rep'].data['shining-1980']")
        assert not errors, errors
        context.close()
        browser.close()


if __name__ == "__main__":
    run()
    print("Confidentialité, amis, ajouts et playlists : OK")
