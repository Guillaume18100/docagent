"""
docautomation_backend URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib.auth.models import User
from rest_framework import status

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root view that provides a list of all available endpoints
    """
    return Response({
        'documents': reverse('document-list', request=request, format=format),
        'document_upload': reverse('document-upload', request=request, format=format),
        'nlp_analyze': reverse('userquery-list', request=request, format=format),
        'conversations': reverse('conversation-list', request=request, format=format),
        'document_templates': reverse('documenttemplate-list', request=request, format=format),
        'document_generation': reverse('generateddocument-list', request=request, format=format),
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not username or not email or not password:
        return Response({
            'error': 'Please provide username, email, and password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({
            'error': 'Username already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({
            'error': 'Email already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    return Response({
        'success': 'User registered successfully',
        'id': user.id,
        'username': user.username,
        'email': user.email
    }, status=status.HTTP_201_CREATED)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', register_user, name='register_user'),
    
    # API root
    path('api/', api_root, name='api-root'),
    
    # API endpoints
    path('api/documents/', include('document_processing.urls')),
    path('api/nlp/', include('nlp.urls')),
    path('api/generate/', include('document_generation.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 