import logging
from typing import Dict, Any, List
from .vector_store import VectorStore
from .llm_service import LLMService

logger = logging.getLogger(__name__)

class RAGPipeline:
    """Main RAG pipeline that combines retrieval and generation"""
    
    def __init__(self, vector_store: VectorStore, llm_service: LLMService):
        self.vector_store = vector_store
        self.llm_service = llm_service
        logger.info("RAG pipeline initialized")
    
    def query(self, query: str, top_k: int = 5, document_ids: List[str] = None) -> Dict[str, Any]:
        """Process a query through the RAG pipeline"""
        try:
            logger.info(f"Processing query: {query[:100]}...")
            
            # Step 1: Retrieve relevant chunks
            retrieved_chunks = self.vector_store.search(
                query=query,
                top_k=top_k,
                document_ids=document_ids
            )
            
            if not retrieved_chunks:
                return {
                    'answer': "I couldn't find any relevant information in the uploaded documents to answer your question.",
                    'sources': [],
                    'metadata': {
                        'retrieved_chunks': 0,
                        'query': query
                    }
                }
            
            # Step 2: Generate response using LLM
            response = self.llm_service.generate_response(query, retrieved_chunks)
            
            # Add retrieval metadata
            response['metadata'].update({
                'retrieved_chunks': len(retrieved_chunks),
                'query': query,
                'top_k': top_k
            })
            
            logger.info(f"Query processed successfully: {len(retrieved_chunks)} chunks retrieved")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                'answer': f"I encountered an error while processing your query: {str(e)}",
                'sources': [],
                'metadata': {
                    'error': str(e),
                    'query': query
                }
            }
    
    def get_relevant_chunks(self, query: str, top_k: int = 5, document_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Get relevant chunks without generating a response"""
        try:
            return self.vector_store.search(
                query=query,
                top_k=top_k,
                document_ids=document_ids
            )
        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            return []
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        try:
            vector_stats = self.vector_store.get_stats()
            llm_connected = self.llm_service.test_connection()
            
            return {
                'vector_store': vector_stats,
                'llm_connected': llm_connected,
                'pipeline_status': 'healthy' if llm_connected else 'llm_disconnected'
            }
        except Exception as e:
            logger.error(f"Error getting pipeline stats: {str(e)}")
            return {
                'error': str(e),
                'pipeline_status': 'error'
            }