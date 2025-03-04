import os
from typing import List, Dict, Any

import openai
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
import pinecone


class SemanticSearchService:
    def __init__(self):
        # Initialize OpenAI and Pinecone
        openai.api_key = os.getenv('OPENAI_API_KEY')

        # Pinecone initialization
        pinecone.init(
            api_key=os.getenv('PINECONE_API_KEY'),
            environment=os.getenv('PINECONE_ENVIRONMENT', 'gcp-starter')
        )

        # Create embeddings
        self.embeddings = OpenAIEmbeddings()

        # Initialize Pinecone index
        self.index_name = os.getenv('PINECONE_INDEX_NAME', 'enterprise-search')

        # Check if index exists, create if not
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI embedding dimension
                metric='cosine'
            )

        # Connect to the index
        self.vector_store = Pinecone.from_existing_index(
            index_name=self.index_name,
            embedding=self.embeddings
        )

    def ingest_documents(self, documents: List[str]):
        """
        Ingest documents into the vector store

        :param documents: List of document texts to be indexed
        """
        # Split documents into chunks if they are long
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        # Split documents
        docs = text_splitter.create_documents(documents)

        # Add to vector store
        Pinecone.from_documents(
            docs,
            self.embeddings,
            index_name=self.index_name
        )

    def perform_semantic_search(
            self,
            query: str,
            top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search on ingested documents

        :param query: Search query string
        :param top_k: Number of top results to return
        :return: List of search results
        """
        try:
            # Perform similarity search
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=top_k
            )

            # Transform results
            formatted_results = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score
                }
                for doc, score in results
            ]

            return formatted_results

        except Exception as e:
            # Log the error (consider using a proper logging framework)
            print(f"Semantic search error: {e}")
            return []
