"""Vérification des fiches et captures ; dépend seulement de Playwright pour les essais."""
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from cineclub_fixture import ROOT, catalogue_fixture, install_routes

CAPTURES = ROOT / "docs/captures/fiches"


def validate_data():
    comp = json.loads((ROOT / "carnet-de-films/complements.json").read_text())
    fixture = catalogue_fixture()
    ids = set()
    for doc in fixture["films"].values():
        ids.update(film["id"] for film in doc.get("films", []))
    for section in comp["sections"].values():
        ids.update(film["id"] for film in section.get("films", []))
    assert ids <= comp["fiches"].keys(), "Des films n'ont pas de complément"
    allowed = {"violence explicite", "violence sexuelle", "suicide", "automutilation",
               "maltraitance", "drogue", "images choquantes"}
    for fid in ids:
        fiche = comp["fiches"][fid]
        assert isinstance(fiche["duree"], int) and 0 < fiche["duree"] < 1000, fid
        assert isinstance(fiche["av"], list) and set(fiche["av"]) <= allowed, fid
        assert 3 <= len(fiche["th"]) <= 5, fid
        assert len(set(fiche["th"])) == len(fiche["th"]), fid
        assert all(1 <= len(theme.split()) <= 2 for theme in fiche["th"]), fid
    with tempfile.TemporaryDirectory() as folder:
        source = (ROOT / "carnet-de-films/index.html").read_text()
        for number, script in enumerate(re.findall(r"<script\b[^>]*>([\s\S]*?)</script>", source)):
            if script.strip():
                path = Path(folder) / f"script-{number}.js"
                path.write_text(script)
                subprocess.run(["node", "--check", str(path)], check=True)
    print(f"Données et syntaxe : {len(ids)} films, OK", flush=True)
    return comp


def ready(page):
    page.goto("https://cineclub.test/carnet-de-films/", wait_until="networkidle")
    page.wait_for_function("window.CC && CC.me && CC.filmInfo && CC.filmInfo('a-history-of-violence-2005')")
    if page.locator("#introX").is_visible():
        page.locator("#introX").click()
    page.locator("#intro").wait_for(state="hidden")


def search(page, title):
    page.locator("#q").fill(title)
    page.wait_for_function("title => document.querySelector('#main .s-head h2')?.textContent === 'Recherche : « ' + title + ' »'", arg=title)
    row = page.locator("#main .film:not(.lz)").first
    row.wait_for()
    return row


def assert_no_overflow(page):
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Débordement horizontal"


def browser_checks():
    from playwright.sync_api import sync_playwright

    CAPTURES.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        executable = os.environ.get("CINECLUB_CHROMIUM")
        if executable is None and Path("/usr/bin/chromium").exists():
            executable = "/usr/bin/chromium"
        browser = pw.chromium.launch(executable_path=executable, args=["--no-sandbox"])
        for device, width, height in [("telephone", 360, 800), ("ordinateur", 1440, 960)]:
            context = browser.new_context(viewport={"width": width, "height": height}, has_touch=device == "telephone", device_scale_factor=1)
            unexpected = install_routes(context)
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
            ready(page)
            for theme in ["jour", "neon"]:
                page.evaluate("theme => AMBI.set(theme)", theme)
                row = search(page, "A History of Violence")
                assert row.get_attribute("data-id") == "a-history-of-violence-2005"
                assert "96 minutes" in row.locator(".m").inner_text()
                assert row.locator(".xtra").is_hidden()
                page.locator("#q").blur()
                page.screenshot(path=CAPTURES / f"{device}-{theme}.png", full_page=True, animations="disabled")
                row.locator(".more").click()
                assert row.locator(".xtra").is_visible()
                assert "identité" in row.locator(".fiche-themes").inner_text()
                row.locator(".fiche-av summary").click()
                assert "violence sexuelle" in row.locator(".fiche-av p").inner_text()
                assert_no_overflow(page)
                page.screenshot(path=CAPTURES / f"{device}-{theme}-details.png", full_page=True, animations="disabled")
                row.locator(".more").click()

            # Une valeur vide dans Firebase doit aussi prendre la priorité.
            row = search(page, "1917")
            page.wait_for_function("document.querySelector('#main .film:not(.lz) .t')?.textContent === '1917'")
            row = page.locator('#main .film[data-id="1917-2019"]')
            assert "121 minutes" in row.locator(".m").inner_text()
            assert row.locator(".fiche-av").count() == 0
            row.locator(".more").click()
            assert row.locator(".fiche-themes").count() == 0
            assert row.locator(".fiche-fiab").count() == 0

            # Les notes s'enregistrent uniquement dans le profil fictif.
            row = search(page, "A History of Violence")
            page.wait_for_function("document.querySelector('#main .film:not(.lz) .t')?.textContent === 'A History of Violence'")
            row.locator('[data-a="vu"]').click()
            row = page.locator('#main .film[data-id="a-history-of-violence-2005"]')
            row.locator('[data-n="9"]').click()
            page.wait_for_function("__fixture.profils['test-membre'].rep['a-history-of-violence-2005'].note10 === 9")
            assert page.evaluate("__fixtureWrites.every(w => w.collection === 'profils' && w.id === 'test-membre')")
            assert_no_overflow(page)

            # Le questionnaire garde le nom validé et les réglages d'accessibilité fonctionnent.
            page.locator("#ccQuiz").click()
            assert "Boussole cinéma" in page.locator("#qzPanel").inner_text()
            page.locator("[data-qzclose]").click()
            page.locator("#aab").click()
            page.locator('[data-taille="grand"]').click()
            assert_no_overflow(page)
            page.locator('[data-taille=""]').click()
            page.locator("#aab").click()
            assert not unexpected, unexpected
            assert not errors, errors
            print(f"{device} : jour, néon, note, priorité Firebase, Grand confort, console : OK", flush=True)
            context.close()
        browser.close()


if __name__ == "__main__":
    validate_data()
    if "--donnees-seules" not in __import__("sys").argv:
        browser_checks()
