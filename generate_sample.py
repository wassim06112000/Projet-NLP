import pandas as pd

# Charger le fichier avec les segments
segments = pd.read_json("data/processed/segments.json", lines=True)

# Prendre un échantillon de 200 morceaux
sample = segments.sample(200, random_state=42).reset_index(drop=True)

# Ajouter une colonne vide pour que tu puisses classer chaque segment
sample["section_type"] = ""

# Sauvegarder dans un fichier CSV pour que tu puisses l'ouvrir dans Excel
sample.to_csv("data/processed/segments_to_annotate.csv", index=False, encoding="utf-8")

print("Fichier généré : data/processed/segments_to_annotate.csv")
