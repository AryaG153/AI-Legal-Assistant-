import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb

def ingest():
    df = pd.read_csv("data/legal_kb.csv")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection("legal_kb")

    for _, row in df.iterrows():
        text = f"{row['title']}. {row['description']}"
        embedding = model.encode(text).tolist()
        collection.add(
            ids=[str(row['id'])],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"category": row['category'], "title": row['title']}]
        )
    print(f"Ingested {len(df)} records into ChromaDB")

if __name__ == "__main__":
    ingest()