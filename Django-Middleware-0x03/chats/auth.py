# messaging_app/chats/auth.py
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class CustomJWTAuthentication(BaseAuthentication):
    """Custom JWT authentication to validate token and user ownership."""
    
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        # Here you would typically validate the token with simplejwt
        # For this example, assume token validation is handled by simplejwt
        try:
            # Placeholder for token decoding (handled by simplejwt middleware)
            from rest_framework_simplejwt.tokens import AccessToken
            token_obj = AccessToken(token)
            user_id = token_obj['user_id']
            user = User.objects.get(id=user_id)
            if not user.is_active:
                raise exceptions.AuthenticationFailed(_('User inactive or deleted'))
            return (user, token)
        except Exception as e:
            raise exceptions.AuthenticationFailed(_('Invalid token: {}').format(str(e)))

    def authenticate_header(self, request):
        return 'Bearer'