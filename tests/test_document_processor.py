"""
Tests for document processing service
"""

import pytest
import tempfile
import os
from services.document_processor import DocumentProcessor

class TestDocumentProcessor:
    
    def setup_method(self):
        """Setup test method"""
        self.processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
    
    def test_validate_file_type_valid(self):
        """Test file type validation with valid files"""
        assert self.processor.validate_file_type('test.pdf') == 'pdf'
        assert self.processor.validate_file_type('test.docx') == 'docx'
        assert self.processor.validate_file_type('test.txt') == 'txt'
    
    def test_validate_file_type_invalid(self):
        """Test file type validation with invalid files"""
        with pytest.raises(ValueError):
            self.processor.validate_file_type('test.doc')
        
        with pytest.raises(ValueError):
            self.processor.validate_file_type('test.xlsx')
        
        with pytest.raises(ValueError):
            self.processor.validate_file_type('test')
    
    def test_extract_text_from_txt(self):
        """Test text extraction from TXT file"""
        content = "This is a test document with multiple lines.\nSecond line here.\nThird line."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            f.flush()
            
            text, pages, words = self.processor.extract_text_from_txt(f.name)
            
            assert text == content
            assert pages >= 1
            assert words == len(content.split())
        
        os.unlink(f.name)
    
    def test_chunk_text(self):
        """Test text chunking"""
        text = "This is a long text that should be split into multiple chunks. " * 10
        
        chunks = self.processor.chunk_text(text)
        
        assert len(chunks) > 1
        assert all('text' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)
        assert all(chunk['metadata']['chunk_index'] == i for i, chunk in enumerate(chunks))
    
    def test_chunk_text_empty(self):
        """Test chunking empty text"""
        chunks = self.processor.chunk_text("")
        assert chunks == []
        
        chunks = self.processor.chunk_text("   ")
        assert chunks == []
    
    def test_chunk_text_with_metadata(self):
        """Test chunking with additional metadata"""
        text = "This is a test text for chunking."
        metadata = {'filename': 'test.txt', 'document_id': 1}
        
        chunks = self.processor.chunk_text(text, metadata)
        
        assert len(chunks) == 1
        assert chunks[0]['metadata']['filename'] == 'test.txt'
        assert chunks[0]['metadata']['document_id'] == 1
        assert 'chunk_index' in chunks[0]['metadata']
    
    def test_validate_file_size(self):
        """Test file size validation"""
        # Create a small test file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            f.flush()
            
            size = self.processor.validate_file_size(f.name, max_size_mb=1)
            assert size > 0
            
            # Test size limit
            with pytest.raises(ValueError):
                self.processor.validate_file_size(f.name, max_size_mb=0)
        
        os.unlink(f.name)