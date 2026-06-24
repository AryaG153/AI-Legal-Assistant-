import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb

def ingest_collection(csv_path: str, collection_name: str):
    if not os.path.exists(csv_path):
        print(f"Skipping ingestion: {csv_path} not found.")
        return 0

    df = pd.read_csv(csv_path)
    model = SentenceTransformer("sentence-transformers/nli-mpnet-base-v2")
    client = chromadb.PersistentClient(path="./chroma_db")

    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.get_or_create_collection(collection_name)
    for _, row in df.iterrows():
        text = f"{row['title']}. {row['description']}"
        embedding = model.encode(text).tolist()
        collection.add(
            ids=[str(row['id'])],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "category": row['category'],
                "title": row['title'],
                "id": str(row['id'])
            }]
        )

    return len(df)


def ingest():
    legal_count = ingest_collection("legal_kb.csv", "legal_kb")
    knowledge_hub_count = ingest_collection("knowledge_hub.csv", "knowledge_hub")

    print(f"Ingested {legal_count} records into legal_kb collection")
    print(f"Ingested {knowledge_hub_count} records into knowledge_hub collection")


if __name__ == "__main__":
    ingest()
