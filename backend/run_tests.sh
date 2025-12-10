#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "Krevera Analytics - Test Suite"
echo "=========================================="
echo ""

if [ -f /.dockerenv ]; then
    echo "📦 Running in Docker container"
    IN_DOCKER=true
else
    echo "💻 Running on local machine"
    IN_DOCKER=false
fi

echo ""

check_test_dependencies() {
    python -c "import pytest" 2>/dev/null
    return $?
}

if ! check_test_dependencies; then
    echo "📦 Installing test dependencies..."

    if [ "$IN_DOCKER" = true ]; then
        pip install -r requirements-test.txt
    else
        if [ -z "$VIRTUAL_ENV" ]; then
            echo ""
            echo -e "${YELLOW}⚠️  No virtual environment detected${NC}"
            echo ""
            echo "It's recommended to use a virtual environment for testing."
            echo "Would you like to create one?"
            echo ""
            read -p "Create virtual environment? (Y/n): " -n 1 -r
            echo ""

            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                echo "Creating virtual environment in ./venv..."
                python -m venv venv

                if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
                    source venv/Scripts/activate
                else
                    source venv/bin/activate
                fi

                echo "✅ Virtual environment created and activated"
            fi
        fi

        pip install -r requirements.txt
        pip install -r requirements-test.txt
    fi

    echo "✅ Test dependencies installed"
    echo ""
fi

TEST_CATEGORY=${1:-all}

echo "🧪 Running tests: $TEST_CATEGORY"
echo ""

case $TEST_CATEGORY in
    "api")
        echo "Running API endpoint tests..."
        pytest tests/test_api_analytics.py -v --tb=short
        ;;
    "models")
        echo "Running database model tests..."
        pytest tests/test_models.py -v --tb=short
        ;;
    "workflow")
        echo "Running Temporal workflow tests..."
        pytest tests/test_activities.py -v --tb=short
        ;;
    "s3")
        echo "Running S3 service tests..."
        pytest tests/test_s3_service.py -v --tb=short
        ;;
    "coverage")
        echo "Running all tests with coverage report..."
        pytest --cov=app --cov-report=term-missing --cov-report=html -v
        echo ""
        echo "📊 Coverage report generated in htmlcov/index.html"
        ;;
    "all"|*)
        echo "Running all tests..."
        pytest -v --tb=short
        ;;
esac

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
fi

echo ""
echo "=========================================="
echo ""

exit $EXIT_CODE