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
from datetime import datetime
from src.utils import log_and_print



base_url = "https://www.legifrance.gouv.fr"
output_path_pdfs = "data/BOCC_no_pdf_direct_link/"
logs_dir = "logs/bocc/"

with open("data/scraping/cleaned/no_pdf_bocc.json", "r", encoding="utf-8") as f : 
    data = json.load(f)


###########################################################################

# récupérer la liste des url de téléchargement pdf de chaque lien de bocc

def get_download_page_list(article : dict, output_path: str = output_path_pdfs) :
    
    download_pages = []
    file_name = ""
    url = ""
    error_message = ""
    
    try :
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
    except Exception as e :
        error_message = f"Erreur de traitement de l'article {article} : {e}"
        pass
    
    return download_pages, file_name, url, error_message


###########################################################################

# récupérer le contenu de tous les PDFs

def get_all_pdfs_contents(download_pages : list, file_name : str, output_path: str = output_path_pdfs) : 

    fail_messages = []
    pdf_binary_content = []
    failed_pdf_download = []
    file_path = f"{output_path}{file_name}.pdf"
    
    try :
        scraper = cloudscraper.create_scraper()
        for dp in download_pages : 
            
            with sync_playwright() as p :
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                resp = scraper.get(dp)
                page.set_content(resp.text)
                
                download_button_elem = page.query_selector("div.header-minimal a.doc-download")
                if not download_button_elem :
                    message = f"❌ Bouton de téléchargement non trouvé sur {dp}"
                    fail_messages.append(message)
                    failed_pdf_download.append(dp)
                    browser.close()
                    continue
                download_link = urljoin(base_url, download_button_elem.get_attribute("href"))
                
                response = scraper.get(download_link)
                if response.content.startswith(b'%PDF') and len(response.content) > 1000 :
                    pdf_binary_content.append(response.content)
                else:
                    message = f"❌ PDF NON récupéré ou corrompu : {download_link}"
                    fail_messages.append(message)
                    failed_pdf_download.append(download_link)
                browser.close()
            
            time.sleep(random.uniform(1,2))
    
    except Exception as e :
        fail_messages.append(f"Exception lors du téléchargement de PDF(s) pour {file_name} : {e}")
    
    return pdf_binary_content, failed_pdf_download, file_path, fail_messages

    
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



###########################################################################
    
# itérer et ajouter de la récursion pour tout récupérer

