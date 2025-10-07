from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from app.models import Document, SessionLocal
from app.document_processor import DocumentProcessor
from app.vector_store import VectorStore
from app.rag_pipeline import RAGPipeline
from app.config import Config

api_bp = Blueprint('api', __name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'RAG API is running'
    }), 200

@api_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Supported types: {Config.ALLOWED_EXTENSIONS}'}), 400
        
        # Check document limit
        db = SessionLocal()
        document_count = db.query(Document).filter(Document.status == 'completed').count()
        if document_count >= Config.MAX_DOCUMENTS:
            db.close()
            return jsonify({'error': f'Maximum document limit ({Config.MAX_DOCUMENTS}) reached'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = str(int(os.path.getmtime(__file__) * 1000)) if os.path.exists(__file__) else '0'
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create document record
        document = Document(
            filename=unique_filename,
            original_filename=filename,
            file_path=file_path,
            file_size=file_size,
            status='processing'
        )
        db.add(document)
        db.commit()
        document_id = document.id
        
        try:
            # Process document
            processor = DocumentProcessor()
            text, page_count = processor.process_document(file_path, filename)
            
            # Update page count
            document.page_count = page_count
            db.commit()
            
            # Chunk text
            chunks = processor.chunk_text(
                text, 
                metadata={
                    'filename': filename,
                    'document_id': str(document_id)
                }
            )
            
            # Add to vector store
            vector_store = VectorStore()
            vector_store.add_documents(chunks, document_id)
            
            # Update document status
            document.chunk_count = len(chunks)
            document.status = 'completed'
            db.commit()
            
            result = document.to_dict()
            db.close()
            
            return jsonify({
                'message': 'Document uploaded and processed successfully',
                'document': result
            }), 201
            
        except Exception as e:
            # Update document status on error
            document.status = 'failed'
            document.error_message = str(e)
            db.commit()
            db.close()
            
            return jsonify({'error': f'Error processing document: {str(e)}'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/query', methods=['POST'])
def query_documents():
    """Query the RAG system"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'No question provided'}), 400
        
        question = data['question']
        top_k = data.get('top_k', Config.TOP_K_RESULTS)
        
        # Process query through RAG pipeline
        rag = RAGPipeline()
        result = rag.query(question, top_k=top_k)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/documents', methods=['GET'])
def list_documents():
    """List all documents with metadata"""
    try:
        db = SessionLocal()
        documents = db.query(Document).all()
        db.close()
        
        return jsonify({
            'documents': [doc.to_dict() for doc in documents],
            'total': len(documents)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/documents/<int:document_id>', methods=['GET'])
def get_document(document_id):
    """Get specific document metadata"""
    try:
        db = SessionLocal()
        document = db.query(Document).filter(Document.id == document_id).first()
        db.close()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify(document.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/documents/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document"""
    try:
        db = SessionLocal()
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            db.close()
            return jsonify({'error': 'Document not found'}), 404
        
        # Delete from vector store
        vector_store = VectorStore()
        vector_store.delete_document(document_id)
        
        # Delete file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database
        db.delete(document)
        db.commit()
        db.close()
        
        return jsonify({'message': 'Document deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        db = SessionLocal()
        total_documents = db.query(Document).count()
        completed_documents = db.query(Document).filter(Document.status == 'completed').count()
        failed_documents = db.query(Document).filter(Document.status == 'failed').count()
        processing_documents = db.query(Document).filter(Document.status == 'processing').count()
        db.close()
        
        # Get vector store stats
        vector_store = VectorStore()
        vector_stats = vector_store.get_collection_stats()
        
        return jsonify({
            'documents': {
                'total': total_documents,
                'completed': completed_documents,
                'processing': processing_documents,
                'failed': failed_documents
            },
            'vector_store': vector_stats,
            'limits': {
                'max_documents': Config.MAX_DOCUMENTS,
                'max_pages_per_document': Config.MAX_PAGES_PER_DOCUMENT
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500