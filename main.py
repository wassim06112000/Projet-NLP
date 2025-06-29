import os
from datetime import date, timedelta
from src.download import download_boamp_day
from src.pars import process_xml_files

def main():
    # Préparation des dossiers
    os.makedirs("data", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # 1. Téléchargement de tous les AO de mars 2025
    '''start = date(2025, 3, 1)
    end = date(2025, 4, 30)
    current = start
    while current <= end:
        download_boamp_day(
            annee=str(current.year),
            mois=f"{current.month:02d}",
            jour=f"{current.day:02d}",
            out_dir="data"
        )
        current += timedelta(days=1)'''

    # 2. Parsing des fichiers téléchargés
   
    input_dir = "data"  # Remplacez par votre vrai chemin
    output_file = "outputs/corpus_boamp_mars2025.json"
    
    # Appel correct sans argument nommé
    process_xml_files(input_dir, output_file)

if __name__ == "__main__":
    main()
