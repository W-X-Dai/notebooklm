from backend import db
from backend.api import ollama_embedding
from backend.rag import rag_pipeline

text = "Andy is a software engineer. He works at a tech company and enjoys coding in Python."
emb = ollama_embedding(text, model="nomic-embed-text:v1.5")
db.add_document("doc_andy", text, emb)

question = "What does Andy do for a living?"
print("\n[問題] ", question)
rag_pipeline(question, top_k=1)

print("All IDs:", db.collection.get()["ids"])
db.collection.delete(ids=["doc_andy"])
db.collection.delete(ids=["doc_ai"])