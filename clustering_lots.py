import json
import re
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import string

# Téléchargement des ressources NLTK si nécessaire
nltk.download('punkt')
nltk.download('stopwords')

# Chargement des données
with open('data/processed/normalized_corpus.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Prétraitement du texte
def preprocess_text(text):
    if text is None:
        return ""
    
    # Convertir en minuscules
    text = text.lower()
    # Supprimer la ponctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Tokenization
    tokens = word_tokenize(text)
    # Supprimer les stopwords
    stop_words = set(stopwords.words('french'))
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

# Extraction des patrons récurrents
def extract_templates(ao_data):
    templates = {
        'project': {
            'title': [],
            'description': [],
            'type': defaultdict(int),
            'cpv_codes': defaultdict(int)
        },
        'tendering_process': {
            'description': [],
            'procedure_type': defaultdict(int)
        },
        'lots': {
            'structure': defaultdict(int),
            'award_criteria': defaultdict(int)
        }
    }
    
    for ao in ao_data:
        # Project info
        project = ao['project']
        templates['project']['title'].append(project['title'])
        templates['project']['description'].append(project['description'])
        templates['project']['type'][project['type']] += 1
        for code in project['cpv_codes']:
            templates['project']['cpv_codes'][code] += 1
        
        # Tendering process
        tendering = ao['tendering_process']
        if tendering['description']:
            templates['tendering_process']['description'].append(tendering['description'])
        templates['tendering_process']['procedure_type'][tendering['procedure_type']] += 1
        
        # Lots info
        for lot in ao['lots']:
            templates['lots']['structure'][len(ao['lots'])] += 1
            for criteria in lot['award_criteria']:
                key = f"{criteria['type']}_{criteria.get('weight', '')}"
                templates['lots']['award_criteria'][key] += 1
    
    return templates

# Classification par domaine
def classify_aos(ao_data):
    # Préparation des données pour le clustering
    texts = []
    for ao in ao_data:
        text = f"{ao['project']['title']} {ao['project']['description']} {ao['project']['type']}"
        for lot in ao['lots']:
            text += f" {lot['title']} {lot['description']}"
        texts.append(preprocess_text(text))
    
    # Vectorisation avec TF-IDF
    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(texts)
    
    # Clustering avec K-means
    num_clusters = 5  # Ajuster selon les besoins
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(X)
    
    # Ajout des labels aux AO
    for i, ao in enumerate(ao_data):
        ao['domain_cluster'] = int(kmeans.labels_[i])
    
    return ao_data, vectorizer, kmeans

# Génération de statistiques
def generate_stats(ao_data):
    stats = {
        'total_aos': len(ao_data),
        'project_types': defaultdict(int),
        'procedure_types': defaultdict(int),
        'avg_lots_per_ao': 0,
        'award_criteria': defaultdict(int),
        'common_cpv_codes': defaultdict(int)
    }
    
    total_lots = 0
    
    for ao in ao_data:
        stats['project_types'][ao['project']['type']] += 1
        stats['procedure_types'][ao['tendering_process']['procedure_type']] += 1
        total_lots += len(ao['lots'])
        
        for code in ao['project']['cpv_codes']:
            stats['common_cpv_codes'][code] += 1
            
        for lot in ao['lots']:
            for criteria in lot['award_criteria']:
                key = f"{criteria['type']} (pondération: {criteria.get('weight', 'N/A')})"
                stats['award_criteria'][key] += 1
    
    stats['avg_lots_per_ao'] = total_lots / len(ao_data) if len(ao_data) > 0 else 0
    
    return stats

# Fonction pour générer des suggestions de texte
def generate_text_suggestions(templates, domain):
    suggestions = {
        'objectif': "",
        'prestations_attendues': "",
        'critères_sélection': ""
    }
    
    # Exemple simple - en pratique, on utiliserait un LLM
    suggestions['objectif'] = f"L'objectif de ce marché est de [décrire l'objectif principal]. Ce type de marché ({domain}) concerne généralement: {', '.join(list(templates['project']['type'].keys())[:3])}."
    
    suggestions['prestations_attendues'] = "Les prestations attendues incluent:\n- [Détailler les principales prestations]\n- [Préciser les livrables]\n- [Mentionner les éventuelles contraintes]"
    
    common_criteria = sorted(templates['lots']['award_criteria'].items(), key=lambda x: x[1], reverse=True)[:3]
    suggestions['critères_sélection'] = "Critères de sélection typiques:\n" + "\n".join([f"- {crit[0]} (apparaît dans {crit[1]} lots)" for crit in common_criteria])
    
    return suggestions

# Fonction principale
def main():
    # 1. Extraction des patrons
    templates = extract_templates(data)
    
    # 2. Classification des AO
    classified_data, vectorizer, kmeans = classify_aos(data)
    
    # 3. Génération des statistiques
    stats = generate_stats(classified_data)
    
    # 4. Préparation des données pour LLM
    # Création d'un DataFrame pour l'analyse
    aos_df = pd.DataFrame([{
        'filename': ao['filename'],
        'project_title': ao['project']['title'],
        'project_type': ao['project']['type'],
        'procedure_type': ao['tendering_process']['procedure_type'],
        'num_lots': len(ao['lots']),
        'domain_cluster': ao['domain_cluster'],
        'text': f"{ao['project']['title']} {ao['project']['description']}"
    } for ao in classified_data])
    
    # 5. Exemple de génération de suggestions
    domain_example = "services"  # Peut être déterminé à partir du clustering
    suggestions = generate_text_suggestions(templates, domain_example)
    
    # Sauvegarde des résultats
    results = {
        'templates': templates,
        'stats': stats,
        'suggestions_example': suggestions,
        'cluster_info': {
            'cluster_centers': kmeans.cluster_centers_.tolist(),
            'feature_names': vectorizer.get_feature_names_out().tolist()
        }
    }
    
    with open('ao_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("Analyse terminée. Résultats sauvegardés dans ao_analysis_results.json")
    
    # Affichage de quelques statistiques
    print("\nQuelques statistiques:")
    print(f"Nombre total d'AO analysés: {stats['total_aos']}")
    print(f"Types de projets: {dict(stats['project_types'])}")
    print(f"Types de procédures: {dict(stats['procedure_types'])}")
    print(f"Nombre moyen de lots par AO: {stats['avg_lots_per_ao']:.2f}")
    
    print("\nExemple de suggestions de texte:")
    for section, text in suggestions.items():
        print(f"\n{section.upper()}:\n{text}")

if __name__ == "__main__":
    main()