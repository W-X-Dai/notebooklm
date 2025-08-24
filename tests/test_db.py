from backend.api import ollama_embedding
from backend.db import add_document, search

# add a document
doc_text = "人工智慧正在改變世界"
doc_emb = ollama_embedding(doc_text)
add_document("doc1", doc_text, doc_emb)

# search
query = "AI 的影響"
query_emb = ollama_embedding(query)
results = search(query_emb)

print("檢索結果:", results["documents"])
