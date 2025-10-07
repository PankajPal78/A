from flask import Blueprint, request, jsonify
from services.rag_service import RAGService
from services.vector_service import VectorService
from services.llm_service import LLMService
import logging

query_bp = Blueprint('query', __name__)
logger = logging.getLogger(__name__)

# Initialize services
vector_service = VectorService()
llm_service = LLMService()
rag_service = RAGService(vector_service, llm_service)

@query_bp.route('/ask', methods=['POST'])
def ask_question():
    """
    Ask a question and get an answer using RAG
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Optional parameters
        document_ids = data.get('document_ids', None)  # Filter by specific documents
        max_chunks = data.get('max_chunks', 5)  # Number of chunks to retrieve
        max_tokens = data.get('max_tokens', 1000)  # Max response length
        
        # Validate parameters
        if max_chunks < 1 or max_chunks > 20:
            return jsonify({'error': 'max_chunks must be between 1 and 20'}), 400
        
        if max_tokens < 100 or max_tokens > 4000:
            return jsonify({'error': 'max_tokens must be between 100 and 4000'}), 400
        
        # Process query using RAG
        result = rag_service.process_query(
            query=query,
            document_ids=document_ids,
            max_chunks=max_chunks,
            max_tokens=max_tokens
        )
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': f'Query processing failed: {str(e)}'}), 500

@query_bp.route('/search', methods=['POST'])
def search_documents():
    """
    Search for relevant document chunks without generating a response
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Optional parameters
        document_ids = data.get('document_ids', None)
        max_chunks = data.get('max_chunks', 10)
        
        # Validate parameters
        if max_chunks < 1 or max_chunks > 50:
            return jsonify({'error': 'max_chunks must be between 1 and 50'}), 400
        
        # Search for similar chunks
        similar_chunks = vector_service.search_similar_chunks(
            query=query,
            n_results=max_chunks,
            document_ids=document_ids
        )
        
        return jsonify({
            'query': query,
            'results': similar_chunks,
            'total_results': len(similar_chunks)
        }), 200
    
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@query_bp.route('/available-documents', methods=['GET'])
def get_available_documents():
    """
    Get list of available documents for querying
    """
    try:
        documents = rag_service.get_available_documents()
        return jsonify({'documents': documents}), 200
    
    except Exception as e:
        logger.error(f"Error getting available documents: {str(e)}")
        return jsonify({'error': f'Failed to retrieve documents: {str(e)}'}), 500

@query_bp.route('/stats', methods=['GET'])
def get_system_stats():
    """
    Get RAG system statistics
    """
    try:
        stats = rag_service.get_document_stats()
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        return jsonify({'error': f'Failed to retrieve stats: {str(e)}'}), 500

@query_bp.route('/test-llm', methods=['POST'])
def test_llm_connection():
    """
    Test the LLM service connection
    """
    try:
        is_connected = llm_service.test_connection()
        
        if is_connected:
            return jsonify({
                'status': 'connected',
                'message': 'LLM service is working correctly'
            }), 200
        else:
            return jsonify({
                'status': 'disconnected',
                'message': 'LLM service is not responding'
            }), 503
    
    except Exception as e:
        logger.error(f"Error testing LLM connection: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'LLM test failed: {str(e)}'
        }), 500