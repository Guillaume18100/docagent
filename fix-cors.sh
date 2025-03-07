#!/bin/bash

# Fix Document Upload CORS Issues - Script

echo "Fixing document upload CORS issues..."

# Stop any running backend server
pkill -f "python manage.py runserver" || true
echo "Stopped any running backend server."

# Navigate to the backend directory
cd docautomation_backend

# Make sure Django and dependencies are installed
source venv/bin/activate || python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install djangorestframework-simplejwt

# Apply migrations if needed
python manage.py migrate

# Create a superuser if it doesn't exist
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')"

# Initialize sample data
python manage.py initialize_data

# Start the backend server on port 8000
python manage.py runserver 0.0.0.0:8000 &

echo "Backend server started on port 8000 with CORS fixes applied."
echo "You can now upload documents from the frontend at http://localhost:8080"
echo ""
echo "IMPORTANT: If you still encounter CORS issues, try these steps:"
echo "1. Clear your browser cache and cookies"
echo "2. Use Chrome with CORS disabled (run Chrome with --disable-web-security flag)"
echo "3. Try the test upload endpoint at http://localhost:8000/api/documents/test-upload/"
echo "4. Check the backend console for detailed error logs" 