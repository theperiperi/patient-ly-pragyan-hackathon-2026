#!/bin/bash
# Quick start script for ABDM Local Development Kit

set -e

echo "=============================================="
echo "ABDM Local Development Kit - Quick Start"
echo "=============================================="
echo ""

# Check if .env exists, if not create from example
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. You can customize it if needed."
    echo ""
fi

# Check Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "🐳 Docker is running"
echo ""

# Build and start services
echo "🏗️  Building and starting all services..."
echo "   This may take a few minutes on first run..."
echo ""

docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to be healthy..."
echo ""

# Wait for services to be healthy
MAX_WAIT=120
ELAPSED=0
INTERVAL=5

while [ $ELAPSED -lt $MAX_WAIT ]; do
    HEALTHY=0
    TOTAL=6  # Gateway, CM, HIP, HIU, Validator, MongoDB

    # Check each service
    if docker-compose ps | grep -q "abdm-gateway.*healthy"; then
        ((HEALTHY++))
    fi
    if docker-compose ps | grep -q "abdm-consent-manager.*healthy"; then
        ((HEALTHY++))
    fi
    if docker-compose ps | grep -q "abdm-hip.*healthy"; then
        ((HEALTHY++))
    fi
    if docker-compose ps | grep -q "abdm-hiu.*healthy"; then
        ((HEALTHY++))
    fi
    if docker-compose ps | grep -q "abdm-fhir-validator.*healthy"; then
        ((HEALTHY++))
    fi
    if docker-compose ps | grep -q "abdm-mongodb.*healthy"; then
        ((HEALTHY++))
    fi

    echo "   Services healthy: $HEALTHY/$TOTAL"

    if [ $HEALTHY -eq $TOTAL ]; then
        break
    fi

    sleep $INTERVAL
    ((ELAPSED += INTERVAL))
done

echo ""

if [ $HEALTHY -eq $TOTAL ]; then
    echo "✅ All services are running and healthy!"
    echo ""
    echo "=============================================="
    echo "ABDM Local Dev Kit is ready!"
    echo "=============================================="
    echo ""
    echo "📚 Service URLs:"
    echo "   Gateway:           http://localhost:8090"
    echo "   Consent Manager:   http://localhost:8091"
    echo "   HIP:              http://localhost:8092"
    echo "   HIU:              http://localhost:8093"
    echo "   FHIR Validator:   http://localhost:8094"
    echo "   Swagger UI:       http://localhost:8080"
    echo "   MongoDB:          mongodb://localhost:27017"
    echo ""
    echo "🔑 Demo Credentials:"
    echo "   Client ID:     sandbox-client"
    echo "   Client Secret: sandbox-secret"
    echo ""
    echo "🚀 Quick Test:"
    echo "   curl http://localhost:8090/health"
    echo ""
    echo "📖 Documentation:"
    echo "   See docs/getting-started/ for tutorials"
    echo ""
    echo "🛑 To stop all services:"
    echo "   docker-compose down"
    echo ""
else
    echo "⚠️  Some services did not become healthy within ${MAX_WAIT}s"
    echo ""
    echo "Check service logs:"
    echo "   docker-compose logs gateway"
    echo "   docker-compose logs consent-manager"
    echo "   docker-compose logs hip"
    echo "   docker-compose logs hiu"
    echo "   docker-compose logs fhir-validator"
    echo "   docker-compose logs mongodb"
    echo ""
fi
