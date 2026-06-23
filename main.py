from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from retriever import retrieve
from groq import Groq
from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import os

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

groq_client = Groq(api_key="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")
mongo = MongoClient("mongodb+srv://ailegalassistant0_db_user:<summerproject2026>@cluster0.1ezfrwn.mongodb.net/?appName=Cluster0", tlsAllowInvalidCertificates=True)
db = mongo["legal_assistant"]
collection = db["queries"]

ROOT_DIR = Path(__file__).resolve().parent

@app.get("/", response_class=FileResponse)
def read_root():
    return FileResponse(ROOT_DIR / "dashboard.html")

@app.get("/{file_path:path}", response_class=FileResponse)
def serve_file(file_path: str):
    safe_path = (ROOT_DIR / file_path).resolve()
    if not str(safe_path).startswith(str(ROOT_DIR)):
        raise HTTPException(status_code=404, detail="Not Found")
    if safe_path.is_file():
        return FileResponse(safe_path)
    raise HTTPException(status_code=404, detail="Not Found")

class Query(BaseModel):
    question: str

@app.post("/ask")
def ask(query: Query):
    """
    Answer legal questions using RAG with improved retrieval and structured responses.
    """
    question = query.question.lower().strip()
    
    # Retrieve relevant laws with distance threshold
    results = retrieve(question, top_k=5, similarity_threshold=50.0)

    laws = results["documents"][0] if results["documents"][0] else []
    metas = results["metadatas"][0] if results["metadatas"][0] else []

    # If no relevant laws found
    if not laws:
        answer = "I don't have information on this topic in my legal knowledge base. Please consult a qualified lawyer for accurate legal advice."
        return {
            "answer": answer,
            "laws": [],
            "confidence": "low",
            "disclaimer": "This is general information, not legal advice."
        }

    # Build context with law references
    context = "\n".join([
        f"- {m['title']}: {d}" 
        for m, d in zip(metas, laws)
    ])

    # Improved prompt with structured output
    prompt = f"""You are an expert Indian legal assistant. Answer the user's question ONLY based on the following laws.

RELEVANT LAWS:
{context}

USER QUESTION: {question}

Provide your answer in the following format:

1. **Applicable Law**: [Cite the specific section/article]

2. **Your Rights**: [Explain what rights the person has based on the law]

3. **What to Do**: [List actionable steps they can take]

4. **Important Note**: [Any conditions, exceptions, or limitations]

Keep the explanation simple and clear. Avoid legal jargon where possible.

---
DISCLAIMER: This is general legal information, not professional legal advice. Always consult a qualified lawyer for your specific situation."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    # Optional: Log to MongoDB
    #collection.insert_one({
    #    "query": question,
    #    "retrieved_laws": [m['title'] for m in metas],
    #    "response": answer,
    #    "timestamp": datetime.now()
    #})

    return {
        "answer": answer,
        "laws": [m['title'] for m in metas],
        "confidence": "high" if metas else "low",
        "disclaimer": "This is general information, not legal advice. Consult a lawyer for your specific situation."
    }