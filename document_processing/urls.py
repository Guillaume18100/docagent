from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, public_upload_document
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import Document
from .utils import process_document
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