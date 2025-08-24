"""
Database module using ChromaDB
"""

import chromadb

client = chromadb.PersistentClient(path="data/chroma")
collection = client.get_or_create_collection("docs")


def add_document(doc_id, text, embedding):
    """
    Add a document to the ChromaDB collection
    """     
    collection.add(
        ids=[doc_id],
        documents=[text],
        embeddings=embedding
    )
    print(f"Document {doc_id} added.")


def search(query_embedding, top_k=5):
    """
    Search for the most relevant document fragments
    """
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    return results
