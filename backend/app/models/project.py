from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Table
from datetime import datetime

from sqlalchemy.orm import relationship

from app.database import Base

# Association table for many-to-many relationship between Project and Group
# project_group_association = Table(
#     'project_group_association',
#     Base.metadata,
#     Column('project_id', Integer, ForeignKey('projects.id')),
#     Column('projectgroup_id', Integer, ForeignKey('projectgroups.id'))
# )


# class ProjectGroup(Base):
#     __tablename__ = "projectgroups"
#
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     name = Column(String, nullable=False)
#     # Add other fields as needed for your Group model
#     # Relationship with Project
#     projects = relationship("Project", secondary=project_group_association, back_populates="projectgroups")

# Define the Project model
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    access_type = Column(String, nullable=True)  # Add access_type field
    state = Column(String, default="DRAFT", nullable=False)  # Add state field with default value
    # projectgroups = relationship("ProjectGroup", secondary=project_group_association, back_populates="projects")

    # Define the relationship with the Document model
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")

# Define the Document model
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.now)
    document_type = Column(String, nullable=False)
    file_extension = Column(String, nullable=True)
    size = Column(String, nullable=False)
    s3_url = Column(String, nullable=False)

    # Foreign key to link the document to a project
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    project = relationship("Project", back_populates="documents")