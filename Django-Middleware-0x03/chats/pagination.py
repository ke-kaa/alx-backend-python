# messaging_app/chats/pagination.py
from rest_framework.pagination import PageNumberPagination

class MessagePagination(PageNumberPagination):
    """Custom pagination class for messages with 20 items per page."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """Customize the paginated response to include total count."""
        return {
            'count': self.page.paginator.count,  
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        }