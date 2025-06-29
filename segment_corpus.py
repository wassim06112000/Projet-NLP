import json
import re
import os
from pathlib import Path

def segment_lot_description(description):
    """
    Segmente la description d'un lot en sous-sections sur motif 'Poste \d+ :' ou
    listes à puces, en renvoyant une liste de segments.
    """
    # Premier niveau : split sur 'Poste X :' ou 'Poste X ' (avec ou sans deux-points)
    pattern = r"(Poste\s+\d+\s*:?)"
    parts = re.split(pattern, description)
    segments = []
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        text = parts[i+1].strip()
        segments.append({"segment_id": header, "text": text})
    
    # Si aucun split n'a été fait, retourner le texte entier
    if not segments:
        segments = [{"segment_id": "whole", "text": description.strip()}]
    return segments

def segment_corpus(input_path, output_path):
    """Charge le corpus normalisé et génère un JSONL de segments par lot."""
    with open(input_path, 'r', encoding='utf-8') as f:
        corpus = json.load(f)
    
    output = []
    for entry in corpus:
        for lot in entry["lots"]:
            segments = segment_lot_description(lot["description"])
            for seg in segments:
                output.append({
                    "filename": entry["filename"],
                    "lot_id": lot["id"],
                    "cpv_code": lot["cpv_code"],
                    "segment_id": seg["segment_id"],
                    "segment_text": seg["text"]
                })
    
    # Sauvegarde en JSONL
    Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in output:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    print(f"✅ Segmentation terminée : {len(output)} segments écrits dans {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Segmente descriptions de lots en sous-parties")
    parser.add_argument("--input", "-i", default="data/processed/normalized_corpus.json", help="Corpus normalisé JSON")
    parser.add_argument("--output", "-o", default="data/processed/segments.jsonl", help="Fichier de sortie JSONL")
    args = parser.parse_args()
    segment_corpus(args.input, args.output)
