#!/bin/bash
set -e

# Check if URL provided
if [ -z "$1" ]; then
    echo "Usage: ./seed.sh <dataset-url>"
    echo ""
    echo "Example:"
    echo "  ./seed.sh https://static.krevera.com/dataset.json"
    exit 1
fi

DATASET_URL=$1

echo "🌱 Seeding database with dataset from:"
echo "   $DATASET_URL"
echo ""

# Run seed command
docker-compose exec backend python seed_cli.py --url "$DATASET_URL"
