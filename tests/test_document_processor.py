import pytest
import tempfile
import os
from services.document_processor import DocumentProcessor

class TestDocumentProcessor:
    """Test cases for DocumentProcessor"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
    
    def test_clean_text(self):
        """Test text cleaning functionality"""
        dirty_text = "This   is    a   test.\n\n\nWith   extra   spaces!"
        clean_text = self.processor._clean_text(dirty_text)
        assert clean_text == "This is a test. With extra spaces!"
    
    def test_split_into_chunks(self):
        """Test text chunking functionality"""
        text = "This is sentence one. This is sentence two. This is sentence three. This is sentence four."
        chunks = self.processor._split_into_chunks(text)
        
        assert len(chunks) > 0
        assert all('id' in chunk for chunk in chunks)
        assert all('text' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)
    
    def test_split_into_chunks_empty_text(self):
        """Test chunking with empty text"""
        chunks = self.processor._split_into_chunks("")
        assert chunks == []
    
    def test_split_into_chunks_short_text(self):
        """Test chunking with text shorter than chunk size"""
        text = "Short text."
        chunks = self.processor._split_into_chunks(text)
        assert len(chunks) == 1
        assert chunks[0]['text'] == text
    
    def test_txt_file_processing(self):
        """Test processing of TXT files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document. It contains multiple sentences. Each sentence should be processed correctly.")
            temp_path = f.name
        
        try:
            chunks = self.processor.process_document(temp_path)
            assert len(chunks) > 0
            assert all('id' in chunk for chunk in chunks)
        finally:
            os.unlink(temp_path)
    
    def test_unsupported_file_type(self):
        """Test error handling for unsupported file types"""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                self.processor.process_document(temp_path)
        finally:
            os.unlink(temp_path)