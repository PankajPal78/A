"""
Pytest configuration and fixtures
"""
import pytest
import os
import tempfile
from app import create_app
from app.utils.database import init_db, Session
from app.models.document import Base

@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    # Create temporary directory for test data
    test_dir = tempfile.mkdtemp()
    
    # Set test environment variables
    os.environ['UPLOAD_FOLDER'] = os.path.join(test_dir, 'uploads')
    os.environ['VECTOR_DB_PATH'] = os.path.join(test_dir, 'vector_db')
    os.environ['DATABASE_URL'] = f'sqlite:///{test_dir}/test.db'
    os.environ['DEBUG'] = 'True'
    
    # Create directories
    os.makedirs(os.environ['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.environ['VECTOR_DB_PATH'], exist_ok=True)
    
    app = create_app()
    app.config['TESTING'] = True
    
    yield app
    
    # Cleanup
    Session.remove()

@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()