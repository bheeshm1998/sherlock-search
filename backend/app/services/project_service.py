import os
import tempfile

import pdfplumber
from fastapi import HTTPException
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from typing import List

from app.config.pinecone_init import pc
from app.database import get_db
from app.models.project import Project, Document
from app.routes.document_routes import get_gemini_embedding
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectAbstractData
from app.utils.s3 import upload_to_s3


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
                    state=project.state
                )
                for project in projects
            ]
        finally:
            db.close()

    @staticmethod
    def getProjectById(project_id: str) -> Project:
        db: Session = next(get_db())
        project = db.query(Project).filter(Project.id == project_id).first()

        # If project not found, raise an HTTP 404 exception
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Return the project details
        return project

    @staticmethod
    def create_project(project_data: ProjectCreate) -> ProjectResponse:
        """
        Create a new project in the database.
        """
        db: Session = next(get_db())
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
    def create_project_v2(project_data: ProjectCreate, files: List[dict] = None) -> ProjectResponse:
        """
        Create a new project in the database with associated documents.
        """
        db: Session = next(get_db())
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