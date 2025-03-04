import pinecone
from app.config import settings

class VectorDatabase:
    def __init__(self):
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        self.index = pinecone.Index(settings.PINECONE_INDEX_NAME)

    def upsert_vectors(self, vectors):
        """Insert or update vectors in Pinecone"""
        self.index.upsert(vectors)

    def query_vectors(self, query_vector, top_k=5):
        """Semantic search in vector database"""
        return self.index.query(
            query_vector,
            top_k=top_k,
            include_metadata=True
        )