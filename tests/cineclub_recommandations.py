"""Programmation personnelle, sans affichage de score ni dépendance aux avis d'autrui."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from cineclub_fixture import ROOT, catalogue_fixture, install_routes


def ready(page):
    page.goto("https://cineclub.test/carnet-de-films/#s00-pour-toi", wait_until="networkidle")
    page.wait_for_function("window.CC && CC.me && CC.filmInfo && CC.filmInfo('matrix-1999')")
    if page.locator("#introX").is_visible():
        page.locator("#introX").click()
    page.locator("#intro").wait_for(state="hidden")
    page.locator('#sec-s00-pour-toi[data-auto="rimes"]').wait_for()


def ids(page):
    return page.locator(".rime-card").evaluate_all("cards=>cards.map(c=>c.dataset.rimeCandidate)")


def run():
    captures = ROOT / "docs/captures/recommandations"
    captures.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None, args=["--no-sandbox"])
        for name, width, height in [("telephone", 360, 800), ("ordinateur", 1440, 960)]:
            context = browser.new_context(viewport={"width": width, "height": height}, has_touch=width < 600)
            unexpected = install_routes(context)
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            ready(page)
            assert page.locator(".rime-card").count() == 3
            initial = ids(page)
            assert len(set(initial)) == 3
            assert page.locator(".rime-card .estp").count() == 0
            assert "Aimé par" not in page.locator("#sec-s00-pour-toi").inner_text()
            assert all(len(text) > 20 and "/10" not in text and "%" not in text for text in page.locator(".rime-phrase").all_inner_texts())
            seen = page.evaluate("Object.keys(__fixture.profils['test-membre'].rep).filter(id=>__fixture.profils['test-membre'].rep[id].etat==='vu')")
            assert not set(initial) & set(seen)
            for theme in ["jour", "neon"]:
                page.evaluate("t=>AMBI.set(t)", theme)
                page.screenshot(path=captures / f"{name}-{theme}.png", animations="disabled", full_page=True)
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")

            page.locator(".rime-card .rime-open").first.click()
            page.locator('#rsSeg [data-ra="vu"]').click()
            page.locator('#rsN [data-rn="9"]').click()
            page.wait_for_function("id=>__fixture.profils['test-membre'].rep[id]?.note10===9", arg=initial[0])
            page.locator("#rsClose").click()
            assert ids(page) == initial, "Noter ne doit pas déplacer les suggestions"
            page.locator("[data-rimeagain]").click()
            assert initial[0] not in ids(page)
            assert ids(page) != initial
            details = page.locator(".rime-tools details")
            details.locator("summary").click()
            page.locator('[data-rimeform] input').fill("Matrix")
            page.locator('[data-rimeform] button').click()
            assert page.locator('.rime-card[data-rime-anchor="matrix-1999"]').count() == 3
            assert "matrix-1999" not in ids(page)
            assert page.evaluate("__fixtureWrites.every(w=>w.collection==='profils'&&w.id==='test-membre')")
            page.locator("#aab").click()
            page.locator('[data-taille="grand"]').click()
            page.locator("#aab").click()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            assert not errors and not unexpected, (errors, unexpected)
            print(f"{name} : trois rimes, phrases, fiche, stabilité après note, autre séance, choix manuel, Grand confort et console : OK", flush=True)
            context.close()

        fixture = catalogue_fixture()
        fixture["profils"]["test-membre"]["rep"] = {}
        fixture["profils"].pop("test-autre")
        orphan = "ancienne-suggestion-seule-test"
        fixture["films"]["s00-pour-toi"]["films"] = [{"id": orphan, "t": "Un film gardé au catalogue", "y": 1990, "d": "Cinéaste de test", "r": ""}]
        fixture["films"]["fiches-6"]["fiches"][orphan] = {"p": "Résumé public fictif.", "k": ["enfance"], "c": "Pays de test", "mv": "courant-test"}
        context = browser.new_context(viewport={"width": 360, "height": 800})
        unexpected = install_routes(context, fixture=fixture)
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        ready(page)
        assert not ids(page)
        page.locator('[data-rimeform] input').fill("Matrix")
        page.locator('[data-rimeform] button').click()
        assert page.locator(".rime-card").count() == 3
        assert page.locator(".rime-card .estp").count() == 0
        target = ids(page)[0]
        page.locator(".rime-open").first.click()
        page.keyboard.press("Escape")
        assert page.locator("#rsheet").is_hidden()
        page.locator(".rime-open").first.click()
        page.locator("#rsGo").click()
        page.locator(f'#main .film[data-id="{target}"]').first.wait_for()
        page.locator("#q").fill("Un film gardé au catalogue")
        page.locator(f'#main .film[data-id="{orphan}"]').wait_for()
        assert page.evaluate("__fixtureWrites.length === 0")
        assert not errors and not unexpected, (errors, unexpected)
        print("Sans notes ni avis d'autres membres : choix manuel, trois rimes et accès à la fiche : OK", flush=True)
        context.close()
        browser.close()


if __name__ == "__main__":
    run()
