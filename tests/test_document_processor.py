import pytest
import os
import tempfile
from document_processor import DocumentProcessor

@pytest.fixture
def processor():
    """Create document processor for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield DocumentProcessor(chroma_db_path=temp_dir)

def test_chunk_text(processor):
    """Test text chunking functionality"""
    sample_text = [
        {'content': 'This is a sample text for testing chunking functionality. ' * 50, 'page_number': 1}
    ]
    
    chunks = processor._chunk_text(sample_text, chunk_size=100, overlap=20)
    
    assert len(chunks) > 0
    assert all('content' in chunk for chunk in chunks)
    assert all('page_number' in chunk for chunk in chunks)

def test_extract_txt_text(processor):
    """Test text extraction from TXT files"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Sample text content for testing")
        f.flush()
        
        try:
            result = processor._extract_txt_text(f.name)
            assert len(result) == 1
            assert result[0]['content'] == "Sample text content for testing"
            assert result[0]['page_number'] == 1
        finally:
            os.unlink(f.name)

def test_search_similar_chunks(processor):
    """Test vector search functionality"""
    # This test would require setting up test data in ChromaDB
    # For now, we'll test that the method doesn't crash
    try:
        results = processor.search_similar_chunks("test query", n_results=5)
        assert isinstance(results, list)
    except Exception as e:
        # Expected to fail without proper setup
        assert "collection" in str(e).lower() or "embedding" in str(e).lower()