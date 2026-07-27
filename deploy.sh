#!/bin/bash
# Deployment script for AURA-KG

set -e

echo "🚀 Starting AURA-KG Deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Load production environment
if [ -f .env.production ]; then
    echo "📝 Loading production environment..."
    export $(cat .env.production | xargs)
fi

# Build the images
echo "🔨 Building Docker images..."
docker-compose build

# Start the services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check status
echo "📊 Checking service status..."
docker-compose ps

echo "✅ Deployment complete!"
echo "🌐 Frontend: http://localhost:8501"
echo "🔄 Neo4j Browser: http://localhost:7474"
