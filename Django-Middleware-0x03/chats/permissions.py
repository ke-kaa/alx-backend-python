
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj

class IsParticipant(permissions.BasePermission):
    """
    Custom permission to only allow users to access their own conversations/messages.
    """

    def has_object_permission(self, request, view, obj):
        return request.user in obj.conversation.participants.all()

class IsParticipantOfConversation(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()

        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()

        return False