from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import UserQuery, Conversation, Message
from .serializers import (
    UserQuerySerializer,
    UserQueryCreateSerializer,
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    MessageCreateSerializer
)
from .utils import analyze_user_query, find_relevant_document_sections, answer_question
from document_processing.models import Document

class UserQueryViewSet(viewsets.ModelViewSet):
    """ViewSet for handling user queries"""
    queryset = UserQuery.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return UserQueryCreateSerializer
        return UserQuerySerializer
    
    def create(self, request, *args, **kwargs):
        """Handle user query analysis"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract data
        query_text = serializer.validated_data['query_text']
        document_ids = serializer.validated_data.get('document_ids', [])
        
        # Analyze the query
        analysis_result = analyze_user_query(query_text)
        
        # Find relevant document sections if document IDs are provided
        if document_ids:
            documents = Document.objects.filter(id__in=document_ids)
            relevant_sections = find_relevant_document_sections(query_text, documents)
            analysis_result['relevant_sections'] = relevant_sections
        
        # Save the query with analysis results
        user_query = serializer.save()
        user_query.analyzed_result = analysis_result
        user_query.save()
        
        # Return the analysis results
        response_serializer = UserQuerySerializer(user_query)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def answer(self, request, pk=None):
        """Answer a question based on the query and related documents"""
        user_query = self.get_object()
        
        # Get the question from the request
        question = request.data.get('question', user_query.query_text)
        
        # Get related documents
        documents = user_query.related_documents.all()
        
        if not documents:
            return Response(
                {"error": "No documents associated with this query"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find relevant sections
        relevant_sections = find_relevant_document_sections(question, documents)
        
        if not relevant_sections:
            return Response(
                {"error": "No relevant sections found in the documents"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Use the most relevant section as context
        context = relevant_sections[0]['text']
        
        # Answer the question
        answer = answer_question(question, context)
        
        # Add source information
        answer['source'] = {
            'document_id': relevant_sections[0]['document_id'],
            'document_title': relevant_sections[0]['document_title'],
            'relevance_score': relevant_sections[0]['score']
        }
        
        return Response(answer)

class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for handling conversations"""
    queryset = Conversation.objects.all().order_by('-updated_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """Add a message to the conversation"""
        conversation = self.get_object()
        
        # Add conversation ID to the request data
        data = request.data.copy()
        data['conversation'] = conversation.id
        
        # Create the message
        serializer = MessageCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        
        # If it's a user message, generate a response
        if message.role == 'user':
            # Analyze the message
            analysis_result = analyze_user_query(message.content)
            
            # Create an assistant response
            response_content = "I understand you're asking about: " + message.content
            
            # Add clarifying questions if available
            if 'clarifying_questions' in analysis_result:
                response_content += "\n\nTo help you better, I need some additional information:\n"
                for i, question in enumerate(analysis_result['clarifying_questions'], 1):
                    response_content += f"\n{i}. {question}"
            
            # Save the assistant response
            Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=response_content
            )
        
        # Return the updated conversation
        conversation_serializer = ConversationSerializer(conversation)
        return Response(conversation_serializer.data)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages in the conversation"""
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data) 