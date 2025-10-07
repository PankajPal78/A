import os
from typing import List, Dict
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import Config

class DocumentProcessor:
    """Handles document ingestion and chunking"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, file_path: str) -> tuple[str, int]:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Tuple of (extracted_text, page_count)
        """
        try:
            reader = PdfReader(file_path)
            page_count = len(reader.pages)
            
            # Check page limit
            if page_count > Config.MAX_PAGES_PER_DOCUMENT:
                raise ValueError(f"Document has {page_count} pages, exceeding the limit of {Config.MAX_PAGES_PER_DOCUMENT}")
            
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text, page_count
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_from_txt(self, file_path: str) -> tuple[str, int]:
        """
        Extract text from TXT file
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            Tuple of (extracted_text, page_count)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Estimate page count (assuming ~500 words per page)
            word_count = len(text.split())
            page_count = max(1, word_count // 500)
            
            return text, page_count
        except Exception as e:
            raise Exception(f"Error extracting text from TXT: {str(e)}")
    
    def process_document(self, file_path: str, filename: str) -> tuple[str, int]:
        """
        Process document and extract text
        
        Args:
            file_path: Path to document
            filename: Name of the file
            
        Returns:
            Tuple of (extracted_text, page_count)
        """
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        if file_extension == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension == 'txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Chunk text into smaller pieces
        
        Args:
            text: Text to chunk
            metadata: Additional metadata to attach to chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = self.text_splitter.split_text(text)
        
        chunk_dicts = []
        for i, chunk in enumerate(chunks):
            chunk_dict = {
                'text': chunk,
                'chunk_index': i,
                'metadata': metadata or {}
            }
            chunk_dicts.append(chunk_dict)
        
        return chunk_dicts