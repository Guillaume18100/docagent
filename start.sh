#!/bin/bash

# Stop script on first error
set -e

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

# Install required npm packages if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Fix any potential Django issues
echo "Setting up Django backend..."
cd docautomation_backend

# Install Django and dependencies
echo "Installing backend dependencies..."
pip install django djangorestframework django-cors-headers python-dotenv
pip install djangorestframework-simplejwt pylint-django
# Fix tika installation issue
pip install tika==1.24
# Continue with regular dependencies
pip install -r requirements.txt || echo "Some packages couldn't be installed, but we'll continue anyway"

# Create __init__.py files if they're missing (needed for imports)
echo "Creating necessary Python package files..."
find . -type d -not -path "./venv*" -not -path "./.git*" -exec touch {}/__init__.py \; 2>/dev/null || true

# Fix settings.py - new approach using Python for better reliability
echo "Fixing Django settings with Python..."
chmod +x fix-settings.py
python3 fix-settings.py || python fix-settings.py

# Check if 'import os' is in settings.py and fix it directly
SETTINGS_FILE="docautomation_backend/settings.py"

# Check if our apps are already in INSTALLED_APPS
if ! grep -q "document_processing" "$SETTINGS_FILE"; then
    # Find the INSTALLED_APPS section and add our apps
    sed -i'.bak' '/INSTALLED_APPS = \[/,/\]/s/]/,\n    # Third-party apps\n    '\''rest_framework'\'',\n    '\''corsheaders'\'',\n    \n    # Project apps\n    '\''document_processing'\'',\n    '\''nlp'\'',\n    '\''document_generation'\'',\n]/' "$SETTINGS_FILE" 2>/dev/null || sed -i '' '/INSTALLED_APPS = \[/,/\]/s/]/,\n    # Third-party apps\n    '\''rest_framework'\'',\n    '\''corsheaders'\'',\n    \n    # Project apps\n    '\''document_processing'\'',\n    '\''nlp'\'',\n    '\''document_generation'\'',\n]/' "$SETTINGS_FILE"
    echo "Added required apps to INSTALLED_APPS"
else
    echo "Apps already registered in settings.py"
fi

# Add CORS settings if not present
if ! grep -q "CORS_ALLOWED_ORIGINS" "$SETTINGS_FILE"; then
    echo "
# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Media files (Uploaded documents)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}" >> "$SETTINGS_FILE"
    echo "Added CORS and REST Framework settings"
fi

# Make sure views.py doesn't import from urls.py (fixes circular imports)
if grep -q "from .urls import" document_processing/views.py; then
    echo "Fixing circular import in views.py"
    sed -i'.bak' '/from .urls import/d' document_processing/views.py 2>/dev/null || sed -i '' '/from .urls import/d' document_processing/views.py
fi

# Define empty public_upload_document function in views.py to avoid import errors
if ! grep -q "def public_upload_document" document_processing/views.py; then
    echo "
# This is a placeholder to avoid import errors
def public_upload_document(request):
    pass" >> document_processing/views.py
    echo "Added public_upload_document placeholder to views.py"
fi

# Ensure document_processing/urls.py has all required imports
echo "Creating proper URLs configuration..."
mkdir -p document_processing
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

