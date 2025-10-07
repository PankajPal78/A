"""
Document processor tests
"""
import pytest
from app.utils.document_processor import DocumentProcessor
import tempfile
import os

class TestDocumentProcessor:
    """Test document processing functionality"""
    
    @pytest.fixture
    def processor(self):
        """Create document processor instance"""
        return DocumentProcessor()
    
    def test_chunk_text(self, processor):
        """Test text chunking"""
        text = "This is a test. " * 200  # Create long text
        chunks = processor.chunk_text(text)
        
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('chunk_index' in chunk for chunk in chunks)
    
    def test_chunk_text_with_metadata(self, processor):
        """Test text chunking with metadata"""
        text = "Test text"
        metadata = {'doc_id': 1, 'filename': 'test.pdf'}
        chunks = processor.chunk_text(text, metadata)
        
        assert len(chunks) > 0
        assert chunks[0]['metadata'] == metadata
    
    def test_extract_text_from_txt(self, processor):
        """Test text extraction from TXT file"""
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document.\nWith multiple lines.")
            temp_path = f.name
        
        try:
            text, page_count = processor.extract_text_from_txt(temp_path)
            assert len(text) > 0
            assert "test document" in text
            assert page_count >= 1
        finally:
            os.unlink(temp_path)
    
    def test_extract_text_empty_file(self, processor):
        """Test extraction from empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            text, page_count = processor.extract_text_from_txt(temp_path)
            assert text == ""
            assert page_count == 1
        finally:
            os.unlink(temp_path)