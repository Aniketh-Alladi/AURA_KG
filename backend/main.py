from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.schemas import QueryRequest, QueryResponse
from backend.rag import answer_query

app = FastAPI(
    title="AURA-KG Retrieval API",
    description="LLM & Graph Retrieval layer for the AURA-KG Knowledge Graph",
    version="1.0.0"
)

# Enable CORS for local frontend development (Nikshith's dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin during local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Simple status endpoint to verify API server is up."""
    return {"status": "ok", "service": "AURA-KG Retrieval API"}


@app.post("/api/v1/query", response_model=QueryResponse)
def handle_query(payload: QueryRequest):
    """
    Primary endpoint invoked by Nikshith's frontend.
    Accepts a natural language question and returns a synthesized answer
    along with node metadata required for graph visual highlighting.
    """
    try:
        result = answer_query(query=payload.query, top_k=payload.top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval processing error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)