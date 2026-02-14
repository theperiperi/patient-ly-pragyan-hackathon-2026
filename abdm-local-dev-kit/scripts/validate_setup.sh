#!/bin/bash
# Validate ABDM Local Dev Kit setup

set -e

echo "=============================================="
echo "ABDM Local Dev Kit - Setup Validation"
echo "=============================================="
echo ""

ERRORS=0

# Check Docker
echo "🐳 Checking Docker..."
if docker --version > /dev/null 2>&1; then
    DOCKER_VERSION=$(docker --version)
    echo "   ✅ $DOCKER_VERSION"
else
    echo "   ❌ Docker not found. Please install Docker Desktop."
    ((ERRORS++))
fi

# Check Docker Compose
echo "🐳 Checking Docker Compose..."
if docker-compose --version > /dev/null 2>&1; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo "   ✅ $COMPOSE_VERSION"
else
    echo "   ❌ Docker Compose not found. Please install Docker Compose."
    ((ERRORS++))
fi

# Check if Docker is running
echo "🐳 Checking Docker daemon..."
if docker info > /dev/null 2>&1; then
    echo "   ✅ Docker daemon is running"
else
    echo "   ❌ Docker daemon is not running. Please start Docker Desktop."
    ((ERRORS++))
fi

# Check required files
echo ""
echo "📁 Checking required files..."

REQUIRED_FILES=(
    "docker-compose.yml"
    ".env.example"
    "scripts/mongo-init.js"
    "services/gateway/main.py"
    "services/gateway/Dockerfile"
    "services/consent_manager/main.py"
    "services/consent_manager/Dockerfile"
    "services/hip/main.py"
    "services/hip/Dockerfile"
    "services/hiu/main.py"
    "services/hiu/Dockerfile"
    "services/fhir_validator/main.py"
    "services/fhir_validator/Dockerfile"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ Missing: $file"
        ((ERRORS++))
    fi
done

# Check FHIR profiles directory
echo ""
echo "📚 Checking FHIR profiles..."
if [ -d "fhir-profiles" ]; then
    PROFILE_COUNT=$(find fhir-profiles -type f -name "*.json" | wc -l)
    echo "   ✅ fhir-profiles/ exists ($PROFILE_COUNT JSON files)"
else
    echo "   ⚠️  fhir-profiles/ directory not found"
    echo "      This is optional but recommended for FHIR validation"
fi

# Check FHIR samples directory
echo ""
echo "📋 Checking FHIR samples..."
if [ -d "fhir-samples" ]; then
    SAMPLE_COUNT=$(find fhir-samples -type f -name "*.json" | wc -l)
    echo "   ✅ fhir-samples/ exists ($SAMPLE_COUNT JSON files)"
else
    echo "   ⚠️  fhir-samples/ directory not found"
    echo "      This is optional but recommended for testing"
fi

# Check .env file
echo ""
echo "🔧 Checking environment configuration..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
else
    echo "   ⚠️  .env file not found (will be created from .env.example on first run)"
fi

# Check port availability
echo ""
echo "🔌 Checking port availability..."

PORTS=(8080 8090 8091 8092 8093 8094 27017)
PORT_NAMES=("Swagger UI" "Gateway" "Consent Manager" "HIP" "HIU" "FHIR Validator" "MongoDB")

for i in "${!PORTS[@]}"; do
    PORT=${PORTS[$i]}
    NAME=${PORT_NAMES[$i]}

    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "   ⚠️  Port $PORT ($NAME) is already in use"
        echo "      Process: $(lsof -Pi :$PORT -sTCP:LISTEN | tail -n 1 | awk '{print $1}')"
    else
        echo "   ✅ Port $PORT ($NAME) is available"
    fi
done

# Summary
echo ""
echo "=============================================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ Validation passed! Your setup is ready."
    echo ""
    echo "Next steps:"
    echo "   1. Run: ./scripts/start.sh"
    echo "   2. Open: http://localhost:8080 (Swagger UI)"
    echo "   3. Read: docs/getting-started/"
else
    echo "❌ Validation failed with $ERRORS error(s)"
    echo ""
    echo "Please fix the errors above and run this script again."
fi
echo "=============================================="
echo ""
