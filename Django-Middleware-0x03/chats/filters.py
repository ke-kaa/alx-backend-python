# messaging_app/chats/filters.py
import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    """Filter set for Message model to filter by user or time range."""
    
    sender = django_filters.NumberFilter(field_name='sender__id', lookup_expr='exact')
    conversation = django_filters.NumberFilter(field_name='conversation__conversation_id', lookup_expr='exact')
    created_at_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'created_at_after', 'created_at_before']