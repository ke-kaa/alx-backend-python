# messaging_app/chats/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsOwnerOrReadOnly
from .filters import MessageFilter
from .pagination import MessagePagination

class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for handling Conversation model operations."""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['conversation_id', 'participants__user_id']
    permission_classes = [IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        """Create a new conversation with participants."""
        participants = request.data.get('participants', [])
        if not participants or len(participants) < 2:
            return Response({"error": "At least two participants required"}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(user_id__in=participants)
        if len(users) != len(participants):
            return Response({"error": "Invalid participant IDs"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(participants=users)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for handling Message model operations."""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter  # Use the custom filter class
    pagination_class = MessagePagination
    #filterset_fields = ['message_id', 'conversation__conversation_id', 'sender__user_id']
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        """Filter messages by conversation if nested."""
        queryset = super().get_queryset()
        conversation = self.kwargs.get('conversation_pk')
        if conversation is not None:
            return queryset.filter(conversation_id=conversation)
        return queryset

    def create(self, request, *args, **kwargs):
        """Create a new message in a conversation."""
        conversation_id = request.data.get('conversation')
        if not conversation_id:
            return Response({"error": "Conversation ID required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(conversation=conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)