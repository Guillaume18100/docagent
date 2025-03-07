#!/bin/bash

echo "=== Fixing dependency and import issues ==="

# Navigate to project root
cd "$(dirname "$0")"

# Install all required dependencies globally and in the virtual environment
echo "Installing dependencies..."
pip install django==4.2.0 djangorestframework==3.14.0 django-cors-headers==4.0.0 python-dotenv==1.0.0
pip install djangorestframework-simplejwt==5.2.2 pylint-django==2.5.3

# Set up environment for the docautomation_backend
cd docautomation_backend

# Create/activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install all the required packages in the virtual environment
echo "Installing packages in virtual environment..."
pip install -r requirements.txt
pip install djangorestframework-simplejwt==5.2.2 pylint-django==2.5.3

# Create missing __init__.py files to make modules importable
echo "Creating missing __init__.py files..."
find . -type d -not -path "./venv*" -not -path "./.git*" -exec touch {}/__init__.py \;

# Make sure docautomation_backend is a proper package
touch __init__.py

# Export PYTHONPATH to include the current directory
export PYTHONPATH=$PYTHONPATH:$(pwd)
echo "export PYTHONPATH=$PYTHONPATH:$(pwd)" >> ~/.bashrc
echo "export PYTHONPATH=$PYTHONPATH:$(pwd)" >> ~/.zshrc

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DEBUG=True
SECRET_KEY=django-insecure-development-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
EOF
fi

# Fix document_processing/urls.py
echo "Fixing document_processing/urls.py..."
cat > document_processing/urls.py << EOF
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import Document
from .utils import process_document
from .views import DocumentViewSet
import threading

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def public_upload_document(request):
    """Public endpoint for document upload"""
    try:
        print("Public upload endpoint called")
        print(f"Content-Type: {request.content_type}")
        print(f"Method: {request.method}")
        print(f"FILES: {request.FILES}")
        print(f"Data: {request.data}")
        
        if 'file' not in request.FILES:
            return Response({'error': 'No file was provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        if 'title' not in request.data:
            return Response({'error': 'No title was provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Create document manually
        document = Document(
            title=request.data['title'],
            file=request.FILES['file']
        )
        document.save()
        
        # Process document in background thread
        threading.Thread(target=process_document, args=(document,)).start()
        
        return Response({
            'id': document.id,
            'title': document.title,
            'success': True,
            'message': 'Document uploaded successfully',
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        print(f"Error in public upload: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

router = DefaultRouter()
router.register('', DocumentViewSet, basename='document')

urlpatterns = [
    # Public direct upload endpoint
    path('public-upload/', public_upload_document, name='public-document-upload'),
    
    # Direct access to the upload endpoint
    path('upload/', DocumentViewSet.as_view({'post': 'upload'}), name='document-upload-direct'),
    
    # Test upload endpoint
    path('test-upload/', DocumentViewSet.as_view({'post': 'test_upload'}), name='document-test-upload'),
    
    # Default router URLs
    path('', include(router.urls)),
]
EOF

# Fix document_processing/views.py to avoid circular imports
echo "Fixing document_processing/views.py..."
sed -i'.bak' '/^from .urls import/d' document_processing/views.py 2>/dev/null || sed -i '' '/^from .urls import/d' document_processing/views.py

echo ""
echo "=== Fix completed ==="
echo "1. All dependencies have been installed"
echo "2. All __init__.py files have been created"
echo "3. PYTHONPATH has been updated"
echo "4. Fixed circular imports in document_processing"
echo ""
echo "Please restart your editor and terminal for changes to take effect."
echo "Then run: python manage.py runserver" 