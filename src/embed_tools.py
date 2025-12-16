import json
import requests
import numpy as np

TOOLS_FILE = "data/tools_seed.json"
EMBED_FILE = "data/tool_embeddings.npy"
ID_FILE = "data/tool_ids.json"

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"

def get_embedding(text):
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": "nomic-embed-text",
            "prompt": text
        },
        timeout=60
    )
    response.raise_for_status()
    return np.array(response.json()["embedding"], dtype="float32")


# Load tools
with open(TOOLS_FILE, "r") as f:
    tools = json.load(f)

embeddings = []
tool_ids = []

print("🔄 Generating embeddings...")

for i, tool in enumerate(tools, start=1):
    embed_text = (
        f"{tool['name']} "
        f"{tool['description']} "
        f"{' '.join(tool['use_cases'])} "
        f"{' '.join(tool['tags'])}"
    )

    vector = get_embedding(embed_text)
    embeddings.append(vector)
    tool_ids.append(tool["id"])

    print(f"✅ {i}/{len(tools)} Embedded: {tool['name']}")

np.save(EMBED_FILE, np.vstack(embeddings))

with open(ID_FILE, "w") as f:
    json.dump(tool_ids, f)

print("🎉 All tool embeddings generated successfully")