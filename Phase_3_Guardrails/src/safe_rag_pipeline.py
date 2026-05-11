import sys
import os
from datetime import datetime

# Add Phase 2 to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Phase_2_RAG_Pipeline', 'src'))

from rag_engine import RAGEngine
import guardrails

class SafeRAGEngine:
    def __init__(self):
        self.engine = RAGEngine()
        
    def ask(self, query: str, chat_history=None) -> str:
        """
        Processes a query securely and contextually:
        1. Pre-processing: PII & Intent Check
        2. RAG Generation (with optional history)
        3. Post-processing: Formatting
        """
        
        # 1. Guardrails (Check current query)
        pii_check = guardrails.check_pii(query)
        if pii_check["blocked"]:
            return pii_check["message"]
            
        intent_check = guardrails.check_intent(query)
        if intent_check["blocked"]:
            return intent_check["message"]
            
        # 2. RAG Generation
        # Pass history for contextual query reformulation
        raw_response = self.engine.ask(query, chat_history=chat_history)
        
        # 3. Post-Processing
        formatted_response = guardrails.enforce_sentence_limit(raw_response, max_sentences=3)
        today_date = datetime.now().strftime("%Y-%m-%d")
        final_response = guardrails.inject_footer(formatted_response, today_date)
        
        return final_response
