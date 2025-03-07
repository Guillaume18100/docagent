from django.db import models
import uuid
import os

def generated_document_path(instance, filename):
    """Generate file path for generated documents"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('generated_documents/', filename)

def template_file_path(instance, filename):
    """Generate file path for template files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('templates/', filename)

class DocumentTemplate(models.Model):
    """Document template model for storing template files"""
    TEMPLATE_TYPES = (
        ('docx', 'DOCX'),
        ('pdf', 'PDF'),
        ('txt', 'Text'),
        ('markdown', 'Markdown'),
        ('html', 'HTML'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=template_file_path, blank=True, null=True)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default='docx')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class GeneratedDocument(models.Model):
    """Generated document model for storing AI-generated documents"""
    GENERATION_STATUS = (
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    FORMAT_TYPES = (
        ('docx', 'DOCX'),
        ('pdf', 'PDF'),
        ('txt', 'Text'),
        ('markdown', 'Markdown'),
        ('html', 'HTML'),
    )
    
    title = models.CharField(max_length=255)
    prompt = models.TextField()
    file = models.FileField(upload_to=generated_document_path, blank=True, null=True)
    output_format = models.CharField(max_length=20, choices=FORMAT_TYPES, default='docx')
    status = models.CharField(max_length=20, choices=GENERATION_STATUS, default='pending')
    content = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    template = models.ForeignKey(DocumentTemplate, on_delete=models.SET_NULL, blank=True, null=True)
    reference_documents = models.ManyToManyField('document_processing.Document', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
