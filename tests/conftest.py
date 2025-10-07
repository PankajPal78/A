import pytest
import tempfile
import os
from app import app, db

@pytest.fixture(scope='session')
def app_context():
    """Create application context for testing"""
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def test_db(app_context):
    """Create test database"""
    db.create_all()
    yield db
    db.drop_all()

@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)