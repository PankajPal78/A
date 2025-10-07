import os
import logging
from typing import List, Dict
import PyPDF2
from docx import Document as DocxDocument
import pandas as pd
import re

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document processing and chunking"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_document(self, file_path: str) -> List[Dict[str, str]]:
        """Process a document and return chunks"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                text = self._extract_pdf_text(file_path)
            elif file_ext == '.docx':
                text = self._extract_docx_text(file_path)
            elif file_ext == '.txt':
                text = self._extract_txt_text(file_path)
            elif file_ext == '.xlsx':
                text = self._extract_excel_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Clean and preprocess text
            text = self._clean_text(text)
            
            # Split into chunks
            chunks = self._split_into_chunks(text)
            
            logger.info(f"Processed document {file_path}: {len(chunks)} chunks created")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise
    
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
            doc = DocxDocument(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            raise
        return text
    
    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except Exception as e:
            logger.error(f"Error extracting TXT text: {str(e)}")
            raise
        return text
    
    def _extract_excel_text(self, file_path: str) -> str:
        """Extract text from Excel file"""
        try:
            df = pd.read_excel(file_path)
            text = ""
            for column in df.columns:
                text += f"{column}: " + " ".join(df[column].astype(str).tolist()) + "\n"
        except Exception as e:
            logger.error(f"Error extracting Excel text: {str(e)}")
            raise
        return text
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    def _split_into_chunks(self, text: str) -> List[Dict[str, str]]:
        """Split text into overlapping chunks"""
        if not text.strip():
            return []
        
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            # If adding this sentence would exceed chunk size, save current chunk
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append({
                    'id': f"chunk_{chunk_id}",
                    'text': current_chunk.strip(),
                    'metadata': {
                        'chunk_size': len(current_chunk),
                        'chunk_index': chunk_id
                    }
                })
                chunk_id += 1
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append({
                'id': f"chunk_{chunk_id}",
                'text': current_chunk.strip(),
                'metadata': {
                    'chunk_size': len(current_chunk),
                    'chunk_index': chunk_id
                }
            })
        
        return chunks