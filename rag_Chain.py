import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List

os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN", "")
load_dotenv()
Google_API_KEY=os.getenv("GOOGLE_API_KEY", "")


# ---- ChromaDB Connection ----
chroma_client = chromadb.PersistentClient(path="./chroma_db")

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    encode_kwargs={"normalize_embeddings": True},
)

vectorstore = Chroma(
    collection_name="videos",
    embedding_function=embeddings,
    client=chroma_client,
)

retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 6, "fetch_k": 20}
)

# ---- LLM ----
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0.3,
    google_api_key=Google_API_KEY
)



from typing_extensions import TypedDict
# ---- State ----
class State(TypedDict):
    question: str
    metadata: List[dict]
    context: str
    answer: str

# ---- Nodes ----
def retrieve_node(state: State):
    print("Retrieving from ChromaDB...")
    docs = retriever.invoke(state["question"])

    context = "\n\n".join(
        f"[Video {doc.metadata.get('video_id')} - Chunk {doc.metadata.get('chunk_index')}]\n{doc.page_content}"
        for doc in docs
    )

    metadata = [doc.metadata for doc in docs]

    return {
        "metadata": metadata,
        "context": context
    }

def answer_node(state: State):
    prompt = f"""
You are a social media analytics expert.
You have data for two videos:
- Video A (YouTube)
- Video B (Instagram Reel)

Rules:
- Answer ONLY using the provided context and metadata
- Always cite which video your answer comes from like this: [Video A] or [Video B]
- If the answer is not in the context, say "I don't have that information"
- Be specific and analytical, not generic

Question:
{state['question']}

Retrieved Context:
{state['context']}

Metadata:
{state['metadata']}
"""

    response = llm.invoke(prompt)

    # Clean response — strip signature/extras Gemini sometimes returns
    content = response.content
    if isinstance(content, list):
        content = " ".join(
            item["text"] for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    return {"answer": content}

# ---- Build Graph ----
graph = StateGraph(State)
graph.add_node("retrieve", retrieve_node)
graph.add_node("answer", answer_node)

graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "answer")
graph.add_edge("answer", END)

from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# ---- Test Questions ----
questions = [
    "Why did Video A get more engagement than Video B?",
    "What's the engagement rate of each?",
    "Compare the hooks in the first 5 seconds.",
    "Who's the creator of Video B and what's their follower count?",
    "Suggest improvements for Video B based on what worked in Video A."
]

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "session_1"}}
    for question in questions:
        print(f"\n{'='*60}")
        print(f"Q: {question}")
        print(f"{'='*60}")

        result = app.invoke({"question": question})

        print(f"A: {result['answer']}")

        print("\nSources:")
        for source in result["metadata"]:
            print(f"  Video {source.get('video_id')} | "
                  f"Chunk {source.get('chunk_index')} | "
                  f"Platform: {source.get('platform')} | "
                  f"Creator: {source.get('creator')}")





#SSE function to stream LLM response in real-time

def stream_answer(question: str, session_id: str):
    
    # Retrieve from both videos separately to guarantee coverage
    docs_a = vectorstore.similarity_search(
        question, k=3,
        filter={"video_id": "A"}
    )
    docs_b = vectorstore.similarity_search(
        question, k=3,
        filter={"video_id": "B"}
    )
    docs = docs_a + docs_b

    context = "\n\n".join(
        f"[Video {doc.metadata.get('video_id')} - Chunk {doc.metadata.get('chunk_index')}]\n{doc.page_content}"
        for doc in docs
    )

    sources = [
        {
            "video_id": doc.metadata.get("video_id"),
            "chunk_index": doc.metadata.get("chunk_index"),
            "platform": doc.metadata.get("platform"),
            "creator": doc.metadata.get("creator"),
            "preview": doc.page_content[:120]
        }
        for doc in docs
    ]

    # rest of your streaming code stays exactly the same

    # Step 2: Build prompt
    prompt = f"""
You are a social media analytics expert.
You have data for two videos:
- Video A (YouTube)
- Video B (Instagram Reel)

Rules:
- Answer ONLY using the provided context and metadata
- Always cite which video your answer comes from like this: [Video A] or [Video B]
- If the answer is not in the context, say "I don't have that information"
- Be specific and analytical

Question:
{question}

Retrieved Context:
{context}
"""

    # Step 3: Stream tokens from Gemini
    for chunk in llm.stream(prompt):
        content = chunk.content

        # Clean if list format
        if isinstance(content, list):
            content = " ".join(
                item["text"] for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            )

        if content:
            yield {"type": "token", "value": content}

    # Step 4: Send sources after all tokens
    yield {"type": "sources", "value": sources}

    # Step 5: Signal done
    yield {"type": "done"}