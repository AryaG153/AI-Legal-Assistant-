import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb

def ingest():
    """
    Ingest legal knowledge base into ChromaDB using improved embeddings.
    Uses nli-mpnet-base-v2 model for better legal document understanding.
    """
    df = pd.read_csv("legal_kb.csv")
    # Better model for legal/semantic understanding
    model = SentenceTransformer("sentence-transformers/nli-mpnet-base-v2")
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Delete existing collection and recreate to use new embeddings
    try:
        client.delete_collection("legal_kb")
    except:
        pass
    
    collection = client.get_or_create_collection("legal_kb")

    for _, row in df.iterrows():
        # Create rich text combining title and description for better embedding
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
    print(f"Ingested {len(df)} records into ChromaDB with improved embeddings")

if __name__ == "__main__":
    ingest()