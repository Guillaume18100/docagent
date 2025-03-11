from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.http import FileResponse
from django.shortcuts import get_object_or_404
import os
import threading
import io
from datetime import datetime

from .models import DocumentTemplate, GeneratedDocument
from document_processing.models import Document

# Serializers
from rest_framework import serializers

class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class GeneratedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedDocument
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# Document Template ViewSet
class DocumentTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for document templates"""
    queryset = DocumentTemplate.objects.all().order_by('-created_at')
    serializer_class = DocumentTemplateSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_permissions(self):
        """Return appropriate permissions"""
        return [AllowAny()]

# Generated Document ViewSet
class GeneratedDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for generated documents"""
    queryset = GeneratedDocument.objects.all().order_by('-created_at')
    serializer_class = GeneratedDocumentSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_permissions(self):
        """Return appropriate permissions"""
        return [AllowAny()]
    
    def create(self, request, *args, **kwargs):
        """Create a new document generation request"""
        try:
            # Extract data from request
            title = request.data.get('title', f"Generated Document {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            prompt = request.data.get('prompt', '')
            output_format = request.data.get('output_format', 'docx')
            template_id = request.data.get('template_id')
            document_ids = request.data.get('document_ids', [])
            
            if not prompt:
                return Response(
                    {'error': 'Prompt is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create the generated document
            generated_doc = GeneratedDocument(
                title=title,
                prompt=prompt,
                output_format=output_format,
                status='pending'
            )
            
            # Add template if provided
            if template_id:
                try:
                    template = DocumentTemplate.objects.get(id=template_id)
                    generated_doc.template = template
                except DocumentTemplate.DoesNotExist:
                    pass
            
            generated_doc.save()
            
            # Add reference documents if provided
            if document_ids and isinstance(document_ids, list):
                for doc_id in document_ids:
                    try:
                        doc = Document.objects.get(id=doc_id)
                        generated_doc.reference_documents.add(doc)
                    except Document.DoesNotExist:
                        pass
            
            # Start generation in background thread
            threading.Thread(target=self.generate_document, args=(generated_doc,)).start()
            
            # Return the created document
            serializer = self.get_serializer(generated_doc)
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
    
    def generate_document(self, generated_doc):
        """Background task to generate document content"""
        try:
            # Update status
            generated_doc.status = 'generating'
            generated_doc.save()
            
            # Get reference document texts if available
            reference_texts = []
            for doc in generated_doc.reference_documents.all():
                if doc.extracted_text:
                    reference_texts.append(doc.extracted_text)
            
            # Generate simple content (placeholder for actual AI generation)
            content = f"""# {generated_doc.title}

## Generated based on your prompt:
"{generated_doc.prompt}"

## This is a placeholder document
This document was created as a demonstration of the document generation feature.
In a production environment, this would be replaced with actual AI-generated content
based on your prompt and reference documents.

## Reference Documents Used:
"""
            
            # Add information about reference documents
            if reference_texts:
                for i, doc in enumerate(generated_doc.reference_documents.all()):
                    content += f"\n### Document {i+1}: {doc.title}\n"
                    content += f"Excerpt: {doc.extracted_text[:200]}...\n"
            else:
                content += "\nNo reference documents were provided."
            
            # Save the generated content
            generated_doc.content = content
            
            # Generate an actual file based on the requested format
            filename = f"{generated_doc.title.replace(' ', '_')}.{generated_doc.output_format}"
            
            # Simple file generation (placeholder)
            from django.core.files.base import ContentFile
            from django.core.files.storage import default_storage
            
            # For simplicity, we're just creating a text file regardless of format
            # In a real implementation, you would use libraries like python-docx, ReportLab, etc.
            file_content = content.encode('utf-8')
            file_path = default_storage.save(f"generated_documents/{filename}", ContentFile(file_content))
            
            # Update the document with the file and mark as completed
            generated_doc.file.name = file_path
            generated_doc.status = 'completed'
            generated_doc.save()
            
        except Exception as e:
            import traceback
            print(f"Error generating document: {str(e)}")
            print(traceback.format_exc())
            
            # Update status to failed
            generated_doc.status = 'failed'
            generated_doc.error_message = str(e)
            generated_doc.save()
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate a document with the same parameters"""
        generated_doc = self.get_object()
        
        # Start regeneration in background thread
        threading.Thread(target=self.generate_document, args=(generated_doc,)).start()
        
        return Response(
            {'status': 'Document regeneration started'},
            status=status.HTTP_202_ACCEPTED
        )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download the generated document file"""
        generated_doc = self.get_object()
        
        if not generated_doc.file:
            return Response(
                {'error': 'No file available for this document'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            file_path = generated_doc.file.path
            
            if not os.path.exists(file_path):
                return Response(
                    {'error': 'File not found on server'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Determine content type
            content_type = 'application/octet-stream'  # Default
            if generated_doc.output_format == 'pdf':
                content_type = 'application/pdf'
            elif generated_doc.output_format == 'docx':
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif generated_doc.output_format == 'txt' or generated_doc.output_format == 'markdown':
                content_type = 'text/plain'
            elif generated_doc.output_format == 'html':
                content_type = 'text/html'
            
            # Serve the file
            response = FileResponse(
                open(file_path, 'rb'),
                content_type=content_type
            )
            
            # Set filename
            filename = f"{generated_doc.title}.{generated_doc.output_format}"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            import traceback
            print(f"Error in download: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
