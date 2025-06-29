import json
import os
import re
from pathlib import Path

def infer_project_type(cpv_codes):
    """Infère le type de projet à partir du préfixe CPV."""
    if not cpv_codes:
        return "other"
    prefix = cpv_codes[0][:2]
    if prefix in ("45", "71"):
        return "works"
    if prefix in ("15", "30"):
        return "supplies"
    if prefix in ("72", "79"):
        return "services"
    return "other"

def normalize_entry(entry):
    """Nettoie et normalise un appel d'offres (AO)."""
    proj = entry.get("project", {})
    # Inférer project.type si manquant
    if not proj.get("type") or proj.get("type") not in ("supplies","services","works","other"):
        proj["type"] = infer_project_type(proj.get("cpv_codes", []))
    # Normaliser estimated_value et currency
    if proj.get("estimated_value") in (None, "", "null"):
        proj["estimated_value"] = 0
    if not proj.get("currency"):
        proj["currency"] = "EUR"
    entry["project"] = proj

    clean_lots = []
    for lot in entry.get("lots", []):
        # Nettoyage description
        desc = lot.get("description") or ""
        lot["description"] = re.sub(r'\s+', ' ', desc).strip()

        # estimated_value pour lot
        ev = lot.get("estimated_value")
        lot["estimated_value"] = float(ev) if ev not in (None, "", "null") else 0

        # currency
        lot["currency"] = lot.get("currency") or "EUR"

        # award_criteria par défaut si vide
        if not lot.get("award_criteria"):
            lot["award_criteria"] = [{
                "type": "cost",
                "description": "Coût (par défaut)",
                "weight": 100
            }]

        clean_lots.append(lot)
    entry["lots"] = clean_lots
    return entry

def clean_and_normalize(input_path, output_path):
    """Charge, normalise et sauvegarde le corpus."""
    with open(input_path, 'r', encoding='utf-8') as f:
        corpus = json.load(f)

    cleaned = [normalize_entry(e) for e in corpus if e.get("lots")]

    # Création dossier sortie
    Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"✅ Corpus nettoyé : {len(cleaned)} AO sauvegardés dans {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Nettoyage et normalisation du corpus AO")
    parser.add_argument("--input", "-i", default="data/corpus_boamp_mars2025.json", help="Fichier JSON brut")
    parser.add_argument("--output", "-o", default="data/processed/normalized_corpus.json", help="Fichier JSON nettoyé")
    args = parser.parse_args()

    clean_and_normalize(args.input, args.output)

