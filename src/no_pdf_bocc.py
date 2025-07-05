import json
import os
import re
from playwright.sync_api import sync_playwright
import cloudscraper
from urllib.parse import urljoin
import time
import random
from PyPDF2 import PdfReader, PdfWriter
import io
from typing import TextIO



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

    
###########################################################################

# enregistrer le pdf
    
def write_binary_to_pdf(pdf_binary_content : list, file_path : str) :
    
    writer = PdfWriter()
    for pdf_bytes in pdf_binary_content :
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages :
            writer.add_page(page)
    output_bytes = io.BytesIO()
    writer.write(output_bytes)
    pdf_concatenate = output_bytes.getvalue()
    
    with open(file_path, "wb") as f : 
        f.write(pdf_concatenate)
    
    
###########################################################################

# fonction pour enregistrer les logs, pour vérifier les echecs

def log_and_print(message : str, logfile : TextIO) : 
    print(message)
    logfile.write(message + "\n")
    logfile.flush()


###########################################################################

# chronometre pour voir combien de temps le traitement prend

def chronometre() :
    
    start_time = time.perf_counter()
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    return 
    
    
    pass






###########################################################################
    
# itérer et ajouter de la récursion pour tout récupérer

def iterate_all_untill_all_downloaded(data :list[dict], max_attempts: int = 3) : 
    
    # début du chronomètre
    start_time = time.perf_counter()
    
    # ouvrir le fichier log dès le départ pour enregistrer les logs
    with open ("scrapping_bocc.log", "a", encoding="utf-8") as logfile :
        log_and_print("\n"+"="*50+"  DÉBUT DE TRAITEMENT  "+"="*50+"\n"
                      +"="*43+f"  NOMBRE D'ARTICLES A TRAITER : {len(data)}  "+"="*43+"\n",
                      logfile)
        
        for article in data : 
        # for article in data[:3] :       # test
            article_start_time = time.perf_counter()
            
            # extraire les liens de téléchargement des pdf et le nom du bocc de chaque page
            download_pages, file_name = get_download_page_list(article)
            log_and_print(f"Début traitement article : {file_name} ({len(download_pages)} PDFs attendus)", logfile)
            
            # tenter de récupérer tous les contenus des fichiers pdf
            attempts = 0
            current_download_pages = download_pages
            pdf_binary_content = []
            
            while current_download_pages and attempts < max_attempts : 
                attempts += 1
                log_and_print(f"Tentative {attempts}/{max_attempts} pour {file_name} ({len(current_download_pages)} PDFs à télécharger)", logfile)
                
                pdf_contents, failed_pdf_download, file_path = get_all_pdfs_contents(current_download_pages, file_name)
                pdf_binary_content.extend(pdf_contents)
                
                if not failed_pdf_download :
                    log_and_print(f"Tous les PDFs pour '{file_name}' téléchargés avec succès.", logfile)
                    break
                
                elif len(failed_pdf_download) == len(current_download_pages) : 
                    log_and_print(f"Aucun progrès pour '{file_name}', arrêt des tentatives.", logfile)
                    break
                
                else :
                    current_download_pages = failed_pdf_download
                    log_and_print(f"{len(failed_pdf_download)} PDFs non téléchargés sur '{file_name}'. Nouvelle tentative.", logfile)
            
            # écrire tous les pdf récupérés dans un fichier
            if len(pdf_binary_content) == len(download_pages) : 
                write_binary_to_pdf(pdf_binary_content, file_path)
                log_and_print(f"PDF fusionné et sauvegardé pour {file_name} : {file_path}", logfile)
            else:
                log_and_print(f"PDF incomplet pour {file_name} : {len(pdf_binary_content)}/{len(download_pages)} téléchargés", logfile)
            article_end_time = time.perf_counter()
            article_execution_time = article_end_time - article_start_time
            log_and_print(f"\nDurée de traitement de l'article - {file_name} : {article_execution_time:.2f} secondes\n", logfile)
            log_and_print("\n"+"#"*123+"\n", logfile)
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time

        log_and_print(f"\nDURÉE TOTALE DE TRAITEMENT : {execution_time:.2f} secondes\n", logfile)
        log_and_print("\n"+"="*51+"  FIN DE TRAITEMENT  "+"="*51+"\n", logfile)
        


###########################################################################


if __name__ =="__main__" :
    iterate_all_untill_all_downloaded(data)

