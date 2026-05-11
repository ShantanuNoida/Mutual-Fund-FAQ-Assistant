try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import sys
import os

# Add necessary paths to sys.path
# Using absolute path logic to work both locally and in deployment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "Phase_3_Guardrails", "src"))
sys.path.append(os.path.join(BASE_DIR, "Phase_2_RAG_Pipeline", "src"))
sys.path.append(BASE_DIR) # Add root to path for cross-phase imports


try:
    from safe_rag_pipeline import SafeRAGEngine
except ImportError as e:
    print(f"Import Error: {e}")
    # Fallback for Vercel if structure is flattened
    sys.path.append(os.path.join(os.getcwd(), "Phase_3_Guardrails", "src"))
    sys.path.append(os.path.join(os.getcwd(), "Phase_2_RAG_Pipeline", "src"))
    from safe_rag_pipeline import SafeRAGEngine

app = FastAPI(title="Mutual Fund Agent API")

# Add CORS middleware to allow Streamlit (Railway) to call Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Railway URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engine
# Note: This might take time on first request in serverless
engine = None

def get_engine():
    global engine
    if engine is None:
        engine = SafeRAGEngine()
    return engine

class QueryRequest(BaseModel):
    prompt: str
    chat_history: Optional[List[Dict[str, str]]] = []

class QueryResponse(BaseModel):
    response: str

@app.get("/")
def read_root():
    return {"status": "online", "message": "Mutual Fund Agent API is running"}

@app.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest):
    try:
        engine = get_engine()
        response = engine.ask(request.prompt, chat_history=request.chat_history)
        return QueryResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
