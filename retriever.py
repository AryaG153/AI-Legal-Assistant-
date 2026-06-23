from sentence_transformers import SentenceTransformer
import chromadb

# Using semantic model for better legal document retrieval
model = SentenceTransformer("sentence-transformers/nli-mpnet-base-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("legal_kb")

def retrieve(query: str, top_k: int = 5, similarity_threshold: float = 50.0):
    """
    Retrieve relevant legal documents based on query.
    
    Args:
        query: User's legal question
        top_k: Number of results to retrieve (default: 5)
        similarity_threshold: Minimum distance score (0-1). Default: 0.3
    
    Returns:
        Filtered results with only documents below distance threshold
    """
    query = query.lower().strip()
    embedding = model.encode(query).tolist()
    
    # Get results from ChromaDB
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    # ChromaDB returns distances (lower is better for cosine distance)
    # Filter by threshold
    if results["distances"] and len(results["distances"]) > 0:
        filtered_docs = []
        filtered_metas = []
        filtered_distances = []
        
        for dist, doc, meta in zip(
            results["distances"][0],
            results["documents"][0],
            results["metadatas"][0]
        ):
            # Only include if below distance threshold (lower distance = higher relevance)
            if dist <= similarity_threshold:
                filtered_docs.append(doc)
                filtered_metas.append(meta)
                filtered_distances.append(dist)
        
        # If no results pass threshold, return top result anyway
        if not filtered_docs and results["documents"][0]:
            filtered_docs = results["documents"][0][:1]
            filtered_metas = results["metadatas"][0][:1]
            filtered_distances = [results["distances"][0][0]]
        
        return {
            "documents": [filtered_docs],
            "metadatas": [filtered_metas],
            "distances": [filtered_distances]
        }
    
    return results