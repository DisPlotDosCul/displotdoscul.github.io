"""Ciel : vrais gestes sur un catalogue public puis 370 films de test en plus."""
import copy
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from cineclub_fixture import ROOT, catalogue_fixture, install_routes


def public_count():
    """Catalogue public + films des compléments, sans doublon (le nombre grandit avec les ajouts)."""
    comp = json.loads((ROOT / "carnet-de-films/complements.json").read_text())
    docs = catalogue_fixture()["films"]
    ids = {film["id"] for doc in docs.values() for film in doc.get("films", [])}
    for sid, section in comp["sections"].items():
        # Les ajouts à une liste absente du jeu d'essai ne s'affichent pas, sauf nouvelle liste titrée.
        if sid in docs or section.get("titre"):
            ids.update(film["id"] for film in section.get("films", []))
    return len(ids)


def ready(page, count=None):
    count = public_count() if count is None else count
    page.goto("https://cineclub.test/carnet-de-films/", wait_until="networkidle")
    page.wait_for_function("window.CC && CC.me && CC.filmInfo && CC.filmInfo('matrix-1999')")
    if page.locator("#introX").is_visible():
        page.locator("#introX").click()
    page.locator("#intro").wait_for(state="hidden")
    page.locator("#skyToggle").click()
    page.wait_for_function("n => document.querySelector('#skyCanvas').dataset.count === String(n)", arg=count)
    page.wait_for_function("document.querySelector('#skyCanvas').dataset.renderMs")


def settled(page):
    page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")


def run():
    captures = ROOT / "docs/captures/ciel"
    captures.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None, args=["--no-sandbox"])
        for name, width, height in [("telephone", 360, 800), ("ordinateur", 1440, 960)]:
            context = browser.new_context(viewport={"width": width, "height": height}, has_touch=True)
            unexpected = install_routes(context)
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            ready(page)
            canvas = page.locator("#skyCanvas")
            layout = canvas.get_attribute("data-layout")
            for theme in ["jour", "neon"]:
                page.evaluate("t => AMBI.set(t)", theme)
                page.locator("#skyMember").select_option("test-autre")
                page.wait_for_function("document.querySelector('#skyCaption').textContent.includes('Camille')")
                page.screenshot(path=captures / f"{name}-{theme}.png", animations="disabled")
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")

            before = canvas.evaluate("c => c.toDataURL()")
            page.locator("#skyMember").select_option("")
            settled(page)
            assert canvas.evaluate("c => c.toDataURL()") != before, "La superposition doit dessiner des lumières"
            assert canvas.get_attribute("data-layout") == layout
            zoom = float(canvas.get_attribute("data-zoom"))
            page.locator("#skyIn").click()
            assert float(canvas.get_attribute("data-zoom")) > zoom
            page.locator("#skyReset").click()
            canvas.focus()
            before = canvas.evaluate("c => c.toDataURL()")
            page.keyboard.press("ArrowRight")
            settled(page)
            assert canvas.evaluate("c => c.toDataURL()") != before
            page.locator("#skyReset").click()
            if name == "telephone":
                cdp = context.new_cdp_session(page)
                cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": 100, "y": 360, "id": 1}, {"x": 250, "y": 360, "id": 2}]})
                cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": 70, "y": 360, "id": 1}, {"x": 280, "y": 360, "id": 2}]})
                cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
                settled(page)
                assert float(canvas.get_attribute("data-zoom")) > zoom
                page.locator("#skyReset").click()
            # Viser un point lumineux effectivement dessiné, sans accéder au modèle privé.
            settled(page)
            point = canvas.evaluate("""c => {const a=c.getContext('2d').getImageData(0,0,c.width,c.height);for(let y=205;y<c.height-100;y++)for(let x=20;x<c.width-20;x++){if(a.data[(y*c.width+x)*4+3]>180)return {x:x,y:y};}return null;}""")
            assert point, "Le ciel doit contenir des étoiles visibles"
            page.mouse.click(point["x"], point["y"])
            page.locator("#rsheet").wait_for(state="visible")
            assert page.locator("#rs-h").inner_text()
            page.locator("#rsClose").click()
            page.locator("#skySearch").fill("Matrix")
            page.locator("#skyResults button").first.click()
            assert page.locator("#rs-h").inner_text() == "Matrix"
            page.locator('#rsN [data-rstep="1"]').click()
            page.wait_for_function("__fixture.profils['test-membre'].rep['matrix-1999'].note10 === 7.6")
            assert canvas.get_attribute("data-layout") == layout, "Noter ne déplace aucune étoile"
            page.locator("#rsClose").click()
            page.keyboard.press("Escape")
            assert page.locator("#sky").is_hidden()
            page.locator("#aab").click()
            page.locator('[data-taille="grand"]').click()
            page.locator("#aab").click()
            page.locator("#skyToggle").click()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            assert round(canvas.bounding_box()["width"]) == width
            page.locator("#skyIn").focus()
            page.keyboard.press("Tab")
            assert canvas.evaluate("c => document.activeElement === c")
            page.keyboard.press("Escape")
            assert page.locator("#skyToggle").evaluate("b => document.activeElement === b")
            assert page.evaluate("__fixtureWrites.every(w => w.collection === 'profils' && w.id === 'test-membre')")
            assert not unexpected, unexpected
            assert not errors, errors
            print(f"{name} : vues, superposition, zoom, gestes, fiche, note, stabilité et console : OK", flush=True)
            context.close()

        fixture = catalogue_fixture()
        source = fixture["films"]["s01-test"]["films"]
        originals = copy.deepcopy(source[:370])
        for i, film in enumerate(originals):
            fid = f"ciel-test-{i}"
            original = film["id"]
            film.update(id=fid, t=f"Étoile de test {i}")
            source.append(film)
            for document in fixture["films"].values():
                if original in document.get("fiches", {}):
                    fiche = copy.deepcopy(document["fiches"][original])
                    break
            fixture["films"]["fiches-6"]["fiches"][fid] = fiche
        fixture["profils"]["test-membre"]["rep"] = {film["id"]: {"etat": "vu", "note10": 8} for film in source}
        context = browser.new_context(viewport={"width": 1440, "height": 960})
        unexpected = install_routes(context, fixture=fixture)
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        total = public_count() + len(originals)
        ready(page, total)
        durations = []
        for _ in range(12):
            page.locator("#skyIn").click()
            settled(page)
            durations.append(float(page.locator("#skyCanvas").get_attribute("data-render-ms")))
        assert max(durations) < 80, durations
        assert not errors and not unexpected, (errors, unexpected)
        report = {"films": total, "rendu_ms_max": max(durations), "rendu_ms_moyen": sum(durations) / len(durations)}
        (captures / "mesures.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(report, ensure_ascii=False), flush=True)
        context.close()
        browser.close()


if __name__ == "__main__":
    run()
