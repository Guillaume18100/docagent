from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import Document
from .utils import process_document
from .views import DocumentViewSet
import threading

# This function is defined here to avoid circular imports
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def public_upload_document(request):
    """Public endpoint for document upload"""
    try:
        print("Public upload endpoint called")
        print(f"Content-Type: {request.content_type}")
        print(f"Method: {request.method}")
        print(f"FILES: {request.FILES}")
        print(f"Data: {request.data}")
        
        if 'file' not in request.FILES:
            return Response({'error': 'No file was provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        if 'title' not in request.data:
            # Use filename as title if not provided
            if 'file' in request.FILES:
                title = request.FILES['file'].name
            else:
                return Response({'error': 'No title was provided'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            title = request.data['title']
            
        # Create document manually
        document = Document(
            title=title,
            file=request.FILES['file']
        )
        document.save()
        
        # Process document in background thread
        def process_and_analyze():
            # First process the document to extract text
            process_document(document)
            
            # Then trigger AI analysis
            from nlp.models import DocumentAnalysis
            from nlp.utils import analyze_document
            
            # Create analysis record
            analysis = DocumentAnalysis(document=document, status='processing')
            analysis.save()
            
            # Run analysis
            try:
                result = analyze_document(document)
                
                # Update analysis record
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
                print(f"AI analysis completed for document {document.id}")
            except Exception as e:
                import traceback
                print(f"Error in AI analysis: {str(e)}")
                print(traceback.format_exc())
                
                # Update analysis record with error
                analysis.status = 'failed'
                analysis.error_message = str(e)
                analysis.save()
        
        threading.Thread(target=process_and_analyze).start()
        
        return Response({
            'id': document.id,
            'title': document.title,
            'success': True,
            'message': 'Document uploaded successfully',
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        print(f"Error in public upload: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

router = DefaultRouter()
router.register('', DocumentViewSet, basename='document')

urlpatterns = [
    # Public direct upload endpoint
    path('public-upload/', public_upload_document, name='public-document-upload'),
    
    # Direct access to the upload endpoint
    path('upload/', DocumentViewSet.as_view({'post': 'upload'}), name='document-upload-direct'),
    
    # Test upload endpoint
    path('test-upload/', DocumentViewSet.as_view({'post': 'test_upload'}), name='document-test-upload'),
    
    # Default router URLs
    path('', include(router.urls)),
]
