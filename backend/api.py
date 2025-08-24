"""
API module using Ollama
"""

import requests
import json

OLLAMA_API_URL = "http://localhost:11434"

def ollama_generation(prompt, model="gpt-oss:latest"):
    """
    Generate text using Ollama API
    """
    url = f"{OLLAMA_API_URL}/api/generate"

    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "n": 1,
        "stream": False
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        result = response.json()
        return result.get("response", "")
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")
    
def ollama_embedding(text, model="nomic-embed-text:v1.5"):
    """
    Get text embedding using Ollama API
    """
    url = f"{OLLAMA_API_URL}/api/embed"

    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "input": text
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        result = response.json()
        return result.get("embeddings", [])
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")
