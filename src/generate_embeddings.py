import os
import json
import numpy as np
import requests

# ================= CONFIG =================

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

TOOLS_FILE = os.path.join(DATA_DIR, "tools_seed.json")
EMBED_FILE = os.path.join(DATA_DIR, "tool_embeddings.npy")
ID_FILE = os.path.join(DATA_DIR, "tool_ids.json")

os.makedirs(DATA_DIR, exist_ok=True)

# ================= LOAD TOOLS =================

with open(TOOLS_FILE, "r", encoding="utf-8") as f:
    tools = json.load(f)

print(f"🔧 Loaded {len(tools)} tools")

# ================= EMBEDDING FUNCTION =================

def embed_text(text: str):
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": EMBED_MODEL,
            "prompt": text
        },
        timeout=30
    )
    response.raise_for_status()
    return response.json()["embedding"]

# ================= GENERATE =================

embeddings = []
tool_ids = []

for tool in tools:
    text = f"""
    {tool['name']}.
    {tool.get('description', '')}.
    Domain: {tool['domain']}.
    Actions: {', '.join(tool['actions'])}.
    Use cases: {', '.join(tool['use_cases'])}.
    Tags: {', '.join(tool.get('tags', []))}.
    """

    print(f"🧠 Embedding: {tool['name']}")

    emb = embed_text(text)
    embeddings.append(emb)
    tool_ids.append(tool["id"])

# ================= SAVE =================

np.save(EMBED_FILE, np.array(embeddings, dtype="float32"))

with open(ID_FILE, "w", encoding="utf-8") as f:
    json.dump(tool_ids, f, indent=2)

print("✅ Embeddings generated successfully")
print("📁 tool_embeddings.npy updated")
print("📁 tool_ids.json updated")