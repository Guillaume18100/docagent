#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Setting up DocAgent project...${NC}"

# Backend Setup
echo -e "\n${GREEN}Setting up backend...${NC}"
cd docautomation_backend

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r ../requirements.txt

# Run migrations
echo "Running migrations..."
python manage.py makemigrations document_processing
python manage.py makemigrations nlp
python manage.py makemigrations document_generation
python manage.py migrate

# Create a superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')"

# Initialize sample data
echo "Initializing sample data..."
python manage.py initialize_data

cd ..

# Frontend Setup
echo -e "\n${GREEN}Setting up frontend...${NC}"
cd src

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the project
echo "Building the project..."
npm run build

cd ..

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "To start the development servers:"
echo -e "1. Backend: cd docautomation_backend && source venv/bin/activate && python manage.py runserver"
echo -e "2. Frontend: cd src && npm run dev" 