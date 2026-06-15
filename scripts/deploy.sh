#!/bin/bash
# deploy.sh - Deployment pipeline step script

echo "🚢 Starting deployment..."
docker-compose -f docker/docker-compose.yml up --build -d
echo "✅ Deployment complete!"
