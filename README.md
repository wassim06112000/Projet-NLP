# Assistant LLM pour Génération Automatique de Sections d’Appels d’Offres

Ce projet propose une solution complète pour l’analyse, la classification et la génération automatique de sections types d’appels d’offres (AO) à partir d’un corpus d’historiques. Il combine des techniques de NLP classiques, du clustering et l’usage d’un LLM (comme Mistral ou OpenAI) pour générer des textes adaptés et structurés.

## Architecture du projet

├── Data
│ └── Outputs
│ └── ao_analysis_results.json # Résultats d'analyse et suggestions pour le LLM
├── src
│ ├── apli.py # Application Streamlit (génération de sections AO via LLM)
│ ├── clustering_lots.py # Script de clustering pour les lots
│ ├── generate_sample.py # Génération d'échantillons de corpus pour tests
│ ├── main.py # Pipeline principal d'analyse, extraction des templates, stats, clustering
│ ├── prompt.py # Fonctions utilitaires pour la génération de prompts structurés
│ └── segment_corpus.py # Découpage et segmentation du corpus d'AO


## Fonctionnalités principales

- **Extraction automatique de patrons récurrents** (template extraction)
- **Clustering K-Means** sur les AO par contenu textuel (TF-IDF)
- **Statistiques descriptives** sur les AO (types, procédures, critères, CPV)
- **Génération de suggestions structurées** pour chaque section type (objectif, prestations, critères)
- **Application Streamlit** permettant de générer dynamiquement des sections d’AO à partir de prompts personnalisés et d’exemples issus du corpus, avec adaptation du registre ou du secteur
- **Support multi-LLM** (Mistral, OpenAI...)

## Installation

```bash
git clone https://github.com/ton-org/assistant-llm-ao.git
cd assistant-llm-ao
python -m venv .venv
source .venv/bin/activate  
pip install -r requirements.txt

## Variables d'environnement :
export MISTRAL_API_KEY=sk-xxx    # pour Mistral
# ou pour OpenAI
export OPENAI_API_KEY=sk-xxx

## Lancer l'application streamlit 

streamlit run src/apli.py

