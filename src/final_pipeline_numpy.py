import os
import json
import numpy as np
import requests
from datetime import datetime

from src.intent_extractor import extract_intent
from src.prompt_rewriter import rewrite_prompt
from src.filter_tools import filter_tools
from src.moderation import is_safe

# ================= PATH SETUP =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

TOOLS_FILE = os.path.join(DATA_DIR, "tools_seed.json")
EMBED_FILE = os.path.join(DATA_DIR, "tool_embeddings.npy")
ID_FILE = os.path.join(DATA_DIR, "tool_ids.json")
BAD_PROMPT_LOG = os.path.join(DATA_DIR, "bad_prompts.log")
FEEDBACK_LOG = os.path.join(DATA_DIR, "user_feedback.jsonl")

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"

# ================= LOAD DATA =================

with open(TOOLS_FILE, "r", encoding="utf-8") as f:
    tools = json.load(f)

tool_map = {t["id"]: t for t in tools}
tool_embeddings = np.load(EMBED_FILE)

with open(ID_FILE, "r", encoding="utf-8") as f:
    tool_ids = json.load(f)

# ================= CACHE =================
EMBED_CACHE = {}

# ================= UTILS =================

def cosine_similarity(matrix, vector):
    matrix = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    vector = vector / np.linalg.norm(vector)
    return np.dot(matrix, vector)

def embed_prompt(prompt: str):
    if prompt in EMBED_CACHE:
        return EMBED_CACHE[prompt]

    try:
        res = requests.post(
            OLLAMA_EMBED_URL,
            json={"model": "nomic-embed-text", "prompt": prompt},
            timeout=None
        )
        res.raise_for_status()

        emb = res.json().get("embedding")
        if not emb:
            return None

        vec = np.array(emb, dtype="float32")
        EMBED_CACHE[prompt] = vec
        return vec

    except Exception as e:
        print("⚠️ Embedding failed:", e)
        return None

# ================= MAIN PIPELINE =================

def recommend_tools(prompt: str, top_k: int = 5):
    print("➡️ User prompt:", prompt)

    # ---------- MODERATION ----------
    if not is_safe(prompt):
        return {
            "original_prompt": prompt,
            "rewritten_prompt": "",
            "confidence": 0.0,
            "confidence_breakdown": {},
            "needs_followup": True,
            "warning": "This request contains restricted content.",
            "tools": []
        }

    # ---------- PROMPT REWRITE ----------
    rewritten = rewrite_prompt(prompt)
    rewrite_failed = rewritten.strip().lower() == prompt.strip().lower()
    print("✏️ Rewritten prompt:", rewritten)

    # ---------- INTENT ----------
    intent = extract_intent(rewritten)

    # ---------- TOOL FILTER ----------
    filtered = filter_tools(intent, tools)
    fallback_used = False

    if not filtered:
        filtered = tools
        fallback_used = True

    filtered_ids = {t["id"] for t in filtered}

    # ---------- EMBEDDINGS ----------
    query_vec = embed_prompt(rewritten)

    results = []
    semantic_score = 0.0

    if query_vec is not None:
        scores = cosine_similarity(tool_embeddings, query_vec)
        ranked = np.argsort(scores)[::-1]

        for idx in ranked:
            tool_id = tool_ids[idx]
            if tool_id in filtered_ids:
                tool = tool_map[tool_id]

                score = float(scores[idx])
                score = max(0.0, min(score, 1.0))  # hard clamp

                results.append({
                    "id": tool["id"],
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "domain": tool["domain"],
                    "actions": tool.get("actions", []),
                    "use_cases": tool.get("use_cases", []),
                    "pricing": tool.get("pricing", "N/A"),
                    "api_available": tool.get("api_available", False),
                    "website": tool.get("website"),
                    "tags": tool.get("tags", []),
                    "score": round(score, 3)
                })

            if len(results) == top_k:
                break

        semantic_score = results[0]["score"] if results else 0.0

    else:
        results = [
            {
                "id": t["id"],
                "name": t["name"],
                "description": t.get("description", ""),
                "domain": t["domain"],
                "actions": t.get("actions", []),
                "use_cases": t.get("use_cases", []),
                "pricing": t.get("pricing", "N/A"),
                "api_available": t.get("api_available", False),
                "website": t.get("website"),
                "tags": t.get("tags", []),
                "score": 0.0
            }
            for t in filtered[:top_k]
        ]

    # ---------- CONFIDENCE BREAKDOWN ----------
    intent_score = 1.0 if intent.get("action") else 0.4
    domain_score = 0.9 if intent.get("domain") else 0.5

    confidence = round(
        (semantic_score * 0.6 + intent_score * 0.25 + domain_score * 0.15) * 100,
        1
    )

    confidence = min(confidence, 100.0)

    confidence_breakdown = {
        "semantic_similarity": round(semantic_score * 100, 1),
        "intent_match": round(intent_score * 100, 1),
        "domain_match": round(domain_score * 100, 1)
    }

    # ---------- FOLLOW-UP QUESTIONS ----------
    follow_up_questions = []
    needs_followup = confidence < 40

    if needs_followup:
        follow_up_questions = [
            "What output do you want (text, image, audio, video)?",
            "Is this for personal or professional use?",
            "Do you prefer free tools only?"
        ]

    # ---------- LOG BAD PROMPTS ----------
    if fallback_used or needs_followup or rewrite_failed:
        with open(BAD_PROMPT_LOG, "a", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow().isoformat()} | {prompt}\n")

    print(
        f"📊 Confidence: {confidence}% | "
        f"Semantic: {confidence_breakdown['semantic_similarity']} | "
        f"Fallback: {fallback_used}"
    )

    return {
        "original_prompt": prompt,
        "rewritten_prompt": rewritten,
        "intent": intent,
        "confidence": confidence,
        "confidence_breakdown": confidence_breakdown,
        "needs_followup": needs_followup,
        "follow_up_questions": follow_up_questions,
        "fallback_used": fallback_used,
        "prompt_suggestions": [
            "Convert my voice recording into text",
            "Create a professional logo for my startup",
            "Write Python code",
            "Make Instagram reels automatically",
            "Summarize a research paper"
        ],
        "tools": results
    }