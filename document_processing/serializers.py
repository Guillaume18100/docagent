from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for the Document model"""
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file', 'document_type', 'extracted_text',
            'metadata', 'processing_status', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'document_type', 'extracted_text', 'metadata', 
                           'processing_status', 'error_message', 'created_at', 'updated_at']

class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading documents"""
    class Meta:
        model = Document
        fields = ['id', 'title', 'file']
        
class DocumentListSerializer(serializers.ModelSerializer):
    """Serializer for listing documents"""
    class Meta:
        model = Document
        fields = ['id', 'title', 'document_type', 'processing_status', 'created_at']
        
class DocumentDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed document view"""
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file', 'document_type', 'extracted_text',
            'metadata', 'processing_status', 'error_message',
            'created_at', 'updated_at'
        ] 