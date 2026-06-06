# RAG Video Analyzer

A full-stack RAG chatbot that analyzes YouTube and Instagram Reels.
Paste two video URLs, get instant analytics, and ask questions about performance.

## Tech Stack
- Frontend: Next.js + Tailwind
- Backend: FastAPI + SSE streaming
- Orchestration: LangGraph
- Embeddings: BAAI/bge-base-en-v1.5 (HuggingFace)
- Vector DB: ChromaDB
- LLM: Gemini 3.5 Flash
- Transcripts: youtube-transcript-api + Whisper

## Why These Choices
(write this yourself — chunk size, vector DB, LLM reasoning)

## Setup
1. Clone the repo
2. Copy .env.example to .env and fill in your keys
3. Install backend: pip install -r requirements.txt
4. Install frontend: cd frontend && npm install
5. Run backend: uvicorn main:app --reload --port 8000
6. Run frontend: npm run dev

## Cost at Scale
(write your scalability reasoning here)