import pytest
from app.document_processor import DocumentProcessor

def test_document_processor_initialization():
    """Test document processor initialization"""
    processor = DocumentProcessor()
    assert processor.text_splitter is not None

def test_chunk_text():
    """Test text chunking"""
    processor = DocumentProcessor()
    text = "This is a test document. " * 100
    chunks = processor.chunk_text(text)
    
    assert len(chunks) > 0
    assert all('text' in chunk for chunk in chunks)
    assert all('chunk_index' in chunk for chunk in chunks)

def test_chunk_text_with_metadata():
    """Test text chunking with metadata"""
    processor = DocumentProcessor()
    text = "This is a test document. " * 100
    metadata = {'filename': 'test.txt', 'document_id': '1'}
    chunks = processor.chunk_text(text, metadata=metadata)
    
    assert len(chunks) > 0
    assert all(chunk['metadata'] == metadata for chunk in chunks)