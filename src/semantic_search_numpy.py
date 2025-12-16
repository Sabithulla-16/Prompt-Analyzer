import numpy as np
import json
import requests

# ---------- FILES ----------
EMBED_FILE = "data/tool_embeddings.npy"
ID_FILE = "data/tool_ids.json"

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"

# ---------- LOAD TOOL EMBEDDINGS ----------
tool_embeddings = np.load(EMBED_FILE)

with open(ID_FILE, "r") as f:
    tool_ids = json.load(f)

# ---------- COSINE SIMILARITY ----------
def cosine_similarity(a, b):
    a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b)
    return np.dot(a_norm, b_norm)

# ---------- EMBED USER PROMPT ----------
def embed_prompt(prompt):
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": "nomic-embed-text",
            "prompt": prompt
        },
        timeout=60
    )
    response.raise_for_status()
    return np.array(response.json()["embedding"], dtype="float32")

# ---------- SEMANTIC SEARCH ----------
def semantic_search(prompt, top_k=5):
    query_vec = embed_prompt(prompt)
    scores = cosine_similarity(tool_embeddings, query_vec)

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            "tool_id": tool_ids[idx],
            "similarity": round(float(scores[idx]), 3)
        })

    return results


# ---------- TEST ----------
if __name__ == "__main__":
    prompt = "Create a professional logo for my startup"
    results = semantic_search(prompt)

    print("\n🔍 Semantic Matches:")
    for r in results:
        print(r)