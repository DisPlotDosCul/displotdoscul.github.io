"""Catégorie « Par réalisateurs » : régions, cinéastes d'au moins deux films, duos, films d'un cinéaste."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from cineclub_fixture import ROOT, catalogue_fixture, install_routes
from cineclub_interface import ready, errors_on


def run():
    captures = ROOT / "docs/captures/interface"
    captures.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None, args=["--no-sandbox"])
        for device, width, height in [("telephone", 360, 800), ("ordinateur", 1440, 960)]:
            context = browser.new_context(service_workers="block", viewport={"width": width, "height": height}, has_touch=device == "telephone")
            unexpected = install_routes(context, fixture=catalogue_fixture())
            page = context.new_page()
            errors = errors_on(page)
            ready(page)
            page.locator('[data-tile="realisateurs"]').click()
            regions = page.locator('#drill [data-sx^="real-"]')
            assert regions.count() >= 4, regions.count()
            page.locator('#drill [data-sx="real-france"]').click()
            chips = page.locator("#drill .sx-open .sx-c")
            names = chips.all_inner_texts()
            assert any(n.startswith("Quentin Dupieux") for n in names), names[:5]
            page.locator("#drill .sx-open .sx-c", has_text="Quentin Dupieux").click()
            page.wait_for_timeout(300)
            shown = page.evaluate("[...new Set([...document.querySelectorAll('#main .film')].map(x => x.dataset.id))].length")
            assert shown >= 10, shown
            page.screenshot(path=str(captures / f"realisateurs-{device}.png"))
            data = page.evaluate("""() => {
              const out = {};
              document.querySelectorAll('#drill [data-sx^="real-"]').forEach(b => out[b.dataset.sx] = b.innerText);
              return out; }""")
            assert "real-amerique-nord" in data and "real-asie" in data, data
            page.locator('#drill [data-sx="real-amerique-nord"]').click()
            us = page.locator("#drill .sx-open .sx-c").all_inner_texts()
            assert any(n.startswith("Joel et Ethan Coen") for n in us), "les frères Coen restent un duo"
            assert any(n.startswith("David Lynch") for n in us)
            assert not errors, errors
            assert not unexpected, unexpected
            context.close()
            print(device, ": régions, cinéastes, duos et films d'un cinéaste : OK")
        browser.close()


if __name__ == "__main__":
    run()
