from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentTemplateViewSet, GeneratedDocumentViewSet

router = DefaultRouter()
router.register('templates', DocumentTemplateViewSet)
router.register('', GeneratedDocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 