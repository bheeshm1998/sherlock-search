import json
import os

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Optional

from supabase import create_client

from app.routes.auth_routes import get_current_user
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

# @router.post("/projects", response_model=ProjectResponse)
# async def create_project(project_data: ProjectCreate):
#     """
#     Create a new project.
#     """
#     project = ProjectService.create_project(project_data)
#     return project


@router.post("/projectsv2", response_model=ProjectResponse)
async def create_project_v2(
        project_data: str = Form(...),
        files: Optional[List[UploadFile]] = File(None),
        groups: Optional[List[str]] = Form("[]")
):
    """
    Create a new project with optional document uploads.

    - project_data: JSON string containing project information
    - files: Optional list of files to upload
    """
    try:
        # Parse project data
        groups = json.loads(groups[0]) if isinstance(groups, list) and len(groups) == 1 else groups
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
        project = ProjectService.create_project_v2(project_create, groups, file_info_list)
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

@router.put("/projectsUP/{project_id}", response_model=ProjectResponse)
async def update_project2(
        project_id: str,
        project_data: str = Form(...),  # JSON string containing description & access type
        files: Optional[List[UploadFile]] = File(None)
):
    """
    Update an existing project:
    - Update **description** & **access type**.
    - Add **new documents** if provided.
    """
    try:
        # Parse project data (JSON string)
        project_dict = json.loads(project_data)
        updated_description = project_dict.get("updated_description")
        access_type = project_dict.get("access_type")
        name = project_dict.get("name")

        # Process files if provided
        file_info_list = []
        if files:
            for file in files:
                filename = file.filename
                content = await file.read()
                size = len(content)
                file_extension = filename.split('.')[-1] if '.' in filename else None

                # Create document metadata
                doc_data = DocumentCreate(
                    name=filename,
                    description=filename,
                    document_type=file_extension.upper() if file_extension else "UNKNOWN",
                    file_extension=file_extension,
                    size=str(size)
                )

                file_info_list.append({
                    "file": filename,
                    "file_obj": content,
                    "doc_data": doc_data
                })

        # Call the service to update the project
        updated_project = ProjectService.update_project_with_files(
            project_id, name, updated_description, access_type, file_info_list
        )
        return updated_project

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/projects/{project_id}", response_model=dict)
async def delete_project(project_id: str):
    """
    Delete an existing project.
    """
    success = ProjectService.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": f"Project '{project_id}' deleted successfully."}


@router.get("/projects/{project_id}")
def get_project_by_id(project_id: int):
    """
    Get details for a project by its ID.
    """
    # Query the project from the database
    project_and_groups = ProjectService.getProjectById(project_id)
    return project_and_groups

@router.put("/projects/{project_id}/publish", response_model=ProjectAbstractData)
async def publish_project(project_id: str):
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
        raise HTTPException(status_code=500, detail=str(e))


# @router.get("/projects/user/{user_id}", response_model=List[ProjectAbstractData])
# async def get_projects_for_user(user_id: str):
#     """
#     Publish an existing project by updating its state to 'published'.
#     """
#     try:
#         # Call the ProjectService method to update the project state
#         projects = ProjectService.get_published_projects()
#         return projects
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/user/{user_id}", response_model=List[ProjectAbstractData])
async def get_projects_for_user_v2(user_id: str, user: dict = Depends(get_current_user)):
    """
    Publish an existing project by updating its state to 'published'.
    """
    # user_id is user email
    try:
        # Call the ProjectService method to update the project state
        projects = ProjectService.get_projects_for_user(user_id)
        return projects
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))