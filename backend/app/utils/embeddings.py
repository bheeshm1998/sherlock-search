import os
import google.generativeai as genai


def get_gemini_embedding(text):
    """
    Generate embeddings for text using Gemini API.
    """
    try:
        # Configure the Gemini API
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

        # Get embeddings model
        embedding_model = "models/embedding-001"  # Update this with the correct model name

        # Generate embedding
        result = genai.embed_content(
            model=embedding_model,
            content=text,
            task_type="retrieval_document"
        )

        # Return the embedding values
        return result["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {e}")
        raise e