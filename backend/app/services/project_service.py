import os
import tempfile

import pdfplumber
from fastapi import HTTPException
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session, joinedload
from uuid import uuid4
from datetime import datetime
from typing import List,Optional

from supabase import create_client, Client

from app.config.pinecone_init import pc, create_project_index
from app.database import get_db
from app.models.project import Project, Document
from app.routes.document_routes import get_gemini_embedding
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectAbstractData
from app.utils.supabase import upload_to_supabase,delete_from_supabase

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
    def getProjectById(project_id: int) -> dict:

        groups = ProjectService.get_groups_by_project(project_id)

        db: Session = next(get_db())
        project = db.query(Project).options(joinedload(Project.documents)).filter(Project.id == project_id).first()

        # If project not found, raise an HTTP 404 exception
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Return the project details
        return {"project": project, "groups": groups}


    @staticmethod
    def get_groups_by_project(project_id: int) -> List[str]:
        group_ids_response = (
            supabase
            .from_("project_groups")
            .select("group_id")
            .eq("project_id", project_id)
            .execute()
        )

        # Extract just the group IDs from the response
        group_ids = [item["group_id"] for item in group_ids_response.data]

        # Second call: Get the group names for these IDs from the groups table
        groups_response = (
            supabase
            .from_("groups")
            .select("id, name")
            .in_("id", group_ids)
            .execute()
        )
        return groups_response.data

    # @deprecated
    # @staticmethod
    # def create_project(project_data: ProjectCreate) -> ProjectResponse:
    #     """
    #     Create a new project in the database.
    #     """
    #     db: Session = next(get_db())
    #
    #     existing_project = db.query(Project).filter_by(name=project_data.name).first()
    #     if existing_project:
    #         raise ValueError(f"A project with the name '{project_data.name}' already exists.")
    #
    #     try:
    #         new_project = Project(
    #             id=str(uuid4()),
    #             name=project_data.name,
    #             description=project_data.description,
    #             created_at=datetime.now(),
    #             updated_at=datetime.now(),
    #         )
    #         db.add(new_project)
    #         db.commit()
    #         db.refresh(new_project)
    #         return ProjectResponse.model_validate(new_project)
    #     except Exception as e:
    #         db.rollback()
    #         raise e
    #     finally:
    #         db.close()

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
    def update_project_with_files(
        project_id: str, name:str, updated_description: str, access_type: str, files: Optional[List[dict]] = None
    ) -> ProjectResponse:
        """
        Update an existing project's description, access type, and manage document changes:
        - Overwrites existing document records.
        - Removes deleted files from database, Supabase & Pinecone.
        - Only uploads new documents to Supabase & inserts them into DB.
        - Updates Pinecone index with only new documents.
        """
        db: Session = next(get_db())
        try:
            # Fetch the project
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise ValueError("Project not found")

            # Update description & access type
            project.name = name
            project.description = updated_description
            project.access_type = access_type
            project.updated_at = datetime.now()

            # Fetch project-specific index
            index_name = f"project-{project_id}"
            index = pc.Index(index_name)

            # Get existing document records (Filter by `id`, NOT `name`)
            existing_docs = {doc.id: doc for doc in project.documents}

            # Track processed document IDs
            processed_doc_ids = set()

            # Process new & existing documents
            if files:
                for file_info in files:
                    file = file_info.get("file")
                    file_obj = file_info.get("file_obj")
                    doc_data = file_info.get("doc_data")

                    if not file or not doc_data:
                        continue

                    # Check if the document already exists based on ID
                    doc_id = doc_data.id if hasattr(doc_data, "id") else str(uuid4())  
                    processed_doc_ids.add(doc_id)

                    if doc_id in existing_docs:
                        # Skip re-uploading existing documents
                        continue

                    # Create a new document record
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

                    if file_obj:
                        # Save file temporarily
                        suffix = f".{doc_data.file_extension}" if doc_data.file_extension else ""
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                            temp_file.write(file_obj)
                            temp_file_path = temp_file.name

                        # Upload to Supabase
                        try:
                            SUPABASE_BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME")
                            supabase_url = upload_to_supabase(temp_file_path, SUPABASE_BUCKET_NAME,project.id,doc_id)
                            new_document.s3_url = supabase_url
                        except Exception as e:
                            print(f"Supabase upload error: {str(e)}")
                            new_document.s3_url = "default"

                        # Process PDF files for embeddings
                        if doc_data.file_extension.lower() == 'pdf':
                            try:
                                texts = []
                                with pdfplumber.open(temp_file_path) as pdf:
                                    for page in pdf.pages:
                                        page_text = page.extract_text()
                                        if page_text:
                                            texts.append(page_text)

                                if texts:
                                    # Split text into chunks
                                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                                    text_chunks = text_splitter.split_text("\n".join(texts))

                                    # Generate embeddings
                                    embeddings = [get_gemini_embedding(chunk) for chunk in text_chunks]

                                    # Prepare vectors for Pinecone
                                    vectors = [
                                        {
                                            "id": f"project_{project_id}_doc_{new_document.id}_chunk_{i}",
                                            "values": embedding,
                                            "metadata": {
                                                "project_id": project_id,
                                                "document_id": new_document.id,
                                                "text": text,
                                                "project_name": project.name,
                                                "document_name": doc_data.name
                                            }
                                        }
                                        for i, (text, embedding) in enumerate(zip(text_chunks, embeddings))
                                    ]

                                    # Insert vectors into Pinecone in batches
                                    batch_size = 100
                                    for i in range(0, len(vectors), batch_size):
                                        batch = vectors[i:i + batch_size]
                                        index.upsert(vectors=batch)
                            except Exception as e:
                                print(f"PDF processing error: {str(e)}")

                        # Cleanup temp file
                        try:
                            os.remove(temp_file_path)
                        except Exception as e:
                            print(f"Error deleting temp file: {e}")

            # Find and delete removed documents (Filter by ID, NOT name)
            removed_docs = set(existing_docs.keys()) - processed_doc_ids
            for doc_id in removed_docs:
                doc_to_remove = existing_docs[doc_id]

                # Delete from Supabase
                try:
                    delete_from_supabase(doc_to_remove.s3_url)
                except Exception as e:
                    print(f"Supabase deletion error: {str(e)}")

                # Delete from Pinecone
                try:
                    index.delete(ids=[f"project_{project_id}_doc_{doc_to_remove.id}"])
                except Exception as e:
                    print(f"Pinecone deletion error: {str(e)}")

                # Remove from database
                db.delete(doc_to_remove)

            # Commit all changes
            db.commit()
            db.refresh(project)
            return ProjectResponse.model_validate(project)

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
    def create_project_v2(project_data: ProjectCreate, groups: List[str], files: List[dict] = None ) -> ProjectResponse:
        """
        Create a new project in the database with associated documents.
        """
        db: Session = next(get_db())

        existing_project = db.query(Project).filter_by(name=project_data.name).first()
        if existing_project:
            raise ValueError(f"A project with the name '{project_data.name}' already exists.")

        try:
            # Create project

            # Ensure a new index is created for the project (if under the limit)


            new_project = Project(
                name=project_data.name,
                description=project_data.description,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                access_type=project_data.access_type,
                state=project_data.state or "DRAFT"
            )
            db.add(new_project)
            db.flush()  # Flush to get project ID without committing
            db.refresh(new_project)  # Ensure ID is populated
            project_id = new_project.id

            try:
                index_name = create_project_index(project_id)
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

            index = None  # Initialize index to avoid NameError
            # Initialize Pinecone if files are provided
            if files:
                try:
                    index = pc.Index(index_name)
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
                    new_document = Document(
                        project_id=project_id,
                        name=doc_data.name,
                        description=doc_data.description,
                        uploaded_at=datetime.now(),
                        document_type=doc_data.document_type,
                        file_extension=doc_data.file_extension,
                        size=doc_data.size,
                        s3_url="default"
                    )
                    db.add(new_document)
                    db.flush()
                    db.refresh(new_document)  # Ensure ID is populated
                    doc_id = new_document.id
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
                            # SUPABASE_BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME")
                            # supabase_url = upload_to_supabase(temp_file_path, SUPABASE_BUCKET_NAME, project_id, doc_id)
                            # if supabase_url:
                            #     new_document.s3_url = supabase_url
                            new_document.s3_url = "default"
                        except Exception as e:
                            print(f"Supabase upload error: {str(e)}")

                        # For PDF files, extract text and create embeddings
                        if doc_data.file_extension and (doc_data.file_extension.lower() == 'pdf' or doc_data.file_extension.lower() == 'doc' or doc_data.file_extension.lower() == 'docx'):
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
                                    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                                        chunk_size=1000,
                                        chunk_overlap=200,
                                        separators=["\n\n", "\n", " ", ""]
                                    )
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

            # Step 2: Fetch group IDs based on the provided group names
            group_query = supabase.table("groups").select("id").in_("name", groups).execute()

            if not group_query.data:
                raise HTTPException(status_code=404, detail="One or more groups not found")

            group_ids = [group["id"] for group in group_query.data]

            # Step 3: Insert records into group_projects table
            group_project_entries = [{"group_id": gid, "project_id": project_id} for gid in group_ids]
            group_project_response = supabase.table("project_groups").insert(group_project_entries).execute()

            if not group_project_response.data:
                raise HTTPException(status_code=500, detail="Failed to associate groups with project")

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

        if not group_ids:
            return []

            # Step 1: Get all project_ids associated with the given group_ids
        project_groups_response = (
            supabase
            .from_("project_groups")
            .select("project_id")
            .in_("group_id", group_ids)
            .execute()
        )

        if not project_groups_response.data:
            return []

        project_ids = list({entry["project_id"] for entry in project_groups_response.data})
        db: Session = next(get_db())
        # Step 2: Fetch projects with state="published"
        projects_response  = (
            db.query(Project)
            .filter(Project.id.in_(project_ids), Project.state == "PUBLISHED")
            .all()
        )

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
            for project in projects_response
            ]


    @staticmethod
    def delete_project(project_id: int):
        """
        Delete a project and its associated resources:
        - Remove project from database
        - Delete associated documents from Supabase
        - Delete Pinecone index
        - Remove project-group associations
        """
        db: Session = next(get_db())
        try:
            # Find the project
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise ValueError("Project not found")

            # Get the Pinecone index name
            index_name = f"project-{project_id}"

            # Delete documents from Supabase and Pinecone
            try:
                # Fetch the Pinecone index
                index = pc.Index(index_name)

                # Delete document vectors from Pinecone
                for document in project.documents:
                    # Delete Supabase file
                    # try:
                    #     delete_from_supabase(document.s3_url)
                    # except Exception as e:
                    #     print(f"Supabase deletion error: {str(e)}")

                    # Delete document vectors from Pinecone
                    try:
                        # # Delete all vectors associated with this document
                        # vector_ids = [
                        #     f"project_{project_id}_doc_{document.id}_chunk_{i}"
                        #     for i in range(1000)  # Assume a reasonable max number of chunks
                        # ]
                        # index.delete(ids=vector_ids)
                        if check_pinecone_index_exists(index_name):
                            try:
                                pc.delete_index(index_name)
                            except Exception as e:
                                print(f"Error deleting Pinecone index: {str(e)}")

                    except Exception as e:
                        print(f"Pinecone vector deletion error: {str(e)}")

            except Exception as e:
                print(f"Error accessing Pinecone index: {str(e)}")

            # Delete project-group associations from Supabase
            # try:
            #     supabase.table("project_groups").delete().eq("project_id", project_id).execute()
            # except Exception as e:
            #     print(f"Error deleting project group associations: {str(e)}")

            # Delete Pinecone index
            # try:
            #     pc.delete_index(index_name)
            # except Exception as e:
            #     print(f"Error deleting Pinecone index: {str(e)}")

            # Delete project and associated documents from database
            db.delete(project)
            db.commit()

            return {"message": "Project deleted successfully"}

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()


def check_pinecone_index_exists(index_name: str) -> bool:
    try:
        # This will raise an exception if the index doesn't exist
        pc.describe_index(index_name)
        return True
    except Exception:
        return False