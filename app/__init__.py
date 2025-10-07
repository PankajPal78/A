"""
Flask application factory
"""
from flask import Flask
from flask_cors import CORS
from app.api.routes import api_bp
from app.utils.database import init_db
import logging

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    with app.app_context():
        init_db()
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Root endpoint
    @app.route('/')
    def index():
        return {
            'service': 'RAG Document Q&A System',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/api/health',
                'upload_document': 'POST /api/documents',
                'list_documents': 'GET /api/documents',
                'get_document': 'GET /api/documents/<id>',
                'delete_document': 'DELETE /api/documents/<id>',
                'query': 'POST /api/query',
                'stats': 'GET /api/stats'
            }
        }
    
    return app