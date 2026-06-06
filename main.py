import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

# Import your existing chain functions
from rag_Chain import stream_answer, retriever

load_dotenv()

app = FastAPI()

# Allow frontend to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Request Models ----
class ChatRequest(BaseModel):
    question: str
    session_id: str = "default_session"

# ---- Chat Endpoint with SSE ----
@app.post("/chat")
async def chat(req: ChatRequest):
    async def event_generator():
        for event in stream_answer(req.question, req.session_id):
            if event["type"] == "token":
                yield {
                    "data": json.dumps({"token": event["value"]})
                }
            elif event["type"] == "sources":
                yield {
                    "data": json.dumps({"sources": event["value"]})
                }
            elif event["type"] == "done":
                yield {
                    "data": "[DONE]"
                }

    return EventSourceResponse(event_generator())

# ---- Health Check ----
@app.get("/")
def root():
    return {"status": "RAG backend running"}

from pydantic import BaseModel

class IngestRequest(BaseModel):
    youtube_url: str
    instagram_url: str

@app.post("/ingest")
async def ingest(req: IngestRequest):
    # For now return hardcoded data to test the frontend
    # Later wire to your real ingestion pipeline
    return {
        "video_A": {
            "platform": "youtube",
            "creator": "English At The Ready",
            "views": 32703,
            "likes": 2176,
            "comments": 95,
            "engagement_rate": 6.94,
            "upload_date": "2026-05-29T19:53:01Z",
            "hashtags": [],
            "title": "Stop Saying ME TOO"
        },
        "video_B": {
            "platform": "instagram",
            "creator": "mercythaddeus_",
            "views": 8337,
            "likes": 587,
            "comments": 683,
            "engagement_rate": 15.23,
            "upload_date": "2026-02-27T18:41:24",
            "hashtags": ["ai", "aitools", "transcription"],
            "followers_count": 174495
        }
    }