from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class RoleEnum(enum.Enum):
    user = "user"
    assistant = "assistant"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(String, nullable=False)  # Message content
    role = Column(Enum(RoleEnum), nullable=False)  # Enum for specifying roles
    timestamp = Column(DateTime, nullable=False)  # Timestamp of the message
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)  # Project Foreign Key
    user_id = Column(String, ForeignKey("users.id"), nullable=False)  # User Foreign Key
