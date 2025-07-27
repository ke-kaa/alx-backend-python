# messaging_app/chats/permissions.py
from rest_framework import permissions
from .models import Conversation, Message

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to allow owners of an object to edit it."""
    
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, or OPTIONS requests (read-only) for all
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check ownership for Conversations
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()
        
        # Check ownership for Messages
        if isinstance(obj, Message):
            return obj.conversation.participants.filter(id=request.user.id).exists()
        
        return False