from fastapi import APIRouter
from pydantic import BaseModel
import requests

router = APIRouter()

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat(req: ChatRequest):
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

    reply = response.json()["message"]["content"]
    return {"reply": reply}