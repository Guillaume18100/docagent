from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DocumentTemplateViewSet, GeneratedDocumentViewSet

# Create a router
router = DefaultRouter()
router.register('templates', DocumentTemplateViewSet, basename='documenttemplate')
router.register('', GeneratedDocumentViewSet, basename='generateddocument')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
] 