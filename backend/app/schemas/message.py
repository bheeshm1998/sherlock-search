from pydantic import BaseModel
from datetime import datetime
from typing import Literal


class MessageCreate(BaseModel):
    content: str
    project_id: str
    user_id: str


class MessageResponse(BaseModel):
    id: str
    content: str
    role: Literal['user', 'assistant']
    timestamp: datetime
    project_id: str
    user_id: str

    class Config:
        from_attributes = True
