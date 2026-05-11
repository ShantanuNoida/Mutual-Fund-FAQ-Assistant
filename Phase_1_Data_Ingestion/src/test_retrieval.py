import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Configuration
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'chroma_db')
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def test_retrieval(query: str, k: int = 3):
    print(f"\n--- Testing Retrieval for Query: '{query}' ---")
    
    if not os.path.exists(CHROMA_DB_DIR):
        print(f"Error: ChromaDB directory '{CHROMA_DB_DIR}' not found. Run ingestion.py first.")
        return

    print("Loading embedding model and vector database...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)
    
    # Perform similarity search
    results = vectorstore.similarity_search(query, k=k)
    
    if not results:
        print("No matching chunks found.")
        return
        
    for i, doc in enumerate(results, 1):
        print(f"\n[Result {i}]")
        print(f"Source URL: {doc.metadata.get('Source URL', 'Unknown')}")
        print(f"Last Updated: {doc.metadata.get('Last Updated Date', 'Unknown')}")
        print(f"Content Preview: {doc.page_content[:200]}...")

if __name__ == "__main__":
    test_queries = [
        "What is the exit load for HDFC Flexi Cap Fund?",
        "Tell me the expense ratio of the Mid-Cap Opportunities fund.",
        "What is the minimum SIP amount?"
    ]
    
    for q in test_queries:
        test_retrieval(q, k=2)
