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
