#!/usr/bin/env python3
# src/validate_schema.py

import json
import os
import sys
from jsonschema import validate, ValidationError

# Chemins par défaut (ajustez si nécessaire)
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
SCHEMA_PATH = os.path.join(ROOT_DIR, "schema.json")
CORPUS_PATH = os.path.join(ROOT_DIR, "outputs", "corpus_boamp_mars2025.json")

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def main(corpus_path=None, schema_path=None):
    corpus_path = corpus_path or CORPUS_PATH
    schema_path = schema_path or SCHEMA_PATH

    # 1. Charger le schéma
    try:
        schema = load_json(schema_path)
    except Exception as e:
        print(f"Erreur de lecture du schéma : {e}")
        sys.exit(1)

    # 2. Charger le corpus
    try:
        corpus = load_json(corpus_path)
    except Exception as e:
        print(f"Erreur de lecture du corpus : {e}")
        sys.exit(1)

    # 3. Validation
    valid_count = 0
    invalid_count = 0

    for idx, ao in enumerate(corpus, start=1):
        filename = ao.get("filename", f"entry#{idx}")
        try:
            validate(instance=ao, schema=schema)
            print(f"[VALID]   {filename}")
            valid_count += 1
        except ValidationError as e:
            print(f"[INVALID] {filename} → {e.message}")
            invalid_count += 1

    # 4. Bilan
    print("\n=== Résultat ===")
    print(f"Total entrées : {len(corpus)}")
    print(f"Validées      : {valid_count}")
    print(f"Échouées      : {invalid_count}")

if __name__ == "__main__":
    # Optionnel : permettre de passer en argument un chemin de corpus ou de schéma
    import argparse
    parser = argparse.ArgumentParser(description="Valide chaque AO d'un corpus JSON contre schema.json")
    parser.add_argument("--corpus", help="Chemin vers le fichier JSON du corpus")
    parser.add_argument("--schema", help="validate_schema.py")
    args = parser.parse_args()

    main(corpus_path=args.corpus, schema_path=args.schema)
