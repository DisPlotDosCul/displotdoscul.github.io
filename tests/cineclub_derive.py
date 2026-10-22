"""Parcours, conservation et partage sans service réel."""
import base64
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from cineclub_fixture import ROOT, install_routes


def ready(page, url="https://cineclub.test/carnet-de-films/"):
    page.goto(url, wait_until="networkidle")
    page.wait_for_function("window.CC && CC.me && CC.filmInfo && CC.filmInfo('matrix-1999')")
    if page.locator("#introX").is_visible():
        page.locator("#introX").click()
    page.locator("#intro").wait_for(state="hidden")


def context_for(browser, width, height):
    context = browser.new_context(viewport={"width": width, "height": height}, has_touch=width < 600)
    unexpected = install_routes(context)
    context.add_init_script("Object.defineProperty(navigator,'share',{value:undefined,configurable:true});Object.defineProperty(navigator,'clipboard',{value:{writeText:async text=>{window.__shared=text;}},configurable:true});")
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    return context, page, errors, unexpected


def run():
    captures = ROOT / "docs/captures/derive"
    captures.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None, args=["--no-sandbox"])
        for name, width, height in [("telephone", 360, 800), ("ordinateur", 1440, 960)]:
            context, page, errors, unexpected = context_for(browser, width, height)
            ready(page)
            page.locator("#drToggle").click()
            page.locator("[data-drstart]").first.click()
            first = page.locator(".dr-film").get_attribute("data-film")
            choices = page.locator("[data-drpath]").evaluate_all("buttons=>buttons.map(b=>b.dataset.next)")
            assert len(choices) == len(set(choices)) == 3 and first not in choices
            reasons = page.locator(".dr-paths .dr-why").all_inner_texts()
            assert len(reasons) == 3 and all(r.strip() for r in reasons), reasons
            for path in ["auteur", "theme", "ailleurs"]:
                page.locator(f'[data-drpath="{path}"]').click()
            assert page.locator(".dr-chain li").count() == 4
            page.locator("[data-drundo]").click()
            assert page.locator(".dr-chain li").count() == 3
            name_value = "Rêve d’été — à l’envers 🌙"
            page.locator("#drName").fill(name_value)
            page.locator("[data-drsave]").click()
            assert "gardé" in page.locator("#drStatus").inner_text()
            for theme in ["jour", "neon"]:
                page.evaluate("t=>AMBI.set(t)", theme)
                page.screenshot(path=captures / f"{name}-{theme}.png", animations="disabled", full_page=True)
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.locator(".dr-film [data-drfilm]").click()
            page.locator("#rsheet").wait_for(state="visible")
            page.locator("#rsClose").click()
            page.locator("[data-drshare]").click()
            page.wait_for_function("window.__shared && __shared.includes('#derive=')")
            url = page.evaluate("__shared")
            encoded = url.split("#derive=", 1)[1]
            payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
            assert payload["n"] == name_value and len(payload["ids"]) == 3
            assert len(set(payload["ids"])) == 3
            assert set(payload) == {"v", "n", "seed", "ids", "by", "w"}
            assert "test-membre" not in url and "note10" not in json.dumps(payload)

            page.reload(wait_until="networkidle")
            if page.locator("#introX").is_visible():
                page.locator("#introX").click()
            page.locator("#intro").wait_for(state="hidden")
            page.locator("#drToggle").click()
            page.locator("[data-drarchive]").click()
            page.locator('[data-drread="0"]').click()
            assert page.locator("#drBody h3").inner_text() == name_value
            assert page.locator(".dr-steps li").count() == 3
            page.locator("[data-drback]").click()
            page.locator("[data-drnew]").click()
            page.locator("#drFind").fill("Shin")
            page.locator("#drFound [data-drstart]").first.click()
            page.locator(".dr-film").wait_for()
            assert not page.locator(".dr-film").get_attribute("data-film") is None
            page.locator("#drClose").click()
            page.locator("#aab").click()
            page.locator('[data-taille="grand"]').click()
            page.locator("#aab").click()
            page.locator("#drToggle").click()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.keyboard.press("Escape")
            assert page.locator("#drift").is_hidden()
            assert page.evaluate("__fixtureWrites.length === 0")
            assert not errors and not unexpected, (errors, unexpected)

            received_context, received, received_errors, received_requests = context_for(browser, width, height)
            ready(received, url)
            received.locator(".dr-film").wait_for()
            assert received.locator("#drName").input_value() == name_value
            assert received.locator(".dr-chain li").count() == 3
            assert received.evaluate("localStorage.getItem('ccDerivesV1-test-membre')") is None
            received.locator("#drName").fill('<img src=x onerror="window.__xss=true">')
            received.locator("[data-drsave]").click()
            received.locator("[data-drarchive]").click()
            received.locator('[data-drread="0"]').click()
            assert received.locator("#drBody img").count() == 0
            assert not received.evaluate("window.__xss || false")
            received.evaluate("location.hash='derive=pas-un-reve'")
            received.wait_for_function("document.querySelector('#drStatus').textContent.includes('incomplet')")
            assert received.evaluate("__fixtureWrites.length === 0")
            assert not received_errors and not received_requests, (received_errors, received_requests)
            print(f"{name} : départ d'un film, trois liens expliqués, retour, carnet, reprise, partage privé, lien invalide, Grand confort et console : OK", flush=True)
            context.close()
            received_context.close()
        browser.close()


if __name__ == "__main__":
    run()
