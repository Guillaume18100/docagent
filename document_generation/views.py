from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from .models import DocumentTemplate, GeneratedDocument
from .serializers import (
    DocumentTemplateSerializer,
    DocumentTemplateListSerializer,
    GeneratedDocumentSerializer,
    GeneratedDocumentListSerializer,
    DocumentGenerationSerializer
)
from .utils import generate_document
import threading

class DocumentTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for handling document templates"""
    queryset = DocumentTemplate.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return DocumentTemplateListSerializer
        return DocumentTemplateSerializer

class GeneratedDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for handling generated documents"""
    queryset = GeneratedDocument.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return GeneratedDocumentListSerializer
        elif self.action == 'create' or self.action == 'generate':
            return DocumentGenerationSerializer
        return GeneratedDocumentSerializer
    
    def create(self, request, *args, **kwargs):
        """Handle document generation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create the generated document
        generated_document = serializer.save(content="", generation_status="pending")
        
        # Generate the document in a background thread
        threading.Thread(target=generate_document, args=(generated_document,)).start()
        
        # Return the generated document
        response_serializer = GeneratedDocumentSerializer(generated_document)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate a document"""
        generated_document = self.get_object()
        
        # Reset the document status
        generated_document.generation_status = 'pending'
        generated_document.error_message = ''
        generated_document.save()
        
        # Generate the document in a background thread
        threading.Thread(target=generate_document, args=(generated_document,)).start()
        
        return Response(
            {'status': 'Document generation started'},
            status=status.HTTP_202_ACCEPTED
        )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download the generated document file"""
        generated_document = self.get_object()
        
        if not generated_document.file:
            return Response(
                {'error': 'No file available for this document'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return FileResponse(
            generated_document.file,
            as_attachment=True,
            filename=f"{generated_document.title}.docx"
        ) 