from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Document
from .serializers import (
    DocumentSerializer, 
    DocumentUploadSerializer,
    DocumentListSerializer,
    DocumentDetailSerializer
)
from .utils import process_document
import threading

class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for handling document operations"""
    queryset = Document.objects.all().order_by('-created_at')
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_permissions(self):
        """Return appropriate permissions based on action"""
        # Allow anyone to upload, list, or retrieve documents
        if self.action in ['upload', 'create', 'list', 'retrieve', 'test_upload']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return DocumentListSerializer
        elif self.action == 'retrieve':
            return DocumentDetailSerializer
        elif self.action == 'create' or self.action == 'upload':
            return DocumentUploadSerializer
        return DocumentSerializer
    
    def create(self, request, *args, **kwargs):
        """Handle document upload and processing"""
        try:
            print(f"Create called with data: {request.data}")
            print(f"Files: {request.FILES}")
            
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                print(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            document = serializer.save()
            
            # Process document in background thread
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
        try:
            print(f"Upload endpoint called with data: {request.data}")
            print(f"Files: {request.FILES}")
            return self.create(request)
        except Exception as e:
            import traceback
            print(f"Error in upload: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Reprocess a document to extract text"""
        document = self.get_object()
        
        # Process document in background thread
        threading.Thread(target=process_document, args=(document,)).start()
        
        return Response(
            {'status': 'Document processing started'},
            status=status.HTTP_202_ACCEPTED
        )
    
    @action(detail=True, methods=['get'])
    def extracted_text(self, request, pk=None):
        """Get only the extracted text from a document"""
        document = self.get_object()
        return Response({
            'id': document.id,
            'title': document.title,
            'extracted_text': document.extracted_text,
            'processing_status': document.processing_status
        })
        
    @action(detail=False, methods=['post'])
    @permission_classes([AllowAny])
    def test_upload(self, request):
        """Test endpoint for diagnosing upload issues"""
        try:
            # Log request details
            print("Received test upload request")
            print(f"Content-Type: {request.content_type}")
            print(f"Method: {request.method}")
            print(f"FILES: {request.FILES}")
            print(f"Data: {request.data}")
            
            # Return success response
            return Response({
                'success': True,
                'message': 'Test upload endpoint reached successfully',
                'received_data': {
                    'files': {k: v.name for k, v in request.FILES.items()},
                    'data': {k: v for k, v in request.data.items() if k != 'file'}
                }
            })
        except Exception as e:
            # Return detailed error information
            import traceback
            return Response({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Export this empty function to avoid import error, the actual implementation is in urls.py
def public_upload_document(request):
    pass 