#!/bin/bash

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

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

# Run the server
echo "Starting the server..."
python manage.py runserver 