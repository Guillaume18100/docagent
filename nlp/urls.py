from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserQueryViewSet, ConversationViewSet

router = DefaultRouter()
router.register('analyze', UserQueryViewSet)
router.register('conversation', ConversationViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 