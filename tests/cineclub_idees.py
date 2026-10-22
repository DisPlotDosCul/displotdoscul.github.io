"""Idées du 22 octobre : dé et recherche, recherche en haut, avis à son nom, apostrophe, flèches ← →."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import cineclub_fixture as cf

# La base fictive n'a pas « add » : on l'ajoute pour les conseils envoyés à tout le monde.
FIREBASE_JS = cf.FIREBASE_JS.replace("      doc:function(id){", "      add:function(v){ var d=this.doc(); return d.set(v).then(function(){ return d; }); },\n      doc:function(id){", 1)
FILM = '#main .film[data-id="it-follows-2014"]'


def open_page(browser, admin):
    fixture = cf.catalogue_fixture()
    if admin:
        fixture["profils"]["test-membre"].update(pid="licia", pseudo="Licia")
        fixture["films"]["pl-camille"] = {"auto": "conseils", "famille": "playlists", "films": [], "ordre": 0.8,
                                          "prenom": "m_test-autre", "titre": "Camille (test)"}
    context = browser.new_context(viewport={"width": 360, "height": 780}, has_touch=True, is_mobile=True)
    cf.FIREBASE_JS = FIREBASE_JS  # lu au moment des requêtes, pas à l'installation
    unexpected = cf.install_routes(context, fixture=fixture)
    if admin:
        html = (cf.ROOT / "carnet-de-films/index.html").read_text().replace(
            "CC.admin = !!(u && uh[1] === ADMIN_SHA);", "CC.admin = true;")
        context.route("https://cineclub.test/carnet-de-films/", lambda r: r.fulfill(content_type="text/html", body=html))
    context.add_init_script("localStorage.setItem('carnetAmbianceV1','neon');")
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
        for admin in (False, True):
            context, page, errors, unexpected = open_page(browser, admin)
            who = "administratrice" if admin else "membre"

            # Le film tiré au hasard se ferme dès qu'on va chercher autre chose.
            page.locator("#dice").click()
            page.locator("#rsheet").wait_for(state="visible")
            page.locator("#q").click()
            assert page.locator("#rsheet").is_hidden(), "le film au hasard cache encore la recherche"

            # La recherche monte en haut de l'écran, les résultats remplissent la page.
            page.locator("#q").type("Swallow")
            page.wait_for_function("document.querySelector('#main .film[data-id=\"swallow-2019\"]')")
            page.wait_for_timeout(100)
            assert page.locator(".row-tools").bounding_box()["y"] < 20
            assert page.locator('#main .film[data-id="swallow-2019"]').bounding_box()["y"] < 300

            # L'apostrophe courbe d'un clavier de téléphone trouve le titre écrit avec l'apostrophe droite.
            page.locator("#q").fill("L’Odyssée")
            page.wait_for_function("document.querySelector('#main .film[data-id=\"2001-l-odyssee-de-l-espace-1968\"]')")

            # On ne donne son avis et on ne commente qu'en son propre nom.
            page.locator("#q").fill("It follows")
            page.locator(FILM).first.wait_for()
            page.locator(FILM + " [data-pl]").first.click()
            names = page.locator(FILM + " .plc [data-pn]").all_inner_texts()
            assert all("Camille" not in n for n in names), names
            assert page.locator(FILM + " [data-newp]").count() == 0
            page.locator(FILM + ' button:has-text("💬")').first.click()
            options = page.locator(FILM + " .c-who option").all_inner_texts()
            assert options == ["Licia" if admin else "Alix (test)"], options
            page.locator(FILM + " .c-in").first.fill("J'aime l'ambiance")
            page.locator(FILM + " [data-cok]").first.click()
            page.wait_for_function("__fixtureWrites.some(w => w.collection === 'commentaires')")
            saved = page.evaluate("__fixtureWrites.filter(w => w.collection === 'commentaires').pop().value")
            assert saved["texte"] == "J'aime l'ambiance" and saved["prenom"] == ("licia" if admin else "m_test-membre"), saved

            # Conseil à tout le monde, avec apostrophes.
            if not page.locator(FILM + " [data-cconseil]").count():
                page.locator(FILM + " [data-pl]").first.click()
            page.locator(FILM + " [data-cconseil]").first.click()
            page.locator('[data-aud="pub"]').click()
            page.locator("#ccSendTxt").fill("Qu'il est bien, l’horreur")
            page.locator("#ccSendGo").click()
            page.wait_for_function("__fixtureWrites.some(w => w.collection === 'messages' && w.value.to === '*')")
            page.locator("[data-ccclose]").first.click()

            # Flèches ← → : retour à l'affichage précédent, puis au suivant.
            page.locator("#qx").click()
            page.locator("#navb").wait_for(state="visible")
            page.locator("#q").fill("Swallow")
            page.wait_for_timeout(400)
            page.locator("#navBack").click()
            page.wait_for_function("document.querySelector('#q').value === ''")
            page.locator("#navFwd").click()
            page.wait_for_function("document.querySelector('#q').value === 'Swallow'")

            assert not errors and not unexpected, (errors, unexpected)
            print(f"{who} : dé et recherche, recherche en haut, apostrophe, avis à son nom, conseil à tous, flèches et console : OK", flush=True)
            context.close()
        browser.close()


if __name__ == "__main__":
    run()
