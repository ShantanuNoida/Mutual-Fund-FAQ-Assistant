import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceInferenceEmbeddings
from langchain_community.vectorstores import Chroma

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Configuration
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'Phase_1_Data_Ingestion', 'chroma_db')
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.1-8b-instant"

# Strict Fact-Only Prompt Template (Updated for conversational tone while keeping constraints)
PROMPT_TEMPLATE = """
You are a professional, helpful, and strictly facts-only Mutual Fund Assistant.
Your goal is to answer the user's query using ONLY the provided context from official documents.

CONSTRAINTS:
1. NO INVESTMENT ADVICE. Do not recommend, opine, or compare funds.
2. DO NOT calculate future returns or SIP maturity amounts.
3. Your answer MUST be exactly 3 sentences or fewer.
4. Use a helpful but professional tone.
5. You MUST include exactly one citation link at the very end, taken from the "Source URL" in the context.
6. If the answer is not in the context, say: "I'm sorry, I couldn't find verified information regarding that in the official documents."

CONTEXT:
{context}

USER QUERY: {question}

RESPONSE:
"""

CONDENSE_PROMPT = """
Given the following conversation and a follow-up question, rephrase the follow-up question to be a standalone question.
If the follow-up is already a standalone question, return it as is.

Chat History:
{chat_history}
Follow-up Question: {question}
Standalone Question:
"""

def format_docs(docs):
    formatted = []
    for doc in docs:
        source = doc.metadata.get("Source URL", "Unknown Source")
        formatted.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n".join(formatted)

class RAGEngine:
    def __init__(self):
        self.embeddings = HuggingFaceInferenceEmbeddings(
            api_key=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=self.embeddings)

        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        self.llm = ChatGroq(temperature=0, model_name=LLM_MODEL)
        
        # Chains
        self.answer_prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
        self.condense_prompt = PromptTemplate.from_template(CONDENSE_PROMPT)
        
    def _condense_question(self, query, chat_history):
        if not chat_history:
            return query
        
        # Turn history into a string
        history_str = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history])
        chain = self.condense_prompt | self.llm | StrOutputParser()
        return chain.invoke({"chat_history": history_str, "question": query})

    def ask(self, query: str, chat_history=None):
        """Processes a query, optionally using chat history for context."""
        # 1. Condense question if history exists
        standalone_query = self._condense_question(query, chat_history)
        
        # 2. RAG Chain
        chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.answer_prompt
            | self.llm
            | StrOutputParser()
        )
        return chain.invoke(standalone_query)
