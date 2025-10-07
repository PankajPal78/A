from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float

class Document:
    """Document model - will be converted to SQLAlchemy model in app.py"""
    __tablename__ = 'documents'
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        return {
            'id': getattr(self, 'id', None),
            'filename': getattr(self, 'filename', ''),
            'original_filename': getattr(self, 'original_filename', ''),
            'file_size': getattr(self, 'file_size', 0),
            'file_type': getattr(self, 'file_type', ''),
            'upload_date': getattr(self, 'upload_date', None).isoformat() if getattr(self, 'upload_date', None) else None,
            'processing_status': getattr(self, 'processing_status', 'pending'),
            'total_pages': getattr(self, 'total_pages', 0),
            'total_chunks': getattr(self, 'total_chunks', 0),
            'processing_error': getattr(self, 'processing_error', None)
        }

class DocumentChunk:
    """DocumentChunk model - will be converted to SQLAlchemy model in app.py"""
    __tablename__ = 'document_chunks'
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        content = getattr(self, 'content', '')
        return {
            'id': getattr(self, 'id', None),
            'document_id': getattr(self, 'document_id', None),
            'chunk_index': getattr(self, 'chunk_index', 0),
            'content': content[:200] + '...' if len(content) > 200 else content,
            'page_number': getattr(self, 'page_number', None),
            'chunk_size': getattr(self, 'chunk_size', 0),
            'embedding_id': getattr(self, 'embedding_id', None)
        }