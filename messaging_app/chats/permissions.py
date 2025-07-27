from rest_framework import permissions

class IsParticipantOrSender(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if hasattr(obj, 'participants'):
            return user in obj.participants.all()
        if hasattr(obj, 'sender'):
            return obj.sender == user or user in obj.conversation.participants.all()
        return False
    



from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allow only authenticated users who are participants of the conversation
    to send, view, update, and delete messages.
    """

    def has_permission(self, request, view):
        # Only authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # For Conversation objects
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        # For Message objects
        if hasattr(obj, 'conversation'):
            # Allow only participants for unsafe methods
            if request.method in ["PUT", "PATCH", "DELETE"]:
                return request.user in obj.conversation.participants.all()
            # Allow viewing if participant
            return request.user in obj.conversation.participants.all()
        return False
