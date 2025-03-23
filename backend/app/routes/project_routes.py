import json

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional

from app.schemas.project import ProjectCreate, ProjectResponse, DocumentCreate, ProjectAbstractData
from app.services.project_service import ProjectService

router = APIRouter()

@router.get("/projects", response_model=List[ProjectAbstractData])
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


@router.post("/projectsv2", response_model=ProjectResponse)
async def create_project_v2(
        project_data: str = Form(...),
        files: Optional[List[UploadFile]] = File(None)
):
    """
    Create a new project with optional document uploads.

    - project_data: JSON string containing project information
    - files: Optional list of files to upload
    """
    try:
        # Parse project data
        project_dict = json.loads(project_data)
        project_create = ProjectCreate(**project_dict)

        # Process files if provided
        file_info_list = []
        if files:
            for file in files:
                # Extract file info
                filename = file.filename
                content = await file.read()
                size = len(content)
                file_extension = filename.split('.')[-1] if '.' in filename else None

                # Create document data
                doc_data = DocumentCreate(
                    name=filename,
                    description=filename,  # You can customize this
                    document_type=file_extension.upper() if file_extension else "UNKNOWN",
                    file_extension=file_extension,
                    size=str(size)  # Convert to string as per your schema
                )

                # Add to file info list
                file_info_list.append({
                    "file": filename,
                    "file_obj": content,
                    "doc_data": doc_data
                })

        # Create project with documents
        project = ProjectService.create_project_v2(project_create, file_info_list)
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project_by_id(project_id: str):
    """
    Get details for a project by its ID.
    """
    # Query the project from the database
    project = ProjectService.getProjectById(project_id)

    return project

@router.put("/projects/{project_id}/publish", response_model=ProjectResponse)
async def publish_project(project_id: int):
    """
    Publish an existing project by updating its state to 'published'.
    """
    try:
        # Call the ProjectService method to update the project state
        project = ProjectService.publish_project(project_id)
        return project
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")