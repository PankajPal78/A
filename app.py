from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
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
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///data/rag_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 104857600))  # 100MB
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', './data/uploads')

# Initialize database
db = SQLAlchemy(app)

# Define models after db initialization
class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processing_status = db.Column(db.String(50), default='pending')
    total_pages = db.Column(db.Integer, default=0)
    total_chunks = db.Column(db.Integer, default=0)
    processing_error = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'processing_status': self.processing_status,
            'total_pages': self.total_pages,
            'total_chunks': self.total_chunks,
            'processing_error': self.processing_error
        }

class DocumentChunk(db.Model):
    __tablename__ = 'document_chunks'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    page_number = db.Column(db.Integer, nullable=True)
    chunk_size = db.Column(db.Integer, nullable=False)
    embedding_id = db.Column(db.String(255), nullable=True)
    
    # Relationship
    document = db.relationship('Document', backref=db.backref('chunks', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'chunk_index': self.chunk_index,
            'content': self.content[:200] + '...' if len(self.content) > 200 else self.content,
            'page_number': self.page_number,
            'chunk_size': self.chunk_size,
            'embedding_id': self.embedding_id
        }

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import and register blueprints
from routes.document_routes import document_bp
from routes.query_routes import query_bp
from routes.health_routes import health_bp

app.register_blueprint(document_bp, url_prefix='/api/documents')
app.register_blueprint(query_bp, url_prefix='/api/query')
app.register_blueprint(health_bp, url_prefix='/api/health')

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('./data/chroma_db', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=False)