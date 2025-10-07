from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import Config

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Document(Base):
    """Document metadata model"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer)
    page_count = Column(Integer)
    chunk_count = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='processing')
    error_message = Column(Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'page_count': self.page_count,
            'chunk_count': self.chunk_count,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'status': self.status,
            'error_message': self.error_message
        }

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()