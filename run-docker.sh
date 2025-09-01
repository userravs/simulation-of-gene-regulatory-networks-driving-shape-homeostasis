#!/bin/bash

# Script to run the Gene Regulatory Network simulation in Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧬 Gene Regulatory Network Simulation${NC}"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data

# Build the image if it doesn't exist or if Dockerfile changed
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
docker-compose build

# Run the container
echo -e "${YELLOW}🚀 Starting container...${NC}"
echo -e "${GREEN}✅ Container is ready!${NC}"
echo ""
echo "Available commands:"
echo "  python examples/run_simulation.py    # Run basic simulation"
echo "  python examples/run_evolution.py    # Run genetic algorithm example"
echo "  python evolution/main_GA.py         # Run main GA application"
echo "  python core/main.py                 # Run visualization simulation"
echo ""
echo "To exit the container, type: exit"
echo ""

# Start interactive shell
docker-compose run --rm grn-simulation
