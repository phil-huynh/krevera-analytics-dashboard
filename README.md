# Krevera Manufacturing Analytics Platform

A full-stack manufacturing quality control analytics platform that processes injection molding machine data to provide real-time insights into production quality, defect patterns, and machine performance.

![Dashboard Overview](./assets/dashboard-overview.png)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Manual Setup](#manual-setup)
- [Data Ingestion](#data-ingestion)
- [Usage](#usage)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

The Krevera Manufacturing Analytics Platform is designed to help manufacturing operations teams monitor and analyze injection molding quality control data in real-time. The platform ingests production data from multiple molding machines, processes it through a robust ETL pipeline, and presents actionable insights through an interactive web dashboard.

### Key Capabilities

- **Real-time Analytics**: Process and visualize quality control data from multiple production lines
- **Defect Analysis**: Track defect patterns, frequencies, and severity across machines and time periods
- **Performance Monitoring**: Monitor cycle times, shot counts, and machine efficiency metrics
- **Historical Analysis**: Query and analyze historical production data with flexible filtering
- **Scalable Architecture**: Distributed workflow orchestration handles high-volume data ingestion

## Features

### Interactive Dashboard

- **6 Visualization Types**: Comprehensive charts covering cycle time trends, defect rates, machine comparisons, and defect distributions
- **Dynamic Filtering**: Filter data by machine, date range, and other criteria with real-time chart updates
- **Mobile Responsive**: Fully responsive design works seamlessly on desktop, tablet, and mobile devices
- **Performance Optimized**: Fast loading and smooth interactions even with large datasets

![Analytics Charts](./assets/analytics-charts.png)

### Data Processing Pipeline

- **Temporal Workflow Orchestration**: Reliable, fault-tolerant data ingestion with automatic retries
- **Distributed Processing**: Handles large datasets (3,000+ products) efficiently
- **S3 Integration**: Scalable cloud storage for dataset archival and retrieval
- **Database Optimization**: Indexed queries and efficient data models for fast analytics

### Analytics Capabilities

- **Cycle Time Analysis**: Track production speed and identify bottlenecks
- **Defect Rate Tracking**: Monitor quality trends over time
- **Top Defects Identification**: Identify most common defect types for prioritized improvement
- **Machine Comparison**: Compare performance metrics across multiple machines
- **Defect Distribution**: Understand defect type prevalence across production
- **Machine-Defect Heatmap**: Visualize defect patterns by machine and defect type

## Architecture

The platform uses a modern microservices architecture with clear separation of concerns:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Vue 3     │────▶│   FastAPI    │────▶│ PostgreSQL  │
│  Frontend   │     │   Backend    │     │  Database   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Temporal   │
                    │   Workflow   │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  LocalStack  │
                    │  S3 Storage  │
                    └──────────────┘
```

### Components

- **Frontend**: Vue 3 + TypeScript + ECharts for rich, interactive visualizations
- **Backend API**: FastAPI with async support for high-performance API endpoints
- **Workflow Engine**: Temporal for reliable data ingestion orchestration
- **Database**: PostgreSQL with optimized indexes for analytical queries
- **Object Storage**: S3-compatible storage (LocalStack for development, AWS S3 for production)
- **Containerization**: Docker Compose for local development and easy deployment

## Tech Stack

### Frontend
- **Framework**: Vue 3 with Composition API
- **Language**: TypeScript
- **Charts**: Apache ECharts
- **HTTP Client**: Axios
- **Build Tool**: Vite
- **Testing**: Vitest + Testing Library

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Workflow**: Temporal
- **Storage**: boto3 (AWS SDK)
- **Testing**: pytest + pytest-asyncio

### Infrastructure
- **Database**: PostgreSQL 15
- **Object Storage**: LocalStack (S3-compatible)
- **Orchestration**: Docker Compose
- **Workflow Engine**: Temporal Server

## Prerequisites

- **Docker Desktop**: Version 4.0+ with Docker Compose
- **Node.js**: Version 18+ (for frontend development)
- **Python**: Version 3.10+ (for backend development)
- **Git**: For cloning the repository

### Platform-Specific Requirements

**Windows Users:**
- **Git for Windows** (includes Git Bash) for running bash scripts
  - Download: https://git-scm.com/download/win
- **Alternative**: WSL2 (Windows Subsystem for Linux)
  - Install: `wsl --install` in PowerShell (Admin)
- **Note**: PowerShell users can run commands manually (see [Troubleshooting](#troubleshooting))

**macOS Users:**
- Bash is pre-installed
- Docker Desktop for Mac

**Linux Users:**
- Bash is pre-installed
- Docker Engine + Docker Compose

### System Requirements

- **RAM**: Minimum 8GB (16GB for best performance)
- **Disk Space**: 5GB free space
- **OS**: macOS, Linux, or Windows 10/11 with WSL2 or Git Bash

## Quick Start

Get the platform running with the automated setup script:

### Unix/Linux/macOS

```bash
# Clone the repository
git clone <repository-url>
cd krevera-analytics

# Setup and load data in one command
chmod +x setup.sh
./setup.sh https://static.krevera.com/dataset.json

# Or setup without data (load it later)
chmod +x setup.sh
./setup.sh
```

### Windows

```powershell
# Clone the repository
git clone <repository-url>
cd krevera-analytics

# With Git Bash
bash setup.sh https://static.krevera.com/dataset.json

# Or setup without data
bash setup.sh
```

**Windows Users**: This project uses bash scripts. Use Git Bash (included with Git for Windows) or WSL2 (Windows Subsystem for Linux). You can also run commands manually as described in the [Manual Setup](#manual-setup) section.

The `setup.sh` script will:
1. ✅ Verify Docker and Docker Compose are installed
2. 📝 Create `.env` configuration files for backend and frontend
3. 🏗️ Build all Docker containers
4. 🚀 Start all services (PostgreSQL, Temporal, LocalStack, Backend, Worker, Frontend)
5. ⏳ Wait for database initialization
6. 🗄️ Run database migrations automatically
7. 📊 Load your dataset (if URL provided)
8. ✅ Services are ready to use

**After setup completes, access:**
- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Temporal UI**: http://localhost:8233

### Manual Quick Start

If you prefer to run commands manually or are on Windows without Git Bash/WSL:

```bash
# Clone the repository
git clone <repository-url>
cd krevera-analytics

# Start all services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps

# Run database migrations (creates tables)
docker-compose exec backend alembic upgrade head

# Seed the database with your data
# Unix/Mac:
./seed.sh <your-dataset-url>

# Windows (PowerShell):
docker-compose exec backend python seed_cli.py --url <your-dataset-url>

# Access the application
open http://localhost:5173
```

The dashboard should now be running with your manufacturing data loaded.

## Manual Setup

For development or when you need more control:

### 1. Clone and Setup

```bash
git clone <repository-url>
cd krevera-analytics
```

### 2. Start Infrastructure Services

```bash
# Start database, Temporal, and LocalStack
docker-compose up -d postgres temporal localstack

# Wait for services to be ready
sleep 30
```

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (creates database tables)
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start Temporal Worker

In a new terminal:

```bash
cd backend
source venv/bin/activate
python -m app.workflows.worker
```

### 5. Setup Frontend

In another new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 6. Access the Application

- **Frontend**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **Temporal UI**: http://localhost:8233

## Data Ingestion

The platform includes a robust data ingestion pipeline that can process manufacturing data from various sources.

### Automatic Seeding (During Setup)

The easiest way is to provide your dataset URL during initial setup:

```bash
./setup.sh https://your-dataset-url.json
```

This will automatically set up the entire platform and load your data.

### Manual Seeding (Anytime)

You can load or replace data at any time using the `seed.sh` script:

```bash
./seed.sh <dataset-url>
```

**Example:**
```bash
./seed.sh https://static.krevera.com/dataset.json
```

**Important Note:** The seed script **replaces** all existing data in the database using `TRUNCATE CASCADE`. If you want to preserve existing data while adding more, you'll need to merge datasets before ingesting.

The script will:
1. Validate the dataset URL
2. Trigger a Temporal workflow
3. Download the dataset
4. Upload to S3 storage
5. Parse and validate the data
6. **Clear existing data** (TRUNCATE CASCADE)
7. Bulk insert new data into PostgreSQL
8. Report completion statistics


### Data Format

The platform expects JSON data with the following structure:

```json
[
  {
    "version": "1.0",
    "timestamp": 1699564800.0,
    "molding_machine_id": "molding-machine-1",
    "object_detection": {
      "reject": false,
      "flash_defect": {
        "reject": true,
        "pixel_severity": {
          "value": 0.75,
          "reject": false
        }
      }
    },
    "molding-machine-state": {
      "CycleTime": 25.5,
      "ShotCount": 1000
    }
  }
]
```

### Workflow Monitoring

Monitor data ingestion progress via Temporal UI:

1. Open http://localhost:8233
2. Navigate to "Workflows"
3. Find your workflow by ID or filter by type
4. View execution history, logs, and status

## Usage

### Dashboard Navigation

The main dashboard provides six analytical views:

1. **Cycle Time Scatter Plot**: Visualize cycle time distribution and trends over time
2. **Defect Rate Trend**: Track defect rates with moving averages
3. **Top Defects Bar Chart**: Identify most common defect types
4. **Machine Comparison Radar**: Compare multiple metrics across machines
5. **Defect Distribution Pie Chart**: Understand defect type prevalence
6. **Machine-Defect Heatmap**: Spot patterns in machine-specific defects

### Filtering Data

Use the filter sidebar to refine your analysis:

- **Machine Filter**: Select one or more machines
- **Date Range**: Choose start and end dates
- **Apply/Reset**: Apply filters or reset to defaults

All charts update in real-time when filters change.

### Exporting Data

API endpoints support exporting filtered data:

```bash
# Export cycle time data
curl "http://localhost:8000/api/v1/analytics/cycle-time?start_date=2024-01-01&end_date=2024-12-31" > cycle_time.json

# Export defect summary
curl "http://localhost:8000/api/v1/analytics/top-defects?limit=10" > top_defects.json
```

## Testing

The platform includes comprehensive test suites for both frontend and backend, with **101 total tests**.

### Quick Test with Docker

The easiest way to run tests without any local setup:

**Unix/Linux/macOS:**
```bash
# From project root directory
chmod +x test-docker.sh
./test-docker.sh

# Run specific test categories
./test-docker.sh api          # API endpoint tests (21 tests)
./test-docker.sh models       # Database model tests (16 tests)
./test-docker.sh workflow     # Temporal workflow tests (7 tests)
./test-docker.sh s3           # S3 service tests (9 tests)
./test-docker.sh coverage     # Generate coverage report
```

**Windows (PowerShell or CMD):**
```powershell
# From project root directory
docker-compose exec -T backend pytest -v --tb=short

# Run specific test categories
docker-compose exec -T backend pytest tests/test_api_analytics.py -v
docker-compose exec -T backend pytest tests/test_models.py -v
docker-compose exec -T backend pytest tests/test_activities.py -v
docker-compose exec -T backend pytest tests/test_s3_service.py -v

# With coverage
docker-compose exec -T backend pytest --cov=app --cov-report=term-missing --cov-report=html -v
```

**Windows (Git Bash or WSL2):**
```bash
bash test-docker.sh
bash test-docker.sh api
```

**Requirements**: Only Docker (no Python or Node.js installation needed)

### Frontend Tests (51 tests)

Frontend tests work identically on all platforms:

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode (for development)
npm run test:watch

# Run specific test file
npm test ChartCard.test.ts
```

**Test Coverage:**
- ✅ Component rendering and props
- ✅ User interactions (clicks, filters)
- ✅ API integration and error handling
- ✅ Chart initialization and updates
- ✅ Responsive behavior
- ✅ Accessibility (a11y)

**Technologies**: Vitest + Testing Library + jsdom

### Backend Tests (50 passing tests)

#### Option 1: Using Docker (Works on all platforms)

**Unix/Linux/macOS:**
```bash
# From project root
./test-docker.sh

# With coverage
./test-docker.sh coverage
```

**Windows:**
```powershell
# From project root
docker-compose exec -T backend pytest -v --tb=short

# With coverage
docker-compose exec -T backend pytest --cov=app --cov-report=html -v
```

#### Option 2: Local Testing (Unix/Linux/macOS only)

The `run_tests.sh` script automatically handles virtual environment creation and dependency installation:

```bash
cd backend

# Run all tests (auto-installs dependencies)
./run_tests.sh

# Run specific test categories
./run_tests.sh api          # API endpoint tests
./run_tests.sh models       # Database model tests
./run_tests.sh workflow     # Temporal workflow tests
./run_tests.sh s3           # S3 service tests

# Run with coverage report
./run_tests.sh coverage
```

**First-time setup**: The script will:
1. Detect if you're in a virtual environment
2. Offer to create one if needed
3. Install test dependencies automatically
4. Run the tests

**Manual setup for Windows** (if preferred):
```powershell
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run tests
pytest -v
```

**Manual setup for Unix/Linux/macOS** (if preferred):
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run tests
pytest -v
```

**Test Coverage:**
- ✅ API endpoints (21 tests) - All REST endpoints with filtering
- ✅ Database models (16 tests) - CRUD operations and relationships
- ✅ S3 operations (9 tests) - Upload, download, error handling
- ✅ Workflow activities (7 tests, 5 passing, 2 xfail) - Data ingestion pipeline

**Technologies**: pytest + pytest-asyncio + SQLAlchemy

**Note on xfail tests**: 3 tests are marked as `xfail` (expected failure) due to SQLite/PostgreSQL differences in the test environment. These tests pass in production with PostgreSQL but are skipped in local testing.

### Platform Compatibility Summary

| Platform | Primary Method | Alternative |
|----------|---------------------|-------------|
| **macOS/Linux** | `./test-docker.sh` | `./run_tests.sh` in backend/ |
| **Windows (Git Bash)** | `bash test-docker.sh` | Git Bash with `./run_tests.sh` |
| **Windows (PowerShell)** | `docker-compose exec -T backend pytest -v` | Manual venv + pytest |
| **Windows (WSL2)** | `./test-docker.sh` | `./run_tests.sh` in backend/ |


### Coverage Reports

**Frontend Coverage:**
```bash
cd frontend
npm run test:coverage
# Opens: frontend/coverage/index.html
```

**Backend Coverage:**
```bash
# Unix/Mac:
./test-docker.sh coverage

# Windows:
docker-compose exec -T backend pytest --cov=app --cov-report=html -v

# Opens: backend/htmlcov/index.html
```

### Test Performance

- Frontend: ~2-3 seconds
- Backend: ~10-15 seconds (includes database setup)
- Total: ~15-20 seconds for complete test suite

## API Documentation

### Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Analytics Endpoints

**Get Machines List**
```http
GET /api/v1/analytics/machines
```

**Get Cycle Time Data**
```http
GET /api/v1/analytics/cycle-time?machine_id=molding-machine-1&start_date=2024-01-01&end_date=2024-12-31
```

**Get Defect Rate**
```http
GET /api/v1/analytics/defect-rate?machine_id=molding-machine-1
```

**Get Top Defects**
```http
GET /api/v1/analytics/top-defects?limit=10
```

**Get Machine Comparison**
```http
GET /api/v1/analytics/machine-comparison
```

**Get Defect Distribution**
```http
GET /api/v1/analytics/defect-distribution
```

**Get Machine-Defect Heatmap**
```http
GET /api/v1/analytics/machine-defect-heatmap
```

#### Health Check

**System Health**
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "krevera-analytics-api",
  "version": "1.0.0",
  "environment": "development"
}
```

## Project Structure
```
krevera-analytics/
├── frontend/                  # Vue 3 frontend application
│   ├── src/
│   │   ├── components/       # Vue components
│   │   │   ├── __tests__/   # Component tests (9 test files)
│   │   │   ├── ChartCard.vue
│   │   │   ├── CycleTimeScatter.vue
│   │   │   ├── DefectDistribution.vue
│   │   │   ├── DefectRateTrend.vue
│   │   │   ├── FiltersSidebar.vue
│   │   │   ├── MachineComparison.vue
│   │   │   ├── MachineDefectHeatmap.vue
│   │   │   └── TopDefects.vue
│   │   ├── views/
│   │   │   └── Dashboard.vue
│   │   ├── services/
│   │   │   └── analytics.ts  # API client
│   │   ├── stores/
│   │   │   ├── filters.ts    # Filter state management
│   │   │   └── preferences.ts
│   │   ├── types/
│   │   │   └── analytics.ts  # TypeScript interfaces
│   │   ├── router/
│   │   │   └── index.ts
│   │   ├── test/
│   │   │   ├── setup.ts
│   │   │   ├── mocks/
│   │   │   └── utils.spec.ts
│   │   ├── App.vue
│   │   └── main.ts
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/
│   │   │       └── analytics.py  # Analytics API endpoints
│   │   ├── models/          # SQLAlchemy models
│   │   │   ├── product.py
│   │   │   ├── machine_state.py
│   │   │   └── defect.py
│   │   ├── schemas/         # Pydantic schemas
│   │   │   └── analytics.py
│   │   ├── workflows/       # Temporal workflows
│   │   │   ├── ingestion.py
│   │   │   └── activities.py
│   │   ├── services/
│   │   │   └── s3_service.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── logging.py
│   │   └── main.py
│   ├── tests/               # Backend test suite (50 tests)
│   │   ├── conftest.py      # Test fixtures
│   │   ├── test_models.py
│   │   ├── test_api_analytics.py
│   │   ├── test_activities.py
│   │   └── test_s3_service.py
│   ├── alembic/             # Database migrations
│   │   ├── env.py
│   │   └── versions/
│   ├── scripts/
│   │   └── init-db.sh
│   ├── seed_cli.py          # CLI for data ingestion
│   ├── worker.py            # Temporal worker
│   ├── run_tests.sh
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-test.txt
│   └── requirements-dev.txt
│
├── docker-compose.yml       # Service orchestration
├── setup.sh                 # Automated setup script
├── seed.sh                  # Data ingestion script
├── test-docker.sh           # Docker-based test runner
├── .gitignore
└── README.md
```

## Development

### Database Migrations

Create a new migration:

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback migration:

```bash
alembic downgrade -1
```

### Adding New Analytics Endpoints

1. **Define the endpoint** in `backend/app/api/v1/analytics.py`:

```python
@router.get("/new-metric")
async def get_new_metric(db: Session = Depends(get_db)):
    # Query logic here
    return {"data": results}
```

2. **Add frontend service method** in `frontend/src/services/api.ts`:

```typescript
export const getNewMetric = async () => {
  const response = await api.get('/analytics/new-metric');
  return response.data;
};
```

3. **Create chart component** in `frontend/src/components/charts/`:

```vue
<script setup lang="ts">
// Chart implementation
</script>
```

4. **Add tests** for both backend and frontend


### Logging

Application logs are available:

```bash
# View backend logs
docker-compose logs -f backend

# View worker logs
docker-compose logs -f worker

# View all logs
docker-compose logs -f
```

## Deployment

### Production Deployment Architecture

For production deployment:

```
┌──────────────────┐
│   CloudFront     │  ◄── CDN for frontend assets
└────────┬─────────┘
         │
┌────────▼─────────┐
│   S3 Bucket      │  ◄── Static frontend hosting
└──────────────────┘

┌──────────────────┐
│  Application     │
│  Load Balancer   │  ◄── HTTPS termination
└────────┬─────────┘
         │
┌────────▼─────────┐
│   ECS Fargate    │  ◄── Backend API containers
│   Auto Scaling   │
└────────┬─────────┘
         │
┌────────▼─────────┐
│   RDS            │  ◄── Managed PostgreSQL
│   PostgreSQL     │
└──────────────────┘

┌──────────────────┐
│   Temporal       │  ◄── Temporal Cloud or self-hosted
│   Cloud          │
└──────────────────┘

┌──────────────────┐
│   S3 Bucket      │  ◄── Dataset storage
└──────────────────┘
```

### Environment Variables

**Backend (.env):**

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/krevera

# AWS/S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=krevera-datasets
S3_ENDPOINT_URL=  # Leave empty for AWS, set for LocalStack

# Temporal
TEMPORAL_HOST=temporal.example.com:7233

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Frontend (.env.production):**

```bash
VITE_API_URL=https://api.example.com
```

### Docker Production Build

Build production images:

```bash
# Backend
docker build -t krevera-backend:latest ./backend

# Frontend
docker build -t krevera-frontend:latest ./frontend
```

### Scaling Considerations

- **API**: Horizontal scaling with load balancer
- **Workers**: Scale Temporal workers based on ingestion volume
- **Database**: Use read replicas for analytics queries
- **Storage**: S3 auto-scales, consider lifecycle policies for old datasets

## Troubleshooting

### Common Issues

**Option 1: Git Bash**

If you're on Windows and bash scripts won't run:
```bash
# Install Git for Windows (includes Git Bash)
# Run scripts with:
bash setup.sh
bash test-docker.sh
bash seed.sh <url>
```

**Option 2 - WSL2:**
```bash
# Install Windows Subsystem for Linux
wsl --install
# Then run scripts normally:
./setup.sh
./test-docker.sh
```

**Option 3 - PowerShell (Manual commands):**
```powershell
# Instead of ./setup.sh, run commands manually:
docker-compose up -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python seed_cli.py --url https://static.krevera.com/dataset.json

# Instead of ./test-docker.sh:
docker-compose exec -T backend pytest -v
```

**Setup script permission denied:**

```bash
# Make the script executable
chmod +x setup.sh
./setup.sh

# Or run with bash directly
bash setup.sh
```

**Docker services won't start:**

```bash
# Check Docker Desktop is running
docker ps

# Restart all services
docker-compose down
docker-compose up -d

# Check service logs
docker-compose logs
```

**Database connection errors:**

```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

**Frontend build errors:**

```bash
# Clear node modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Backend import errors:**

```bash
# Reinstall Python dependencies
cd backend
pip install -r requirements.txt --force-reinstall
```

**Temporal workflow failures:**

1. Check Temporal UI at http://localhost:8233
2. View workflow execution history
3. Check worker logs: `docker-compose logs worker`
4. Verify S3 connectivity: `docker-compose logs localstack`

### Port Conflicts

If ports are already in use:

```bash
# Check what's using a port
lsof -i :5173  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL

# Kill process or modify docker-compose.yml ports
```

### Performance Issues

**Slow queries:**

```sql
-- Check for missing indexes
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public';

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM products WHERE molding_machine_id = 'machine-1';
```

**Large dataset ingestion:**

- Increase worker memory in docker-compose.yml
- Batch size tuning in `backend/app/workflows/activities.py`
- Consider partitioning `products` table by date

### Getting Help

- Check logs: `docker-compose logs [service]`
- Review Temporal UI for workflow status
- Verify API health: `curl http://localhost:8000/health`
- Frontend console: Open browser DevTools

## License

MIT License - see LICENSE file for details

---

For questions or issues, please open an issue in the repository.