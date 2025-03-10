from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your PostgreSQL database details
DATABASE_URL = "postgresql://abhishek:abhishek@localhost:5432/abhishek"

# Create a SQLAlchemy database engine
engine = create_engine(DATABASE_URL)

# Create a session for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()
