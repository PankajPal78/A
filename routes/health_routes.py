from flask import Blueprint, jsonify
from services.vector_service import VectorService
from services.llm_service import LLMService
import logging

health_bp = Blueprint('health', __name__)
logger = logging.getLogger(__name__)

@health_bp.route('/', methods=['GET'])
def health_check():
    """
    Basic health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'service': 'RAG API',
        'version': '1.0.0'
    }), 200

@health_bp.route('/detailed', methods=['GET'])
def detailed_health_check():
    """
    Detailed health check including all services
    """
    try:
        health_status = {
            'status': 'healthy',
            'service': 'RAG API',
            'version': '1.0.0',
            'components': {}
        }
        
        # Check vector database
        try:
            vector_service = VectorService()
            vector_stats = vector_service.get_collection_stats()
            health_status['components']['vector_database'] = {
                'status': 'healthy',
                'total_chunks': vector_stats.get('total_chunks', 0)
            }
        except Exception as e:
            health_status['components']['vector_database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_status['status'] = 'degraded'
        
        # Check LLM service
        try:
            llm_service = LLMService()
            is_connected = llm_service.test_connection()
            health_status['components']['llm_service'] = {
                'status': 'healthy' if is_connected else 'unhealthy',
                'connected': is_connected
            }
            if not is_connected:
                health_status['status'] = 'degraded'
        except Exception as e:
            health_status['components']['llm_service'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_status['status'] = 'degraded'
        
        # Check database
        try:
            from app import db
            db.session.execute('SELECT 1')
            health_status['components']['database'] = {
                'status': 'healthy'
            }
        except Exception as e:
            health_status['components']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_status['status'] = 'degraded'
        
        # Determine overall status
        if health_status['status'] == 'healthy':
            return jsonify(health_status), 200
        else:
            return jsonify(health_status), 503
    
    except Exception as e:
        logger.error(f"Error in detailed health check: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'RAG API',
            'error': str(e)
        }), 500