"""
Database models for document metadata
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Document(Base):
    """Document metadata model"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    page_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='uploaded')  # uploaded, processing, indexed, failed
    error_message = Column(Text, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'page_count': self.page_count,
            'chunk_count': self.chunk_count,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'status': self.status,
            'error_message': self.error_message
        }