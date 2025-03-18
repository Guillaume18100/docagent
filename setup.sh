#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Setting up Document Automation Environment${NC}"

# Create backend virtual environment
echo -e "${GREEN}Setting up backend...${NC}"
cd docautomation_backend

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install NLP dependencies
echo "Installing NLP dependencies..."
pip install nltk transformers

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate

# Deactivate virtual environment
deactivate

cd ..

# Setup frontend
echo -e "${GREEN}Setting up frontend...${NC}"
cd src

# Check if Node.js is installed
if ! command -v npm &> /dev/null; then
    echo -e "${YELLOW}Node.js/npm is not installed. Skipping frontend setup.${NC}"
    echo -e "${YELLOW}Please install Node.js and run 'npm install' in the src directory.${NC}"
    cd ..
    exit 0
fi

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

cd ..

echo -e "${GREEN}Setup complete! You can now run the application using:${NC}"
echo -e "${BLUE}make start${NC}" 