import json
from playwright.sync_api import sync_playwright
import cloudscraper
from urllib.parse import urljoin
import os
import re
import random
import time
from utils import log_and_print



base_url = "https://www.legifrance.gouv.fr"
output_path = "data/conventions_etendues/"
logs_dir = "logs/convention_etendues/"
os.makedirs(output_path, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)

with open("data/scraping/cleaned/pdf_cleaned_conventions_etendues.json", "r", encoding="utf-8") as f :
    data = json.load(f)


########################################################################

def download_pdfs(data, base_url, output_path) : 
    failed_downloads = []
    
    for article in data :
        pdf_url = article["lien PDF"]
        convention_name_init = article["titre"].split("(")[0]
        forbiden_characters = r'[<>:"/\\|?*]'
        convention_name = re.sub(forbiden_characters, '_', convention_name_init)
        
        idcc = article["IDCC"]
        
        print(convention_name)
        print("lien de télechargement : ", pdf_url)

        file_name = f"{idcc} - {convention_name[:200]}" if idcc else convention_name[:255]
        
        scraper = cloudscraper.create_scraper()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            resp = scraper.get(pdf_url)
            page.set_content(resp.text)

            download_element = page.query_selector("div.header-minimal a.doc-download")
            if not download_element:
                print("Élément non trouvé - probablement bloqué par Cloudflare")
                browser.close()
                failed_downloads.append(article)
                continue
            else : 
                download_link = urljoin(base_url, download_element.get_attribute("href"))
                response = scraper.get(download_link)
                
                if response.content.startswith(b'%PDF') and len(response.content) > 1000:
                    file_path = f"{output_path}/{file_name}.pdf"

                    if not os.path.exists(file_path):
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        print(f"✅ Fichier créé : {file_name}.pdf")
                    else:
                        counter = 1
                        while os.path.exists(f"{output_path}/{file_name}_{counter}.pdf"):
                            counter += 1
                        duplicate_path = f"{output_path}/{file_name}_{counter}.pdf"
                        with open(duplicate_path, "wb") as f:
                            f.write(response.content)
                        print(f"✅ Doublon créé : {file_name}_{counter}.pdf")
                else:
                    print("❌ Fichier PDF invalide")
                    failed_downloads.append(article)
                browser.close()
        time.sleep(random.uniform(1,2))
        print("-"*100)
    return failed_downloads


######################################################


def iterate_until_all_downloaded(list_data, base_url, output_path, max_attempts=3) : 
    current_data = list_data
    attempt = 0
    
    while current_data and attempt < max_attempts:
        attempt += 1
        print(f"Tentative {attempt}/{max_attempts} - {len(current_data)} articles à traiter")
        
        failed_downloads = download_pdfs(current_data, base_url, output_path)
        
        if not failed_downloads:
            print("tous les articles ont été téléchargés avec succès !")
            break
        elif len(failed_downloads) == len(current_data):
            print("aucun progrès détecté, arrêt pour éviter la boucle infinie")
            break
        else:
            current_data = failed_downloads
            print(f"{len(failed_downloads)} articles ont échoué, nouvelle tentative...")
    
    return failed_downloads


######################################################

if __name__ == "__main__" : 
    
    failed_downloads = iterate_until_all_downloaded(data, base_url, output_path)
    print("traitement terminé ")
    print(f"articles restants : {failed_downloads}")

