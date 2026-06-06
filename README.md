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
I have kept chunk size=500 overlap=50 to standard number that will break down the text into reasonable chunks and also will not lose focus on meaning,
Langgraph is used because I wanted the conversation to have a memory attached to it and BGE is used because it's free and better than open AI.
Gemini is used as an LLM because it is better than Ollama can support upto 1M Tokkens and it's also free,cost effective.


## Setup
1. Clone the repo
2. Copy .env.example to .env and fill in your keys
3. Install backend: pip install -r requirements.txt
4. Install frontend: cd frontend && npm install
5. Run backend: uvicorn main:app --reload --port 8000
6. Run frontend: npm run dev

## Cost at Scale

The project was built with scalability and cost efficiency in mind. For embeddings, I used BAAI/bge-base-en-v1.5, an open-source model that can be run locally without any per-request charges. This allows transcript embeddings to be generated once and reused for future queries, significantly reducing operational costs.

For answer generation, the system uses Gemini. During development, Gemini's free tier was sufficient for testing and experimentation, making it a practical choice for a student project. Since only the most relevant transcript chunks are retrieved from ChromaDB and sent to the model, token usage remains relatively low compared to sending entire transcripts.

At a small scale, the application can run on a single machine with ChromaDB stored locally, resulting in minimal infrastructure costs. As usage grows, the backend can be deployed to cloud services and the vector database can be migrated to a managed solution without major architectural changes.

Overall, the combination of local embeddings, vector-based retrieval, and Gemini-powered responses provides a good balance between performance, scalability, and cost, making the system suitable for both prototype development and larger deployments.
