from django.urls import path, include
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Main router for conversations
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested router for messages under conversations
messages_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
messages_router.register(r'messages', MessageViewSet, basename='conversation-messages')

message_list = MessageViewSet.as_view({
    'get': 'list',
    'post': 'create',
})


urlpatterns = [
    path('', include(router.urls)),
    path('', include(messages_router.urls)),
    path('conversations/<int:conversation_id>/messages/', message_list, name='conversation-messages'),

]
