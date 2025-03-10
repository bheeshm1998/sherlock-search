import os
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List

from app.schemas.project import ProjectResponse
from app.services.search_service import SemanticSearchService

router = APIRouter()

# Configuration: Set upload folder
UPLOAD_FOLDER = "./uploaded_pdfs"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/semantic")
async def semantic_search(request: SearchRequest):
    print("Inside the semantic search api")
    search_service = SemanticSearchService()

    # Optional: Ingest documents first (do this during initial setup)
    sample_docs = [
        "Enterprise search helps organizations find information quickly.",
        "Machine learning improves search accuracy and relevance.",
        "Vector databases enable semantic search capabilities."
    ]
    search_service.ingest_documents(sample_docs)

    # Perform search
    results = search_service.perform_semantic_search(
        query=request.query,
        top_k=request.top_k
    )

    return {"results": results}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    print("Inside the upload file api")
    """
    Endpoint to upload PDF files
    """
    # Check if uploaded file is a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save the file
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    return {"message": f"File '{file.filename}' uploaded successfully", "path": file_location}

@router.get("/debug")
async def debug_endpoint():
    """
    Simple debug endpoint to check if the service is running
    """
    return {"status": "Service is running", "uploaded_folder": UPLOAD_FOLDER}

@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects():
    """
    Get all projects
    """

    # Sample projects
    projects = [
        ProjectResponse(
            id="1",
            name="ProjectResponse Alpha",
            description="This is ProjectResponse Alpha",
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        ProjectResponse(
            id="2",
            name="ProjectResponse Beta",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]


    return projects

@router.post("/projects", response_model=ProjectResponse)
async def create_project(project: ProjectResponse):
    """
    Create a new project
    """

    # Sample projects
    projects = [
        ProjectResponse(
            id="1",
            name="ProjectResponse Alpha",
            description="This is ProjectResponse Alpha",
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        ProjectResponse(
            id="2",
            name="ProjectResponse Beta",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]


    # Generate a new unique ID
    project.id = str(uuid4())
    project.created_at = datetime.now()
    project.updated_at = datetime.now()
    projects.append(project)

    return project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, updated_project: ProjectResponse):
    """
    Edit an existing project
    """

    # Sample projects
    projects = [
        ProjectResponse(
            id="1",
            name="ProjectResponse Alpha",
            description="This is ProjectResponse Alpha",
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        ProjectResponse(
            id="2",
            name="ProjectResponse Beta",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]

    for index, project in enumerate(projects):
        if project.id == project_id:
            # Update project details
            projects[index] = ProjectResponse(
                id=project.id,  # Keep the original ID
                name=updated_project.name,
                description=updated_project.description,
                created_at=project.created_at,  # Preserve the original creation time
                updated_at=datetime.now()  # Update the timestamp for the edit
            )
            return projects[index]

    raise HTTPException(status_code=404, detail="ProjectResponse not found")

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """
    Delete an existing project
    """

    projects = [
        ProjectResponse(
            id="1",
            name="ProjectResponse Alpha",
            description="This is ProjectResponse Alpha",
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        ProjectResponse(
            id="2",
            name="ProjectResponse Beta",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]


    for project in projects:
        if project.id == project_id:
            projects.remove(project)
            return {"message": f"ProjectResponse with ID '{project_id}' has been deleted."}

    raise HTTPException(status_code=404, detail="ProjectResponse not found")