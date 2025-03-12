import os
import tempfile

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, UploadFile, File

from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.pinecone_init import llm, embeddings, pc


router = APIRouter()

load_dotenv()

# Get API keys and configuration from environment
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

load_dotenv()

@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        # Load the PDF and split it into chunks
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)

        # Generate embeddings for each chunk
        texts_embeddings = embeddings.embed_documents([text.page_content for text in texts])

        # Upsert embeddings into Pinecone
        index = pc.Index(PINECONE_INDEX_NAME)
        vectors = []
        for i, (text, embedding) in enumerate(zip(texts, texts_embeddings)):
            vectors.append({
                "id": f"doc_{i}",
                "values": embedding,
                "metadata": {"text": text.page_content}
            })

        index.upsert(vectors=vectors)

        # Clean up the temporary file
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