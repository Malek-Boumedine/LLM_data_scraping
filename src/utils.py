from PyPDF2 import PdfReader
import os
from typing import TextIO
import json



################################################################################################

# enregistrement dans un json

def save_data_json(data: list[dict], json_file_name: str, output_path: str = "data/scrapping") -> None: 
    output_file = os.path.join(output_path, json_file_name)
    with open(output_file, "w", encoding="utf-8") as output_file:
        json.dump(data, output_file, indent=4, ensure_ascii=False)


##########################################################################################

# focntion pour vérifier l'état des fichiers pdf (pdfs corrompus, pas de pages, pas de texte ...)

def check_pdf_health(files_path: str, auto_remove: bool = False) -> tuple[int, list[str], list[str], list[str]]: 
    
    os.makedirs(files_path, exist_ok=True)
    pdf_files_list = [file for file in os.listdir(files_path) if file.endswith(".pdf")]
    pdf_files_number = len(pdf_files_list)
    messages_logs = []
    valid_files = []
    invalid_files = []
    
    for file in pdf_files_list :
        file_path = os.path.join(files_path, file)
        try :
            reader = PdfReader(file_path)
            valid_files.append(file)
            messages_logs.append(f"Fichier OK : {file}")
            page = reader.pages[0]
            text = page.extract_text()
        
        except Exception as e :
            invalid_files.append(file)
            messages_logs.append(f"Erreur fichier {file} : {e}")
    
    if invalid_files : 
        print(f"{len(invalid_files)} fichiers invalides ont été trouvés ! ")
        if auto_remove:
            for file in invalid_files:
                os.remove(os.path.join(files_path, file))
                print("Suppression automatique de :", file)
                
        else :
            try :
                answer = input("Voulez-vous les supprimer ? (O/n)")
                if answer.lower() in ["n", "no", "non"] :
                    print("Suppression annulée ")
                else :
                    for file in invalid_files :
                        os.remove(os.path.join(files_path, file))
                        print(f"suppression validée : {file}")
                print("\nFin de traitement\n")
            except Exception as e: 
                print(f"Erreur lors du traitement : {e}")
                pass
    
    return pdf_files_number, messages_logs, valid_files, invalid_files


##########################################################################################

# fonction qui permet d'écrire les logs

def log_and_print(message : str, logfile : TextIO) -> None : 
    print(message)
    logfile.write(message + "\n")
    logfile.flush()


##########################################################################################

