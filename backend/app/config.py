from pydantic_settings import BaseSettings

class Settings:
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str = 'gcp-starter'

settings = Settings()
