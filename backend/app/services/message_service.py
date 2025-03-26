from sqlalchemy.orm import Session
from app.database import get_db
from app.models.message import Message
from app.schemas.message import MessageCreate
from datetime import datetime
import uuid


class MessageService:
    @staticmethod
    def create_user_message(message_data: MessageCreate) -> Message:
        """
        Create and save the user's message in the database.
        """
        db: Session = next(get_db())  # The database dependency is only here
        try:
            new_message = Message(
                id=str(uuid.uuid4()),  # Generate a unique ID
                content=message_data.content,
                role=message_data.role,  # User role
                timestamp=datetime.utcnow(),  # Timestamp added
                project_id=message_data.project_id,
                user_id=message_data.user_id,
            )
            db.add(new_message)
            db.commit()
            db.refresh(new_message)
            return new_message
        finally:
            db.close()

    @staticmethod
    def create_assistant_message(content: str, project_id: str, user_id: str) -> Message:
        """
        Create and save the assistant's response message in the database.
        """
        db: Session = next(get_db())  # The database dependency is only here
        try:
            new_message = Message(
                id=str(uuid.uuid4()),  # Generate a unique ID
                content=content,
                role="assistant",  # Assistant role
                timestamp=datetime.utcnow(),  # Timestamp added
                project_id=project_id,
                user_id=user_id,
            )
            db.add(new_message)
            db.commit()
            db.refresh(new_message)
            return new_message
        finally:
            db.close()

    @staticmethod
    def get_project_messages(project_id: str, user_id: str) -> list[Message]:
        """
        Fetch all messages for a specific project ID.
        """
        db: Session = next(get_db())  # The database dependency is only here
        try:
            messages = (
                db.query(Message)
                .filter(Message.project_id == project_id)
                .filter(Message.user_id == user_id)  # Additional filter for user_id
                .order_by(Message.timestamp.asc())  # Order by timestamp
                .all()
            )
            return messages
        finally:
            db.close()

    @staticmethod
    def create_message(message_data: MessageCreate) -> Message:
        """
        Create and save the assistant's response message in the database.
        """
        db: Session = next(get_db())  # The database dependency is only here
        try:
            new_message = Message(
                id=str(uuid.uuid4()),  # Generate a unique ID
                content=message_data.content,
                role=message_data.role,  # Assistant role
                timestamp=datetime.utcnow(),  # Timestamp added
                project_id=message_data.project_id,
                user_id=message_data.user_id,
            )
            db.add(new_message)
            db.commit()
            db.refresh(new_message)
            return new_message
        finally:
            db.close()