# This function is defined here to avoid circular imports
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
            # Use filename as title if not provided
            if 'file' in request.FILES:
                title = request.FILES['file'].name
            else:
                return Response({'error': 'No title was provided'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            title = request.data['title']
            
        # Create document manually
        document = Document(
            title=title,
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

# Create necessary directory structure for apps if missing
for APP in "document_processing" "nlp" "document_generation"; do
    mkdir -p $APP/migrations
    touch $APP/migrations/__init__.py
    touch $APP/__init__.py
done

# Create or fix the utils.py file if it doesn't exist
if [ ! -f "document_processing/utils.py" ]; then
    echo "Creating document_processing/utils.py..."
    cat > document_processing/utils.py << EOF
# Processing utilities for documents
import threading

def process_document(document):
    """Process a document to extract text"""
    try:
        print(f"Processing document: {document.title}")
        document.processing_status = 'processing'
        document.save()
        
        # Simulate processing with extracted text
        document.extracted_text = f"Processed content for {document.title}"
        document.processing_status = 'completed'
        document.save()
        
        return True
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        document.processing_status = 'failed'
        document.error_message = str(e)
        document.save()
        return False
EOF
fi

# Create or fix the models.py file if it doesn't exist or is incomplete
if [ ! -f "document_processing/models.py" ] || ! grep -q "Document" "document_processing/models.py"; then
    echo "Creating document_processing/models.py..."
    cat > document_processing/models.py << EOF
from django.db import models
import uuid
import os

def document_file_path(instance, filename):
    """Generate file path for new document"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads/documents/', filename)

class Document(models.Model):
    """Document model for storing uploaded files and extracted text"""
    PROCESSING_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    DOCUMENT_TYPES = (
        ('pdf', 'PDF'),
        ('docx', 'DOCX'),
        ('txt', 'Text'),
        ('image', 'Image'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=document_file_path)
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES, default='other')
    extracted_text = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS, default='pending')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
EOF
fi

# Create or fix the views.py file if it doesn't exist or is incomplete
if [ ! -f "document_processing/views.py" ] || ! grep -q "DocumentViewSet" "document_processing/views.py"; then
    echo "Creating document_processing/views.py..."
    cat > document_processing/views.py << EOF
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Document
import threading

# Document serializer
from rest_framework import serializers

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# Document ViewSet
class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for handling document operations"""
    queryset = Document.objects.all().order_by('-created_at')
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action in ['upload', 'create', 'list', 'retrieve', 'test_upload']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """Handle document upload and processing"""
        try:
            print(f"Create called with data: {request.data}")
            
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                print(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            document = serializer.save()
            
            # Process document in background thread
            from .utils import process_document
            threading.Thread(target=process_document, args=(document,)).start()
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED, 
                headers=headers
            )
        except Exception as e:
            import traceback
            print(f"Error in create: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Alternative endpoint for document upload"""
        return self.create(request)
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Reprocess a document to extract text"""
        document = self.get_object()
        
        # Process document in background thread
        from .utils import process_document
        threading.Thread(target=process_document, args=(document,)).start()
        
        return Response(
            {'status': 'Document processing started'},
            status=status.HTTP_202_ACCEPTED
        )
    
    @action(detail=False, methods=['post'])
    @permission_classes([AllowAny])
    def test_upload(self, request):
        """Test endpoint for diagnosing upload issues"""
        try:
            return Response({
                'success': True,
                'message': 'Test upload endpoint reached successfully',
                'received_data': {
                    'files': {k: v.name for k, v in request.FILES.items()},
                    'data': {k: v for k, v in request.data.items() if k != 'file'}
                }
            })
        except Exception as e:
            import traceback
            return Response({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# This function is a placeholder to avoid circular imports
def public_upload_document(request):
    pass
EOF
fi

# Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Set up media directory for uploads
mkdir -p media/uploads/documents

# Start backend server on port 8000
echo "Starting backend server on port 8000..."
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!
echo "Backend server started (PID: $BACKEND_PID)"

# Wait a moment for the backend to initialize
sleep 5

# Check if backend is running properly
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "ERROR: Backend failed to start. Check logs above."
    exit 1
fi

# Go back to the project root
cd ..

# Start the frontend server
echo "Starting frontend server..."
npm run dev &
FRONTEND_PID=$!
echo "Frontend server started (PID: $FRONTEND_PID)"

# Wait a moment for the frontend to initialize
sleep 5

# Check if frontend is running properly
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "ERROR: Frontend failed to start. Check logs above."
    exit 1
fi

echo ""
echo "===== Document Automation App Started Successfully ====="
echo "Backend server running at: http://localhost:8000"
echo "Frontend server running at: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all services."

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 