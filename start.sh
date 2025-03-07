#!/bin/bash

# Function to handle cleanup when script exits
cleanup() {
    echo "Shutting down services..."
    pkill -f "python manage.py runserver" || true
    pkill -f "npm run dev" || true
    exit 0
}

# Trap ctrl-c and call cleanup
trap cleanup SIGINT SIGTERM EXIT

echo "===== Starting Document Automation Application ====="

# Ensure we're in the project root directory
cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv || python -m venv .venv || echo "Failed to create virtual environment. Please install Python 3.8+ and try again."
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
else
    echo "Warning: Could not find virtual environment activation script. Continuing without it..."
fi

# Install required npm packages if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install || echo "Warning: Failed to install some npm packages. The frontend may not work correctly."
fi

# Fix any potential Django issues
echo "Setting up Django backend..."
cd docautomation_backend || { echo "Error: docautomation_backend directory not found!"; exit 1; }

# Install Django and dependencies
echo "Installing backend dependencies..."
pip install --upgrade pip || echo "Warning: Failed to upgrade pip. Continuing with existing version."
pip install django djangorestframework django-cors-headers python-dotenv || echo "Warning: Failed to install Django core packages."
pip install djangorestframework-simplejwt pylint-django || echo "Warning: Failed to install JWT authentication packages."

# Install document processing dependencies
echo "Installing document processing dependencies..."
pip install tika==1.24 pytesseract pdf2image python-docx PyPDF2 Pillow || echo "Warning: Some document processing packages couldn't be installed."

# Install AI dependencies
echo "Installing AI dependencies..."
pip install transformers torch gpt4all || echo "Warning: AI packages couldn't be installed. AI features will be disabled."

# Continue with regular dependencies
echo "Installing remaining dependencies..."
pip install -r requirements.txt || echo "Warning: Some packages couldn't be installed, but we'll continue anyway."

# Create __init__.py files if they're missing (needed for imports)
echo "Creating necessary Python package files..."
find . -type d -not -path "./venv*" -not -path "./.git*" -exec touch {}/__init__.py \; 2>/dev/null || true

# Fix settings.py - new approach using Python for better reliability
echo "Fixing Django settings with Python..."
if [ -f "fix-settings.py" ]; then
    chmod +x fix-settings.py
    python fix-settings.py || echo "Warning: Failed to fix settings.py with Python script."
else
    echo "Warning: fix-settings.py not found. Settings may not be configured correctly."
fi

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate || echo "Warning: Failed to apply migrations. The database may not be set up correctly."

# Start the Django server in the background
echo "Starting Django backend server..."
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Wait a moment for Django to start
sleep 3

# Check if Django server is running
if ps -p $DJANGO_PID > /dev/null; then
    echo "Django server started successfully!"
else
    echo "Warning: Django server failed to start. Check for errors above."
fi

# Go back to project root and start the frontend
cd ..
echo "Starting frontend development server..."
cd src || { echo "Error: src directory not found!"; exit 1; }
npm run dev &
FRONTEND_PID=$!

# Wait a moment for the frontend to start
sleep 3

# Check if frontend server is running
if ps -p $FRONTEND_PID > /dev/null; then
    echo "Frontend server started successfully!"
else
    echo "Warning: Frontend server failed to start. Check for errors above."
fi

echo "===== Setup Complete ====="
echo "Backend running at: http://localhost:8000"
echo "Frontend running at: http://localhost:8080 (or another port if 8080 is in use)"
echo "Press Ctrl+C to stop all services"

# Keep the script running
wait 