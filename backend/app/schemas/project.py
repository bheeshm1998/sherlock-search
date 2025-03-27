from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class Group(BaseModel):
    id: int
    name: str

# Model for creating a new document
class DocumentCreate(BaseModel):
    name: int
    description: Optional[str] = None
    document_type: str
    file_extension: Optional[str] = None
    size: str

# Model for responding with document details
class DocumentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    uploaded_at: datetime
    document_type: str
    file_extension: Optional[str]
    size: str

    class Config:
        from_attributes = True  # Enable ORM mode (previously `orm_mode`)

# Model for creating a new project
class ProjectCreate(BaseModel):
    name: int
    description: Optional[str] = None
    access_type: Optional[str] = None
    state: Optional[str] = "DRAFT"  # Default state is DRAFT
    groups: Optional[str] = "ALL"
    documents: Optional[List[DocumentCreate]] = None  # Include documents field
    groups: Optional[List[Group]] = None

# Model for responding with project details
class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    access_type: Optional[str]
    groups: Optional[str]
    state: str
    documents: List[DocumentResponse]  # Include documents field
    groups: List[Group]

    class Config:
        from_attributes = True  # Enable ORM mode (previously `orm_mode`)

# Model for creating a new project
class ProjectAbstractData(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    access_type: Optional[str] = None
    state: Optional[str] = "DRAFT"  # Default state is DRAFT
    num_documents: int
    updated_at: datetime
    groups: List[Group]
