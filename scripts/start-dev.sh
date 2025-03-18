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

# Get the actual port from Vite logs if possible, otherwise use default port
VITE_LOG=$(ps -p $FRONTEND_PID -o args= | grep -o "http://localhost:[0-9]*" || echo "http://localhost:8080")
if [[ $VITE_LOG == "" ]]; then
    FRONTEND_URL="http://localhost:8080/"
else
    FRONTEND_URL=$VITE_LOG/
fi

echo -e "${GREEN}Frontend running at $FRONTEND_URL${NC}"

# Open browser after a short delay to ensure servers are fully initialized
sleep 2
echo -e "${BLUE}Opening browser...${NC}"

# Check the operating system and open browser accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - Use -a flag to specify Safari if needed
    open "$FRONTEND_URL" || open -a "Safari" "$FRONTEND_URL" || echo -e "${YELLOW}Unable to open browser automatically. Please navigate to $FRONTEND_URL manually.${NC}"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "$FRONTEND_URL" &>/dev/null || sensible-browser "$FRONTEND_URL" &>/dev/null || x-www-browser "$FRONTEND_URL" &>/dev/null || echo -e "${YELLOW}Unable to automatically open browser. Please navigate to $FRONTEND_URL manually.${NC}"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    start "$FRONTEND_URL"
else
    echo -e "${YELLOW}Unable to automatically open browser. Please navigate to $FRONTEND_URL manually.${NC}"
fi

# Keep script running
echo -e "${BLUE}Both servers are running. Press Ctrl+C to stop.${NC}"
wait $BACKEND_PID $FRONTEND_PID 