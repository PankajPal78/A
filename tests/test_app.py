import pytest
import tempfile
import os
from app import app, db, Document

class TestApp:
    """Test cases for Flask application"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.app.config['UPLOAD_FOLDER'], ignore_errors=True)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_upload_document_no_file(self):
        """Test upload endpoint with no file"""
        response = self.client.post('/api/documents')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_upload_document_empty_filename(self):
        """Test upload endpoint with empty filename"""
        response = self.client.post('/api/documents', data={'file': ''})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_list_documents_empty(self):
        """Test listing documents when none exist"""
        response = self.client.get('/api/documents')
        assert response.status_code == 200
        data = response.get_json()
        assert data == []
    
    def test_get_nonexistent_document(self):
        """Test getting a document that doesn't exist"""
        response = self.client.get('/api/documents/nonexistent_id')
        assert response.status_code == 404
    
    def test_delete_nonexistent_document(self):
        """Test deleting a document that doesn't exist"""
        response = self.client.delete('/api/documents/nonexistent_id')
        assert response.status_code == 404
    
    def test_query_no_data(self):
        """Test query endpoint with no data"""
        response = self.client.post('/api/query')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_query_missing_query(self):
        """Test query endpoint with missing query"""
        response = self.client.post('/api/query', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_get_stats(self):
        """Test stats endpoint"""
        response = self.client.get('/api/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_documents' in data
        assert 'completed_documents' in data
        assert 'failed_documents' in data
        assert 'total_chunks' in data
    
    def test_document_model(self):
        """Test Document model"""
        with self.app.app_context():
            doc = Document(
                filename='test.txt',
                original_filename='test.txt',
                file_type='.txt',
                file_size=100
            )
            db.session.add(doc)
            db.session.commit()
            
            assert doc.id is not None
            assert doc.filename == 'test.txt'
            assert doc.status == 'processing'
            
            # Test to_dict method
            doc_dict = doc.to_dict()
            assert 'id' in doc_dict
            assert 'filename' in doc_dict
            assert 'upload_date' in doc_dict