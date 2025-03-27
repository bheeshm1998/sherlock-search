import os

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables from .env file
load_dotenv()

# Get API keys and configuration from environment
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

def create_project_index(project_id):
    """Creates a new index for the project if under limit."""
    existing_indexes = pc.list_indexes().names()
    
    if len(existing_indexes) >= 5:
        raise Exception("Maximum index limit reached. Cannot create a new project.")
    
    index_name = f"project-{project_id}"
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
    return index_name

__all__ = ["pc", "create_project_index"]
