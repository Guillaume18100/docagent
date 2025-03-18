#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Starting DocAgent in Development Mode${NC}"

# Check if Python virtual environment exists
if [ ! -d "docautomation_backend/venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Running setup first...${NC}"
    ./setup.sh
fi

# Function to handle cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup INT TERM

# Start backend server
echo -e "${GREEN}Starting Django backend server...${NC}"
cd docautomation_backend
source venv/bin/activate
python manage.py runserver 8000 &
BACKEND_PID=$!
cd ..

# Check if backend started successfully
sleep 2
if ! ps -p $BACKEND_PID > /dev/null; then
    echo -e "${RED}Failed to start backend server. Check logs for details.${NC}"
    exit 1
fi

echo -e "${GREEN}Backend running at http://localhost:8000${NC}"
echo -e "${GREEN}API available at http://localhost:8000/api${NC}"
echo -e "${GREEN}Admin interface available at http://localhost:8000/admin${NC}"

# Start frontend server
echo -e "${GREEN}Starting frontend development server...${NC}"
cd src
npm run dev &
FRONTEND_PID=$!
cd ..

# Check if frontend started successfully
sleep 5
if ! ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${RED}Failed to start frontend server. Check logs for details.${NC}"
    kill $BACKEND_PID
    exit 1
fi

echo -e "${GREEN}Frontend running at http://localhost:5173${NC}"

# Keep script running
echo -e "${BLUE}Both servers are running. Press Ctrl+C to stop.${NC}"
wait $BACKEND_PID $FRONTEND_PID 