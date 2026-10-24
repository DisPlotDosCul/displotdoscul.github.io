"""Retouches d'interface : téléphone, ordinateur et écritures uniquement fictives."""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from cineclub_fixture import ROOT, catalogue_fixture, install_routes


def ready(page):
    page.goto("https://cineclub.test/carnet-de-films/", wait_until="networkidle")
    page.wait_for_function("window.CC && CC.me && CC.filmInfo && CC.filmInfo('matrix-1999')")
    if page.locator("#introX").is_visible():
        box = page.locator("#introX").bounding_box()
        assert box["y"] + box["height"] <= page.viewport_size["height"] - 43
        page.locator("#introX").click()
    page.locator("#intro").wait_for(state="hidden")


def errors_on(page):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    return errors


def open_list(page, sid):
    target = page.locator(f'#toc [data-s="{sid}"]')
    if not target.is_visible():
        page.locator('[data-tile="carnet"]').click()
    target.click()


def run():
    captures = ROOT / "docs/captures/interface"
    captures.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None, args=["--no-sandbox"])
        for device, width, height in [("telephone", 360, 800), ("ordinateur", 1440, 960)]:
            fixture = catalogue_fixture()
            entries = fixture["films"]["s01-test"]["films"][:25]
            fixture["profils"]["test-membre"]["rep"] = {
                film["id"]: {"etat": "vu", "note10": 9 - i / 10}
                for i, film in enumerate(entries)
            }
            context = browser.new_context(viewport={"width": width, "height": height}, has_touch=device == "telephone")
            unexpected = install_routes(context, fixture=fixture)
            page = context.new_page()
            errors = errors_on(page)
            ready(page)
            assert page.evaluate("CC.auth.languageCode") == "fr"
            assert page.locator('label[for="q"]').is_hidden(), "l'aide au-dessus de la recherche est retirée"
            assert page.locator(".nbulbs i").count() == 8
            assert page.locator(".nbulbs .dead").count() == 1
            assert page.locator("#ccRanger").is_hidden(), "Le rangement reste réservé à l'administratrice"
            if device == "telephone":
                # Deux rangées compactes : Communauté et Mon compte, puis Boussole, Dérive et Ciel ; chaque libellé tient sur une ligne.
                account = [page.locator(f"#{bid}").bounding_box() for bid in ("ccMbr", "ccMe")]
                assert len({round(box["y"]) for box in account}) == 1, account
                exploration = [page.locator(f"#{bid}").bounding_box() for bid in ("ccQuiz", "skyToggle", "drToggle")]
                assert len({round(box["y"]) for box in exploration}) == 1, exploration
                assert exploration[0]["y"] > account[0]["y"]
                assert all(box["height"] >= 40 and box["width"] >= 44 for box in account + exploration)
                assert page.evaluate("['ccMbr','ccMe','ccQuiz','skyToggle','drToggle'].every(id => { const b = document.getElementById(id); return b.scrollWidth <= b.clientWidth + 1; })"), "un libellé est coupé"
            for theme in ("jour", "neon"):
                page.evaluate("theme => AMBI.set(theme)", theme)
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                if theme == "neon":
                    title = page.locator("h1")
                    assert title.evaluate("h => getComputedStyle(h).borderTopWidth") == "0px"
                    assert title.evaluate("h => getComputedStyle(h,'::after').content") == "none"
                    assert title.evaluate("h => getComputedStyle(h).textShadow") != "none"
                    assert page.locator(".nl").count() == 9
                page.screenshot(path=captures / f"{device}-{theme}.png", animations="disabled")

            # Le classement et le message contiennent vingt titres.
            open_list(page, "s18-mes-statistiques")
            page.wait_for_function("document.querySelectorAll('.st-top > li').length === 20")
            page.locator("[data-sharetop]").click()
            assert page.locator("#ssheet-h").inner_text() == "Partager ton top 20"
            assert len(re.findall(r"^\d+\. ", page.locator("#shTxt").input_value(), re.M)) == 20
            page.locator("#shClose").click()
            order = page.locator('.st-top [data-tstep="1"]').evaluate_all("bs => bs.map(b => b.dataset.tid)")
            # Le deuxième film dépasse le premier sans bouger sous le doigt,
            # même une fois les écritures différées et le rafraîchissement terminés.
            for _ in range(3):
                page.locator('.st-top [data-tstep="1"]').nth(1).click()
            page.wait_for_function("id => __fixture.profils['test-membre'].rep[id].note10 === 9.2", arg=order[1])
            page.wait_for_function("__fixtureWrites.some(w => w.collection === 'profils')")
            page.wait_for_timeout(3400)
            assert page.locator('.st-top [data-tstep="1"]').evaluate_all("bs => bs.map(b => b.dataset.tid)") == order
            open_list(page, "s16-classement")
            page.wait_for_function("document.querySelector('#sec-s16-classement')")
            open_list(page, "s18-mes-statistiques")
            page.wait_for_function("document.querySelectorAll('.st-top > li').length === 20")
            assert page.locator('.st-top [data-tstep="1"]').first.get_attribute("data-tid") == order[1], page.locator('.st-top [data-tstep="1"]').evaluate_all("bs => bs.map(b => [b.dataset.tid, __fixture.profils['test-membre'].rep[b.dataset.tid].note10])")
            for theme in ("jour", "neon"):
                page.evaluate("theme => AMBI.set(theme)", theme)
                page.locator(".st-b").filter(has=page.locator(".st-top")).screenshot(path=captures / f"{device}-{theme}-top20.png", animations="disabled")

            # Retrouver l'éditeur et enregistrer un ordre dans le seul faux Firebase.
            page.evaluate("CC.admin=true")
            page.locator("#aab").click()
            page.locator("#ccRanger").wait_for(state="visible")
            page.locator("#ccRanger").click()
            families = page.locator('.rg [data-rgf][data-dir="1"]').evaluate_all("bs => bs.map(b => b.dataset.rgf)")
            page.locator('.rg [data-rgf][data-dir="1"]').first.click()
            page.wait_for_function("__fixtureWrites.some(w => w.collection==='films' && w.id==='rangement')")
            saved = page.evaluate("__fixture.films.rangement.familles")
            assert saved[:2] == [families[1], families[0]]
            lists = page.locator('.rg [data-rgs][data-dir="1"]').evaluate_all("bs => bs.map(b => b.dataset.rgs)")
            assert len(lists) >= 2
            page.locator('.rg [data-rgs][data-dir="1"]').first.click()
            page.wait_for_function("__fixture.films.rangement.listes?.carnet?.length > 0")
            assert page.evaluate("__fixture.films.rangement.listes.carnet.slice(0,2)") == [lists[1], lists[0]]
            page.locator("[data-rgdone]").click()
            page.locator("#aab").click()
            page.locator('[data-taille="grand"]').click()
            page.locator("#aab").click()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            assert page.evaluate("__fixtureWrites.every(w => (w.collection==='profils' && w.id==='test-membre') || (w.collection==='films' && w.id==='rangement'))")
            assert not errors and not unexpected, (errors, unexpected)
            print(f"{device} : boutons, néon, top 20 et partage, ordre stable, rangement fictif et console : OK", flush=True)
            context.close()

        # Le clin d'œil est isolé et s'efface dès qu'on interagit ou choisit Calme.
        context = browser.new_context(viewport={"width": 360, "height": 800})
        unexpected = install_routes(context)
        page = context.new_page()
        errors = errors_on(page)
        page.clock.install()
        ready(page)
        page.clock.fast_forward(9000)
        assert page.locator("button.cc-wink").count() == 1
        assert page.locator("h1.cc-wink").count() == 0
        page.locator("#aab").click()
        assert page.locator(".cc-wink").count() == 0
        page.locator('[data-opt="calme"]').click()
        page.locator("#aab").click()
        page.clock.fast_forward(40000)
        assert page.locator(".cc-wink").count() == 0
        page.locator("#aab").click()
        page.locator('[data-opt="calme"]').click()
        page.locator('[data-taille="grand"]').click()
        page.locator("#aab").click()
        page.clock.fast_forward(40000)
        assert page.locator(".cc-wink").count() == 0
        page.locator("#aab").click()
        page.locator('[data-taille=""]').click()
        page.locator("#aab").click()
        page.emulate_media(reduced_motion="reduce")
        page.clock.fast_forward(40000)
        assert page.locator(".cc-wink").count() == 0
        assert not errors and not unexpected, (errors, unexpected)
        context.close()
        # La fiche d'un autre carnet nomme la bonne personne et reste en lecture.
        context = browser.new_context(viewport={"width": 360, "height": 800})
        unexpected = install_routes(context)
        context.add_init_script("sessionStorage.setItem('ccView','test-autre');sessionStorage.setItem('ccViewName','Camille (test)');")
        page = context.new_page()
        errors = errors_on(page)
        ready(page)
        page.locator("#skyToggle").click()
        page.locator("#skySearch").fill("Shining")
        page.locator("#skyResults button").first.click()
        page.wait_for_function("document.querySelector('#skyCanvas').dataset.focus === 'shining-1980'")
        page.locator("#skyPick").click()
        assert "par Camille (test)" in page.locator("#rsM").inner_text()
        page.locator("#rsClose").click()
        page.keyboard.press("Escape")
        assert page.locator("#ccRanger").is_hidden()
        assert page.evaluate("__fixtureWrites.length") == 0
        assert not errors and not unexpected, (errors, unexpected)
        context.close()
        browser.close()
        print("Clin d'œil : une commande, arrêt à l'interaction, Calme, Grand confort et réduction des animations : OK", flush=True)


if __name__ == "__main__":
    run()
