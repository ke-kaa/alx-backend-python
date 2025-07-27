from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from .models import Conversation, Message, CustomUser
from .pagination import MessagePagination
from .serializers import (
    UserSerializer,
    ConversationSerializer,
    MessageSerializer
)
from .permissions import IsParticipant, IsOwner
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    serializer_class = ConversationSerializer


    filter_backends = [filters.SearchFilter]
    search_fields = ['participants__username']

    def get_queryset(self):
        # Only show conversations the current user is a participant in
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        conversation.save()


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated,IsOwner,IsParticipant]


    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['text', 'sender__username']
    ordering_fields = ['timestamp']
    pagination_class = MessagePagination

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise PermissionDenied("Conversation not found.")

        if self.request.user not in conversation.participants.all():
            raise PermissionDenied("You're not a participant of this conversation.")

        return Message.objects.filter(conversation_id=conversation_id)

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_id')
        conversation = Conversation.objects.get(id=conversation_id)

        if self.request.user not in conversation.participants.all():
            raise PermissionDenied("You can't send messages to a conversation you don't belong to.")

        serializer.save(sender=self.request.user, conversation=conversation)


