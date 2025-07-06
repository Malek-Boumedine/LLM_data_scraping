from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import cloudscraper
import os
import time
import random
from dotenv import load_dotenv

load_dotenv()



output_path = "data/scrapping/"
os.makedirs(output_path, exist_ok=True)
base_url = "https://www.legifrance.gouv.fr"
start_url = os.getenv("START_URL_BOCC", "https://www.legifrance.gouv.fr/liste/bocc?intervalPublication=&idcc_suggest=&titre_suggest=&sortValue=BOCC_SORT_DESC&pageSize=9999&page=1&tab_selection=all#bocc")


################################################################################################

# extraire les articles :

def extract_bocc_articles_informations(start_url : str = start_url) -> list[dict]:

    articles_data = []
    scraper = cloudscraper.create_scraper()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        resp = scraper.get(start_url)
        page.set_content(resp.text)
        
        try :
            articles = page.query_selector_all("article.result-item.item-for-liste-idcc")
            
            for article in articles:
                try :
                    title_elem = article.query_selector("h3.title-result-item a")
                    title = title_elem.inner_text().strip()
                except Exception as e :
                    title = None
                    print(f"Erreur lors de la récupération du titre de l'article {article} : {e}")
                
                try :
                    article_pdf_list_elem = article.query_selector("a")
                    article_pdf_list_link = urljoin(base_url, article_pdf_list_elem.get_attribute("href"))
                except Exception as e:
                    article_pdf_list_link = None
                    print(f"Erreur lors de la récupération du lien PDF de l'article {article} : {e}")
                    
                try :
                    pdf_link_elem = article.query_selector("a.doc-download.doc-small.doc-small-bocc")
                    if pdf_link_elem:
                        pdf_link = urljoin(base_url, pdf_link_elem.get_attribute("href"))
                    else:
                        pdf_link = None
                except Exception as e :
                    pdf_link = None
                    print(f"Erreur lors de la récupération du lien direct de téléchargement du pdf de l'article {article} : {e}")
                
                if any([title, article_pdf_list_link, pdf_link]):
                    articles_data.append({
                        "titre": title,
                        "lien article": article_pdf_list_link,
                        "lien PDF": pdf_link,
                    })
                    
                time.sleep(random.uniform(1, 2))

        except Exception as e :
            print(f"Erreur pendant la lecture de la page du lien {start_url} : {e}")
        
        finally :
            print("Nombre total d'articles récupérés : ", len(articles_data))
            browser.close()
    
    return articles_data


################################################################################################

