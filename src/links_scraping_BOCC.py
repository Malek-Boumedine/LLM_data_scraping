from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import cloudscraper
import os
import json
import time
import random



os.makedirs("data", exist_ok=True)
base_url = "https://www.legifrance.gouv.fr"
url_tpl = "https://www.legifrance.gouv.fr/liste/bocc?intervalPublication=&idcc_suggest=&titre_suggest=&sortValue=BOCC_SORT_DESC&pageSize=100&page={}&tab_selection=all#bocc"

scraper = cloudscraper.create_scraper()

resp = scraper.get(url_tpl.format(1))
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_content(resp.text)
    pager = page.query_selector("div.container-pager nav ul li.pager-item:nth-last-child(2) span")
    total_pages = int(pager.inner_text().strip())
    print("nombre de pages :", total_pages)
    browser.close()

articles_data = []
total_articles = 0

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for n in range(1, total_pages + 1) :
    # for n in range(1, 2 + 1) : # pour les tests
        url = url_tpl.format(n)
        resp = scraper.get(url)
        page.set_content(resp.text)
        articles = page.query_selector_all("article.result-item.item-for-liste-idcc")
        print(f"Page {n} : {len(articles)} articles")
        for article in articles:
            titre = article.query_selector("h3.title-result-item a").inner_text().strip()
            article_link = urljoin(base_url, article.query_selector("a").get_attribute("href"))
            pdf_link_elem = article.query_selector("a.doc-download.doc-small.doc-small-bocc")
            if pdf_link_elem:
                pdf_link = urljoin(base_url, pdf_link_elem.get_attribute("href"))
            else:
                pdf_link = None
            # pdf_link = urljoin(base_url, pdf_link_elem.get_attribute("href"))
            
            articles_data.append({
                "titre": titre,
                "lien article": article_link,
                "lien PDF": pdf_link,
            })
            total_articles += 1
        time.sleep(random.uniform(2, 4))
        
    print(f"nombre d'articles total trouvés à la page {n} : {total_articles}")
    print("longueur de la liste articles_data : ", len(articles_data))
    browser.close()

# enregistrement dans un json
with open("data/scrapping/articles_links_BOCC.json", "w", encoding="utf-8") as output_file:
    json.dump(articles_data, output_file, indent=4, ensure_ascii=False)
