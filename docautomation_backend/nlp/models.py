from django.db import models
from document_processing.models import Document

class DocumentAnalysis(models.Model):
    """Model for storing AI analysis of documents"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='analyses')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Analysis results
    summary = models.TextField(blank=True)
    keywords = models.JSONField(default=list, blank=True)
    sentiment = models.FloatField(default=0.0)  # -1.0 to 1.0
    entities = models.JSONField(default=list, blank=True)
    topics = models.JSONField(default=list, blank=True)
    
    # Processing status
    ANALYSIS_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    status = models.CharField(max_length=20, choices=ANALYSIS_STATUS, default='pending')
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Analysis of {self.document.title} ({self.created_at})"

class Conversation(models.Model):
    """Model for storing document-related conversations"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, default="New Conversation")
    
    class Meta:
        ordering = ['-updated_at']
        
    def __str__(self):
        return f"{self.title} - {self.document.title}"

class Message(models.Model):
    """Model for storing conversation messages"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    created_at = models.DateTimeField(auto_now_add=True)
    
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    
    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
