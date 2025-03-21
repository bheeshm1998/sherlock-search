import os
from typing import Tuple, List
import google.generativeai as genai

from app.schemas.gemini_chat import GeminiChatRequest

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

class GeminiChatService:
    """
    Service to validate user intent and filter queries based on their relevance.
    """
    @staticmethod
    def handleChat(self, request: GeminiChatRequest) -> Tuple[bool, str]:
        # Call Gemini API
        response = genai.generate_content(
            model="gemini-1.5-pro",  # Adjust model version if needed
            contents=[{"role": "user", "parts": [{"text": request.query}]}],
            tools=[{
                "name": "EnterpriseChatTool",
                "description": "Retrieves enterprise knowledge-based answers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "User's enterprise-related query"}
                    },
                    "required": ["query"]
                }
            }]
        )
        return {"response": response.text}
