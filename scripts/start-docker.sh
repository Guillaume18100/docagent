#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Starting DocAgent with Docker${NC}"

# Start Docker containers
echo -e "${GREEN}Starting Docker containers...${NC}"
docker-compose up -d

# Check if containers started successfully
sleep 3
if [ "$(docker-compose ps --services --filter 'status=running' | wc -l)" -ne 3 ]; then
    echo -e "${RED}Failed to start all containers. Check logs with 'docker-compose logs'${NC}"
    echo -e "${YELLOW}Shutting down containers...${NC}"
    docker-compose down
    exit 1
fi

# Print status information
echo -e "${GREEN}All containers running successfully!${NC}"
echo -e "${GREEN}Frontend: http://localhost:8080${NC}"
echo -e "${GREEN}Backend API: http://localhost:8000/api${NC}"
echo -e "${GREEN}Admin interface: http://localhost:8000/admin${NC}"

# Wait for services to fully initialize
echo -e "${YELLOW}Waiting for services to fully initialize...${NC}"
sleep 5

# Open browser
echo -e "${BLUE}Opening browser...${NC}"

# Check the operating system and open browser accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "http://localhost:8080/"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "http://localhost:8080/" &>/dev/null || sensible-browser "http://localhost:8080/" &>/dev/null || x-www-browser "http://localhost:8080/" &>/dev/null || echo -e "${YELLOW}Unable to automatically open browser. Please navigate to http://localhost:8080/ manually.${NC}"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    start "http://localhost:8080/"
else
    echo -e "${YELLOW}Unable to automatically open browser. Please navigate to http://localhost:8080/ manually.${NC}"
fi

echo -e "${BLUE}Services are now running. Use 'docker-compose down' to stop.${NC}" 