from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from typing import List
from app.database import get_db
from app.database import SessionLocal
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectResponse


class ProjectService:

    @staticmethod
    def get_all_projects() -> List[ProjectResponse]:
        """
        Fetch all projects from the database.
        """
        db: Session = next(get_db())
        projects = db.query(Project).all()
        db.close()
        return [ProjectResponse.model_validate(project) for project in projects]

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