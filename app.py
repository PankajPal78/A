from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import logging
from dotenv import load_dotenv

from services.document_processor import DocumentProcessor
from services.vector_store import VectorStore
from services.llm_service import LLMService
from services.rag_pipeline import RAGPipeline

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///data/rag_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize database
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
class Document(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='processing')  # processing, completed, failed
    chunk_count = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'upload_date': self.upload_date.isoformat(),
            'status': self.status,
            'chunk_count': self.chunk_count,
            'error_message': self.error_message
        }

# Initialize services
document_processor = DocumentProcessor()
vector_store = VectorStore()
llm_service = LLMService()
rag_pipeline = RAGPipeline(vector_store, llm_service)

# Create tables
with app.app_context():
    db.create_all()

# Frontend route
@app.route('/')
def index():
    """Serve the main frontend interface"""
    return render_template('index.html')

# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/api/documents', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file:
            return jsonify({'error': 'Invalid file'}), 400
        
        # Check file type
        allowed_extensions = {'.pdf', '.docx', '.txt', '.xlsx'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'File type {file_ext} not supported'}), 400
        
        # Secure filename and save
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Create database record
        document = Document(
            filename=unique_filename,
            original_filename=filename,
            file_type=file_ext,
            file_size=os.path.getsize(filepath)
        )
        db.session.add(document)
        db.session.commit()
        
        # Process document asynchronously
        try:
            chunks = document_processor.process_document(filepath)
            vector_store.add_documents(document.id, chunks)
            
            # Update document status
            document.status = 'completed'
            document.chunk_count = len(chunks)
            db.session.commit()
            
            logger.info(f"Document {document.id} processed successfully with {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error processing document {document.id}: {str(e)}")
            document.status = 'failed'
            document.error_message = str(e)
            db.session.commit()
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document_id': document.id,
            'status': document.status
        }), 201
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all uploaded documents"""
    try:
        documents = Document.query.all()
        return jsonify([doc.to_dict() for doc in documents])
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get specific document metadata"""
    try:
        document = Document.query.get_or_404(document_id)
        return jsonify(document.to_dict())
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document and its chunks"""
    try:
        document = Document.query.get_or_404(document_id)
        
        # Remove from vector store
        vector_store.delete_document(document_id)
        
        # Delete file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], document.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Delete from database
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'message': 'Document deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def query_documents():
    """Query the RAG system"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        top_k = data.get('top_k', 5)
        
        # Get response from RAG pipeline
        response = rag_pipeline.query(query, top_k=top_k)
        
        return jsonify({
            'query': query,
            'response': response['answer'],
            'sources': response['sources'],
            'metadata': response['metadata']
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        total_documents = Document.query.count()
        completed_documents = Document.query.filter_by(status='completed').count()
        failed_documents = Document.query.filter_by(status='failed').count()
        total_chunks = db.session.query(db.func.sum(Document.chunk_count)).scalar() or 0
        
        return jsonify({
            'total_documents': total_documents,
            'completed_documents': completed_documents,
            'failed_documents': failed_documents,
            'total_chunks': total_chunks
        })
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)