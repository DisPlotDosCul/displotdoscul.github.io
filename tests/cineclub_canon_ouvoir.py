"""Canon des artistes (page à part, liens vers les fiches) et « Où le voir » (plateformes via TMDB fictif)."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from cineclub_fixture import ROOT, catalogue_fixture, install_routes
from cineclub_interface import ready, errors_on

PROVIDERS = {"results": {"FR": {"link": "https://www.themoviedb.org/movie/1018/watch?locale=FR",
    "flatrate": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/n.png", "display_priority": 1}],
    "rent": [{"provider_id": 2, "provider_name": "Apple TV", "logo_path": "/a.png", "display_priority": 2}]}}}


def tmdb(route):
    url = route.request.url
    if "/watch/providers" in url:
        route.fulfill(content_type="application/json", body=json.dumps(PROVIDERS))
    elif "/search/" in url:
        route.fulfill(content_type="application/json", body=json.dumps({"results": [{"id": 1018, "title": "Mulholland Drive", "release_date": "2001-05-16", "vote_count": 9000}]}))
    elif "image.tmdb.org" in url:
        route.fulfill(content_type="image/png", body=b"")
    else:
        route.fulfill(content_type="application/json", body=json.dumps({"id": 1018, "credits": {"crew": [{"job": "Director", "name": "David Lynch"}]}, "images": {}}))


def run():
    captures = ROOT / "docs/captures/interface"
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None, args=["--no-sandbox"])
        context = browser.new_context(service_workers="block", viewport={"width": 390, "height": 860}, has_touch=True)
        unexpected = install_routes(context, fixture=catalogue_fixture())
        context.route("**/api.themoviedb.org/**", tmdb)
        context.route("**/image.tmdb.org/**", tmdb)
        page = context.new_page()
        errors = errors_on(page)
        # Canon des artistes : les quatre classements, et un lien « Fiche » quand le film est au catalogue.
        page.goto("https://cineclub.test/carnet-de-films/canon.html", wait_until="networkidle")
        page.wait_for_selector("#list li")
        assert page.locator("#list li").count() == 100
        page.wait_for_function("document.querySelector('a.c-cc[href*=\"mulholland-drive-2001\"]')")
        page.locator("#onlycc").check()
        n = page.locator("#list li").count()
        assert 10 < n < 100, n
        page.screenshot(path=str(captures / "canon-telephone.png"))
        page.locator('.tab[data-v="auteurs"]').click()
        assert page.locator(".group h3", has_text="David Lynch").count() == 1
        # La fiche s'ouvre dans le Ciné-club.
        page.goto("https://cineclub.test/carnet-de-films/#film=mulholland-drive-2001", wait_until="networkidle")
        page.wait_for_function("window.CC && CC.filmInfo && CC.filmInfo('mulholland-drive-2001')")
        page.locator("#rsheet").wait_for(state="visible")
        assert page.locator("#rs-h").inner_text() == "Mulholland Drive"
        assert "Canon" in page.locator("#rsK").inner_text()
        # Où le voir : abonnement et location, avec la source.
        page.locator('#rsOuv [data-ouv="mulholland-drive-2001"]').click()
        page.wait_for_selector("#rsOuv .ouv-p")
        txt = page.locator("#rsOuv .ouv").inner_text()
        assert "Abonnement" in txt and "Netflix" in txt and "Location" in txt and "JustWatch" in txt, txt
        page.screenshot(path=str(captures / "ou-le-voir-telephone.png"))
        # Le lien « Autres façons de choisir » mène au Canon.
        page.locator("#rsClose").click()
        page.locator("#ccMoreB").click()
        assert page.locator("#ccCanon").is_visible()
        assert not errors, errors
        assert not unexpected, unexpected
        print("Canon des artistes, lien vers la fiche et « Où le voir » : OK")
        browser.close()


if __name__ == "__main__":
    run()
