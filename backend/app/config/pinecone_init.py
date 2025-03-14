import os

from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables from .env file
load_dotenv()

# Get API keys and configuration from environment
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

from langchain_community.chat_models import ChatOpenAI
print("PINECONE_API_KEY", os.getenv("PINECONE_API_KEY"))

print("OPENAI_API_KEY", OPENAI_API_KEY)

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)


# Create index if it doesn't exist
if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=768,  # OpenAI embeddings dimension
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

# Initialize embeddings
embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)


# Initialize LLM
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0,
    api_key=OPENAI_API_KEY
)

# Export initialized objects for later use
__all__ = ["llm", "embeddings", "pc"]
