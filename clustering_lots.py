import json
import pandas as pd
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

# Charger les données
with open("data/processed/normalized_corpus.json", "r", encoding="utf-8") as f:
    ao_data = json.load(f)

# Extraire les descriptions
descriptions = []
meta_infos = []

for entry in ao_data:
    ao_type = entry.get("project", {}).get("type", "unknown")
    for lot in entry.get("lots", []):
        desc = lot.get("description", "")
        if isinstance(desc, str) and len(desc.strip()) > 30:
            descriptions.append(desc.strip())
            meta_infos.append({
                "ao_type": ao_type,
                "title": lot.get("title", ""),
                "description": desc.strip()
            })

# Encoder les descriptions
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(descriptions, show_progress_bar=True)

# Clustering
n_clusters = 7
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
clusters = kmeans.fit_predict(embeddings)

# Résultats
for i, meta in enumerate(meta_infos):
    meta["cluster"] = int(clusters[i])

df = pd.DataFrame(meta_infos)
df.to_csv("clustered_lots_embeddings.csv", index=False, encoding="utf-8")
print(df.groupby("cluster").size())
