from django.db import models
import uuid
import os
from document_processing.models import Document

def generated_document_path(instance, filename):
    """Generate file path for new generated document"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('generated/documents/', filename)

class DocumentTemplate(models.Model):
    """Model for document templates"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    template_content = models.TextField()
    variables = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class GeneratedDocument(models.Model):
    """Model for storing generated documents"""
    GENERATION_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    title = models.CharField(max_length=255)
    template = models.ForeignKey(DocumentTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    file = models.FileField(upload_to=generated_document_path, null=True, blank=True)
    parameters = models.JSONField(default=dict)
    source_documents = models.ManyToManyField(Document, blank=True, related_name='generated_documents')
    generation_status = models.CharField(max_length=20, choices=GENERATION_STATUS, default='pending')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title 