"""Idées du 10 et du 12 novembre : en-tête lisible, sous-catégories ouvertes sous la liste, santé mentale dans les thèmes,
compteurs, pied de page, autres façons de choisir, et avis de recherche dans la communauté."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import cineclub_fixture as cf

FIREBASE_JS = cf.FIREBASE_JS.replace("      doc:function(id){", "      add:function(v){ var d=this.doc(); return d.set(v).then(function(){ return d; }); },\n      doc:function(id){", 1)


def run():
    cf.FIREBASE_JS = FIREBASE_JS
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None, args=["--no-sandbox"])
        for width in (360, 1100):
            context = browser.new_context(service_workers="block", viewport={"width": width, "height": 800}, has_touch=width < 600, is_mobile=width < 600)
            unexpected = cf.install_routes(context)
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.goto("https://cineclub.test/carnet-de-films/", wait_until="networkidle")
            page.wait_for_function("window.CC && CC.me && CC.filmInfo && CC.filmInfo('matrix-1999')")
            if page.locator("#introX").is_visible():
                page.locator("#introX").click()

            # En-tête : « Réglages » à droite, plus de bouton soleil, « ← Retour » seulement après un changement d'affichage.
            aab, head = page.locator("#aab").bounding_box(), page.locator("header.top").bounding_box()
            assert "Réglages" in page.locator("#aab").inner_text() and aab["x"] > head["x"] + head["width"] / 2
            assert page.locator("#nuitb").is_hidden() and page.locator("#topBack").is_hidden()
            # Le compteur du haut garde seulement « répondus ».
            assert "répondus" in page.locator("#stats").inner_text() and "vus" not in page.locator("#stats").inner_text()

            # Santé mentale : plus de catégorie à part, une liste dans les thèmes avec une sous-catégorie par trouble.
            assert page.locator('[data-tile="sante"]').count() == 0
            page.locator('[data-tile="themes"]').click()
            page.locator('[data-sx="s54-sante-mentale"]').click()
            block = page.locator(".sx-open")
            assert block.locator("[data-sxl], [data-sxp]").count() >= 10, block.inner_text()
            assert page.locator("#topBack").is_visible(), "la flèche du haut n'apparaît pas"
            first = block.locator("[data-sxl]").first
            label = first.inner_text().split("\n")[0].rsplit(" ", 1)[0]
            first.click()
            page.wait_for_selector("#sec-s54-sante-mentale select[data-subp]")
            assert page.locator("#sec-s54-sante-mentale select[data-subp]").evaluate("s => s.options[s.selectedIndex].textContent").find(label.strip()) >= 0
            # Retour : on revient d'abord à l'affichage précédent, puis à l'accueil, sans quitter le site.
            page.locator("#topBack").click()
            page.wait_for_timeout(300)

            # Envies : chaque envie montre son nombre de films.
            page.evaluate("window.scrollTo(0, 0)")
            page.locator('[data-tile="envies"]').click()
            assert page.locator("#toc [data-e1] .sc").count() >= 5

            # Mon carnet : les vus, oubliés et notés sont là.
            page.locator('[data-tile="carnet"]').click()
            assert "oubli" in page.locator("#carnetSt").inner_text()

            # Autres façons de choisir : un seul bouton, chaque façon expliquée.
            cf.open_more(page)
            assert page.locator("#ccMore .ccm-d").count() == 4

            # Pied de page : partager le Ciné-club, écrire à l'équipe (la boîte à idées s'ouvre).
            assert page.locator("[data-shareapp]").is_visible()
            page.locator("[data-contact]").click()
            page.wait_for_selector("#toc form[data-idform] textarea")
            assert "message pour l'équipe" in page.locator("#toc form[data-idform]").inner_text()

            # Avis de recherche : depuis une recherche sans résultat, puis dans la communauté.
            page.evaluate("window.scrollTo(0, 0)")
            page.locator("#q").fill("zzzz film introuvable")
            page.locator("[data-avopen]").click()
            page.locator("#avTxt").fill("Une fille avec un groin de cochon, maudite par une sorcière, qui cherche l'amour")
            page.wait_for_function("document.querySelector('#avSugg') && document.querySelector('#avSugg').textContent.indexOf('Penelope') >= 0")
            page.locator("[data-avk='une série']").click()
            page.locator("[data-avsend]").click()
            page.wait_for_function("Object.values(__fixture.messages || {}).some(m => m.type === 'avis' && m.to === '*' && m.genre === 'une série')")
            assert "Votre avis de recherche" in page.locator("#msheetBody").inner_text()
            assert page.locator("[data-avdel]").count() == 1

            assert not errors and not unexpected, (errors, unexpected)
            print(f"{width} px : en-tête, retour, compteur, santé mentale dans les thèmes, sous-catégories, envies, carnet, autres façons, pied de page, avis de recherche et console : OK", flush=True)
            context.close()
        browser.close()


if __name__ == "__main__":
    run()
