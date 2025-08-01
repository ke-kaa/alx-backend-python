
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MessagePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'total_messages': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'messages': data,
        })
