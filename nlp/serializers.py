from rest_framework import serializers
from .models import UserQuery, Conversation, Message
from document_processing.serializers import DocumentListSerializer

class UserQuerySerializer(serializers.ModelSerializer):
    """Serializer for the UserQuery model"""
    related_documents = DocumentListSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserQuery
        fields = ['id', 'query_text', 'analyzed_result', 'related_documents', 'created_at']
        read_only_fields = ['id', 'analyzed_result', 'related_documents', 'created_at']

class UserQueryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a user query"""
    document_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = UserQuery
        fields = ['id', 'query_text', 'document_ids']
    
    def create(self, validated_data):
        document_ids = validated_data.pop('document_ids', [])
        user_query = UserQuery.objects.create(**validated_data)
        
        # Add related documents if provided
        if document_ids:
            user_query.related_documents.set(document_ids)
        
        return user_query

class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model"""
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for the Conversation model"""
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a conversation"""
    class Meta:
        model = Conversation
        fields = ['id', 'title']

class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a message"""
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'conversation']
        read_only_fields = ['id'] 