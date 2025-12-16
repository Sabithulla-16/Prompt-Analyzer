from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.final_pipeline_numpy import recommend_tools, tool_map
from src.chat_api import router as chat_router

app = FastAPI(title="AI Tool Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(chat_router)

class PromptRequest(BaseModel):
    prompt: str

@app.post("/recommend")
def recommend(req: PromptRequest):
    return recommend_tools(req.prompt)

@app.post("/feedback")
def tool_feedback(data: dict):
    with open("data/user_feedback.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")
    return {"status": "recorded"}

@app.get("/tool/{tool_id}")
def get_tool(tool_id: str):
    tool = tool_map.get(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool