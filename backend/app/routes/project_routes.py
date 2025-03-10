import os
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List

from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project_service import ProjectService

router = APIRouter()

# Configuration: Set upload folder
UPLOAD_FOLDER = "./uploaded_pdfs"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint to upload PDF files.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    return {"message": f"File '{file.filename}' uploaded successfully", "path": file_location}

@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects():
    """
    Get all projects.
    """
    projects = ProjectService.get_all_projects()
    return projects

@router.post("/projects", response_model=ProjectResponse)
async def create_project(project_data: ProjectCreate):
    """
    Create a new project.
    """
    project = ProjectService.create_project(project_data)
    return project

@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, updated_data: dict):
    """
    Edit an existing project.
    """
    project = ProjectService.update_project(project_id, updated_data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/projects/{project_id}", response_model=dict)
async def delete_project(project_id: str):
    """
    Delete an existing project.
    """
    success = ProjectService.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": f"Project '{project_id}' deleted successfully."}