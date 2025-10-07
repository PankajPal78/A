#!/bin/bash

# Verification script for RAG Document Q&A System
# Checks if all components are properly configured

echo "🔍 Verifying RAG Document Q&A System Setup..."
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

# Check function
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $1"
        ((FAIL++))
    fi
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARN++))
}

# 1. Check Docker
echo "📦 Checking Docker..."
command -v docker &> /dev/null
check "Docker is installed"

command -v docker-compose &> /dev/null
check "Docker Compose is installed"

if command -v docker &> /dev/null; then
    docker --version | grep "Docker version" &> /dev/null
    check "Docker is running"
fi
echo ""

# 2. Check Python (for local dev)
echo "🐍 Checking Python..."
command -v python3 &> /dev/null
check "Python 3 is installed"

if command -v python3 &> /dev/null; then
    python3 --version | grep -E "3\.(9|10|11|12)" &> /dev/null
    check "Python version is 3.9+"
fi
echo ""

# 3. Check project structure
echo "📁 Checking project structure..."

[ -f "app.py" ]
check "app.py exists"

[ -f "requirements.txt" ]
check "requirements.txt exists"

[ -f "Dockerfile" ]
check "Dockerfile exists"

[ -f "docker-compose.yml" ]
check "docker-compose.yml exists"

[ -f ".env" ]
check ".env file exists"

[ -d "app" ]
check "app/ directory exists"

[ -d "config" ]
check "config/ directory exists"

[ -d "data" ]
check "data/ directory exists"

echo ""

# 4. Check data directories
echo "📂 Checking data directories..."

[ -d "data/uploads" ]
check "data/uploads/ exists"

[ -d "data/vector_db" ]
check "data/vector_db/ exists"

[ -d "data/metadata" ]
check "data/metadata/ exists"

echo ""

# 5. Check application files
echo "🔧 Checking application files..."

[ -f "app/__init__.py" ]
check "app/__init__.py exists"

[ -f "app/api/routes.py" ]
check "app/api/routes.py exists"

[ -f "app/services/rag_service.py" ]
check "app/services/rag_service.py exists"

[ -f "app/services/vector_store.py" ]
check "app/services/vector_store.py exists"

[ -f "app/services/llm_service.py" ]
check "app/services/llm_service.py exists"

[ -f "app/utils/document_processor.py" ]
check "app/utils/document_processor.py exists"

echo ""

# 6. Check configuration
echo "⚙️  Checking configuration..."

if [ -f ".env" ]; then
    # Check if API key is set
    if grep -q "GEMINI_API_KEY=.\+" .env && ! grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env; then
        check "Gemini API key is configured"
    else
        warn "Gemini API key not configured (required for queries)"
    fi
    
    grep -q "LLM_PROVIDER=" .env
    check "LLM provider is configured"
fi

echo ""

# 7. Check documentation
echo "📚 Checking documentation..."

[ -f "README.md" ]
check "README.md exists"

[ -f "QUICKSTART.md" ]
check "QUICKSTART.md exists"

[ -f "DEPLOYMENT.md" ]
check "DEPLOYMENT.md exists"

[ -f "CONTRIBUTING.md" ]
check "CONTRIBUTING.md exists"

echo ""

# 8. Check test infrastructure
echo "🧪 Checking test infrastructure..."

[ -f "pytest.ini" ]
check "pytest.ini exists"

[ -f "app/tests/conftest.py" ]
check "Test configuration exists"

[ -f "app/tests/test_api.py" ]
check "API tests exist"

[ -f "run_tests.sh" ]
check "Test runner script exists"

echo ""

# 9. Check scripts
echo "📜 Checking utility scripts..."

[ -f "setup.sh" ]
check "setup.sh exists"

[ -x "setup.sh" ]
check "setup.sh is executable"

[ -f "example_usage.py" ]
check "example_usage.py exists"

[ -f "postman_collection.json" ]
check "Postman collection exists"

echo ""

# 10. Check if API is running (optional)
echo "🌐 Checking if API is running..."

if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    check "API is running and healthy"
    
    # Get API version info
    API_INFO=$(curl -s http://localhost:5000/ | grep -o '"service":"[^"]*"' | cut -d':' -f2 | tr -d '"')
    echo -e "   ${GREEN}→${NC} Service: $API_INFO"
else
    warn "API is not running (run: docker-compose up)"
fi

echo ""
echo "=================================="
echo "📊 Verification Summary"
echo "=================================="
echo -e "${GREEN}Passed:${NC} $PASS"
echo -e "${YELLOW}Warnings:${NC} $WARN"
echo -e "${RED}Failed:${NC} $FAIL"
echo ""

if [ $FAIL -eq 0 ] && [ $WARN -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Your setup is complete.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Make sure GEMINI_API_KEY is set in .env"
    echo "2. Run: docker-compose up --build"
    echo "3. Test: curl http://localhost:5000/api/health"
    echo ""
elif [ $FAIL -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Setup is mostly complete with some warnings.${NC}"
    echo ""
    echo "Please address the warnings above before deploying."
    echo ""
else
    echo -e "${RED}❌ Setup incomplete. Please fix the failed checks.${NC}"
    echo ""
    echo "Run ./setup.sh to fix missing files and directories."
    echo ""
    exit 1
fi