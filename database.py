from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processing_status = db.Column(db.String(50), default='pending')
    chunk_count = db.Column(db.Integer, default=0)
    metadata = db.Column(db.Text)  # JSON string for additional metadata
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'upload_date': self.upload_date.isoformat(),
            'processing_status': self.processing_status,
            'chunk_count': self.chunk_count,
            'metadata': self.metadata
        }

class QueryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    document_ids = db.Column(db.Text)  # JSON string of document IDs used
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.Float)  # Response time in seconds
    
    def to_dict(self):
        return {
            'id': self.id,
            'query': self.query,
            'response': self.response,
            'document_ids': self.document_ids,
            'timestamp': self.timestamp.isoformat(),
            'response_time': self.response_time
        }

def init_db():
    """Initialize the database with all tables"""
    db.create_all()
    print("Database initialized successfully")

def get_document_by_id(document_id):
    """Get document by ID"""
    return Document.query.get(document_id)

def get_all_documents():
    """Get all documents"""
    return Document.query.all()

def create_document(filename, original_filename, file_path, file_size, file_type, metadata=None):
    """Create a new document record"""
    document = Document(
        filename=filename,
        original_filename=original_filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        metadata=metadata
    )
    db.session.add(document)
    db.session.commit()
    return document

def update_document_status(document_id, status, chunk_count=None):
    """Update document processing status"""
    document = Document.query.get(document_id)
    if document:
        document.processing_status = status
        if chunk_count is not None:
            document.chunk_count = chunk_count
        db.session.commit()
        return document
    return None

def log_query(query, response, document_ids, response_time):
    """Log a query and its response"""
    query_log = QueryLog(
        query=query,
        response=response,
        document_ids=document_ids,
        response_time=response_time
    )
    db.session.add(query_log)
    db.session.commit()
    return query_log