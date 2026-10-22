"""Idées du 22 octobre : dé, recherche, avis à son nom, apostrophe, flèches, résumé, Boussole, boîte à idées, images, mode édition."""
import json
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
    # TMDB simulé : aucune requête ne part vers le vrai service.
    context.route("https://api.themoviedb.org/**", lambda r: r.fulfill(content_type="application/json", body=json.dumps(
        {"results": [{"id": 694}]} if "/search/" in r.request.url else {"backdrops": [{"file_path": "/image-%d.jpg" % i, "iso_639_1": None} for i in range(6)]})))
    context.route("https://image.tmdb.org/**", lambda r: r.fulfill(content_type="image/svg+xml", body='<svg xmlns="http://www.w3.org/2000/svg" width="16" height="9"/>'))
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

            # Le résumé reste visible sur une fiche ordinaire.
            assert page.locator('#main .film[data-id="swallow-2019"] .why').first.is_visible()
            page.locator("#qx").click()

            # Boussole : questionnaire déjà rempli → questions repliées ; « Pas vu » s'enregistre tout de suite.
            page.locator("#ccQuiz").click()
            assert page.locator("#qzPanel .qz-ok").is_visible() and page.locator('#qzPanel [data-qz="sombre"]').count() == 0
            fid = page.locator("#qzPanel [data-qzf]").first.get_attribute("data-qzf")
            assert page.locator("#qzPanel [data-qzf]").count() == 40
            page.locator(f'#qzPanel [data-qzf="{fid}"][data-v="pv"]').click()
            page.wait_for_function("id => (__fixture.profils['test-membre'].rep[id] || {}).etat === 'pas_vu'", arg=fid)
            page.locator('#qzPanel [data-qzmode="q2"]').click()
            page.locator('#qzPanel [data-qz="k_reve"][data-v="1"]').click()
            page.locator("#qzPanel [data-qzsave]").click()
            page.wait_for_function("__fixture.profils['test-membre'].quiz.k_reve === 1 && __fixture.profils['test-membre'].quiz.sombre === 1")
            page.locator("#qzPanel [data-qzclose]").click()

            # Boîte à idées : modifier une suggestion, ajouter un film.
            page.locator("#toc .idb").first.click()
            page.locator('#toc [data-idkind="amelio"]').click()
            page.locator("#toc form[data-idform] textarea").fill("Une idée à corriger")
            page.locator("#toc form[data-idform] button[type=submit]").click()
            page.locator("#toc button[data-idedit]").first.click()
            page.locator("#toc form[data-idedit] textarea").fill("Une idée corrigée, avec l'apostrophe")
            page.locator("#toc form[data-idedit] button[type=submit]").click()
            page.wait_for_function("Object.values(__fixture.idees || {}).some(x => x.texte === \"Une idée corrigée, avec l'apostrophe\")")
            page.locator('#toc [data-idkind="film"]').click()
            page.locator("#toc form[data-idfilm] [name=titre]").fill("Un film imaginaire de test")
            page.locator("#toc form[data-idfilm] [name=annee]").fill("2020")
            page.locator("#toc form[data-idfilm] button[type=submit]").click()
            page.wait_for_function("__fixtureWrites.some(w => (w.collection === 'propositions' && w.value.titre === 'Un film imaginaire de test') || (w.collection === 'films' && JSON.stringify(w.value).includes('Un film imaginaire de test')))")

            # Images du film : quatre images dans la fiche, qui restent après un redessin.
            page.locator("#q").fill("Shining")
            card = '#main .film[data-id="shining-1980"]'
            page.locator(card).first.wait_for()
            page.locator(card + " [data-img]").first.click()
            page.wait_for_function("s => document.querySelectorAll(s + ' .fimg img').length === 4", arg=card)
            assert page.locator(card + " .fimg-s").first.inner_text() == "Images : TMDB"
            page.locator(card + ' [data-a="pas_vu"]').first.click()
            page.wait_for_timeout(300)
            assert page.locator(card + " .fimg img").count() == 4
            page.locator("#qx").click()

            # Mode édition : réservé à l'administratrice ; disposition, texte et couleur enregistrés ensemble.
            page.locator("#aab").click()
            if not admin:
                assert page.locator("#ccEdit").is_hidden()
                page.locator("#aab").click()
            else:
                page.locator("#ccEdit").click()
                page.locator('#edPanel [data-edmv="top|toc|-1"]').click()
                assert page.evaluate("document.querySelector('#toc').compareDocumentPosition(document.querySelector('.bar')) & Node.DOCUMENT_POSITION_FOLLOWING")
                page.locator('#edPanel [data-edtab="textes"]').click()
                page.locator('#edPanel [data-edtx="btn.ciel"]').fill("✦ Mes étoiles")
                assert page.locator("#skyToggle").inner_text() == "✦ Mes étoiles"
                page.locator('#edPanel [data-edtab="couleurs"]').click()
                page.locator('#edPanel [data-edcol="--vu"]').evaluate("e => { e.value = '#00aaff'; e.dispatchEvent(new Event('input', { bubbles:true })); }")
                page.locator("#edPanel [data-edsave]").click()
                page.wait_for_function("__fixture.films.apparence && __fixture.films.apparence.t['btn.ciel'] === '✦ Mes étoiles' && __fixture.films.apparence.c.neon['--vu'] === '#00aaff' && __fixture.films.apparence.o.top[1] === 'toc'")
                page.locator("#edPanel [data-edclose]").click()
                assert page.locator("#skyToggle").inner_text() == "✦ Mes étoiles"

            assert not errors and not unexpected, (errors, unexpected)
            print(f"{who} : dé et recherche, recherche en haut, apostrophe, avis à son nom, conseil à tous, flèches, résumé, Boussole, idées, images, mode édition et console : OK", flush=True)
            context.close()
        browser.close()


if __name__ == "__main__":
    run()
