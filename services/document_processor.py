import os
import PyPDF2
import docx
from typing import List, Dict, Tuple
import logging
from app import Document, DocumentChunk
from app import db
import tiktoken

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def process_document(self, document: Document) -> bool:
        """
        Process a document and create chunks
        """
        try:
            logger.info(f"Processing document: {document.filename}")
            document.processing_status = 'processing'
            db.session.commit()
            
            # Extract text based on file type
            if document.file_type.lower() == 'pdf':
                text_content = self._extract_pdf_text(document.file_path)
            elif document.file_type.lower() in ['docx', 'doc']:
                text_content = self._extract_docx_text(document.file_path)
            else:
                raise ValueError(f"Unsupported file type: {document.file_type}")
            
            if not text_content.strip():
                raise ValueError("No text content extracted from document")
            
            # Count pages (approximate for PDFs)
            if document.file_type.lower() == 'pdf':
                document.total_pages = self._count_pdf_pages(document.file_path)
            else:
                document.total_pages = 1
            
            # Create chunks
            chunks = self._create_chunks(text_content, document.id)
            
            # Save chunks to database
            for chunk_data in chunks:
                chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=chunk_data['index'],
                    content=chunk_data['content'],
                    page_number=chunk_data.get('page_number'),
                    chunk_size=len(chunk_data['content'])
                )
                db.session.add(chunk)
            
            document.total_chunks = len(chunks)
            document.processing_status = 'completed'
            db.session.commit()
            
            logger.info(f"Successfully processed document {document.filename} with {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error processing document {document.filename}: {str(e)}")
            document.processing_status = 'failed'
            document.processing_error = str(e)
            db.session.commit()
            return False
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise
        return text
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            raise
    
    def _count_pdf_pages(self, file_path: str) -> int:
        """Count pages in PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except Exception as e:
            logger.error(f"Error counting PDF pages: {str(e)}")
            return 1
    
    def _create_chunks(self, text: str, document_id: int) -> List[Dict]:
        """Create text chunks with overlap"""
        # Tokenize text
        tokens = self.encoding.encode(text)
        
        chunks = []
        chunk_index = 0
        start = 0
        
        while start < len(tokens):
            # Calculate end position
            end = min(start + self.chunk_size, len(tokens))
            
            # Extract chunk tokens
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Skip empty chunks
            if chunk_text.strip():
                chunks.append({
                    'index': chunk_index,
                    'content': chunk_text.strip(),
                    'page_number': None  # Will be calculated if needed
                })
                chunk_index += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap if end < len(tokens) else end
        
        return chunks
    
    def get_document_chunks(self, document_id: int) -> List[DocumentChunk]:
        """Get all chunks for a document"""
        return DocumentChunk.query.filter_by(document_id=document_id).order_by(DocumentChunk.chunk_index).all()
    
    def get_chunk_by_id(self, chunk_id: int) -> DocumentChunk:
        """Get a specific chunk by ID"""
        return DocumentChunk.query.get(chunk_id)