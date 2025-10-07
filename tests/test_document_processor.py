import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from services.document_processor import DocumentProcessor
from models.document import Document

class TestDocumentProcessor:
    
    def setup_method(self):
        self.processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
    
    def test_chunk_creation(self):
        """Test that text is properly chunked"""
        text = "This is a test document. " * 100  # Create a long text
        chunks = self.processor._create_chunks(text, document_id=1)
        
        assert len(chunks) > 0
        assert all('content' in chunk for chunk in chunks)
        assert all('index' in chunk for chunk in chunks)
        
        # Check that chunks don't exceed the specified size
        for chunk in chunks:
            assert len(chunk['content']) <= self.processor.chunk_size + 100  # Some tolerance
    
    def test_empty_text_handling(self):
        """Test handling of empty text"""
        chunks = self.processor._create_chunks("", document_id=1)
        assert len(chunks) == 0
    
    def test_short_text_handling(self):
        """Test handling of text shorter than chunk size"""
        text = "This is a short text."
        chunks = self.processor._create_chunks(text, document_id=1)
        
        assert len(chunks) == 1
        assert chunks[0]['content'] == text
        assert chunks[0]['index'] == 0
    
    @patch('services.document_processor.PyPDF2.PdfReader')
    def test_pdf_text_extraction(self, mock_pdf_reader):
        """Test PDF text extraction"""
        # Mock PDF reader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample PDF text content"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b"fake pdf content")
            temp_file_path = temp_file.name
        
        try:
            text = self.processor._extract_pdf_text(temp_file_path)
            assert text == "Sample PDF text content\n"
        finally:
            os.unlink(temp_file_path)
    
    @patch('services.document_processor.docx.Document')
    def test_docx_text_extraction(self, mock_docx):
        """Test DOCX text extraction"""
        # Mock DOCX document
        mock_paragraph = MagicMock()
        mock_paragraph.text = "Sample DOCX text content"
        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_paragraph]
        mock_docx.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_file.write(b"fake docx content")
            temp_file_path = temp_file.name
        
        try:
            text = self.processor._extract_docx_text(temp_file_path)
            assert text == "Sample DOCX text content\n"
        finally:
            os.unlink(temp_file_path)
    
    def test_chunk_overlap(self):
        """Test that chunks have proper overlap"""
        text = "Word1 Word2 Word3 Word4 Word5 Word6 Word7 Word8 Word9 Word10 " * 20
        chunks = self.processor._create_chunks(text, document_id=1)
        
        if len(chunks) > 1:
            # Check that consecutive chunks have some overlap
            chunk1_end = chunks[0]['content'][-50:]
            chunk2_start = chunks[1]['content'][:50]
            
            # There should be some common words between chunks
            chunk1_words = set(chunk1_end.split())
            chunk2_words = set(chunk2_start.split())
            assert len(chunk1_words.intersection(chunk2_words)) > 0