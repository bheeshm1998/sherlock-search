from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest
from app.schemas.message import MessageCreate, MessageResponse
from app.services.chat_service import ChatService
from app.services.message_service import MessageService


router = APIRouter()

@router.get("/messages/{project_id}", response_model=list[MessageResponse])
def get_project_messages(project_id: str):
    """
    Endpoint to fetch all messages for a specific project.
    """
    try:
        messages = MessageService.get_project_messages(project_id)
        if not messages:
            raise HTTPException(status_code=404, detail="No messages found for the specified project")
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e.__cause__.__str__()}")


@router.post("/chat/")
async def chat(request: ChatRequest):
    try:
        # Call the service to handle the chat logic
        chatService = ChatService()
        response = chatService.handle_chat(user_message = request.query)
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

