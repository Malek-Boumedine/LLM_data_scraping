import json
import os
import re
from playwright.sync_api import sync_playwright
import cloudscraper
from urllib.parse import urljoin
import time
import random



base_url = "https://www.legifrance.gouv.fr"
output_path = "data/BOCC_no_pdf_direct_link/"

with open("data/scraping/cleaned/no_pdf_bocc.json", "r", encoding="utf-8") as f : 
    data = json.load(f)


###########################################################################

# récupérer la liste des url de téléchargement pdf de chaque lien de bocc

def get_download_page_list(article : dict) :

    os.makedirs(output_path, exist_ok=True)
    url = article["lien article"].replace("id", "titre_suggest=&sortValue=BOCC_SORT_NUM_ASC&pageSize=100&page=1&tab_selection=all&id")      # pour avoir tous les pdf des conventions dans une seule page
    title = article["titre"]
    forbiden_characters = r'[<>:"/\\|?*]'
    file_name = re.sub(forbiden_characters, "_", title)[:250]
    
    scraper = cloudscraper.create_scraper()
    
    with sync_playwright() as p : 
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        resp = scraper.get(url)
        page.set_content(resp.text)
        
        pdf_elements = page.query_selector_all("article.result-item.item-for-liste-idcc a.doc-download.doc-small.doc-small-bocc")
        download_pages = [urljoin(base_url, e.get_attribute("href")) for e in pdf_elements]
        
        browser.close()
    
    return download_pages, file_name


###########################################################################

# récupérer le contenu de tous les PDFs

def get_all_pdfs_contents(download_pages : list, file_name : str) : 

    scraper = cloudscraper.create_scraper()
    
    pdf_binary_content = []
    failed_pdf_download = []
    for dp in download_pages : 
        
        with sync_playwright() as p :
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            resp = scraper.get(dp)
            page.set_content(resp.text)
            
            download_button_elem = page.query_selector("div.header-minimal a.doc-download")
            download_link = urljoin(base_url, download_button_elem.get_attribute("href"))
            
            response = scraper.get(download_link)
            if response.content.startswith(b'%PDF') and len(response.content) > 1000 :
                file_path = f"{output_path}/{file_name}.pdf"
                pdf_binary_content.append(response.content)
            else:
                print(f"❌ PDF NON récupéré ou corrompu : {download_link}")
                failed_pdf_download.append(download_link)
            browser.close()
        
        time.sleep(random.uniform(1,2))
    
    return pdf_binary_content, failed_pdf_download, file_path

    
