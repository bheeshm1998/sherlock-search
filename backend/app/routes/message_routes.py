from fastapi import APIRouter, HTTPException

from app.config.pinecone_init import pc
from app.schemas.gemini_chat import GeminiChatRequest
from app.schemas.chat import ChatRequest
from app.schemas.message import MessageResponse, MessageCreate
from app.services.chat_service import ChatService
from app.services.gemini_chat_service import GeminiChatService
from app.services.intent_service import IntentService
from app.services.message_service import MessageService


router = APIRouter()

@router.get("/messages/{project_id}/{user_id}", response_model=list[MessageResponse])
def get_messages(project_id: str, user_id: str):
    """
    Endpoint to fetch all messages for a specific project.
    """
    try:
        messages = MessageService.get_project_messages(project_id, user_id)
        if not messages:
            raise HTTPException(status_code=404, detail="No messages found for the specified project")
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e.__cause__.__str__()}")


@router.post("/chat/{project_id}/{user_id}")
async def chat(request: MessageCreate):
    try:
        # Call the service to handle the chat logic
        chatService = ChatService(project_id = request.project_id)
        messageService = MessageService()
        messageService.create_message(request)
        response = chatService.handle_chat(user_message = request.content)
        messageRequestForAssistant = MessageCreate(project_id=request.project_id, user_id=request.user_id, content=response, role ="assistant")
        messageService.create_message(messageRequestForAssistant)
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate_query")
async def validate_user_query(query: str):
    """
    API endpoint to validate user query before forwarding to LLM.

    :param query: User's query string
    :return: Validation response
    """

    # Initialize vector database

    # Allowed topics/documents the user can query about
    allowed_contexts = ["machine learning", "AI models", "document processing"]

    # Create an IntentService instance
    intent_service = IntentService(vector_database=pc, allowed_contexts=allowed_contexts)

    is_valid, reason = intent_service.validate_query(query)
    if not is_valid:
        return {"success": False, "message": reason}

    # Query is valid; pass it forward to the LLM
    chatService = ChatService()
    response = chatService.handle_chat(user_message = query)
    return {"success": True, "response": response}

# @router.post("/chat-with-gemini/")
# async def chat_with_gemini(request: ChatRequest):
#     try:
#         # Call Gemini API
#         response = GeminiChatService.handleChat(request)
#         return response
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# Integration with firebase auth routes
# @router.get("/chat/")
# async def chat_with_ai(user: str = Depends(verify_user)):
#     return {"message": f"Hello {user}, how can I help you?"}