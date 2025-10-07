# Contributing to RAG Document Q&A System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, Docker version)
   - Relevant logs and error messages

### Suggesting Enhancements

1. **Check existing feature requests**
2. **Provide clear use case** and benefit
3. **Include implementation ideas** if possible

### Pull Requests

1. **Fork the repository**
```bash
git clone https://github.com/yourusername/rag-document-qa.git
cd rag-document-qa
```

2. **Create a feature branch**
```bash
git checkout -b feature/amazing-feature
```

3. **Make your changes**
   - Follow the coding standards below
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
```bash
# Run tests
pytest app/tests/ -v

# Run linting
flake8 app/

# Test with Docker
docker-compose up --build
```

5. **Commit your changes**
```bash
git add .
git commit -m "Add amazing feature"
```

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding tests
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Build/tooling changes

6. **Push to your fork**
```bash
git push origin feature/amazing-feature
```

7. **Create Pull Request**
   - Provide clear description
   - Reference related issues
   - Include screenshots if UI changes
   - Ensure CI passes

## Development Setup

### Local Environment

1. **Clone repository**
```bash
git clone <repository-url>
cd rag-document-qa
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Configure environment**
```bash
cp .env.example .env
# Add your API keys
```

5. **Run in development mode**
```bash
export DEBUG=True
python app.py
```

### Development Dependencies

Create `requirements-dev.txt` for development tools:
```
pytest==7.4.3
pytest-cov==4.1.0
flake8==6.1.0
black==23.11.0
isort==5.12.0
mypy==1.7.1
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small
- Maximum line length: 100 characters

### Code Formatting

Use Black for formatting:
```bash
black app/
```

Use isort for imports:
```bash
isort app/
```

### Type Hints

Add type hints where possible:
```python
def process_document(file_path: str, file_type: str) -> tuple[str, int]:
    """Process document and return text and page count"""
    ...
```

### Docstrings

Use Google-style docstrings:
```python
def add_documents(self, chunks: List[Dict], document_id: int):
    """
    Add document chunks to vector store.
    
    Args:
        chunks: List of chunk dictionaries with 'text' and 'metadata'
        document_id: Document ID for tracking
        
    Returns:
        None
        
    Raises:
        ValueError: If chunks list is empty
    """
    ...
```

## Testing Guidelines

### Writing Tests

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test component interactions
3. **API Tests**: Test API endpoints

### Test Structure

```python
class TestFeature:
    """Test feature description"""
    
    def test_specific_behavior(self):
        """Test specific behavior description"""
        # Arrange
        input_data = ...
        
        # Act
        result = function(input_data)
        
        # Assert
        assert result == expected
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest app/tests/test_api.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run with verbose output
pytest -v
```

### Test Coverage

- Aim for >80% code coverage
- Test edge cases and error handling
- Mock external services (LLM APIs, etc.)

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Update README.md for user-facing changes
- Update API documentation for endpoint changes

### Documentation Files

- `README.md`: Main documentation
- `QUICKSTART.md`: Quick start guide
- `DEPLOYMENT.md`: Deployment instructions
- `CONTRIBUTING.md`: This file
- API comments: Inline documentation

## Project Structure

```
rag-document-qa/
├── app/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── models/
│   │   └── document.py        # Database models
│   ├── services/
│   │   ├── vector_store.py    # Vector database service
│   │   ├── llm_service.py     # LLM integration
│   │   └── rag_service.py     # RAG pipeline
│   ├── utils/
│   │   ├── database.py        # Database utilities
│   │   └── document_processor.py  # Document processing
│   ├── tests/
│   │   ├── conftest.py        # Test fixtures
│   │   ├── test_api.py        # API tests
│   │   └── test_*.py          # Other tests
│   └── __init__.py            # App factory
├── config/
│   └── settings.py            # Configuration
├── data/                      # Data directories
├── app.py                     # Entry point
├── requirements.txt           # Dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose
└── README.md                  # Documentation
```

## Adding New Features

### 1. New LLM Provider

Create a new method in `LLMService`:

```python
def _generate_provider_response(self, prompt: str) -> str:
    """Generate response using new provider"""
    # Implementation
```

### 2. New Document Type

Add to `DocumentProcessor`:

```python
def extract_text_from_docx(self, file_path: str) -> tuple[str, int]:
    """Extract text from DOCX file"""
    # Implementation
```

### 3. New API Endpoint

Add to `app/api/routes.py`:

```python
@api_bp.route('/new-endpoint', methods=['POST'])
def new_endpoint():
    """New endpoint description"""
    # Implementation
```

## Review Process

1. **Code Review**: At least one maintainer approval required
2. **CI Checks**: All tests must pass
3. **Documentation**: Must be updated for changes
4. **Changelog**: Significant changes should update CHANGELOG.md

## Release Process

1. Update version in `app/__init__.py`
2. Update CHANGELOG.md
3. Create release tag
4. Build and test Docker image
5. Create GitHub release

## Questions?

- Open an issue for questions
- Join discussions in GitHub Discussions
- Check existing documentation

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project acknowledgments

Thank you for contributing! 🎉