import requests
from bs4 import BeautifulSoup
import os

def download_boamp_day(annee: str, mois: str, jour: str, out_dir: str):
    """
    Télécharge tous les fichiers XML d'un jour donné (dossier sans ZIP)
    """
    base_url = f"https://echanges.dila.gouv.fr/OPENDATA/BOAMP/{annee}/{mois.zfill(2)}/{jour.zfill(2)}/"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    xml_links = [base_url + a['href'] for a in soup.find_all('a') if a['href'].endswith('.xml')]

    os.makedirs(out_dir, exist_ok=True)
    print(f"{len(xml_links)} fichiers XML trouvés.")

    for xml_url in xml_links:
        fname = xml_url.split("/")[-1]
        
        try:
            resp = requests.get(xml_url)
            with open(os.path.join(out_dir, fname), "wb") as f:
                f.write(resp.content)
        except Exception as e:
            print(f"Erreur sur {fname}: {e}")

    print("Téléchargement terminé !")

# Exemple d’utilisation :
# download_boamp_day("2025", "01", "03", "data/")
