from typing import List, Dict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from app.config import Config

class VectorStore:
    """Manages vector database operations using ChromaDB"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=Config.VECTOR_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=Config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[Dict], document_id: int):
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of chunk dictionaries
            document_id: ID of the parent document
        """
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Prepare metadata
        metadatas = []
        ids = []
        for i, chunk in enumerate(chunks):
            metadata = {
                'document_id': str(document_id),
                'chunk_index': chunk['chunk_index'],
                **chunk.get('metadata', {})
            }
            metadatas.append(metadata)
            ids.append(f"doc_{document_id}_chunk_{i}")
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Search for relevant chunks
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant chunks with metadata
        """
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def delete_document(self, document_id: int):
        """
        Delete all chunks for a document
        
        Args:
            document_id: ID of the document to delete
        """
        # Get all chunks for this document
        results = self.collection.get(
            where={"document_id": str(document_id)}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector store"""
        count = self.collection.count()
        return {
            'total_chunks': count,
            'collection_name': Config.COLLECTION_NAME
        }