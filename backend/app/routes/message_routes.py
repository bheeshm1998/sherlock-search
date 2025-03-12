from fastapi import APIRouter, HTTPException
from app.schemas.message import MessageCreate, MessageResponse
from app.services.message_service import MessageService
from app.llm.llm_wrapper import LLMWrapper

router = APIRouter()

# Assume LLMWrapper is your utility for interacting with the LLM
llm = LLMWrapper()


@router.post("/messages", response_model=MessageResponse)
def send_message_to_llm(message_data: MessageCreate):
    print("message data: ", message_data)
    """
    Endpoint to send a message to the LLM and handle the assistant's response.
    - Create (store) the user's message.
    - Process the user's message by calling the LLM.
    - Create (store) the LLM's response.
    - Return the LLM's response.
    """
    try:
        # Step 1: Save the user's message using the service layer
        user_message = MessageService.create_user_message(message_data)

        # Step 2: Get LLM's response for the message
        llm_response_text = llm.get_response(user_message.content)

        if not llm_response_text:
            raise HTTPException(status_code=500, detail="LLM failed to process the message")

        # Step 3: Save the LLM's response using the service layer
        assistant_message = MessageService.create_assistant_message(
            content=llm_response_text,
            project_id=user_message.project_id,
            user_id=user_message.user_id
        )

        # Step 4: Return the assistant's response
        return assistant_message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e.__cause__.__str__()}")


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
