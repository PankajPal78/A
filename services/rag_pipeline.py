"""
RAG (Retrieval-Augmented Generation) pipeline service
"""

import logging
import time
from typing import List, Dict, Any, Optional
from .vector_store import VectorStore
from .llm_service import LLMService
from models.document import QueryLog, db

logger = logging.getLogger(__name__)

class RAGPipeline:
    """Main RAG pipeline for document Q&A"""
    
    def __init__(self, vector_store: VectorStore, llm_service: LLMService,
                 top_k: int = 5, similarity_threshold: float = 0.7):
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        
        logger.info(f"Initialized RAG pipeline with top_k={top_k}, threshold={similarity_threshold}")
    
    def query(self, query_text: str, document_ids: Optional[List[int]] = None,
              top_k: Optional[int] = None, similarity_threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Process a query through the complete RAG pipeline
        
        Args:
            query_text: User's question
            document_ids: Optional list of specific document IDs to search
            top_k: Number of chunks to retrieve (overrides default)
            similarity_threshold: Minimum similarity score (overrides default)
        
        Returns:
            Complete response with answer, sources, and metadata
        """
        try:
            start_time = time.time()
            
            # Use provided parameters or defaults
            k = top_k or self.top_k
            threshold = similarity_threshold or self.similarity_threshold
            
            logger.info(f"Processing query: '{query_text[:100]}...' with k={k}, threshold={threshold}")
            
            # Step 1: Retrieve relevant chunks
            retrieval_start = time.time()
            retrieved_chunks = self.vector_store.similarity_search(
                query=query_text,
                top_k=k,
                document_ids=document_ids,
                similarity_threshold=threshold
            )
            retrieval_time = time.time() - retrieval_start
            
            if not retrieved_chunks:
                return {
                    'query': query_text,
                    'answer': "I couldn't find any relevant information in the uploaded documents to answer your question.",
                    'sources': [],
                    'retrieved_chunks': 0,
                    'similarity_scores': [],
                    'source_documents': [],
                    'retrieval_time': retrieval_time,
                    'generation_time': 0.0,
                    'total_time': time.time() - start_time,
                    'provider': self.llm_service.provider_name
                }
            
            # Step 2: Generate response using LLM
            generation_start = time.time()
            llm_response = self.llm_service.generate_response(
                query=query_text,
                context_chunks=retrieved_chunks
            )
            generation_time = time.time() - generation_start
            
            # Step 3: Prepare response metadata
            similarity_scores = [chunk.get('similarity_score', 0.0) for chunk in retrieved_chunks]
            source_documents = list(set([
                chunk.get('metadata', {}).get('document_id') 
                for chunk in retrieved_chunks 
                if chunk.get('metadata', {}).get('document_id')
            ]))
            
            total_time = time.time() - start_time
            
            # Step 4: Prepare final response
            response = {
                'query': query_text,
                'answer': llm_response['response'],
                'sources': llm_response['sources'],
                'retrieved_chunks': len(retrieved_chunks),
                'similarity_scores': similarity_scores,
                'source_documents': source_documents,
                'retrieval_time': retrieval_time,
                'generation_time': generation_time,
                'total_time': total_time,
                'provider': llm_response['provider'],
                'chunks_details': [
                    {
                        'text_preview': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text'],
                        'similarity_score': chunk.get('similarity_score', 0.0),
                        'source': chunk.get('metadata', {}).get('filename', 'Unknown'),
                        'chunk_index': chunk.get('metadata', {}).get('chunk_index', 0)
                    }
                    for chunk in retrieved_chunks
                ]
            }
            
            # Step 5: Log the query
            self._log_query(response)
            
            logger.info(f"Query processed successfully in {total_time:.2f}s "
                       f"(retrieval: {retrieval_time:.2f}s, generation: {generation_time:.2f}s)")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise
    
    def _log_query(self, response: Dict[str, Any]):
        """Log query and response to database"""
        try:
            query_log = QueryLog(
                query_text=response['query'],
                response_text=response['answer'],
                retrieved_chunks=response['retrieved_chunks'],
                similarity_scores=str(response['similarity_scores']),
                source_documents=str(response['source_documents']),
                retrieval_time=response['retrieval_time'],
                generation_time=response['generation_time'],
                total_time=response['total_time']
            )
            
            db.session.add(query_log)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error logging query: {str(e)}")
            # Don't raise exception for logging errors
    
    def get_query_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent query history"""
        try:
            query_logs = QueryLog.query.order_by(QueryLog.created_at.desc()).limit(limit).all()
            return [log.to_dict() for log in query_logs]
        except Exception as e:
            logger.error(f"Error getting query history: {str(e)}")
            return []
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline performance statistics"""
        try:
            # Get vector store stats
            vector_stats = self.vector_store.get_collection_stats()
            
            # Get query stats from database
            total_queries = QueryLog.query.count()
            
            # Calculate average response times
            avg_retrieval_time = db.session.query(db.func.avg(QueryLog.retrieval_time)).scalar() or 0
            avg_generation_time = db.session.query(db.func.avg(QueryLog.generation_time)).scalar() or 0
            avg_total_time = db.session.query(db.func.avg(QueryLog.total_time)).scalar() or 0
            
            # Get LLM provider info
            provider_info = self.llm_service.get_provider_info()
            
            return {
                'vector_store': vector_stats,
                'query_stats': {
                    'total_queries': total_queries,
                    'avg_retrieval_time': round(avg_retrieval_time, 3),
                    'avg_generation_time': round(avg_generation_time, 3),
                    'avg_total_time': round(avg_total_time, 3)
                },
                'llm_provider': provider_info,
                'pipeline_config': {
                    'top_k': self.top_k,
                    'similarity_threshold': self.similarity_threshold
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting pipeline stats: {str(e)}")
            return {}
    
    def update_config(self, top_k: Optional[int] = None, 
                     similarity_threshold: Optional[float] = None):
        """Update pipeline configuration"""
        if top_k is not None:
            self.top_k = max(1, min(top_k, 20))  # Limit between 1 and 20
            logger.info(f"Updated top_k to {self.top_k}")
        
        if similarity_threshold is not None:
            self.similarity_threshold = max(0.0, min(similarity_threshold, 1.0))  # Limit between 0 and 1
            logger.info(f"Updated similarity_threshold to {self.similarity_threshold}")
    
    def validate_query(self, query_text: str) -> bool:
        """Validate query text"""
        if not query_text or not query_text.strip():
            return False
        
        if len(query_text.strip()) < 3:
            return False
        
        if len(query_text) > 1000:  # Reasonable query length limit
            return False
        
        return True