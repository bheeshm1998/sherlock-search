from app.database import Base, engine

# from app.models.project import Project
from app.models.message import Message
# from app.models.project import Document

# Function to create all tables
def create_tables():
    print("Creating tables in the database...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    create_tables()