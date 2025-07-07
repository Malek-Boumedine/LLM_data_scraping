import json
import os
from playwright.sync_api import sync_playwright
import cloudscraper
from urllib.parse import urljoin
from src.utils import log_and_print
from datetime import datetime
import time
import random



base_url = "https://www.legifrance.gouv.fr"
output_path = "data/conventions_etendues/"
logs_dir = "logs/convention_etendues/"

os.makedirs(output_path, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)

with open ("data/scraping/cleaned/no_pdf_cleaned_conventions_etendues.json", "r", encoding="utf-8") as f : 
    data = json.load(f)
    

########################################################################

# fonction pour télécharger manuellement les pdfs

def download_manually(data: list[dict] = data, logs_dir: str = logs_dir):
    
    now_str = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    log_path = os.path.join(logs_dir, f"scrapping_pdf_conventions_etendues_{now_str}.log")
    
    with open(log_path, "a", encoding="utf-8") as logfile:
        log_and_print(
            "\n" + "=" * 50 + "  DÉBUT DE TRAITEMENT  " + "=" * 50 + "\n"
            + "=" * 43 + f"  NOMBRE D'ARTICLES À TRAITER : {len(data)}  " + "=" * 43,
            logfile,
        )
        log_and_print("-" * 130, logfile)
        
        for x, article in enumerate(data, 1):
            url = article.get("lien article")
            title = article.get("titre", "Sans titre")
            full_text_link = None

            message = (
                f"\n{'='*50} ARTICLE {x}/{len(data)} {'='*50}\n\n"
                f"Titre : {title}\nURL : {url}"
            )
            log_and_print(message, logfile)
            
            try:
                scraper = cloudscraper.create_scraper()
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    resp = scraper.get(url)
                    page.set_content(resp.text)
                    full_text_elem = page.query_selector("a.title-link.title-texte-idcc")
                    if full_text_elem:
                        full_text_link = urljoin(base_url, full_text_elem.get_attribute("href"))
                        msg = f"✅ Lien 'texte intégral' récupéré : {full_text_link}"
                        log_and_print(msg, logfile)
                    else:
                        msg = "❌ Impossible de trouver le lien 'texte intégral' dans la page."
                        log_and_print(msg, logfile)
                    browser.close()
            except Exception as e:
                msg = f"❌ Erreur lors de la récupération du lien : {e}"
                log_and_print(msg, logfile)
                continue  # Passe à l'article suivant

            if full_text_link:
                msg_open = (
                    "➡️  Ouverture du navigateur pour téléchargement manuel…\n"
                    "Veuillez cliquer sur le bouton IMPRIMER, puis choisir 'Enregistrer en PDF' dans ./data/conventions_etendues\n"
                    "Quand le téléchargement est terminé, fermez la fenêtre OU revenez ici et appuyez sur Entrée pour continuer."
                )
                log_and_print(msg_open, logfile)
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=False)
                    page = browser.new_page()
                    page.goto(full_text_link)
                    input_msg = "Appuyez sur Entrée UNE FOIS le téléchargement terminé et la fenêtre fermée…"
                    log_and_print(input_msg, logfile)
                    input()
                    browser.close()
                log_and_print("PDF téléchargé manuellement, passage à l'article suivant.\n", logfile)
            else:
                msg_warn = (
                    "⚠️  Ce document doit être traité complètement à la main (lien non trouvé).\n"
                    "⚠️ Téléchargement manuel complet requis (lien non récupéré).\n")
                log_and_print(msg_warn, logfile)
            
            time.sleep(random.uniform(1,2))

        log_and_print("#" * 40 + "  FIN DE TRAITEMENT  " + "#" * 40, logfile)
        log_and_print("Tous les articles ont été proposés à l'utilisateur pour téléchargement manuel.", logfile)


########################################################################

if __name__ == "__main__" : 
    
    download_manually()
