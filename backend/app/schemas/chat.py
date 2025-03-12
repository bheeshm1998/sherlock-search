
from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    query: str
    document_ids: Optional[List[str]] = None
    k: int = 5

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]