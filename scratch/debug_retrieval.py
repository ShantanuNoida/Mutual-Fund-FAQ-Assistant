import os
import sys
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DB_DIR = os.path.join(BASE_DIR, "Phase_1_Data_Ingestion", "chroma_db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def debug_retrieval(query):
    print(f"\n--- DEBUGGING RETRIEVAL FOR: '{query}' ---")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    if not os.path.exists(CHROMA_DB_DIR):
        print(f"Error: ChromaDB not found at {CHROMA_DB_DIR}")
        return

    vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)
    results = vectorstore.similarity_search(query, k=5)
    
    print(f"Found {len(results)} chunks.")
    for i, res in enumerate(results):
        print(f"\n[Chunk {i+1}]")
        print(f"Source: {res.metadata.get('Source URL')}")
        print(f"Content Snippet: {res.page_content[:500]}...")
        print("-" * 30)

if __name__ == "__main__":
    queries = [
        "What is the exit load for HDFC Flexi Cap Fund?",
        "HDFC Mid Cap Opportunities Fund expense ratio",
        "minimum SIP amount for HDFC Focused 30 Fund"
    ]
    for q in queries:
        debug_retrieval(q)
