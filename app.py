from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///data/rag_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 104857600))  # 100MB
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', './uploads')

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models and routes
from models import Document, DocumentChunk
from routes import document_bp, query_bp

# Register blueprints
app.register_blueprint(document_bp, url_prefix='/api/documents')
app.register_blueprint(query_bp, url_prefix='/api/query')

@app.route('/')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'RAG System API is running',
        'version': '1.0.0'
    })

@app.route('/api/health')
def detailed_health():
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'vector_db': 'connected',
        'llm_api': 'configured'
    })

if __name__ == '__main__':
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('./data', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=False)