from collections import defaultdict
from datetime import datetime
import logging
import time
import os
from django.http import HttpResponseForbidden, JsonResponse

# Configure logging to file
logger = logging.getLogger(__name__)
log_path = os.path.join(os.path.dirname(__file__), '..', 'requests.log')
handler = logging.FileHandler(log_path)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_entry)
        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour

        # Allow only between 18:00 (6PM) and 21:00 (9PM)
        if current_hour < 18 or current_hour >= 21:
            return HttpResponseForbidden("Access to chat is restricted at this hour.")

        return self.get_response(request)

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_logs = defaultdict(list)  # {ip_address: [timestamp, ...]}

    def __call__(self, request):
        ip = self.get_client_ip(request)
        current_time = time.time()

        # Only apply rate limiting to POST requests to /api/messages/ or similar
        if request.method == 'POST' and request.path.startswith('/api/messages'):
            self.cleanup_old_requests(ip, current_time)

            if len(self.request_logs[ip]) >= 5:
                return JsonResponse(
                    {"error": "Rate limit exceeded. Max 5 messages per minute."},
                    status=429
                )

            self.request_logs[ip].append(current_time)

        return self.get_response(request)

    def cleanup_old_requests(self, ip, now):
        # Keep only timestamps within the last 60 seconds
        self.request_logs[ip] = [
            timestamp for timestamp in self.request_logs[ip]
            if now - timestamp < 60
        ]

    def get_client_ip(self, request):
        # Try to get real IP if behind proxy
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # Only run check if user is authenticated and accessing a restricted endpoint
        if request.path.startswith('/api/') and request.method in ['POST', 'PUT', 'DELETE']:
            if not user.is_authenticated:
                return JsonResponse({'detail': 'Authentication required'}, status=401)

            # Deny access if role is not admin or moderator
            if not hasattr(user, 'role') or user.role not in ['admin', 'moderator']:
                return JsonResponse({'detail': 'Permission denied: Admins and moderators only'}, status=403)

        response = self.get_response(request)
        return response

