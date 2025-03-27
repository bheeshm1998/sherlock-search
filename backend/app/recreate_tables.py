from app.database import Base, engine

from app.models.project import Project, Document
from app.models.message import Message

# Function to drop and recreate tables
def recreate_tables():
    print("Dropping old tables...")
    Base.metadata.drop_all(bind=engine)  # Drop all tables

    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)  # Create tables with updated schema

    print("Database tables recreated successfully.")

if __name__ == "__main__":
    recreate_tables()
