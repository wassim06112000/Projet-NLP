import streamlit as st
import json
import os
from mistralai.client import MistralClient

# -- Chargement des suggestions --
try:
    with open("ao_analysis_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    suggestions = data.get("suggestions_example", {})
except FileNotFoundError:
    st.error("Le fichier ao_analysis_results.json est introuvable.")
    suggestions = {}

st.title("📝 Générateur de sections AO (Assistant LLM)")

# Tu peux remplir la liste secteurs avec ce qui ressort le plus souvent dans ton JSON (ou laisse libre)
secteurs_possibles = [
    "Services de propreté",
    "Maintenance technique",
    "Travaux publics",
    "Fournitures de bureau",
    "Assurances",
    "Services informatiques",
    "Transport",
    "Restauration collective",
    "Espaces verts",
    "Sécurité",
    "Autre (à préciser ci-dessous)"
]

titre = st.text_input("Titre du projet", "Entretien des locaux municipaux")
type_marche = st.selectbox("Type de projet", ["services", "supplies", "works"])
secteur = st.selectbox("Secteur/domaine d'activité", secteurs_possibles)
if secteur == "Autre (à préciser ci-dessous)":
    secteur = st.text_input("Préciser le secteur", "")

contraintes = st.text_area("Contraintes spécifiques", "Intervention rapide, respect de l'environnement")
section = st.selectbox("Section à générer", ["objectif", "prestations_attendues", "critères_sélection"])
registre = st.selectbox("Registre/ton", ["formel", "technique", "accessible"])

if st.button("Générer la section"):
    exemple = suggestions.get(section, "")
    prompt = (
        f"Génère la section '{section}' d'un appel d'offres.\n"
        f"Titre: {titre}\n"
        f"Type: {type_marche}\n"
        f"Secteur: {secteur}\n"
        f"Contraintes: {contraintes}\n"
        f"Registre: {registre}\n"
        f"Exemple de formulation typique : {exemple}\n"
        f"Réponds en français et de façon professionnelle selon le registre demandé."
    )

    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    if not mistral_api_key:
        st.error("API key Mistral manquante. Défini la variable d'environnement MISTRAL_API_KEY.")
    else:
        try:
            mistral_client = MistralClient(api_key=mistral_api_key)
            response = mistral_client.chat(
                model="mistral-medium",
                messages=[{"role": "user", "content": prompt}]
            )
            generated_text = response.choices[0].message.content
            st.markdown("### Section générée :")
            st.write(generated_text)
        except Exception as e:
            st.error(f"Erreur lors de la génération : {e}")

with st.expander("Voir exemples de formulation (issus du corpus JSON)"):
    st.write(suggestions)
