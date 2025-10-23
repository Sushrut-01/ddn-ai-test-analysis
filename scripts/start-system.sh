#!/bin/bash

echo "========================================"
echo "DDN AI System Startup Script"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure your credentials"
    echo ""
    echo "Run: cp .env.example .env"
    exit 1
fi

echo "[1/5] Stopping any running containers..."
docker-compose down

echo ""
echo "[2/5] Building Docker images..."
docker-compose build

echo ""
echo "[3/5] Starting all services..."
docker-compose up -d

echo ""
echo "[4/5] Waiting for services to initialize (30 seconds)..."
sleep 30

echo ""
echo "[5/5] Checking service health..."
echo ""

curl -f http://localhost:5005/health && echo "Dashboard API: OK" || echo "Dashboard API: FAILED"
curl -f http://localhost:3000 && echo "Dashboard UI: OK" || echo "Dashboard UI: FAILED"
curl -f http://localhost:5678 && echo "n8n: OK" || echo "n8n: FAILED"
curl -f http://localhost:5000/health && echo "LangGraph: OK" || echo "LangGraph: FAILED"

echo ""
echo "========================================"
echo "System Started Successfully!"
echo "========================================"
echo ""
echo "Access points:"
echo "- Dashboard UI: http://localhost:3000"
echo "- Dashboard API: http://localhost:5005"
echo "- n8n Workflows: http://localhost:5678"
echo "- LangGraph Service: http://localhost:5000"
echo "- MongoDB: localhost:27017"
echo "- PostgreSQL: localhost:5432"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo "========================================"
