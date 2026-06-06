import chromadb
from langchain_huggingface import HuggingFaceEmbeddings

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("videos")

print(f"Total documents: {collection.count()}")

# Print all documents directly without querying
results = collection.get()

for doc, meta in zip(results["documents"], results["metadatas"]):
    print(f"\nVideo {meta.get('video_id')} | Chunk {meta.get('chunk_index')}")
    print(doc[:300])
    print("---")