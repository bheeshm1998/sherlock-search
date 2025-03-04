from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.search_service import SemanticSearchService

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/semantic")
async def semantic_search(request: SearchRequest):
    search_service = SemanticSearchService()

    # Optional: Ingest documents first (do this during initial setup)
    sample_docs = [
        "Enterprise search helps organizations find information quickly.",
        "Machine learning improves search accuracy and relevance.",
        "Vector databases enable semantic search capabilities."
    ]
    search_service.ingest_documents(sample_docs)

    # Perform search
    results = search_service.perform_semantic_search(
        query=request.query,
        top_k=request.top_k
    )

    return {"results": results}