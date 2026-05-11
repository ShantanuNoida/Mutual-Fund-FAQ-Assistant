import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.dirname(__file__))

from rag_engine import RAGEngine

def run_tests():
    try:
        engine = RAGEngine()
    except Exception as e:
        print(f"Failed to initialize RAG Engine: {e}")
        return

    test_queries = [
        "What is a mutual fund?",
        "What is the exit load for HDFC Flexi Cap Fund?",
        "Should I invest in HDFC Mid Cap or Flexi Cap? Which is better?" # Testing refusal constraint
    ]
    
    print("\n" + "="*50)
    for q in test_queries:
        print(f"\n[QUERY]: {q}")
        response = engine.ask(q)
        print(f"\n[RESPONSE]:\n{response}")
        print("-" * 50)

if __name__ == "__main__":
    run_tests()
