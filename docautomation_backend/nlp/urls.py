from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalysisViewSet, ConversationViewSet

# Create a router
router = DefaultRouter()
router.register('analysis', AnalysisViewSet, basename='analysis')
router.register('conversation', ConversationViewSet, basename='conversation')

urlpatterns = [
    # Direct access to analysis endpoints
    path('analyze/', AnalysisViewSet.as_view({'post': 'analyze_document', 'get': 'get_document_analysis'}), name='analyze-document'),
    
    # Router URLs
    path('', include(router.urls)),
] 