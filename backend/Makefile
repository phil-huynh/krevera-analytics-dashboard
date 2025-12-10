.PHONY: help setup start stop restart logs clean migrate seed test status

help:
	@echo "Krevera Manufacturing Analytics - Available Commands"
	@echo "===================================================="
	@echo ""
	@echo "  make setup     - Full setup (build, start, migrate)"
	@echo "  make start     - Start all services"
	@echo "  make stop      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - View logs (all services)"
	@echo "  make clean     - Remove containers and volumes"
	@echo "  make migrate   - Run database migrations manually"
	@echo "  make seed      - Seed database (requires DATASET_URL)"
	@echo "  make test      - Run tests"
	@echo "  make status    - Show service status"
	@echo ""

setup: clean
	@./setup.sh

start:
	@docker-compose up -d
	@make status

stop:
	@docker-compose down

restart:
	@docker-compose restart
	@make status

logs:
	@docker-compose logs -f

clean:
	@docker-compose down -v
	@echo "🧹 Cleaned up containers and volumes"

migrate:
	@docker-compose exec backend alembic upgrade head
	@echo "✅ Migrations applied"

seed:
	@if [ -z "$(DATASET_URL)" ]; then \
		echo "❌ Error: DATASET_URL not set"; \
		echo "Usage: make seed DATASET_URL=https://your-dataset-url.json"; \
		exit 1; \
	fi
	@docker-compose exec backend python seed_cli.py --url $(DATASET_URL)
	@echo "✅ Database seeded"

test:
	@docker-compose exec backend pytest --cov=app
	@echo "✅ Tests complete"

status:
	@echo ""
	@echo "📊 Service Status:"
	@docker-compose ps
	@echo ""
	@echo "🌐 Application URLs:"
	@echo "   Frontend:    http://localhost:5173"
	@echo "   Backend API: http://localhost:8000/docs"
	@echo "   Health:      http://localhost:8000/health"
	@echo ""