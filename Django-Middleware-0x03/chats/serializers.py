# messaging_app/chats/serializers.py
from rest_framework import serializers  # Import serializers module for ValidationError
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with custom validation."""
    custom_note = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")

    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'created_at', 'custom_note']

    def validate_custom_note(self, value):
        """Validate custom_note field."""
        if len(value) > 200:
            raise serializers.ValidationError("Custom note cannot exceed 200 characters.")
        return value

class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model with sender details and custom validation."""
    sender = UserSerializer(read_only=True)
    custom_status = serializers.CharField(max_length=50, required=False, default="sent")

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'message_body', 'sent_at', 'custom_status']

    def validate_message_body(self, value):
        """Validate that message_body is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty or whitespace.")
        return value

    def validate_custom_status(self, value):
        """Validate custom_status field."""
        valid_statuses = ['sent', 'read', 'delivered']
        if value.lower() not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of {valid_statuses}.")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with nested messages and participants."""
    messages = MessageSerializer(many=True, read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at', 'message_count']

    def get_message_count(self, obj):
        """Return the number of messages in the conversation."""
        return obj.messages.count()

    def validate_messages(self, value):
        """Validate nested messages to ensure at least one message exists."""
        if not value or len(value) == 0:
            raise serializers.ValidationError("A conversation must contain at least one message.")
        return value

    def validate(self, data):
        """Custom validation to ensure at least two participants."""
        if 'participants' not in self.context or len(self.context['participants']) < 2:
            raise serializers.ValidationError("A conversation must have at least two participants.")
        return data

    def create(self, validated_data):
        """Custom create method to handle nested participants and messages."""
        participants_data = self.context.get('participants', [])
        conversation = Conversation.objects.create()
        conversation.participants.set(participants_data)
        # Handle nested messages (requires a view to provide message data)
        messages_data = validated_data.get('messages', [])
        for message_data in messages_data:
            Message.objects.create(conversation=conversation, **message_data)
        return conversation