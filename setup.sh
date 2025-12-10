#!/bin/bash
set -e  # Exit on error

echo "=========================================="
echo "Krevera Manufacturing Analytics Dashboard"
echo "Setup Script"
echo "=========================================="
echo ""

# Check for optional dataset URL argument
DATASET_URL="$1"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker daemon is running"
echo ""

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env file..."
    cat > backend/.env << EOF
# Database Configuration
DATABASE_URL=postgresql://krevera:krevera_pass@postgres:5432/krevera_analytics
POSTGRES_USER=krevera
POSTGRES_PASSWORD=krevera_pass
POSTGRES_DB=krevera_analytics

# Temporal Configuration
TEMPORAL_HOST=temporal:7233

# S3 Configuration (LocalStack)
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_REGION=us-east-1
S3_BUCKET_NAME=krevera-datasets
S3_ENDPOINT_URL=http://localstack:4566

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
EOF
    echo "✅ Created backend/.env"
else
    echo "✅ backend/.env already exists"
fi

if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend/.env file..."
    cat > frontend/.env << EOF
VITE_API_BASE_URL=http://localhost:8000
EOF
    echo "✅ Created frontend/.env"
else
    echo "✅ frontend/.env already exists"
fi

echo ""
echo "🏗️  Building Docker containers..."
echo "   (This may take several minutes on first run)"
docker-compose build

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Docker build failed. Please check the errors above."
    exit 1
fi

echo ""
echo "🚀 Starting services..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Failed to start services. Please check the errors above."
    exit 1
fi

echo ""
echo "⏳ Waiting for services to be healthy..."
echo "   - PostgreSQL database"
echo "   - Temporal server"
echo "   - LocalStack (S3)"
echo "   - Backend API"
sleep 10

# Wait for backend to be healthy
echo ""
echo "🔍 Checking service health..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend API is healthy"
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo "❌ Backend API failed to start within timeout"
        echo "   Check logs with: docker-compose logs backend"
        exit 1
    fi

    echo "   Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

echo ""
echo "📊 Running database migrations..."
docker-compose exec -T backend alembic upgrade head

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Database migrations failed"
    echo "   Check logs with: docker-compose logs backend"
    exit 1
fi

echo "✅ Database migrations complete"
echo ""

# Seed database if URL was provided
if [ -n "$DATASET_URL" ]; then
    echo "=========================================="
    echo "Database Seeding"
    echo "=========================================="
    echo ""
    echo "🌱 Seeding database with dataset from:"
    echo "   $DATASET_URL"
    echo ""
    echo "   This may take 2-5 minutes depending on dataset size..."
    echo ""

    # Use the seed.sh script
    ./seed.sh "$DATASET_URL"

    if [ $? -ne 0 ]; then
        echo ""
        echo "⚠️  Database seeding failed, but services are running"
        echo "   You can retry seeding with:"
        echo "   ./seed.sh $DATASET_URL"
    fi
    echo ""
fi

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "🌐 Access your application:"
echo ""
echo "   Frontend Dashboard:  http://localhost:5173"
echo "   Backend API:         http://localhost:8000"
echo "   API Documentation:   http://localhost:8000/docs"
echo "   Temporal UI:         http://localhost:8233"
echo ""

# Show appropriate next steps based on whether data was seeded
if [ -z "$DATASET_URL" ]; then
    echo "📊 Next Step - Seed Your Database:"
    echo ""
    echo "   To load your manufacturing data, run:"
    echo "   ./seed.sh <your-dataset-url>"
    echo ""
    echo "   Example:"
    echo "   ./seed.sh https://static.krevera.com/dataset.json"
    echo ""
else
    echo "✅ Database seeded successfully!"
    echo ""
    echo "   You can view your data at http://localhost:5173"
    echo ""
    echo "   To reload with different data:"
    echo "   ./seed.sh <new-dataset-url>"
    echo ""
fi

echo "📋 Useful commands:"
echo ""
echo "   Stop services:       docker-compose down"
echo "   View logs:           docker-compose logs -f"
echo "   View specific logs:  docker-compose logs -f [backend|frontend|worker]"
echo "   Restart services:    docker-compose restart"
echo ""
echo "📚 For more information, see README.md"
echo ""