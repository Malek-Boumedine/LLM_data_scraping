import json
from playwright.sync_api import sync_playwright
import cloudscraper
from urllib.parse import urljoin
import os
import re
import random
import time
from utils import log_and_print
from datetime import datetime



base_url = "https://www.legifrance.gouv.fr"
output_path = "data/BOCC_pdf_direct_link/"
logs_dir = "logs/bocc/"

with open("data/scraping/cleaned/pdf_bocc.json", "r", encoding="utf-8") as f : 
    data = json.load(f)


##################################################

def get_download_link(article: dict, base_url: str) -> tuple[str, str, str, str]:
    """
    Renvoie le lien de téléchargement du PDF, le nom du fichier nettoyé, le titre original, et un message d'erreur.
    """
    error_message = ""
    url = article["lien PDF"]
    title = article["titre"]
    forbiden_characters = r'[<>:"/\\|?*]'
    file_name = re.sub(forbiden_characters, '_', title)[:250]
    download_link = ""
    try:
        scraper = cloudscraper.create_scraper()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            resp = scraper.get(url)
            page.set_content(resp.text)
            download_elem = page.query_selector("div.header-minimal a.doc-download")
            if download_elem:
                download_link = urljoin(base_url, download_elem.get_attribute("href"))
            else:
                error_message = f"❌ Élément de téléchargement non trouvé pour {title}"
            browser.close()
    except Exception as e:
        error_message = f"Erreur lors de la récupération du lien PDF ({title}): {e}"
    return download_link, file_name, title, error_message

    
##################################################


def download_pdf(download_link: str, file_path: str) -> tuple[bool, str]:
    """
    Tente de télécharger et d'enregistrer le PDF à l'emplacement file_path.
    Retourne un booléen de succès et un message de log.
    """
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(download_link)
        if response.content.startswith(b'%PDF') and len(response.content) > 1000:
            with open(file_path, "wb") as f:
                f.write(response.content)
            return True, f"✅ Fichier créé : {os.path.basename(file_path)}"
        else:
            return False, f"❌ PDF NON récupéré ou corrompu : {download_link}"
    except Exception as e:
        return False, f"❌ Exception lors du téléchargement : {e}"


##################################################


def iterate_all_untill_all_downloaded(data: list[dict], output_path: str = output_path, max_attempts: int = 3):
    
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)
    now_str = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    log_path = f"{logs_dir}scrapping_pdf_bocc_{now_str}.log"
    files_already_downloaded = set(os.listdir(output_path))
    start_time = time.perf_counter()
    failed_articles = []

    with open(log_path, "a", encoding="utf-8") as logfile:
        log_and_print(
            "\n" + "=" * 50 + "  DÉBUT DE TRAITEMENT  " + "=" * 50 + "\n"
            + "=" * 43 + f"  NOMBRE D'ARTICLES A TRAITER : {len(data)}  " + "=" * 43,
            logfile,
        )
        log_and_print("-" * 130, logfile)

        for x, article in enumerate(data, 1):
            try:
                download_link, file_name, title, error_message = get_download_link(article, base_url)
                file_path = os.path.join(output_path, f"{file_name}.pdf")
                log_and_print(f"Article {x}/{len(data)} : {title}", logfile)
                
                if f"{file_name}.pdf" in files_already_downloaded:
                    log_and_print(f"\n⏩ SKIP : {file_name}.pdf déjà téléchargé, passage à l'article suivant.", logfile)
                    log_and_print("-" * 130, logfile)
                    continue

                if error_message:
                    log_and_print(error_message, logfile)
                    failed_articles.append(article)
                    continue

                ok, message = download_pdf(download_link, file_path)
                log_and_print(message, logfile)
                if not ok:
                    failed_articles.append(article)
                log_and_print("-" * 130, logfile)
                time.sleep(random.uniform(1, 2))

            except Exception as e:
                log_and_print(f"❌ Exception sur l'article {x} : {e}", logfile)
                failed_articles.append(article)
                continue

        end_time = time.perf_counter()
        log_and_print(
            f"\n⏱️ DURÉE TOTALE DE TRAITEMENT : {end_time - start_time:.2f} secondes",
            logfile,
        )
        log_and_print("\n" + "=" * 51 + "  FIN DE TRAITEMENT  " + "=" * 51 + "\n", logfile)

    return failed_articles


##################################################
    

if __name__ == "__main__":
    with open("data/scraping/cleaned/pdf_bocc.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    failed = iterate_all_untill_all_downloaded(data)
    print("Traitement terminé.")
    print(f"Articles restants (échecs) : {len(failed)}")