def iterate_all_untill_all_downloaded(data: list[dict], output_path: str = output_path_pdfs,  max_attempts: int = 3, max_attempt_article: int = 3) : 
    
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)
    files_already_downloaded = os.listdir(output_path)
        
    # début du chronomètre
    start_time = time.perf_counter()
    
    # ouvrir le fichier log dès le départ pour enregistrer les logs
    now_str = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
    with open(f"{logs_dir}scrapping_no_pdf_bocc_{now_str}.log", "a", encoding="utf-8") as logfile:
        log_and_print("\n"+"="*50+"  DÉBUT DE TRAITEMENT  "+"="*50+"\n"
                      +"="*43+f"  NOMBRE D'ARTICLES A TRAITER : {len(data)}  "+"="*43,
                      logfile)
        log_and_print("-"*130, logfile)
        
        try :
            
            for x, article in enumerate(data, 1):
            # for x, article in enumerate(data[:3], 1):
                try :
                        
                    # vérifier que le fichier n'a pas été déja téléchargé
                    
                    download_pages, file_name, url, error_message = get_download_page_list(article)
                    if f"{file_name}.pdf" in files_already_downloaded :
                        log_and_print(f"\n⏩ SKIP : {file_name}.pdf déjà téléchargé, passage à l'article suivant.", logfile)
                        log_and_print("\n"+"-"*130, logfile)
                        continue
                    
                    else :
                        
                        log_and_print(f"Article {x}/{len(data)} : "+"\n",logfile)
                        article_start_time = time.perf_counter()
                        
                        # essayer d'extraire les liens de téléchargement des pdf et le nom du bocc de chaque page
                        attempt_article = 0
                        
                        if error_message :
                            log_and_print(error_message, logfile)
                        
                        while len(download_pages) == 0 and attempt_article < max_attempt_article :
                            attempt_article +=1
                            log_and_print(f"❓ Tentative {attempt_article}/{max_attempt_article} Aucun pdf trouvé pour l'article : {file_name} ({len(download_pages)} PDFs trouvés) ❓",logfile)
                            download_pages, file_name, url, error_message = get_download_page_list(article)
                            if error_message:
                                log_and_print(error_message, logfile)
                            
                        if len(download_pages) == 0 :
                            log_and_print(f"❌ Aucun fichier PDF trouvé pour l'article {file_name}, on passe au suivant.\n\n" + "#"*123 + "\n",logfile)
                            continue
                        
                        log_and_print(f"Début traitement article : {file_name} ({len(download_pages)} PDFs attendus)", logfile)
                        log_and_print(f"URL : {url}"+"\n"+"."*30, logfile)
                        
                        # tenter de récupérer tous les contenus des fichiers pdf
                        attempts = 0
                        current_download_pages = download_pages
                        pdf_binary_content = []
                        # file_path = f"{output_path}/{file_name}.pdf"
                        
                        while current_download_pages and attempts < max_attempts : 
                            attempts += 1
                            log_and_print(f"Tentative {attempts}/{max_attempts} pour {file_name} ({len(current_download_pages)} PDFs à télécharger)", logfile)
                            
                            pdf_contents, failed_pdf_download, file_path, fail_messages = get_all_pdfs_contents(current_download_pages, file_name)
                            pdf_binary_content.extend(pdf_contents)
                            
                            if not failed_pdf_download :
                                log_and_print(f"Tous les PDFs pour '{file_name}' téléchargés avec succès.", logfile)
                                if fail_messages :
                                    for msg in fail_messages:
                                        log_and_print(msg, logfile)
                                break
                            
                            elif len(failed_pdf_download) == len(current_download_pages) : 
                                log_and_print(f"Aucun progrès pour '{file_name}', arrêt des tentatives.", logfile)
                                if fail_messages :
                                    for msg in fail_messages:
                                        log_and_print(msg, logfile)
                                break
                            
                            else :
                                current_download_pages = failed_pdf_download
                                log_and_print(f"{len(failed_pdf_download)} PDFs non téléchargés sur '{file_name}'. Nouvelle tentative.", logfile)
                        
                        # écrire tous les pdf récupérés dans un fichier
                        if len(pdf_binary_content) == len(download_pages) and len(download_pages) != 0: 
                            write_binary_to_pdf(pdf_binary_content, file_path)
                            
                            log_and_print(f"🦾 PDF fusionné et sauvegardé pour {file_name} : {file_path} 🦾", logfile)
                        elif len(download_pages) == 0 : 
                            log_and_print("❌ Aucun fichier pdf trouvé pour cet article ! Echec de traitement ❌ ", logfile)
                            continue
                        else:
                            log_and_print(f"🥺 💔 PDF incomplet pour {file_name} : {len(pdf_binary_content)}/{len(download_pages)} téléchargés 💔 🥺", logfile)
                            
                        article_end_time = time.perf_counter()
                        article_execution_time = article_end_time - article_start_time
                        log_and_print(f"\nDurée de traitement de l'article - {file_name} : {article_execution_time:.2f} secondes\n", logfile)
                        log_and_print("\n"+"#"*123+"\n", logfile)
                    
                except Exception as e :
                    log_and_print(f"❌ Exception sur l'article {x} ({file_name}) : {e}", logfile)
                    continue
                
            end_time = time.perf_counter()
            execution_time = end_time - start_time

            log_and_print(f"\n⏱️ DURÉE TOTALE DE TRAITEMENT : {execution_time:.2f} secondes", logfile)
            log_and_print("\n"+"="*51+"  FIN DE TRAITEMENT  "+"="*51+"\n", logfile)
        
        except Exception as e:
            log_and_print(f"❌ Exception critique : {e}", logfile)
        

###########################################################################


if __name__ =="__main__" :
    iterate_all_untill_all_downloaded(data)


