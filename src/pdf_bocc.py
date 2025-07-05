import json
from playwright.sync_api import sync_playwright
import cloudscraper
from urllib.parse import urljoin
import os
import re
import random
import time



base_url = "https://www.legifrance.gouv.fr"

output_path = "data/BOCC/"

with open("data/scraping/cleaned/pdf_bocc.json", "r", encoding="utf-8") as f : 
    data = json.load(f)

# print(len(data))            # 744
# data_ok_pdf = [d["lien PDF"] for d in data if not d["lien PDF"] is None]
# print(len(data_ok_pdf))     # 744

def download_pdfs(data, base_url, output_path) : 
    
    failed_downloads = []
    os.makedirs(output_path, exist_ok=True)
    for article in data : 
        url = article["lien PDF"]
        article_title = article["titre"]
        forbiden_characters = r'[<>:"/\\|?*]'
        convention_name = re.sub(forbiden_characters, '_', article_title)
        file_name = convention_name[:250]

        print(file_name)
        print(url)

        scraper = cloudscraper.create_scraper()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            resp = scraper.get(url)
            page.set_content(resp.text)
            
            download_elem = page.query_selector("div.header-minimal a.doc-download")
            if not download_elem : 
                print("Élément non trouvé - probablement bloqué par Cloudflare")
                browser.close()
                failed_downloads.append(article)
                continue
            else :
                download_link = urljoin(base_url, download_elem.get_attribute("href"))
                response = scraper.get(download_link)
                
                if response.content.startswith(b'%PDF') and len(response.content) > 1000:
                    file_path = f"{output_path}/{file_name}.pdf"
                    if not os.path.exists(file_path):
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        print(f"✅ Fichier créé : {file_name}.pdf")
                    else :
                        counter = 1
                        while os.path.exists(f"{output_path}/{file_name}_{counter}.pdf"):
                            counter += 1
                        duplicate_path = f"{output_path}/{file_name}_{counter}.pdf"
                        with open(duplicate_path, "wb") as f:
                            f.write(response.content)
                        print(f"✅ Doublon créé : {file_name}_{counter}.pdf")
                else :
                    print("❌ Fichier PDF invalide")
                    failed_downloads.append(article)
                browser.close()
        time.sleep(random.uniform(1,2))
        print("-"*100)
    return failed_downloads

    
##################################################


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


##################################################
    
if __name__ == "__main__" : 

    failed_downloads = iterate_until_all_downloaded(data, base_url, output_path)
    print("traitement terminé ")
    print(f"articles restants : {failed_downloads}")
    print(f"nombre : {len(failed_downloads)}")












