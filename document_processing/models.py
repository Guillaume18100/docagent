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
    metadata = models.JSONField(default=dict, blank=True)
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS, default='pending')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def file_extension(self):
        """Return the file extension"""
        name, extension = os.path.splitext(self.file.name)
        return extension.lower()[1:]
    
    def determine_document_type(self):
        """Determine document type based on file extension"""
        extension = self.file_extension()
        if extension == 'pdf':
            return 'pdf'
        elif extension in ['doc', 'docx']:
            return 'docx'
        elif extension == 'txt':
            return 'txt'
        elif extension in ['jpg', 'jpeg', 'png', 'tiff', 'bmp']:
            return 'image'
        else:
            return 'other'
    
    def save(self, *args, **kwargs):
        """Override save method to determine document type"""
        if not self.document_type or self.document_type == 'other':
            self.document_type = self.determine_document_type()
        super().save(*args, **kwargs) 