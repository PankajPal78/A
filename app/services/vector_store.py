"""
Vector store service for managing document embeddings
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from config.settings import VECTOR_DB_PATH, EMBEDDING_MODEL, TOP_K_RESULTS
import logging

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Service for managing vector embeddings and similarity search"""
    
    def __init__(self):
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=VECTOR_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Vector store initialized with {self.collection.count()} documents")
    
    def add_documents(self, chunks: List[Dict], document_id: int):
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'
            document_id: Document ID for tracking
        """
        if not chunks:
            return
        
        texts = [chunk['text'] for chunk in chunks]
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"doc_{document_id}_chunk_{i}"
            ids.append(chunk_id)
            
            metadata = {
                'document_id': str(document_id),
                'chunk_index': str(i),
                'filename': chunk['metadata'].get('filename', ''),
                'page_count': str(chunk['metadata'].get('page_count', 0))
            }
            metadatas.append(metadata)
        
        # Add to collection
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(chunks)} chunks for document {document_id}")
    
    def search(self, query: str, top_k: int = TOP_K_RESULTS, document_id: int = None) -> List[Dict]:
        """
        Search for relevant document chunks
        
        Args:
            query: Search query
            top_k: Number of results to return
            document_id: Optional filter by document ID
        
        Returns:
            List of relevant chunks with metadata and scores
        """
        # Build where filter if document_id is provided
        where_filter = None
        if document_id is not None:
            where_filter = {"document_id": str(document_id)}
        
        # Query the collection
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'id': results['ids'][0][i]
                })
        
        logger.info(f"Found {len(formatted_results)} relevant chunks for query")
        return formatted_results
    
    def delete_document(self, document_id: int):
        """
        Delete all chunks for a specific document
        
        Args:
            document_id: Document ID to delete
        """
        # Get all IDs for this document
        results = self.collection.get(
            where={"document_id": str(document_id)}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector store"""
        return {
            'total_chunks': self.collection.count(),
            'collection_name': self.collection.name
        }