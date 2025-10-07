"""
Database models for document management
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import json

db = SQLAlchemy()

class Document(db.Model):
    """Document model for storing document metadata"""
    
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    
    # Content metadata
    total_pages = db.Column(db.Integer, default=0)
    total_chunks = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer, default=0)
    
    # Processing status
    status = db.Column(db.String(50), default='uploaded')  # uploaded, processing, processed, error
    error_message = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    # Vector database reference
    collection_ids = db.Column(db.Text, nullable=True)  # JSON array of chunk IDs in vector DB
    
    def __repr__(self):
        return f'<Document {self.filename}>'
    
    def to_dict(self):
        """Convert document to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'total_pages': self.total_pages,
            'total_chunks': self.total_chunks,
            'word_count': self.word_count,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'collection_ids': json.loads(self.collection_ids) if self.collection_ids else []
        }
    
    def update_status(self, status, error_message=None):
        """Update document processing status"""
        self.status = status
        self.error_message = error_message
        self.updated_at = datetime.utcnow()
        if status == 'processed':
            self.processed_at = datetime.utcnow()
        db.session.commit()
    
    def add_collection_ids(self, chunk_ids):
        """Add chunk IDs to the document"""
        if self.collection_ids:
            existing_ids = json.loads(self.collection_ids)
            existing_ids.extend(chunk_ids)
            self.collection_ids = json.dumps(existing_ids)
        else:
            self.collection_ids = json.dumps(chunk_ids)
        db.session.commit()

class QueryLog(db.Model):
    """Model for logging user queries and responses"""
    
    __tablename__ = 'query_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    query_text = db.Column(db.Text, nullable=False)
    response_text = db.Column(db.Text, nullable=True)
    
    # Retrieval metadata
    retrieved_chunks = db.Column(db.Integer, default=0)
    similarity_scores = db.Column(db.Text, nullable=True)  # JSON array
    source_documents = db.Column(db.Text, nullable=True)  # JSON array of document IDs
    
    # Performance metrics
    retrieval_time = db.Column(db.Float, default=0.0)  # seconds
    generation_time = db.Column(db.Float, default=0.0)  # seconds
    total_time = db.Column(db.Float, default=0.0)  # seconds
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<QueryLog {self.id}>'
    
    def to_dict(self):
        """Convert query log to dictionary"""
        return {
            'id': self.id,
            'query_text': self.query_text,
            'response_text': self.response_text,
            'retrieved_chunks': self.retrieved_chunks,
            'similarity_scores': json.loads(self.similarity_scores) if self.similarity_scores else [],
            'source_documents': json.loads(self.source_documents) if self.source_documents else [],
            'retrieval_time': self.retrieval_time,
            'generation_time': self.generation_time,
            'total_time': self.total_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }