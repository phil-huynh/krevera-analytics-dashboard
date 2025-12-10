#!/bin/bash
set -e

echo "=========================================="
echo "Krevera Analytics - Docker Test Suite"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker Desktop."
    exit 1
fi

echo "🐳 Running tests in Docker container..."
echo ""

# Parse test category argument
TEST_CATEGORY=${1:-all}

case $TEST_CATEGORY in
    "api")
        echo "Running API endpoint tests..."
        docker-compose exec -T backend pytest tests/test_api_analytics.py -v --tb=short
        ;;
    "models")
        echo "Running database model tests..."
        docker-compose exec -T backend pytest tests/test_models.py -v --tb=short
        ;;
    "workflow")
        echo "Running Temporal workflow tests..."
        docker-compose exec -T backend pytest tests/test_activities.py -v --tb=short
        ;;
    "s3")
        echo "Running S3 service tests..."
        docker-compose exec -T backend pytest tests/test_s3_service.py -v --tb=short
        ;;
    "coverage")
        echo "Running all tests with coverage report..."
        docker-compose exec -T backend pytest --cov=app --cov-report=term-missing --cov-report=html -v
        echo ""
        echo "📊 Coverage report generated in backend/htmlcov/index.html"
        ;;
    "all"|*)
        echo "Running all tests..."
        docker-compose exec -T backend pytest -v --tb=short
        ;;
esac

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed"
fi

echo ""
echo "=========================================="
echo ""

exit $EXIT_CODE