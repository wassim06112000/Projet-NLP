
import json
import re
from collections import defaultdict, Counter
import pandas as pd

def load_normalized_data(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def group_descriptions_by_type(data):
    grouped = defaultdict(list)
    for entry in data:
        ao_type = entry.get("project", {}).get("type", "unknown")
        for lot in entry.get("lots", []):
            desc = lot.get("description", "")
            if isinstance(desc, str) and len(desc.strip()) > 30:
                grouped[ao_type].append(desc.strip())
    return grouped

def extract_frequent_phrases(descriptions, top_n=10):
    sentences = []
    for desc in descriptions:
        chunks = re.split(r"[.:]", desc)
        sentences += [s.strip() for s in chunks if len(s.strip()) > 30]
    counter = Counter(sentences)
    return counter.most_common(top_n)

def generate_templates_by_type(grouped_data, top_n=10):
    template_data = []
    for ao_type, descs in grouped_data.items():
        phrases = extract_frequent_phrases(descs, top_n)
        for phrase, count in phrases:
            template_data.append({
                "ao_type": ao_type,
                "phrase": phrase,
                "count": count
            })
    return pd.DataFrame(template_data)

# Exemple d'utilisation :
if __name__ == "__main__":
    data = load_normalized_data("data/processed/normalized_corpus.json")
    grouped = group_descriptions_by_type(data)
    df = generate_templates_by_type(grouped, top_n=10)
    print(df)
