"""
Vector store service using ChromaDB for document embeddings
"""

import os
import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class VectorStore:
    """Service for managing document embeddings in ChromaDB"""
    
    def __init__(self, persist_directory: str = "./chroma_db", 
                 collection_name: str = "documents",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        
        # Ensure persist directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info(f"Loaded embedding model: {embedding_model}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
        
        # Get or create collection
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Document chunks for RAG system"}
            )
            logger.info(f"Connected to collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def add_documents(self, chunks: List[Dict[str, Any]], document_id: int) -> List[str]:
        """
        Add document chunks to the vector store
        Returns list of chunk IDs
        """
        try:
            if not chunks:
                return []
            
            # Prepare data for ChromaDB
            chunk_ids = []
            texts = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                # Generate unique ID for each chunk
                chunk_id = f"doc_{document_id}_chunk_{i}_{str(uuid.uuid4())[:8]}"
                chunk_ids.append(chunk_id)
                texts.append(chunk['text'])
                
                # Prepare metadata
                metadata = chunk.get('metadata', {}).copy()
                metadata.update({
                    'document_id': document_id,
                    'chunk_id': chunk_id,
                    'chunk_index': i
                })
                metadatas.append(metadata)
            
            # Generate embeddings
            embeddings = self.generate_embeddings(texts)
            
            # Add to collection
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(chunk_ids)} chunks to vector store for document {document_id}")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    def similarity_search(self, query: str, top_k: int = 5, 
                         document_ids: Optional[List[int]] = None,
                         similarity_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity
        Returns list of matching chunks with metadata and scores
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embeddings([query])[0]
            
            # Prepare where clause for filtering by document IDs
            where_clause = None
            if document_ids:
                where_clause = {"document_id": {"$in": document_ids}}
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            matches = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    # Convert distance to similarity score (ChromaDB uses cosine distance)
                    distance = results['distances'][0][i]
                    similarity_score = 1 - distance  # Convert distance to similarity
                    
                    # Apply similarity threshold
                    if similarity_score >= similarity_threshold:
                        match = {
                            'id': results['ids'][0][i],
                            'text': results['documents'][0][i],
                            'metadata': results['metadatas'][0][i],
                            'similarity_score': similarity_score,
                            'distance': distance
                        }
                        matches.append(match)
            
            logger.info(f"Found {len(matches)} matching chunks for query")
            return matches
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}")
            raise
    
    def get_document_chunks(self, document_id: int) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        try:
            results = self.collection.get(
                where={"document_id": document_id},
                include=["documents", "metadatas"]
            )
            
            chunks = []
            if results['ids']:
                for i in range(len(results['ids'])):
                    chunk = {
                        'id': results['ids'][i],
                        'text': results['documents'][i],
                        'metadata': results['metadatas'][i]
                    }
                    chunks.append(chunk)
            
            return sorted(chunks, key=lambda x: x['metadata'].get('chunk_index', 0))
            
        except Exception as e:
            logger.error(f"Error getting document chunks: {str(e)}")
            raise
    
    def delete_document(self, document_id: int) -> int:
        """Delete all chunks for a specific document"""
        try:
            # Get all chunk IDs for the document
            results = self.collection.get(
                where={"document_id": document_id},
                include=["metadatas"]
            )
            
            if results['ids']:
                # Delete chunks
                self.collection.delete(ids=results['ids'])
                deleted_count = len(results['ids'])
                logger.info(f"Deleted {deleted_count} chunks for document {document_id}")
                return deleted_count
            
            return 0
            
        except Exception as e:
            logger.error(f"Error deleting document chunks: {str(e)}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection"""
        try:
            # Get collection info
            collection_info = self.collection.get(include=["metadatas"])
            
            total_chunks = len(collection_info['ids']) if collection_info['ids'] else 0
            
            # Count unique documents
            document_ids = set()
            if collection_info['metadatas']:
                for metadata in collection_info['metadatas']:
                    if 'document_id' in metadata:
                        document_ids.add(metadata['document_id'])
            
            stats = {
                'total_chunks': total_chunks,
                'total_documents': len(document_ids),
                'collection_name': self.collection_name,
                'embedding_model': self.embedding_model_name
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            raise
    
    def reset_collection(self):
        """Reset the entire collection (use with caution)"""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document chunks for RAG system"}
            )
            logger.info(f"Reset collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error resetting collection: {str(e)}")
            raise