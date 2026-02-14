#!/bin/bash
# Reset ABDM Local Dev Kit to clean state

set -e

echo "=============================================="
echo "ABDM Local Dev Kit - Data Reset"
echo "=============================================="
echo ""

# Confirm with user
read -p "⚠️  This will delete all data in MongoDB. Continue? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Reset cancelled."
    exit 1
fi

echo ""
echo "🛑 Stopping all services..."
docker-compose down

echo ""
echo "🗑️  Removing MongoDB volume..."
docker volume rm abdm-local-dev-kit_mongodb_data 2>/dev/null || echo "   Volume already removed or doesn't exist"

echo ""
echo "🚀 Starting services with fresh database..."
docker-compose up -d

echo ""
echo "⏳ Waiting for MongoDB to initialize..."
sleep 10

echo ""
echo "✅ Reset complete!"
echo ""
echo "The database has been reset to clean state."
echo "Demo client credentials are available:"
echo "   Client ID:     sandbox-client"
echo "   Client Secret: sandbox-secret"
echo ""
echo "To seed with sample data, run:"
echo "   python data/generators/seed_database.py"
echo ""
