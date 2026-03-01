"""Authentication middleware."""
import os
import base64
from django.http import HttpResponse
from django.conf import settings


class AdminAuthMiddleware:
    """Middleware for admin authentication."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path.startswith('/admin'):
            if not self._basic_auth(request):
                response = HttpResponse('Unauthorized', status=401)
                response['WWW-Authenticate'] = 'Basic realm="Admin"'
                return response
        
        return self.get_response(request)
    
    def _basic_auth(self, request):
        """Check basic authentication."""
        user = getattr(settings, 'ADMIN_USER', os.getenv('ADMIN_USER'))
        pwd = getattr(settings, 'ADMIN_PASSWORD', os.getenv('ADMIN_PASSWORD'))
        
        if not user or not pwd:
            return True
        
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth or not auth.startswith('Basic '):
            return False
        
        try:
            decoded = base64.b64decode(auth[6:]).decode()
            u, p = decoded.split(':', 1)
            return u == user and p == pwd
        except Exception:
            return False
