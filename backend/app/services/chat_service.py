from pinecone import Pinecone
from openai import OpenAI
import os

class ChatService:
    def __init__(self):
        # Initialize Pinecone
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        self.index = self.pc.Index(self.index_name)

        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_relevant_chunks(self, query: str, top_k: int = 5):
        """
        Retrieve relevant chunks from the Pinecone vector store based on the query.
        """
        # Generate embeddings for the query
        query_embedding = self.openai_client.embeddings.create(
            input=query,
            model="text-embedding-ada-002"
        ).data[0].embedding

        # Query Pinecone for relevant chunks
        query_response = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        # Extract relevant chunks
        relevant_chunks = []
        for match in query_response.matches:
            relevant_chunks.append(match.metadata["text"])

        return relevant_chunks

    def generate_chat_response(self, system_prompt: str, user_prompt: str):
        """
        Generate a response using OpenAI's Chat API.
        """
        response = self.openai_client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content

    @staticmethod
    def handle_chat(self, user_message: str):
        """
        Handle the chat logic:
        1. Retrieve relevant chunks from Pinecone.
        2. Generate a response using OpenAI's Chat API.
        """
        # Step 1: Get relevant chunks from Pinecone
        relevant_chunks = self.get_relevant_chunks(user_message)

        # Step 2: Create the system prompt and user prompt
        system_prompt = """
        You are a helpful assistant. Use the following information to answer the user's question.
        If the information is not relevant, use your own knowledge to provide a helpful response.
        """
        user_prompt = f"""
        User's question: {user_message}

        Relevant information:
        {relevant_chunks}
        """

        # Step 3: Generate the response using OpenAI
        response = self.generate_chat_response(system_prompt, user_prompt)

        return response