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
        if self.action in ['upload', 'create', 'list', 'retrieve', 'test_upload', 'preview', 'download', 'extracted_text']:
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

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        Get a preview of the document
        """
        print(f"Preview called for document ID: {pk}")
        document = self.get_object()
        
        # Return a basic preview with document details and first part of extracted text
        preview_text = ""
        if document.extracted_text:
            # Get the first 500 characters of text as preview
            preview_text = document.extracted_text[:500]
            if len(document.extracted_text) > 500:
                preview_text += "..."
                
        preview_data = {
            'id': document.id,
            'title': document.title,
            'document_type': document.document_type,
            'created_at': document.created_at,
            'status': document.processing_status,
            'preview_text': preview_text,
        }
        
        return Response(preview_data)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download the document file
        """
        import os
        from django.http import FileResponse, HttpResponse
        from django.conf import settings
        
        document = self.get_object()
        
        try:
            # Get the file path
            file_path = document.file.path
            
            # Check if file exists
            if not os.path.exists(file_path):
                return Response(
                    {'error': 'File not found on server'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Determine content type based on file extension
            content_type = 'application/octet-stream'  # Default
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                content_type = 'application/pdf'
            elif file_extension == '.docx':
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif file_extension == '.doc':
                content_type = 'application/msword'
            elif file_extension == '.txt':
                content_type = 'text/plain'
                
            # Serve the file
            response = FileResponse(
                open(file_path, 'rb'),
                content_type=content_type
            )
            response['Content-Disposition'] = f'attachment; filename="{document.title}"'
            return response
            
        except Exception as e:
            import traceback
            print(f"Error in download: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=True, methods=['get'])
    def extracted_text(self, request, pk=None):
        """
        Get the extracted text from a document
        """
        document = self.get_object()
        
        return Response({
            'id': document.id,
            'title': document.title,
            'extracted_text': document.extracted_text,
            'processing_status': document.processing_status
        })

# This function is a placeholder to avoid circular imports
def public_upload_document(request):
    pass
