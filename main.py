from src.links_scraping_conventions_etendues import extract_ce_articles_informations
from src.links_scraping_BOCC import extract_bocc_articles_informations
from src.links_preprocessing import preprocessing_bocc, preprocessing_ce
from src.pdf_conventions_etendues_download import iterate_all_untill_all_downloaded as pdf_ce_down
from src.no_pdf_conventions_etendues_download import download_manually
from src.pdf_bocc import iterate_all_untill_all_downloaded as pdf_bocc_down
from src.no_pdf_bocc import iterate_all_untill_all_downloaded as no_pdf_bocc_down
from src.utils import check_pdf_health
import json
import sys
import time
import os



def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    while True:
        clear_screen()
        print("="*20 + "  Bienvenue au programme de scraping des fichiers de conventions collectives  " + "="*20)
        print("""
        🔔 IMPORTANT : Pour une premiere utilisation, suivez les étapes 1 jusqu'à 6 dans l'ordre. 🔔
        🔔 en cas d'erreur sur une étape, la relancer jusqu'à ce qu'elle se termine avec succès 🔔
    
    
    1. Scraper le json des conventions étendues
    2. Scraper le json des Bulletins Officiels des Conventions Collectives 
    3. Télécharger les Bulletins Officiels des Conventions Collectives avec lien PDF direct
    4. Télécharger les Bulletins Officiels des Conventions Collectives sans lien PDF direct
    5. Télécharger les conventions étendues avec lien PDF direct
    6. Télécharger les conventions étendues sans lien PDF direct (scraping semi automatique)
    7. Vérifier la santé des fichiers PDF téléchargés
    8. Consulter les logs
    9. Quitter
        """)
        try:
            choice = int(input("Faites un choix (1-9) : ").strip())
            if choice == 1:
                print("Les anciennes données seront écrasées, voulez-vous continuer ? ")
                ch = input("Votre choix (O/n) :  ").lower()
                if ch in ["o", "y", "oui", "yes", ""] :
                    extract_ce_articles_informations()
                    print("Scraping des conventions étendues terminé.")
                else :
                    print("Abandon ...")
                
            elif choice == 2:
                print("Les anciennes données seront écrasées, voulez-vous continuer ? ")
                ch = input("Votre choix (O/n) :  ").lower()
                if ch in ["o", "y", "oui", "yes", ""] :
                    extract_bocc_articles_informations()
                    print("Scraping des BOCC terminé.")
                else :
                    print("Abandon ...")
                
            elif choice == 3:
                preprocessing_bocc()
                time.sleep(1)
                with open("data/scraping/cleaned/pdf_bocc.json", "r", encoding="utf-8") as f:
                    data3 = json.load(f)
                pdf_bocc_down(data3)
                print("Téléchargement des BOCC avec PDF direct terminé.")
                
            elif choice == 4:
                preprocessing_bocc()
                time.sleep(1)
                with open("data/scraping/cleaned/no_pdf_bocc.json", "r", encoding="utf-8") as f:
                    data4 = json.load(f)

                no_pdf_bocc_down(data4)
                print("Téléchargement des BOCC sans PDF direct terminé.")
                
            elif choice == 5:
                preprocessing_ce()
                time.sleep(1)
                with open("data/scraping/cleaned/pdf_cleaned_conventions_etendues.json", "r", encoding="utf-8") as f:
                    data5 = json.load(f)
                pdf_ce_down(data5)
                print("Téléchargement des conventions étendues avec PDF direct terminé.")
                
            elif choice == 6:
                preprocessing_ce()
                time.sleep(1)
                with open("data/scraping/cleaned/no_pdf_cleaned_conventions_etendues.json", "r", encoding="utf-8") as f:
                    data6 = json.load(f)
                download_manually(data6)
                print("Téléchargement manuel terminé.")
                
            elif choice == 7:
                pdf_health_menu()
                
            elif choice == 8:
                logs_menu()
                
            elif choice == 9:
                print("\nMerci d'avoir utilisé ce programme. À bientôt !")
                time.sleep(1)
                sys.exit(0)
                
            else:
                print("Erreur de saisie ! Veuillez saisir un chiffre entre 1 et 9.")
                
        except Exception as e:
            print(f"Erreur : {e}")
        input("\nAppuyez sur Entrée pour revenir au menu...")

def pdf_health_menu():
    while True:
        clear_screen()
        print("""
        Vérification de la santé des fichiers PDF :
        1. Vérifier la santé des PDF BOCC (avec possibilité de suppression)
        2. Vérifier la santé des PDF conventions étendues (avec possibilité de suppression)
        3. Retour au menu principal
        """)
        try:
            choice = int(input("Votre choix (1-3) : ").strip())

            if choice == 1:
                print("\nVérification des PDF BOCC avec lien direct :")
                total1, logs1, valid1, invalid1 = check_pdf_health("data/BOCC_pdf_direct_link")
                print(f"{len(invalid1)} fichiers PDF corrompus (BOCC avec lien direct).")

                print("\nVérification des PDF BOCC sans lien direct :")
                total2, logs2, valid2, invalid2 = check_pdf_health("data/BOCC_no_pdf_direct_link")
                print(f"{len(invalid2)} fichiers PDF corrompus (BOCC sans lien direct).")

                print(f"\nTotal de fichiers corrompus BOCC : {len(invalid1) + len(invalid2)}")
            elif choice == 2:
                total, logs, valid, invalid = check_pdf_health("data/conventions_etendues")
                print(f"{len(invalid)} fichiers PDF corrompus (conventions étendues).")            
            elif choice == 3:
                break
            else:
                print("Veuillez entrer un chiffre entre 1 et 3.")
        except Exception as e:
            print(f"Erreur : {e}")
        input("\nAppuyez sur Entrée pour continuer...")

def logs_menu():
    while True:
        clear_screen()
        print("""
        Consultation des logs :
        1. Logs des BOCC : afficher la liste et choisir un fichier à consulter
        2. Logs des conventions étendues : afficher la liste et choisir un fichier à consulter
        3. Retour au menu principal
        """)
        try:
            choice = int(input("Votre choix (1-3) : ").strip())
            if choice == 1:
                show_log_files("logs/bocc/")
            elif choice == 2:
                show_log_files("logs/convention_etendues/")
            elif choice == 3:
                break
            else:
                print("Veuillez entrer un chiffre entre 1 et 3.")
        except Exception as e:
            print(f"Erreur : {e}")
        input("\nAppuyez sur Entrée pour continuer...")

def show_log_files(log_dir):
    files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    if not files:
        print("Aucun fichier de log trouvé.")
        return
    for idx, f in enumerate(files, 1):
        print(f"{idx}. {f}")
    try:
        num = int(input("Numéro du log à afficher (0 pour retour) : ").strip())
        if num == 0:
            return
        filename = files[num-1]
        with open(os.path.join(log_dir, filename), 'r', encoding="utf-8") as f:
            print("\n" + "="*30)
            print(f.read())
            print("="*30)
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    main_menu()
