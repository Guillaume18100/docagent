#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Starting DocAgent with Docker${NC}"

# Check if docker is installed and running
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed or not in PATH. Please install Docker and try again.${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}docker-compose is not installed or not in PATH. Please install docker-compose and try again.${NC}"
    exit 1
fi

# Start Docker containers
echo -e "${GREEN}Starting Docker containers...${NC}"
docker-compose up -d --build

# Check if containers are running
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to start containers. See error above.${NC}"
    exit 1
fi

# Wait for backend container to be ready
echo -e "${GREEN}All containers running successfully!${NC}"
echo -e "${GREEN}Frontend: http://localhost:8080${NC}"
echo -e "${GREEN}Backend API: http://localhost:8000/api${NC}"
echo -e "${GREEN}Admin interface: http://localhost:8000/admin${NC}"

# Install NLP dependencies in the backend container
echo -e "${GREEN}Installing NLP dependencies in backend container...${NC}"
docker exec docagent-backend-1 pip install nltk transformers
docker exec docagent-backend-1 python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Apply migrations
echo -e "${GREEN}Applying database migrations...${NC}"
docker exec docagent-backend-1 python manage.py migrate

echo -e "${GREEN}Waiting for services to fully initialize...${NC}"
sleep 5

# Open browser
echo -e "${GREEN}Opening browser...${NC}"
# Check the operating system and open browser accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - Try multiple browsers
    open "http://localhost:8080" || open -a "Safari" "http://localhost:8080" || open -a "Google Chrome" "http://localhost:8080" || open -a "Firefox" "http://localhost:8080" || echo -e "${YELLOW}Unable to open browser automatically. Please navigate to http://localhost:8080 manually.${NC}"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "http://localhost:8080" &>/dev/null || sensible-browser "http://localhost:8080" &>/dev/null || x-www-browser "http://localhost:8080" &>/dev/null || echo -e "${YELLOW}Unable to automatically open browser. Please navigate to http://localhost:8080 manually.${NC}"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    start "http://localhost:8080"
else
    echo -e "${YELLOW}Unable to automatically open browser. Please navigate to http://localhost:8080 manually.${NC}"
fi

echo -e "${GREEN}Services are now running. Use 'docker-compose down' to stop.${NC}" 