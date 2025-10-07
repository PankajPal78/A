import os
import PyPDF2
import docx
from typing import List, Dict, Any
import hashlib
import json
from datetime import datetime
import tiktoken

class DocumentProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"Error extracting text from TXT: {str(e)}")
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from various file types"""
        if file_type.lower() == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type.lower() in ['docx', 'doc']:
            return self.extract_text_from_docx(file_path)
        elif file_type.lower() == 'txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise Exception(f"Unsupported file type: {file_type}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.encoding.encode(text))
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Split text into chunks with overlap"""
        if not text.strip():
            return []
        
        # Split by sentences first
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        current_tokens = 0
        chunk_id = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_tokens = self.count_tokens(sentence)
            
            # If adding this sentence would exceed chunk size, save current chunk
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunks.append({
                    'id': chunk_id,
                    'text': current_chunk.strip(),
                    'tokens': current_tokens,
                    'start_char': 0,  # Simplified for now
                    'end_char': len(current_chunk)
                })
                chunk_id += 1
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_text + " " + sentence if overlap_text else sentence
                current_tokens = self.count_tokens(current_chunk)
            else:
                current_chunk += sentence + ". " if current_chunk else sentence + ". "
                current_tokens += sentence_tokens
        
        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append({
                'id': chunk_id,
                'text': current_chunk.strip(),
                'tokens': current_tokens,
                'start_char': 0,
                'end_char': len(current_chunk)
            })
        
        return chunks
    
    def process_document(self, file_path: str, file_type: str, document_id: int) -> Dict[str, Any]:
        """Process a document and return chunks and metadata"""
        try:
            # Extract text
            text = self.extract_text(file_path, file_type)
            
            if not text.strip():
                raise Exception("No text content found in document")
            
            # Check if document is too large (approximate 1000 pages limit)
            total_tokens = self.count_tokens(text)
            estimated_pages = total_tokens / 500  # Rough estimate: 500 tokens per page
            
            if estimated_pages > 1000:
                raise Exception(f"Document too large: estimated {estimated_pages:.0f} pages (max 1000)")
            
            # Chunk the text
            chunks = self.chunk_text(text)
            
            if not chunks:
                raise Exception("No chunks generated from document")
            
            # Prepare metadata
            metadata = {
                'total_tokens': total_tokens,
                'estimated_pages': estimated_pages,
                'chunk_count': len(chunks),
                'processing_date': datetime.utcnow().isoformat(),
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap
            }
            
            return {
                'chunks': chunks,
                'metadata': metadata,
                'success': True
            }
            
        except Exception as e:
            return {
                'chunks': [],
                'metadata': {'error': str(e)},
                'success': False
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return ['pdf', 'docx', 'doc', 'txt']