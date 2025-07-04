from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import json



with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    
    base_url = "https://www.legifrance.gouv.fr"
    url = "https://www.legifrance.gouv.fr/liste/idcc?idcc_suggest=&titre_suggest=&facetteEtat=VIGUEUR&facetteEtat=VIGUEUR_ETEN&facetteEtat=VIGUEUR_NON_ETEN&sortValue=DATE_UPDATE&pageSize=50&page={page_number}&tab_selection=all#idcc"
    page.goto(url.format(page_number=1))
    
    total_pages_text = page.query_selector("div.container-pager nav ul li.pager-item:nth-child(5) span").inner_text().strip()
    total_pages = int(total_pages_text)
    print("nombre de pages : ", total_pages, type(total_pages))
    
    total_articles = 0
    articles_data = []    
    
    for n in range(1, total_pages+1) : 
    # for n in range(1,1+1) :   # pour les tests
        page_link = url.format(page_number = str(n))
        articles = page.query_selector_all('article.result-item.item-for-liste-idcc')
        for article in articles : 
            titre = article.query_selector("a").inner_text().strip()
            article_link = urljoin(base_url, article.query_selector("a").get_attribute("href"))
            
            pdf_link = article.query_selector("div.picto-download.picto-downloadCenter a")
            if pdf_link : 
                pdf_exists = True
                pdf_link = urljoin(base_url, pdf_link.get_attribute("href"))
                idcc_selector = article.query_selector('div.code-title-convention-container div.h4.code-title-convention') 
                idcc = idcc_selector.inner_text().strip() if idcc_selector else None
            else :
                idcc_selector = article.query_selector('div.code-title-convention-container.code-title-convention-containerAlign div.h4.code-title-convention') 
                idcc = idcc_selector.inner_text().strip() if idcc_selector else None
                pdf_exists = False
                pdf_link = None
            
            articles_data.append({
                "titre": titre,
                "lien article": article_link, 
                "PDF existant" : pdf_exists,
                "lien PDF" : pdf_link,
                "IDCC" : idcc
            })            
            total_articles += 1

    print(f"Nombre d'articles total trouvés : {total_articles}")
    print("longueur de la liste articles_data : ", len(articles_data) )
    browser.close()
    
# enregistrement des données dans un fichier json et csv
json_object = json.dumps(articles_data, indent=4, ensure_ascii=False)
with open("data/articles_links.json", "w", encoding="utf-8") as output_file : 
    output_file.write(json_object)

