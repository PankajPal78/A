"""
Tests for vector store service
"""

import pytest
import tempfile
import shutil
from services.vector_store import VectorStore

class TestVectorStore:
    
    def setup_method(self):
        """Setup test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.vector_store = VectorStore(
            persist_directory=self.temp_dir,
            collection_name="test_collection",
            embedding_model="all-MiniLM-L6-v2"
        )
    
    def teardown_method(self):
        """Cleanup test method"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_embeddings(self):
        """Test embedding generation"""
        texts = ["This is a test sentence.", "Another test sentence."]
        embeddings = self.vector_store.generate_embeddings(texts)
        
        assert len(embeddings) == 2
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)
    
    def test_add_documents(self):
        """Test adding documents to vector store"""
        chunks = [
            {
                'text': 'This is the first chunk of text.',
                'metadata': {'chunk_index': 0, 'filename': 'test.txt'}
            },
            {
                'text': 'This is the second chunk of text.',
                'metadata': {'chunk_index': 1, 'filename': 'test.txt'}
            }
        ]
        
        chunk_ids = self.vector_store.add_documents(chunks, document_id=1)
        
        assert len(chunk_ids) == 2
        assert all(isinstance(chunk_id, str) for chunk_id in chunk_ids)
        assert all('doc_1_chunk_' in chunk_id for chunk_id in chunk_ids)
    
    def test_similarity_search(self):
        """Test similarity search"""
        # First add some documents
        chunks = [
            {
                'text': 'Machine learning is a subset of artificial intelligence.',
                'metadata': {'chunk_index': 0, 'filename': 'ml.txt'}
            },
            {
                'text': 'Natural language processing deals with human language.',
                'metadata': {'chunk_index': 1, 'filename': 'nlp.txt'}
            },
            {
                'text': 'Vector databases store high-dimensional vectors.',
                'metadata': {'chunk_index': 0, 'filename': 'vectors.txt'}
            }
        ]
        
        self.vector_store.add_documents(chunks, document_id=1)
        
        # Search for similar content
        results = self.vector_store.similarity_search(
            query="artificial intelligence and machine learning",
            top_k=2
        )
        
        assert len(results) <= 2
        assert all('similarity_score' in result for result in results)
        assert all('text' in result for result in results)
        assert all('metadata' in result for result in results)
        
        # The ML-related chunk should have higher similarity
        if len(results) > 0:
            assert 'machine learning' in results[0]['text'].lower()
    
    def test_get_document_chunks(self):
        """Test getting chunks for a specific document"""
        chunks = [
            {
                'text': 'First chunk',
                'metadata': {'chunk_index': 0}
            },
            {
                'text': 'Second chunk',
                'metadata': {'chunk_index': 1}
            }
        ]
        
        self.vector_store.add_documents(chunks, document_id=1)
        
        retrieved_chunks = self.vector_store.get_document_chunks(document_id=1)
        
        assert len(retrieved_chunks) == 2
        assert retrieved_chunks[0]['metadata']['chunk_index'] == 0
        assert retrieved_chunks[1]['metadata']['chunk_index'] == 1
    
    def test_delete_document(self):
        """Test deleting document chunks"""
        chunks = [
            {
                'text': 'Chunk to be deleted',
                'metadata': {'chunk_index': 0}
            }
        ]
        
        self.vector_store.add_documents(chunks, document_id=1)
        
        # Verify chunk exists
        retrieved_chunks = self.vector_store.get_document_chunks(document_id=1)
        assert len(retrieved_chunks) == 1
        
        # Delete document
        deleted_count = self.vector_store.delete_document(document_id=1)
        assert deleted_count == 1
        
        # Verify chunk is deleted
        retrieved_chunks = self.vector_store.get_document_chunks(document_id=1)
        assert len(retrieved_chunks) == 0
    
    def test_get_collection_stats(self):
        """Test getting collection statistics"""
        stats = self.vector_store.get_collection_stats()
        
        assert 'total_chunks' in stats
        assert 'total_documents' in stats
        assert 'collection_name' in stats
        assert 'embedding_model' in stats
        
        assert stats['collection_name'] == 'test_collection'
        assert stats['embedding_model'] == 'all-MiniLM-L6-v2'