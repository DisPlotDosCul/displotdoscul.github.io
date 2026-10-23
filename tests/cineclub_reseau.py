"""Réseau social : mode express, affinités, films en commun, soirée ciné, import Letterboxd et IMDb, invitation."""
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from cineclub_fixture import catalogue_fixture, install_routes


def open_page(browser, fixture=None, url="https://cineclub.test/carnet-de-films/"):
    context = browser.new_context(viewport={"width": 360, "height": 780}, has_touch=True, is_mobile=True)
    unexpected = install_routes(context, fixture=fixture)
    context.add_init_script("Object.defineProperty(navigator,'share',{value:undefined,configurable:true});"
                            "Object.defineProperty(navigator,'clipboard',{value:{writeText:async t=>{window.__shared=t;}},configurable:true});"
                            "localStorage.setItem('carnetAmbianceV1','neon');")
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto(url, wait_until="networkidle")
    page.wait_for_function("window.CC && CC.me && CC.filmInfo && CC.filmInfo('matrix-1999')")
    if page.locator("#introX").is_visible():
        page.locator("#introX").click()
    return context, page, errors, unexpected


def rep(page, fid):
    return page.evaluate("id => __fixture.profils['test-membre'].rep[id] || null", fid)


def run():
    folder = Path(tempfile.mkdtemp())
    (folder / "ratings.csv").write_text("Date,Name,Year,Letterboxd URI,Rating\n2024-01-01,Cube,1997,https://boxd.it/x,4.5\n2024-01-02,\"Un film, inconnu\",2001,https://boxd.it/z,2\n")
    (folder / "imdb.csv").write_text("Const,Your Rating,Date Rated,Title,Original Title,URL,Title Type,IMDb Rating,Runtime (mins),Year,Genres,Num Votes,Release Date,Directors\n"
                                     "tt1,8,2024-01-01,Cure,Kyua,https://imdb,Movie,7.4,111,1997,Horror,1,1997-12-27,Kiyoshi Kurosawa\n")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None, args=["--no-sandbox"])
        context, page, errors, unexpected = open_page(browser)

        # Mode express : un toucher par film, chaque réponse enregistrée, retour possible.
        page.locator("#ccXp").click()
        first = page.locator("#xpBody .xp-card").get_attribute("data-film")
        page.locator('#xpBody [data-xp="9"]').click()
        page.wait_for_function("id => (__fixture.profils['test-membre'].rep[id] || {}).note10 === 9", arg=first)
        second = page.locator("#xpBody .xp-card").get_attribute("data-film")
        assert second != first
        page.locator('#xpBody [data-xp="pv"]').click()
        page.wait_for_function("id => (__fixture.profils['test-membre'].rep[id] || {}).etat === 'pas_vu'", arg=second)
        page.locator("#xpBody [data-xpundo]").click()
        page.wait_for_function("id => !__fixture.profils['test-membre'].rep[id]", arg=second)
        assert page.locator("#xpBody .xp-card").get_attribute("data-film") == second
        page.locator('#xpBody [data-xp="skip"]').click()
        for v in ["7", "4", "vu", "9", "7", "pv", "9", "4", "7"]:
            page.locator(f'#xpBody [data-xp="{v}"]').first.click()
        # Toutes les dix réponses : la récompense, avec l'affinité.
        page.locator("#xpBody .xp-reward").wait_for()
        assert "Toi et Camille (test)" in page.locator("#xpBody").inner_text(), page.locator("#xpBody").inner_text()
        assert "%" in page.locator("#xpBody .xp-big").inner_text()
        page.locator("#xpBody [data-xppeer]").first.click()

        # Profil d'un membre : affinité, adorés tous les deux, ses coups de cœur.
        body = page.locator("#msheetBody")
        body.locator(".aff").wait_for()
        txt = body.inner_text().lower()
        assert "d'affinité" in txt and "adorés tous les deux" in txt, txt[:300]

        # Soirée ciné : des films qu'aucun des deux n'a vus, avec une estimation pour chacun.
        page.locator('[data-ctab="soiree"]').click()
        page.locator("[data-soi]").first.click()
        films = page.locator("#msheetBody .soi-f")
        assert films.count() >= 5
        seen = page.evaluate("Object.keys(__fixture.profils).flatMap(u => Object.entries(__fixture.profils[u].rep).filter(([k, v]) => v.etat === 'vu').map(([k]) => k))")
        titles = [t.split("\n")[0] for t in films.all_inner_texts()]
        assert "Matrix" not in titles and "Shining" not in titles, titles
        assert "Toi" in films.first.inner_text() and "Camille (test)" in films.first.inner_text()

        # Invitation : un lien qui emporte une partie de mes notes.
        page.locator('[data-ctab="membres"]').click()
        page.locator("[data-invite]").click()
        page.wait_for_function("window.__shared && __shared.includes('#compare=')")
        link = page.evaluate("__shared").split("\n")[-1]
        page.locator("[data-ccclose]").first.click()

        # Import : Letterboxd (note sur 5 → sur 10) et IMDb ; les réponses déjà données sont gardées.
        page.locator("#ccMe").click()
        page.locator("[data-ccimport]").click()
        page.locator("#impFile").set_input_files(str(folder / "ratings.csv"))
        page.locator("#impPanel .imp-sum").wait_for()
        assert "1 film" in page.locator("#impPanel .imp-sum").inner_text()
        assert "1 pas dans le carnet" in page.locator("#impPanel").inner_text()
        page.locator("[data-impgo]").click()
        page.wait_for_function("(__fixture.profils['test-membre'].rep['cube-1997'] || {}).note10 === 9")
        page.locator("#ccMe").click()
        page.locator("[data-ccimport]").click()
        page.locator("#impFile").set_input_files(str(folder / "imdb.csv"))
        page.locator("[data-impgo]").click()
        page.wait_for_function("(__fixture.profils['test-membre'].rep['cure-1997'] || {}).note10 === 8")
        assert rep(page, "matrix-1999")["note10"] == 7.5

        # Statistiques : la précision de la boussole.
        page.locator('#toc [data-tile="carnet"]').click()
        page.locator("#toc .sub", has_text="statistiques").first.click()
        assert "précision de ta boussole" in page.locator("#main").inner_text()
        assert not errors and not unexpected, (errors, unexpected)
        context.close()

        # Le lien ouvert par quelqu'un d'autre : le mode express « Compare-toi à … », et l'affinité au bout de dix films.
        fixture = catalogue_fixture()
        fixture["profils"]["test-membre"].update(pseudo="Zoé (test)", rep={})
        context, page, errors, unexpected = open_page(browser, fixture=fixture, url=link)
        page.locator("#xp").wait_for(state="visible")
        assert page.locator("#xpTitle").inner_text() == "Compare-toi à Alix (test)"
        for _ in range(10):
            page.locator('#xpBody [data-xp="9"]').click()
        page.locator("#xpBody .xp-reward").wait_for()
        assert "Toi et Alix (test)" in page.locator("#xpBody").inner_text()
        assert not errors and not unexpected, (errors, unexpected)
        context.close()
        browser.close()
        print("Express, retour, récompense, affinité, films en commun, soirée ciné, invitation, import Letterboxd et IMDb, précision et console : OK", flush=True)


if __name__ == "__main__":
    run()
