import logging
from typing import List, Dict, Any
from services.vector_service import VectorService
from services.llm_service import LLMService
from app import Document

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, vector_service: VectorService, llm_service: LLMService):
        self.vector_service = vector_service
        self.llm_service = llm_service
    
    def process_query(self, query: str, document_ids: List[int] = None, 
                     max_chunks: int = 5, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Process a query using the RAG pipeline
        """
        try:
            logger.info(f"Processing query: {query[:100]}...")
            
            # Step 1: Retrieve relevant chunks using vector search
            similar_chunks = self.vector_service.search_similar_chunks(
                query=query,
                n_results=max_chunks,
                document_ids=document_ids
            )
            
            if not similar_chunks:
                return {
                    "response": "I couldn't find any relevant information in the uploaded documents to answer your question.",
                    "metadata": {
                        "context_chunks_used": 0,
                        "search_performed": True,
                        "no_results": True
                    },
                    "context_chunks": []
                }
            
            # Step 2: Generate response using LLM with retrieved context
            llm_response = self.llm_service.generate_response(
                query=query,
                context_chunks=similar_chunks,
                max_tokens=max_tokens
            )
            
            # Step 3: Combine results
            result = {
                "response": llm_response["response"],
                "metadata": {
                    **llm_response["metadata"],
                    "search_performed": True,
                    "no_results": False,
                    "query": query
                },
                "context_chunks": similar_chunks
            }
            
            logger.info(f"Successfully processed query with {len(similar_chunks)} context chunks")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "response": f"I encountered an error while processing your query: {str(e)}",
                "metadata": {
                    "error": str(e),
                    "search_performed": False
                },
                "context_chunks": []
            }
    
    def get_available_documents(self) -> List[Dict[str, Any]]:
        """
        Get list of available documents for querying
        """
        try:
            documents = Document.query.filter_by(processing_status='completed').all()
            return [doc.to_dict() for doc in documents]
        except Exception as e:
            logger.error(f"Error getting available documents: {str(e)}")
            return []
    
    def get_document_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system
        """
        try:
            # Get document stats
            total_docs = Document.query.count()
            processed_docs = Document.query.filter_by(processing_status='completed').count()
            failed_docs = Document.query.filter_by(processing_status='failed').count()
            
            # Get vector database stats
            vector_stats = self.vector_service.get_collection_stats()
            
            return {
                "documents": {
                    "total": total_docs,
                    "processed": processed_docs,
                    "failed": failed_docs
                },
                "vector_database": vector_stats
            }
        except Exception as e:
            logger.error(f"Error getting document stats: {str(e)}")
            return {
                "documents": {"total": 0, "processed": 0, "failed": 0},
                "vector_database": {"total_chunks": 0}
            }