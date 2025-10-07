"""
Document processing service for text extraction and chunking
"""

import os
import logging
from typing import List, Dict, Any, Tuple
import PyPDF2
from docx import Document as DocxDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Service for processing uploaded documents"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        # Initialize tokenizer for token counting
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.tokenizer = None
    
    def extract_text_from_pdf(self, file_path: str) -> Tuple[str, int, int]:
        """
        Extract text from PDF file
        Returns: (text_content, page_count, word_count)
        """
        try:
            text_content = ""
            page_count = 0
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                # Check page limit
                if page_count > 1000:
                    raise ValueError(f"Document has {page_count} pages, exceeding limit of 1000 pages")
                
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            
            word_count = len(text_content.split())
            return text_content.strip(), page_count, word_count
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            raise
    
    def extract_text_from_docx(self, file_path: str) -> Tuple[str, int, int]:
        """
        Extract text from DOCX file
        Returns: (text_content, page_count, word_count)
        """
        try:
            doc = DocxDocument(file_path)
            text_content = ""
            
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            
            # Estimate page count (rough approximation: 250 words per page)
            word_count = len(text_content.split())
            page_count = max(1, word_count // 250)
            
            # Check page limit
            if page_count > 1000:
                raise ValueError(f"Document has approximately {page_count} pages, exceeding limit of 1000 pages")
            
            return text_content.strip(), page_count, word_count
            
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {str(e)}")
            raise
    
    def extract_text_from_txt(self, file_path: str) -> Tuple[str, int, int]:
        """
        Extract text from TXT file
        Returns: (text_content, page_count, word_count)
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                text_content = file.read()
            
            word_count = len(text_content.split())
            # Estimate page count (rough approximation: 250 words per page)
            page_count = max(1, word_count // 250)
            
            # Check page limit
            if page_count > 1000:
                raise ValueError(f"Document has approximately {page_count} pages, exceeding limit of 1000 pages")
            
            return text_content.strip(), page_count, word_count
            
        except Exception as e:
            logger.error(f"Error extracting text from TXT {file_path}: {str(e)}")
            raise
    
    def extract_text(self, file_path: str, file_type: str) -> Tuple[str, int, int]:
        """
        Extract text from file based on file type
        Returns: (text_content, page_count, word_count)
        """
        file_type = file_type.lower()
        
        if file_type == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type == 'docx':
            return self.extract_text_from_docx(file_path)
        elif file_type == 'txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Split text into chunks for vector storage
        Returns list of chunk dictionaries with text and metadata
        """
        try:
            if not text.strip():
                return []
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create chunk objects with metadata
            chunk_objects = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    'chunk_index': i,
                    'chunk_size': len(chunk),
                    'word_count': len(chunk.split())
                }
                
                # Add token count if tokenizer is available
                if self.tokenizer:
                    try:
                        chunk_metadata['token_count'] = len(self.tokenizer.encode(chunk))
                    except Exception:
                        pass
                
                # Merge with provided metadata
                if metadata:
                    chunk_metadata.update(metadata)
                
                chunk_objects.append({
                    'text': chunk,
                    'metadata': chunk_metadata
                })
            
            return chunk_objects
            
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            raise
    
    def process_document(self, file_path: str, filename: str, file_type: str) -> Dict[str, Any]:
        """
        Complete document processing pipeline
        Returns processing results with text, chunks, and metadata
        """
        try:
            # Extract text
            text_content, page_count, word_count = self.extract_text(file_path, file_type)
            
            if not text_content.strip():
                raise ValueError("No text content found in document")
            
            # Create base metadata
            base_metadata = {
                'filename': filename,
                'file_type': file_type,
                'file_path': file_path,
                'total_pages': page_count,
                'total_words': word_count
            }
            
            # Chunk the text
            chunks = self.chunk_text(text_content, base_metadata)
            
            return {
                'text_content': text_content,
                'chunks': chunks,
                'page_count': page_count,
                'word_count': word_count,
                'chunk_count': len(chunks),
                'metadata': base_metadata
            }
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {str(e)}")
            raise

    def validate_file_type(self, filename: str) -> str:
        """Validate and return file type"""
        allowed_extensions = {'pdf', 'docx', 'txt'}
        file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_extension not in allowed_extensions:
            raise ValueError(f"File type '{file_extension}' not supported. Allowed types: {allowed_extensions}")
        
        return file_extension
    
    def validate_file_size(self, file_path: str, max_size_mb: int = 100) -> int:
        """Validate file size and return size in bytes"""
        file_size = os.path.getsize(file_path)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            raise ValueError(f"File size {file_size / (1024*1024):.1f}MB exceeds limit of {max_size_mb}MB")
        
        return file_size