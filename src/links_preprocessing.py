import json
import os
from src.utils import save_data_json



data_path = "data/scraping"
output_path = os.path.join(data_path, "cleaned")
os.makedirs(output_path, exist_ok=True)


######################################################

# conventions étendues

def preprocessing_ce(output_path: str = output_path) -> None:
    conventions_pdf = []
    conventions_no_pdf = []
    scraped_file_name = "articles_links_conventions_etendues.json"
    scraped_file = os.path.join(data_path, scraped_file_name)
    with open(scraped_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        for article in data:
            titre = article.get("titre", "").lower()
            lien_pdf = article.get("lien PDF")
            # Vérifie que c'est bien une convention
            if titre.startswith("convention"):
                # Teste si lien_pdf est une vraie chaîne non vide
                if isinstance(lien_pdf, str) and lien_pdf.strip():
                    conventions_pdf.append(article)
                else:
                    conventions_no_pdf.append(article)
                    
    conventions_pdf_file_name = "pdf_cleaned_conventions_etendues.json"
    save_data_json(conventions_pdf, conventions_pdf_file_name, output_path)
    
    conventions_no_pdf_file_name = "no_pdf_cleaned_conventions_etendues.json"
    save_data_json(conventions_no_pdf, conventions_no_pdf_file_name, output_path)


######################################################

# BOCC

def preprocessing_bocc(output_path: str = output_path) -> None:

    bocc_pdf = []
    bocc_no_pdf = []
    scraped_file = os.path.join(data_path, "articles_links_BOCC.json")
    
    with open(scraped_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        for article in data:
            if article.get("lien PDF") is None:
                bocc_no_pdf.append(article)
            else:
                bocc_pdf.append(article)
                
    bocc_pdf_file_name = "pdf_bocc.json"
    save_data_json(bocc_pdf, bocc_pdf_file_name, output_path)
    
    bocc_no_pdf_file_name = "no_pdf_bocc.json"
    save_data_json(bocc_no_pdf, bocc_no_pdf_file_name, output_path)
    

######################################################

if __name__ == "__main__" :
    
    preprocessing_ce(output_path)
    preprocessing_bocc(output_path)





