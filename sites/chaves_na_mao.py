import csv
import time
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

CSV_URLS = "data/imoveis_links.csv"
CSV_DETALHES = "data/imoveis_detalhes.csv"

BASE_URL = "https://www.chavesnamao.com.br"
URL_TEMPLATE = "https://www.chavesnamao.com.br/imoveis/pi-teresina/?pg={}"

def coletar_links():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        todas_urls = set()
        pagina = 1
        sem_novos = 0

        while True:
            url = URL_TEMPLATE.format(pagina)
            print(f"🌐 Página {pagina}")
            try:
                page.goto(url, timeout=15000)
                page.wait_for_selector('div[data-template="card"]', timeout=10000)
            except:
                pagina += 1
                continue

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

            cards = page.locator('div[data-template="card"]')
            novos = set()
            for i in range(cards.count()):
                a_tags = cards.nth(i).locator('a:has(span.card-module__cvK-Xa__cardContent)')
                for j in range(a_tags.count()):
                    href = a_tags.nth(j).get_attribute("href")
                    if href:
                        full_url = BASE_URL + href if href.startswith("/") else href
                        if full_url not in todas_urls:
                            novos.add(full_url)

            if not novos:
                sem_novos += 1
                if sem_novos >= 3:
                    break
            else:
                sem_novos = 0
                todas_urls.update(novos)

            pagina += 1

        browser.close()

        with open(CSV_URLS, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Link"])
            for url in sorted(todas_urls):
                writer.writerow([url])

        print(f"✅ {len(todas_urls)} URLs salvas em {CSV_URLS}")


def extrair_detalhes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        with open(CSV_URLS, "r", encoding="utf-8-sig") as f:
            urls = [row[0] for row in csv.reader(f)][1:]

        dados = []
        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] {url}")
            try:
                page.goto(url, timeout=15000)
                page.wait_for_timeout(2000)

                preco = page.locator("table b").first.inner_text()
                endereco = page.locator("address h2 b").first.inner_text()
                area = page.locator("li:has(p[aria-label='area']) b").first.inner_text()
                try:
                    caminho = urlparse(url).path
                    slug = caminho.split("/")[2]  # /imovel/<slug>/id-xxxxx
                    tipo = slug.split("-")[0]
                    if tipo == 'sala':
                        tipo = slug.split("-")[0], '-', slug.split("-")[1]
                except:
                    tipo = "-"

                dados.append([url, preco, endereco, tipo, area])
            except:
                dados.append([url, "-", "-", "-", "-"])

        browser.close()

        with open(CSV_DETALHES, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Link", "Preco", "Endereco", "Tipo", "Area"])
            writer.writerows(dados)

        print(f"✅ {len(dados)} registros salvos em {CSV_DETALHES}")
