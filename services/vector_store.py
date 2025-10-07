import os
import logging
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import uuid

logger = logging.getLogger(__name__)

class VectorStore:
    """Handles vector storage and retrieval using ChromaDB"""
    
    def __init__(self, persist_directory: str = "data/chroma_db"):
        self.persist_directory = persist_directory
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Vector store initialized with {self.collection.count()} documents")
    
    def add_documents(self, document_id: str, chunks: List[Dict[str, Any]]):
        """Add document chunks to the vector store"""
        try:
            if not chunks:
                logger.warning(f"No chunks to add for document {document_id}")
                return
            
            # Prepare data for ChromaDB
            texts = [chunk['text'] for chunk in chunks]
            chunk_ids = [f"{document_id}_{chunk['id']}" for chunk in chunks]
            metadatas = []
            
            for chunk in chunks:
                metadata = chunk.get('metadata', {})
                metadata.update({
                    'document_id': document_id,
                    'chunk_id': chunk['id']
                })
                metadatas.append(metadata)
            
            # Add to collection
            self.collection.add(
                documents=texts,
                ids=chunk_ids,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(chunks)} chunks for document {document_id}")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    def search(self, query: str, top_k: int = 5, document_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        try:
            # Prepare where clause for filtering by document IDs
            where_clause = {}
            if document_ids:
                where_clause = {"document_id": {"$in": document_ids}}
            
            # Search in ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if results['distances'] else None
                    })
            
            logger.info(f"Found {len(formatted_results)} similar chunks for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise
    
    def delete_document(self, document_id: str):
        """Delete all chunks for a specific document"""
        try:
            # Get all chunk IDs for this document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
            else:
                logger.warning(f"No chunks found for document {document_id}")
                
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'collection_name': self.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting vector store stats: {str(e)}")
            return {'error': str(e)}
    
    def clear_all(self):
        """Clear all documents from the vector store"""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection("document_chunks")
            self.collection = self.client.create_collection(
                name="document_chunks",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Cleared all documents from vector store")
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            raise