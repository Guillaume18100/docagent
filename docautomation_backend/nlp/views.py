from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import threading
import logging
import json

from document_processing.models import Document
from .models import DocumentAnalysis, Conversation, Message
from .utils import analyze_document

# Serializers
from rest_framework import serializers

logger = logging.getLogger(__name__)

class DocumentAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentAnalysis
        fields = '__all__'
        read_only_fields = ('created_at',)

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('created_at',)

class AnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for handling document analysis operations"""
    queryset = DocumentAnalysis.objects.all()
    serializer_class = DocumentAnalysisSerializer
    
    def get_permissions(self):
        """Return appropriate permissions based on action"""
        return [AllowAny()]
    
    @action(detail=False, methods=['post'])
    def analyze_document(self, request):
        """Analyze a document based on document_id"""
        document_id = request.data.get('document_id')
        
        if not document_id:
            return Response(
                {'error': 'document_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            document = Document.objects.get(id=document_id)
            
            # Check if document has already been analyzed
            analysis = DocumentAnalysis.objects.filter(document=document).first()
            
            if not analysis:
                # Create a new analysis record
                analysis = DocumentAnalysis(document=document, status='processing')
                analysis.save()
                
                # Run the analysis in a background thread
                def analyze_in_background():
                    try:
                        result = analyze_document(document)
                        
                        if result['success']:
                            analysis.summary = result['results']['summary']
                            analysis.keywords = result['results']['keywords']
                            analysis.sentiment = result['results']['sentiment']
                            analysis.entities = result['results']['entities']
                            analysis.topics = result['results']['topics']
                            analysis.status = 'completed'
                        else:
                            analysis.status = 'failed'
                            analysis.error_message = result.get('error', 'Unknown error')
                        
                        analysis.save()
                    except Exception as e:
                        logger.error(f"Error in background analysis: {str(e)}")
                        analysis.status = 'failed'
                        analysis.error_message = str(e)
                        analysis.save()
                
                threading.Thread(target=analyze_in_background).start()
                
                return Response({
                    'message': 'Analysis started',
                    'analysis_id': analysis.id,
                    'status': analysis.status
                })
            else:
                return Response({
                    'message': 'Analysis already exists',
                    'analysis_id': analysis.id,
                    'status': analysis.status
                })
        
        except Document.DoesNotExist:
            return Response(
                {'error': f'Document with id {document_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get', 'post'])
    def get_document_analysis(self, request):
        """Get the analysis for a document based on document_id"""
        # For GET requests from URL params
        if request.method == 'GET':
            document_id = request.query_params.get('document_id')
        # For POST requests from request body
        else:  # POST method
            document_id = request.data.get('document_id')
            
        if not document_id:
            return Response(
                {'error': 'document_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            document = Document.objects.get(id=document_id)
            analysis = DocumentAnalysis.objects.filter(document=document).first()
            
            if not analysis:
                return Response(
                    {'error': f'No analysis found for document with id {document_id}', 'status': 'not_found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = self.serializer_class(analysis)
            return Response(serializer.data)
            
        except Document.DoesNotExist:
            return Response(
                {'error': f'Document with id {document_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving analysis: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get', 'post'])
    def analyze(self, request):
        """
        GET: Get analysis for a document
        POST: Analyze a document with a specific query
        """
        if request.method == 'GET':
            document_id = request.query_params.get('document_id')
            if not document_id:
                return Response(
                    {'error': 'document_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                document = Document.objects.get(id=document_id)
                analysis = DocumentAnalysis.objects.filter(document=document).first()
                
                if not analysis:
                    # Create a new analysis record and start analysis
                    analysis = DocumentAnalysis(document=document, status='pending')
                    analysis.save()
                    
                    # Start analysis in background
                    def analyze_in_background():
                        try:
                            result = analyze_document(document)
                            
                            if result['success']:
                                analysis.summary = result['results']['summary']
                                analysis.keywords = result['results']['keywords']
                                analysis.sentiment = result['results']['sentiment']
                                analysis.entities = result['results']['entities']
                                analysis.topics = result['results']['topics']
                                analysis.status = 'completed'
                            else:
                                analysis.status = 'failed'
                                analysis.error_message = result.get('error', 'Unknown error')
                            
                            analysis.save()
                        except Exception as e:
                            logger.error(f"Error in background analysis: {str(e)}")
                            analysis.status = 'failed'
                            analysis.error_message = str(e)
                            analysis.save()
                    
                    threading.Thread(target=analyze_in_background).start()
                
                serializer = self.serializer_class(analysis)
                return Response(serializer.data)
            
            except Document.DoesNotExist:
                return Response(
                    {'error': f'Document with id {document_id} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                logger.error(f"Error retrieving analysis: {str(e)}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        elif request.method == 'POST':
            document_id = request.data.get('document_id')
            if not document_id and not request.data.get('document_ids'):
                return Response(
                    {'error': 'document_id or document_ids is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process single document_id or list of document_ids
            document_ids = request.data.get('document_ids', [])
            if document_id and not document_ids:
                document_ids = [document_id]
            
            query_text = request.data.get('query_text', '')
            operation_type = request.data.get('operation_type', 'general')
            
            try:
                # For now, just handle the first document in the list
                if document_ids:
                    document_id = document_ids[0]
                    document = Document.objects.get(id=document_id)
                    
                    # Get or create the analysis for this document
                    analysis, created = DocumentAnalysis.objects.get_or_create(
                        document=document,
                        defaults={'status': 'completed'}  # Assume completed if it exists
                    )
                    
                    if created or analysis.status != 'completed':
                        # If we just created it or it's not complete, trigger analysis
                        def analyze_in_background():
                            try:
                                result = analyze_document(document)
                                
                                if result['success']:
                                    analysis.summary = result['results']['summary']
                                    analysis.keywords = result['results']['keywords']
                                    analysis.sentiment = result['results']['sentiment']
                                    analysis.entities = result['results']['entities']
                                    analysis.topics = result['results']['topics']
                                    analysis.status = 'completed'
                                else:
                                    analysis.status = 'failed'
                                    analysis.error_message = result.get('error', 'Unknown error')
                                
                                analysis.save()
                            except Exception as e:
                                logger.error(f"Error in background analysis: {str(e)}")
                                analysis.status = 'failed'
                                analysis.error_message = str(e)
                                analysis.save()
                        
                        threading.Thread(target=analyze_in_background).start()
                    
                    # Get or create a conversation for this document
                    conversation, created = Conversation.objects.get_or_create(
                        document=document,
                        defaults={'title': f"Conversation about {document.title}"}
                    )
                    
                    # Create user message
                    user_message = Message.objects.create(
                        conversation=conversation,
                        role='user',
                        content=query_text
                    )
                    
                    # Generate response based on operation type and analysis results
                    response_text = "I've processed your request."
                    
                    # Check if analysis is completed
                    if analysis.status == 'completed':
                        try:
                            if operation_type == 'summarize':
                                response_text = f"Here's a summary of the document:\n\n{analysis.summary or 'No summary available yet.'}"
                            elif operation_type == 'simplify':
                                response_text = f"Here's the document in simpler language:\n\n{analysis.summary or 'No summary available yet.'}"
                            elif operation_type == 'extract':
                                # Extract actions from entities or keywords
                                actions = []
                                if analysis.keywords:
                                    for keyword in analysis.keywords:
                                        if any(action_word in keyword.lower() for action_word in ['do', 'complete', 'finish', 'review', 'send', 'create', 'update']):
                                            actions.append(f"- {keyword}")
                                
                                if actions:
                                    response_text = f"I found these action items in the document:\n\n" + "\n".join(actions)
                                else:
                                    response_text = "I couldn't find specific action items in this document."
                            elif operation_type == 'format':
                                if analysis.keywords:
                                    response_text = f"Here's a suggested structure for the document:\n\n1. Introduction\n2. Key Points\n   - {' - '.join(analysis.keywords[:5] if analysis.keywords else ['No keywords available'])}\n3. Details\n4. Conclusion"
                                else:
                                    response_text = "Here's a suggested structure for the document:\n\n1. Introduction\n2. Key Points\n3. Details\n4. Conclusion"
                            elif operation_type == 'legal':
                                keywords = ', '.join(analysis.keywords[:5]) if analysis.keywords else 'None found'
                                response_text = f"Legal Analysis:\n\nThe document appears to have a {analysis.sentiment or 'neutral'} tone. Key legal terms identified: {keywords}"
                            elif operation_type == 'translate':
                                response_text = f"Translation service is currently in development. Here's a summary in English:\n\n{analysis.summary or 'No summary available yet.'}"
                            else:
                                # Generic response using analysis data
                                topics = ', '.join(analysis.topics[:3]) if analysis.topics else 'various topics'
                                response_text = f"I've analyzed the document. It has a {analysis.sentiment or 'neutral'} sentiment. Key topics include: {topics}. Would you like to know more about anything specific?"
                        except Exception as e:
                            logger.error(f"Error generating response: {str(e)}")
                            response_text = "I encountered an issue while analyzing this document. Please try a different query or document."
                    else:
                        response_text = f"The document is still being analyzed (status: {analysis.status}). Please try again shortly."
                    
                    # Create system response
                    system_message = Message.objects.create(
                        conversation=conversation,
                        role='assistant',
                        content=response_text
                    )
                    
                    # Return conversation data
                    return Response({
                        'conversation': {
                            'id': conversation.id,
                            'title': conversation.title,
                        },
                        'messages': [
                            {
                                'id': user_message.id,
                                'role': user_message.role,
                                'content': user_message.content,
                                'timestamp': user_message.created_at
                            },
                            {
                                'id': system_message.id,
                                'role': system_message.role,
                                'content': system_message.content,
                                'timestamp': system_message.created_at
                            }
                        ],
                        'result': response_text
                    })
                else:
                    return Response(
                        {'error': 'No valid document IDs provided'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            except Document.DoesNotExist:
                return Response(
                    {'error': f'Document with id {document_id} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for handling document conversations"""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    
    def get_permissions(self):
        """Return appropriate permissions based on action"""
        return [AllowAny()]
    
    def list(self, request):
        """List conversations, filtered by document_id if provided"""
        document_id = request.query_params.get('document_id')
        if document_id:
            queryset = self.queryset.filter(document_id=document_id)
        else:
            queryset = self.queryset
        
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a conversation"""
        conversation = self.get_object()
        messages = Message.objects.filter(conversation=conversation).order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """Add a message to a conversation"""
        conversation = self.get_object()
        
        role = request.data.get('role')
        content = request.data.get('content')
        
        if not role or not content:
            return Response(
                {'error': 'role and content are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user message
        message = Message.objects.create(
            conversation=conversation,
            role=role,
            content=content
        )
        
        # If this is a user message, generate an assistant response
        if role == 'user':
            # Get the document
            document = conversation.document
            
            # Generate a response (placeholder)
            assistant_content = "I've received your message. How can I help you with this document?"
            
            # Create assistant message
            assistant_message = Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=assistant_content
            )
            
            # Return both messages
            return Response({
                'user_message': MessageSerializer(message).data,
                'assistant_message': MessageSerializer(assistant_message).data
            })
        
        # Return the created message
        serializer = MessageSerializer(message)
        return Response(serializer.data)
    
    def create(self, request):
        """Create a new conversation for a document"""
        document_id = request.data.get('document_id')
        title = request.data.get('title')
        
        if not document_id:
            return Response(
                {'error': 'document_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            document = Document.objects.get(id=document_id)
            
            if not title:
                title = f"Conversation about {document.title}"
            
            # Create the conversation
            conversation = Conversation.objects.create(
                document=document,
                title=title
            )
            
            # Add a system message to start
            Message.objects.create(
                conversation=conversation,
                role='system',
                content=f"This is a conversation about the document '{document.title}'. How can I help you with this document?"
            )
            
            # Return the created conversation
            serializer = self.serializer_class(conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Document.DoesNotExist:
            return Response(
                {'error': f'Document with id {document_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
