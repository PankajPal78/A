"""
Database utility functions
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.models.document import Base
from config.settings import DATABASE_URL

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(engine)

def get_session():
    """Get database session"""
    return Session()

def close_session():
    """Close database session"""
    Session.remove()