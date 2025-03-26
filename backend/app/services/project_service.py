import os
import tempfile

import pdfplumber
from fastapi import HTTPException
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.utils import deprecated
from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from typing import List

from supabase import create_client, Client

from app.config.pinecone_init import pc
from app.database import get_db
from app.models.project import Project, Document, project_group_association, ProjectGroup
from app.routes.document_routes import get_gemini_embedding
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectAbstractData
from app.utils.supabase import upload_to_supabase

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class ProjectService:

    @staticmethod
    def get_all_projects() -> List[ProjectAbstractData]:
        """
        Fetch all projects from the database and return them as ProjectAbstractData.
        """
        db: Session = next(get_db())
        try:
            projects = db.query(Project).all()  # Retrieve all projects from the database
            # Transform each Project into ProjectAbstractData
            return [
                ProjectAbstractData(
                    id=project.id,
                    name=project.name,
                    description=project.description,
                    access_type=project.access_type,
                    state=project.state,
                    num_documents=len(project.documents),
                    updated_at=project.updated_at
                )
                for project in projects
            ]
        finally:
            db.close()

    @staticmethod
    def publish_project(project_id):
        """
        Updates the project's state to 'published' in the database.
        """
        db: Session = next(get_db())
        # Fetch project by ID
        project = db.query(Project).filter_by(id=project_id).first()

        if not project:
            raise ValueError(f"Project with ID {project_id} not found.")

        # Update project state
        project.state = 'PUBLISHED'
        project.updated_at = datetime.now()

        # Commit changes to the database
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to update project state: {str(e)}")

        return ProjectAbstractData(
                    id=project.id,
                    name=project.name,
                    description=project.description,
                    access_type=project.access_type,
                    state=project.state,
                    num_documents=len(project.documents),
                    updated_at=project.updated_at
                )

    @staticmethod
    def getProjectById(project_id: str) -> Project:
        db: Session = next(get_db())
        project = db.query(Project).filter(Project.id == project_id).first()

        # If project not found, raise an HTTP 404 exception
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Return the project details
        return project

    @deprecated
    @staticmethod
    def create_project(project_data: ProjectCreate) -> ProjectResponse:
        """
        Create a new project in the database.
        """
        db: Session = next(get_db())

        existing_project = db.query(Project).filter_by(name=project_data.name).first()
        if existing_project:
            raise ValueError(f"A project with the name '{project_data.name}' already exists.")

        try:
            new_project = Project(
                id=str(uuid4()),
                name=project_data.name,
                description=project_data.description,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.add(new_project)
            db.commit()
            db.refresh(new_project)
            return ProjectResponse.model_validate(new_project)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def update_project(project_id: str, updated_data: dict) -> ProjectResponse:
        """
        Update an existing project.
        """
        db: Session = next(get_db())
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise ValueError("Project not found")

            project.name = updated_data.get("name", project.name)
            project.description = updated_data.get("description", project.description)
            project.updated_at = datetime.now()
            db.commit()
            db.refresh(project)
            return ProjectResponse.model_validate(project)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def delete_project(project_id: str) -> bool:
        """
        Delete a project by ID.
        """
        db: Session = next(get_db())
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return False

            db.delete(project)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def get_published_projects() -> List[ProjectAbstractData]:
        """
        Fetch all projects from the database and return them as ProjectAbstractData.
        """
        db: Session = next(get_db())
        try:
            projects = db.query(Project).filter(Project.state == "PUBLISHED").all()  # Retrieve all projects from the database
            # Transform each Project into ProjectAbstractData
            return [
                ProjectAbstractData(
                    id=project.id,
                    name=project.name,
                    description=project.description,
                    access_type=project.access_type,
                    state=project.state,
                    num_documents=len(project.documents),
                    updated_at=project.updated_at
                )
                for project in projects
            ]
        finally:
            db.close()


    @staticmethod
    def create_project_v2(project_data: ProjectCreate, files: List[dict] = None) -> ProjectResponse:
        """
        Create a new project in the database with associated documents.
        """
        db: Session = next(get_db())

        existing_project = db.query(Project).filter_by(name=project_data.name).first()
        if existing_project:
            raise ValueError(f"A project with the name '{project_data.name}' already exists.")

        try:
            # Create project
            project_id = str(uuid4())
            new_project = Project(
                id=project_id,
                name=project_data.name,
                description=project_data.description,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                access_type=project_data.access_type,
                state=project_data.state or "DRAFT"
            )
            db.add(new_project)
            db.flush()  # Flush to get project ID without committing

            # Initialize Pinecone if files are provided
            if files:
                try:
                    index = pc.Index(os.environ.get("PINECONE_INDEX_NAME"))
                except Exception as e:
                    print(f"Error initializing Pinecone: {str(e)}")
                    # Continue anyway, we'll skip vector storage if Pinecone fails

            # Process documents if any
            if files:
                for file_info in files:
                    file = file_info.get("file")
                    file_obj = file_info.get("file_obj")
                    doc_data = file_info.get("doc_data")

                    if not file or not doc_data:
                        continue

                    # Create document record
                    doc_id = str(uuid4())
                    new_document = Document(
                        id=doc_id,
                        project_id=project_id,
                        name=doc_data.name,
                        description=doc_data.description,
                        uploaded_at=datetime.now(),
                        document_type=doc_data.document_type,
                        file_extension=doc_data.file_extension,
                        size=doc_data.size
                    )
                    db.add(new_document)

                    # Process the file if it exists
                    if file_obj:
                        # Save file temporarily
                        suffix = f".{doc_data.file_extension}" if doc_data.file_extension else ""
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                            temp_file.write(file_obj)
                            temp_file_path = temp_file.name

                        # Upload to S3
                        # try:
                        #     s3_url = upload_to_s3(temp_file_path, doc_data.name)
                        #     new_document.s3_url = s3_url  # Add this field to your Document model
                        # except Exception as e:
                        #     print(f"S3 upload error: {str(e)}")
                        # new_document.s3_url = "default"

                        # Upload to Supabase
                        try:
                            SUPABASE_BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME")
                            supabase_url = upload_to_supabase(temp_file_path, SUPABASE_BUCKET_NAME,  doc_data.name)
                            new_document.s3_url = supabase_url  # Add this field to your Document model
                        except Exception as e:
                            print(f"Supabase upload error: {str(e)}")
                        new_document.s3_url = "default"
                        # For PDF files, extract text and create embeddings
                        if doc_data.file_extension and doc_data.file_extension.lower() == 'pdf':
                            try:
                                # Extract text from PDF
                                texts = []
                                with pdfplumber.open(temp_file_path) as pdf:
                                    for page in pdf.pages:
                                        page_text = page.extract_text()
                                        if page_text:
                                            texts.append(page_text)

                                if texts and index:
                                    # Split text into chunks
                                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                                    text_chunks = text_splitter.split_text("\n".join(texts))

                                    # Generate embeddings
                                    embeddings = [get_gemini_embedding(chunk) for chunk in text_chunks]

                                    # Prepare vectors for Pinecone
                                    vectors = [
                                        {
                                            "id": f"project_{project_id}_doc_{doc_id}_chunk_{i}",
                                            "values": embedding,
                                            "metadata": {
                                                "project_id": project_id,
                                                "document_id": doc_id,
                                                "text": text,
                                                "project_name": project_data.name,
                                                "document_name": doc_data.name
                                            }
                                        }
                                        for i, (text, embedding) in enumerate(zip(text_chunks, embeddings))
                                    ]

                                    # Insert vectors in batches
                                    batch_size = 100
                                    for i in range(0, len(vectors), batch_size):
                                        batch = vectors[i:i + batch_size]
                                        index.upsert(vectors=batch)
                            except Exception as e:
                                print(f"PDF processing error: {str(e)}")

                        # Cleanup temp file
                        try:
                            os.remove(temp_file_path)
                        except:
                            pass

            # Commit all changes
            db.commit()
            db.refresh(new_project)
            return ProjectResponse.model_validate(new_project)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()


@staticmethod
def get_projects_for_user(email: str) -> List[ProjectAbstractData]:
    # Step 1: Get email ID from emails table
    email_response = supabase.from_("emails").select("id").eq("email", email).single().execute()
    email_data = email_response.data

    if not email_data:
        raise HTTPException(status_code=404, detail="Email not found")

    email_id = email_data["id"]

    # Step 2: Get group IDs from email_groups table
    email_groups_response = (
        supabase.from_("email_groups").select("group_id").eq("email_id", email_id).execute()
    )
    email_groups_data = email_groups_response.data

    if not email_groups_data:
        return {"groups": []}  # No groups found for this email

    group_ids = [eg["group_id"] for eg in email_groups_data]

    # Step 3: Get group details from groups table
    groups_response = supabase.from_("groups").select("*").in_("id", group_ids).execute()
    db: Session = next(get_db())
    list_of_projects = get_projects_by_group_names(db, groups_response.data)
    return [
        ProjectAbstractData(
            id=project.id,
            name=project.name,
            description=project.description,
            access_type=project.access_type,
            state=project.state,
            num_documents=len(project.documents),
            updated_at=project.updated_at
        )
        for project in list_of_projects
    ]

    return {"groups": groups_response.data}

def get_projects_by_group_names(db: Session, group_names: list[str]):
    return db.execute(
        select(Project)
        .join(project_group_association)
        .join(ProjectGroup, ProjectGroup.id == project_group_association.c.projectgroup_id)
        .where(ProjectGroup.name.in_(group_names), Project.state == "PUBLISHED")
    ).scalars().all()