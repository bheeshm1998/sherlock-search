from fastapi import APIRouter, HTTPException

from app import llm
from app.schemas.message import MessageCreate, MessageResponse
from app.services.message_service import MessageService

router = APIRouter()

@router.get("/debug")
async def debug_endpoint():
    """
    Simple debug endpoint to check if the service is running
    """
    return {"status": "Service is running"}


