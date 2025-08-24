from backend import api

response = api.ollama_generation("Hello, world!")
vec = api.ollama_embedding("Hello, world!")

print("Generation Response:", response)
print("Embedding Vector:", vec)