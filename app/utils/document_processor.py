"""
Document processing utilities for chunking and text extraction
"""
import PyPDF2
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP, MAX_PAGES_PER_DOCUMENT

class DocumentProcessor:
    """Process documents for RAG pipeline"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def extract_text_from_pdf(self, file_path: str) -> tuple[str, int]:
        """
        Extract text from PDF file
        Returns: (text, page_count)
        """
        text = ""
        page_count = 0
        
        try:
            # Use PyMuPDF for better text extraction
            doc = fitz.open(file_path)
            page_count = len(doc)
            
            # Check page limit
            if page_count > MAX_PAGES_PER_DOCUMENT:
                raise ValueError(f"Document exceeds maximum page limit of {MAX_PAGES_PER_DOCUMENT}")
            
            for page_num in range(page_count):
                page = doc[page_num]
                text += page.get_text()
            
            doc.close()
        except Exception as e:
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    page_count = len(pdf_reader.pages)
                    
                    if page_count > MAX_PAGES_PER_DOCUMENT:
                        raise ValueError(f"Document exceeds maximum page limit of {MAX_PAGES_PER_DOCUMENT}")
                    
                    for page in pdf_reader.pages:
                        text += page.extract_text()
            except Exception as e2:
                raise Exception(f"Failed to extract text from PDF: {str(e2)}")
        
        return text, page_count
    
    def extract_text_from_txt(self, file_path: str) -> tuple[str, int]:
        """
        Extract text from TXT file
        Returns: (text, page_count)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            # Estimate page count (assuming ~3000 chars per page)
            page_count = max(1, len(text) // 3000)
            return text, page_count
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()
            page_count = max(1, len(text) // 3000)
            return text, page_count
    
    def extract_text(self, file_path: str, file_type: str) -> tuple[str, int]:
        """
        Extract text from document based on file type
        Returns: (text, page_count)
        """
        if file_type == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type in ['txt', 'text']:
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks
        Returns: List of chunk dictionaries with text and metadata
        """
        chunks = self.text_splitter.split_text(text)
        
        # Create chunk objects with metadata
        chunk_objects = []
        for i, chunk in enumerate(chunks):
            chunk_obj = {
                'text': chunk,
                'chunk_index': i,
                'metadata': metadata or {}
            }
            chunk_objects.append(chunk_obj)
        
        return chunk_objects
    
    def process_document(self, file_path: str, file_type: str, document_id: int, filename: str) -> List[Dict]:
        """
        Complete document processing pipeline
        Returns: List of processed chunks with metadata
        """
        # Extract text
        text, page_count = self.extract_text(file_path, file_type)
        
        if not text.strip():
            raise ValueError("No text could be extracted from the document")
        
        # Prepare metadata
        metadata = {
            'document_id': document_id,
            'filename': filename,
            'page_count': page_count,
            'file_path': file_path
        }
        
        # Chunk text
        chunks = self.chunk_text(text, metadata)
        
        return chunks, page_count