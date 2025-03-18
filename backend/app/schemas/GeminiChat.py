from pydantic import BaseModel

# for integrating with Gemini Plugin

class GeminiChatRequest(BaseModel):
    query: str