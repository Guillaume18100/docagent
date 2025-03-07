from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
import json
from datetime import datetime

# Simple view for conversations
@api_view(['GET'])
@permission_classes([AllowAny])
def conversation_list(request):
    """
    List conversations for a document or all conversations
    """
    print("Conversation list endpoint called")
    document_id = request.query_params.get('document_id')
    
    # For now, return an empty list - we'll implement actual conversation storage later
    if document_id:
        print(f"Getting conversations for document {document_id}")
        return Response([])
    else:
        return Response([])

@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_query(request):
    """
    Analyze a user query against document(s)
    """
    print("Analyze query endpoint called")
    try:
        data = request.data
        print(f"Query data: {data}")
        
        query_text = data.get('query_text', '')
        document_ids = data.get('document_ids', [])
        
        if not query_text:
            return Response(
                {'error': 'No query text provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        print(f"Processing query: {query_text}")
        print(f"For documents: {document_ids}")
        
        # Generate a simple response for now
        current_time = datetime.now().isoformat()
        
        # Create response with both user message and system response
        response = {
            'userMessage': {
                'id': f'user-{int(datetime.now().timestamp())}',
                'document_id': document_ids[0] if document_ids else None,
                'content': query_text,
                'sender': 'user',
                'timestamp': current_time
            },
            'systemResponse': {
                'id': f'system-{int(datetime.now().timestamp())}',
                'document_id': document_ids[0] if document_ids else None,
                'content': f"I've processed your query: '{query_text}'. This is a placeholder response from the document automation system.",
                'sender': 'system',
                'timestamp': current_time
            }
        }
        
        return Response(response)
        
    except Exception as e:
        print(f"Error in analyze query: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Create a router
router = DefaultRouter()

urlpatterns = [
    # Conversation endpoints
    path('conversation/', conversation_list, name='conversation-list'),
    
    # Query analysis endpoint
    path('analyze/', analyze_query, name='analyze-query'),
    
    # Include router URLs
    path('', include(router.urls)),
] 