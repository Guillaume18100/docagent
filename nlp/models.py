from django.db import models
from document_processing.models import Document

class UserQuery(models.Model):
    """Model for storing user queries and NLP analysis results"""
    query_text = models.TextField()
    analyzed_result = models.JSONField(default=dict, blank=True)
    related_documents = models.ManyToManyField(Document, blank=True, related_name='user_queries')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.query_text[:50]

class Conversation(models.Model):
    """Model for storing conversation history"""
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Message(models.Model):
    """Model for storing messages in a conversation"""
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}" 