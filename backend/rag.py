"""
Rag module
"""

import json
import requests
from backend.db import search
from backend.api import ollama_embedding

OLLAMA_API_URL = "http://localhost:11434"

def rag_pipeline(question, embed_model="nomic-embed-text:v1.5", llm_model="gpt-oss:latest", top_k=3):
    # 1. embedding input question
    q_emb = ollama_embedding(question, model=embed_model)

    # 2. search relevant documents
    results = search(q_emb, top_k=top_k)
    if results is None or "documents" not in results or not results["documents"]:
        context = ""
    else:
        context = "\n".join(results["documents"][0])

    # 3. generate answer with context
    prompt = f"Answer the question based on the following context in Chinese:\n\n{context}\n\nQuestion: {question}"

    url = f"{OLLAMA_API_URL}/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {"model": llm_model, "prompt": prompt}

    r = requests.post(url, headers=headers, data=json.dumps(payload), stream=True)

    answer = ""
    # stream output
    for line in r.iter_lines():
        if line:
            answer += json.loads(line)["response"]
    return answer

