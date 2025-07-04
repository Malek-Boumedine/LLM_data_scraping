import json
import os



## conventions etendues

os.makedirs("data/scraping/cleaned", exist_ok=True)
conventions_pdf = []
conventions_no_pdf = []

with open ("data/scraping/articles_links_conventions_etendues.json", "r", encoding="utf-8") as f : 
    data = json.load(f)
    
    for article in data :
        if article["titre"].lower().startswith("convention") :
            if article["lien PDF"] is None:
                conventions_no_pdf.append(article)
            else : 
                conventions_pdf.append(article)
                

with open("data/scraping/cleaned/pdf_cleaned_conventions_etendues.json", "w") as f : 
    json.dump(conventions_pdf, f, indent=4, ensure_ascii=False)


with open("data/scraping/cleaned/no_pdf_cleaned_conventions_etendues.json", "w") as f : 
    json.dump(conventions_no_pdf, f, indent=4, ensure_ascii=False)


######################################################

## BOCC

bocc_pdf = []
bocc_no_pdf = []

with open("data/scraping/articles_links_BOCC.json", "r", encoding="utf_8") as f : 
    data = json.load(f)

    for article in data : 
        if article["lien PDF"] is None : 
            bocc_no_pdf.append(article)
        else : 
            bocc_pdf.append(article)

with open("data/scraping/cleaned/no_pdf_bocc.json", "w", encoding="utf-8") as f : 
    json.dump(bocc_no_pdf, f, indent=4, ensure_ascii=False)
    
with open("data/scraping/cleaned/pdf_bocc.json", "w", encoding="utf-8") as f : 
    json.dump(bocc_pdf, f, indent=4, ensure_ascii=False)
    
    
    


