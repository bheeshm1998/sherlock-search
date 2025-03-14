import os
import tempfile
import logging
from typing import List

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, UploadFile, File

from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
# from pinecone import Pinecone

from app.config.pinecone_init import llm, embeddings, pc

from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
import pdfplumber  # Alternative to PyPDFLoader

# Initialize Gemini API

router = APIRouter()

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

logger = logging.getLogger("uvicorn")

# Get API keys and configuration from environment
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

load_dotenv()

# Function to get embeddings from Gemini
def get_gemini_embedding(text: str) -> List[float]:
    response = genai.embed_content(
        model="models/embedding-001",  # Use Gemini's embedding model
        content=text,
        task_type="retrieval_document"  # Use retrieval_query for queries
    )
    return response["embedding"]  # Extracts the list of floats

# @router.post("/upload-pdf/")
# async def upload_pdf(file: UploadFile = File(...)):
#     logger.info("File received successfully")
#     try:
#         # Save the uploaded file to a temporary file
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
#             temp_file.write(await file.read())
#             temp_file_path = temp_file.name
#
#         # Load the PDF and split it into chunks
#         loader = PyPDFLoader(temp_file_path)
#         documents = loader.load()
#
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         texts = text_splitter.split_documents(documents)
#
#         # Generate embeddings for each chunk
#         print("text length ", texts.count)
#         texts_embeddings = embeddings.embed_documents([text.page_content for text in texts])
#         print("texts_embeddings_count", texts_embeddings.count())
#         # Upsert embeddings into Pinecone
#         index = pc.Index(PINECONE_INDEX_NAME)
#         vectors = []
#         for i, (text, embedding) in enumerate(zip(texts, texts_embeddings)):
#             vectors.append({
#                 "id": f"doc_{i}",
#                 "values": embedding,
#                 "metadata": {"text": text.page_content}
#             })
#
#         index.upsert(vectors=vectors)
#
#         # Clean up the temporary file
#         os.remove(temp_file_path)
#
#         return {"message": "PDF uploaded and processed successfully"}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-pdf-2/")
async def upload_pdf_2(file: UploadFile = File(...)):
    print("YOYO")
    try:
        # Save uploaded PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        # Extract text from PDF
        texts = []
        with pdfplumber.open(temp_file_path) as pdf:
            for page in pdf.pages:
                texts.append(page.extract_text())

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        text_chunks = text_splitter.split_text("\n".join(texts))

        # Generate embeddings using Gemini

        # Generate embeddings using Gemini
        embeddings = [get_gemini_embedding(chunk) for chunk in text_chunks]

        # Initialize Pinecone client
        # pc = (api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)  # Use Pinecone, not pinecone
        index = pc.Index(PINECONE_INDEX_NAME)  # Access Index from the Pinecone client

        # Prepare and upsert embeddings into Pinecone
        vectors = [
            {
                "id": f"doc_{i}",
                "values": embedding,
                "metadata": {"text": text}
            }
            for i, (text, embedding) in enumerate(zip(text_chunks, embeddings))
        ]

        index.upsert(vectors=vectors)

        # Cleanup
        os.remove(temp_file_path)

        return {"message": "PDF uploaded and processed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/")
async def list_documents(limit: int = 10):
    try:
        # Get the Pinecone index
        index = pc.Index(PINECONE_INDEX_NAME)

        # Use the query method to retrieve a list of vectors
        # Note: Pinecone does not support listing all vectors directly, so we use a dummy query
        query_response = index.query(
            vector=[0] * 1536,  # Dummy vector (all zeros)
            top_k=limit,  # Limit the number of results
            include_metadata=True  # Include metadata in the response
        )

        # Extract document IDs and metadata from the response
        documents = []
        for match in query_response.matches:
            documents.append({
                "id": match.id,
                "metadata": match.metadata
            })

        return {"documents": documents}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-document/{document_id}")
async def delete_document(document_id: str):
    try:
        # Get the Pinecone index
        index = pc.Index(PINECONE_INDEX_NAME)

        # Delete the document by its ID
        delete_response = index.delete(ids=[document_id])

        # Check if the deletion was successful
        if not delete_response:
            raise HTTPException(status_code=404, detail="Document not found or already deleted")

        return {"message": f"Document with ID '{document_id}' deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))