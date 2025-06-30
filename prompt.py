import json
import random

# Charger le JSON (à adapter avec le vrai chemin de ton fichier)
with open("ao_analysis_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Récupérer quelques exemples d'objectifs pour les AO de type "services"
exemples = []
for titre in data["templates"]["project"]["title"]:
    # Ici tu pourrais filtrer selon le type si besoin (ici juste un échantillon aléatoire)
    exemples.append(titre)
    if len(exemples) >= 3:  # On prend les 3 premiers pour l'exemple
        break

# Construire un prompt pour l'IA
prompt = (
    "Tu es un expert en rédaction d'appels d'offres publics.\n"
    "Voici des exemples d'objectifs de marchés de services :\n"
    + "\n".join(f"- {ex}" for ex in exemples) +
    "\n\nRédige un nouvel objectif pour un marché de services de nettoyage, avec la contrainte d'intervention sous 24h."
)

print("Prompt pour l'IA :\n")
print(prompt)
