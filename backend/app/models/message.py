from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer


from app.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(String, nullable=False)  # Message content
    role = Column(String, nullable=False)  # Enum for specifying roles
    timestamp = Column(DateTime, nullable=False)  # Timestamp of the message
    project_id = Column(String, nullable=False)  # Project Foreign Key
    user_id = Column(String, nullable=False)  # User Foreign Key
