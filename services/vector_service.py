import chromadb
from chromadb.config import Settings
import os
import logging
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from app import DocumentChunk
from app import db

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_document_chunks(self, document_id: int, chunks: List[DocumentChunk]) -> bool:
        """
        Add document chunks to vector database
        """
        try:
            logger.info(f"Adding {len(chunks)} chunks for document {document_id} to vector database")
            
            # Prepare data for ChromaDB
            chunk_ids = []
            chunk_texts = []
            chunk_metadatas = []
            
            for chunk in chunks:
                chunk_id = f"doc_{document_id}_chunk_{chunk.id}"
                chunk_ids.append(chunk_id)
                chunk_texts.append(chunk.content)
                chunk_metadatas.append({
                    "document_id": document_id,
                    "chunk_id": chunk.id,
                    "chunk_index": chunk.chunk_index,
                    "page_number": chunk.page_number or 0,
                    "chunk_size": chunk.chunk_size
                })
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(chunk_texts).tolist()
            
            # Add to ChromaDB
            self.collection.add(
                ids=chunk_ids,
                documents=chunk_texts,
                embeddings=embeddings,
                metadatas=chunk_metadatas
            )
            
            # Update chunk records with embedding IDs
            for i, chunk in enumerate(chunks):
                chunk.embedding_id = chunk_ids[i]
            
            db.session.commit()
            
            logger.info(f"Successfully added chunks for document {document_id} to vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding chunks to vector database: {str(e)}")
            db.session.rollback()
            return False
    
    def search_similar_chunks(self, query: str, n_results: int = 5, document_ids: List[int] = None) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Prepare where clause for filtering by document IDs
            where_clause = {}
            if document_ids:
                where_clause["document_id"] = {"$in": document_ids}
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            # Format results
            similar_chunks = []
            if results['ids'] and results['ids'][0]:
                for i, chunk_id in enumerate(results['ids'][0]):
                    chunk_data = {
                        'chunk_id': chunk_id,
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i]
                    }
                    similar_chunks.append(chunk_data)
            
            logger.info(f"Found {len(similar_chunks)} similar chunks for query")
            return similar_chunks
            
        except Exception as e:
            logger.error(f"Error searching vector database: {str(e)}")
            return []
    
    def get_chunk_by_embedding_id(self, embedding_id: str) -> Dict[str, Any]:
        """
        Get a specific chunk by its embedding ID
        """
        try:
            results = self.collection.get(ids=[embedding_id])
            if results['ids']:
                return {
                    'chunk_id': results['ids'][0],
                    'content': results['documents'][0],
                    'metadata': results['metadatas'][0]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting chunk by embedding ID: {str(e)}")
            return None
    
    def delete_document_chunks(self, document_id: int) -> bool:
        """
        Delete all chunks for a document from vector database
        """
        try:
            # Get all chunk IDs for the document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting chunks from vector database: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database collection
        """
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {"total_chunks": 0, "collection_name": "unknown"}