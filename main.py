from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from retriever import retrieve
from groq import Groq
from pymongo import MongoClient
from datetime import datetime
import os

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

groq_client = Groq(api_key="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")
mongo = MongoClient("mongodb+srv://ailegalassistant0_db_user:<summerproject2026>@cluster0.1ezfrwn.mongodb.net/?appName=Cluster0", tlsAllowInvalidCertificates=True)
db = mongo["legal_assistant"]
collection = db["queries"]

class Query(BaseModel):
    question: str

@app.post("/ask")
def ask(query: Query):
    question = query.question.lower().strip()
    results = retrieve(question)

    laws = results["documents"][0]
    metas = results["metadatas"][0]

    context = "\n".join([f"- {m['title']}: {d}" for m, d in zip(metas, laws)])

    prompt = f"""You are an Indian legal assistant. Based on the following laws, answer the user's question clearly and simply.

Relevant Laws:
{context}

User Question: {question}

Give a clear explanation of their rights and what legal actions they can take."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    #collection.insert_one({
     #   "query": question,
      #  "retrieved_laws": [m['title'] for m in metas],
      #  "response": answer,
       # "timestamp": datetime.now()
   # })

    return {"answer": answer, "laws": [m['title'] for m in metas]}