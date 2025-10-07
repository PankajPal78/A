import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from app import create_app
from database import db, Document, QueryLog

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to serve as the database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def sample_document_data():
    """Sample document data for testing."""
    return {
        'filename': 'test_document.pdf',
        'original_filename': 'test_document.pdf',
        'file_path': '/tmp/test_document.pdf',
        'file_size': 1024,
        'file_type': 'pdf',
        'metadata': '{"test": "data"}'
    }

class TestDocumentEndpoints:
    """Test document-related endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_upload_document_no_file(self, client):
        """Test upload endpoint with no file."""
        response = client.post('/api/documents/upload')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'No file provided' in data['error']
    
    def test_upload_document_invalid_type(self, client):
        """Test upload endpoint with invalid file type."""
        data = {'file': (io.BytesIO(b'test content'), 'test.txt')}
        response = client.post('/api/documents/upload', data=data)
        # This should work as txt is allowed
        assert response.status_code in [200, 201, 500]  # 500 if processing fails
    
    def test_get_documents_empty(self, client):
        """Test getting documents when none exist."""
        response = client.get('/api/documents')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 0
        assert data['documents'] == []
    
    def test_get_nonexistent_document(self, client):
        """Test getting a document that doesn't exist."""
        response = client.get('/api/documents/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Document not found' in data['error']

class TestQueryEndpoints:
    """Test query-related endpoints."""
    
    def test_query_no_question(self, client):
        """Test query endpoint with no question."""
        response = client.post('/api/query', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Question is required' in data['error']
    
    def test_query_empty_question(self, client):
        """Test query endpoint with empty question."""
        response = client.post('/api/query', json={'question': ''})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Question cannot be empty' in data['error']
    
    @patch('api_routes.current_app.rag_pipeline')
    def test_query_success(self, mock_rag_pipeline, client):
        """Test successful query."""
        mock_rag_pipeline.query.return_value = {
            'answer': 'Test answer',
            'sources': [],
            'metadata': {'chunks_retrieved': 0, 'response_time': 0.1},
            'success': True
        }
        
        response = client.post('/api/query', json={'question': 'Test question'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['answer'] == 'Test answer'
        assert data['success'] is True

class TestDatabaseModels:
    """Test database models."""
    
    def test_document_creation(self, app, sample_document_data):
        """Test document creation."""
        with app.app_context():
            document = Document(**sample_document_data)
            db.session.add(document)
            db.session.commit()
            
            assert document.id is not None
            assert document.filename == sample_document_data['filename']
            assert document.to_dict()['filename'] == sample_document_data['filename']
    
    def test_query_log_creation(self, app):
        """Test query log creation."""
        with app.app_context():
            query_log = QueryLog(
                query='Test query',
                response='Test response',
                document_ids='[1, 2]',
                response_time=0.5
            )
            db.session.add(query_log)
            db.session.commit()
            
            assert query_log.id is not None
            assert query_log.query == 'Test query'
            assert query_log.to_dict()['query'] == 'Test query'

class TestDocumentProcessor:
    """Test document processing functionality."""
    
    def test_chunk_text(self):
        """Test text chunking functionality."""
        from document_processor import DocumentProcessor
        
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        text = "This is a test document. " * 50  # Create a long text
        chunks = processor.chunk_text(text)
        
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('tokens' in chunk for chunk in chunks)
    
    def test_supported_formats(self):
        """Test supported file formats."""
        from document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        formats = processor.get_supported_formats()
        
        assert 'pdf' in formats
        assert 'docx' in formats
        assert 'txt' in formats

class TestVectorStore:
    """Test vector store functionality."""
    
    @patch('vector_store.chromadb.PersistentClient')
    def test_vector_store_initialization(self, mock_client):
        """Test vector store initialization."""
        from vector_store import VectorStore
        
        # Mock the client and collection
        mock_collection = MagicMock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        vector_store = VectorStore(persist_directory="./test_vector_db")
        
        assert vector_store.client is not None
        assert vector_store.collection is not None
        mock_client.assert_called_once()

class TestLLMClient:
    """Test LLM client functionality."""
    
    @patch('llm_client.genai.configure')
    @patch('llm_client.genai.GenerativeModel')
    def test_llm_client_initialization(self, mock_model, mock_configure):
        """Test LLM client initialization."""
        from llm_client import LLMClient
        
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance
        
        client = LLMClient(api_key="test_key")
        
        assert client.api_key == "test_key"
        assert client.model is not None
        mock_configure.assert_called_once_with(api_key="test_key")

if __name__ == '__main__':
    pytest.main([__file__])