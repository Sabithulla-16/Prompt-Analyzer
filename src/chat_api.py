from fastapi import APIRouter
from pydantic import BaseModel
import requests
import os

router = APIRouter()

OLLAMA_CHAT_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
) + "/api/chat"

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat(req: ChatRequest):
    try:
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": "qwen2:0.5b",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant for user questions."
                    },
                    {
                        "role": "user",
                        "content": req.message
                    }
                ],
                "stream": False
            },
            timeout=45
        )

        response.raise_for_status()

        data = response.json()
        reply = data.get("message", {}).get("content")

        if not reply:
            raise ValueError("Empty response from Ollama")

        return {"reply": reply}

    except Exception as e:
        # ✅ Safe fallback for Render / Cloud
        return {
            "reply": (
                "⚠️ Chat is unavailable on the hosted version.\n\n"
                "Reason: Ollama runs locally and cannot be accessed from cloud hosting.\n\n"
                "👉 To use chat, run the backend locally with Ollama running."
            )
        }