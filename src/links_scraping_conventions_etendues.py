from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import cloudscraper
import os
import random
import time
from dotenv import load_dotenv

load_dotenv()



output_path = "data/scraping/"
os.makedirs(output_path, exist_ok=True)
base_url = "https://www.legifrance.gouv.fr"
start_url = os.getenv("START_URL_CONV_ETEN", "https://www.legifrance.gouv.fr/liste/idcc?facetteTexteBase=TEXTE_BASE&facetteEtat=VIGUEUR_ETEN&facetteEtat=VIGUEUR_NON_ETEN&sortValue=DATE_UPDATE&pageSize=9999&page=1&tab_selection=all#idcc")


################################################################################################

# extraire les articles :

def extract_ce_articles_informations(start_url : str = start_url) -> list[dict]:
    
    articles_data = []
    scraper = cloudscraper.create_scraper()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        resp = scraper.get(start_url)
        page.set_content(resp.text)
        
        try :
            articles = page.query_selector_all('article.result-item.item-for-liste-idcc')
        except Exception as e :
            print(f"Erreur pendant la lecture de la page du lien {start_url} : {e}")
        
        print("\n"+"#"*80+"\n"+f"nombre total d'articles : {len(articles)} articles"+"\n"+"#"*80+"\n")
        
        for article in articles :
            title = None
            article_link = None
            pdf_exists = None
            pdf_link = None
            idcc = None
            try :
                title_elem = article.query_selector("a")
                title = title_elem.inner_text().strip()
            except Exception as e:
                print(f"Erreur lors de la récupération du titre de l'article {article} : {e}")
            
            article_link_elem = article.query_selector("a")
            try :
                article_link = urljoin(base_url, article_link_elem.get_attribute("href"))
            except Exception as e :
                print(f"Erreur lors de la récupération de l'article {article} : {e}")
                
            try : 
                pdf_link_elem = article.query_selector("div.picto-download.picto-downloadCenter a")
                
                if pdf_link_elem:
                    pdf_exists = True
                    pdf_link = urljoin(base_url, pdf_link_elem.get_attribute("href"))
                    idcc_selector = article.query_selector('div.code-title-convention-container div.h4.code-title-convention')
                    idcc = idcc_selector.inner_text().strip() if idcc_selector else None
                    
                else:
                    idcc_selector = article.query_selector('div.code-title-convention-container.code-title-convention-containerAlign div.h4.code-title-convention')
                    idcc = idcc_selector.inner_text().strip() if idcc_selector else None
                    pdf_exists = False
                    pdf_link = None
            except Exception as e :
                print(f"Erreur lors de la récupération de la balise contenant le pdf de l'article {article} : {e}")
                
            articles_data.append({
                "titre": title,
                "lien article": article_link,
                "PDF existant": pdf_exists,
                "lien PDF": pdf_link,
                "IDCC": idcc,
            })
            
        time.sleep(random.uniform(1, 2))
            
        print("Nombre total d'articles récupérés : ", len(articles_data))
        browser.close()
        
    return articles_data


################################################################################################

