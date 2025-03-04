from pydantic_settings import BaseSettings

class Settings:
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str = 'gcp-starter'
    PINECONE_INDEX_NAME: str = 'enterprise-search'

settings = Settings()