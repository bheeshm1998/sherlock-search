from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# Model for creating a new document
class DocumentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    document_type: str
    file_extension: Optional[str] = None
    size: str

# Model for responding with document details
class DocumentResponse(BaseModel):
    id: str
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
    name: str
    description: Optional[str] = None
    access_type: Optional[str] = None
    state: Optional[str] = "DRAFT"  # Default state is DRAFT
    documents: Optional[List[DocumentCreate]] = None  # Include documents field

# Model for responding with project details
class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    access_type: Optional[str]
    state: str
    documents: List[DocumentResponse]  # Include documents field

    class Config:
        from_attributes = True  # Enable ORM mode (previously `orm_mode`)