#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Starting DocAgent in Production Mode${NC}"

# Check if Python virtual environment exists
if [ ! -d "docautomation_backend/venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Running setup first...${NC}"
    ./setup.sh
fi

# Build frontend
echo -e "${GREEN}Building frontend...${NC}"
cd src
npm run build
BUILD_EXIT_CODE=$?
cd ..

if [ $BUILD_EXIT_CODE -ne 0 ]; then
    echo -e "${RED}Frontend build failed. Please check the logs.${NC}"
    exit 1
fi

echo -e "${GREEN}Frontend build successful.${NC}"

# Collect static files
echo -e "${GREEN}Collecting static files...${NC}"
cd docautomation_backend
source venv/bin/activate
python manage.py collectstatic --noinput
COLLECTSTATIC_EXIT_CODE=$?

if [ $COLLECTSTATIC_EXIT_CODE -ne 0 ]; then
    echo -e "${RED}Static file collection failed. Please check the logs.${NC}"
    exit 1
fi

# Start backend using gunicorn
echo -e "${GREEN}Starting Django backend with Gunicorn...${NC}"
gunicorn docautomation_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120

echo -e "${GREEN}Server is running at http://localhost:8000${NC}" 