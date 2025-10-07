import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.models import Base, engine

@pytest.fixture
def app():
    """Create application for testing"""
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['UPLOAD_FOLDER'] = '/tmp/test_uploads'
    os.environ['VECTOR_DB_PATH'] = '/tmp/test_vectordb'
    
    app = create_app()
    
    # Create test directories
    os.makedirs('/tmp/test_uploads', exist_ok=True)
    os.makedirs('/tmp/test_vectordb', exist_ok=True)
    
    yield app
    
    # Cleanup
    import shutil
    if os.path.exists('/tmp/test_uploads'):
        shutil.rmtree('/tmp/test_uploads')
    if os.path.exists('/tmp/test_vectordb'):
        shutil.rmtree('/tmp/test_vectordb')

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()