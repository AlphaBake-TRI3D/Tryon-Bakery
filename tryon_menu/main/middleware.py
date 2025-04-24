from django.utils import timezone
from .models import PageLogs

class PageLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request before the view
        response = self.get_response(request)
        # Process response after the view
        
        # Exclude static files and admin pages if needed
        path = request.path
        if not path.startswith('/static/') and not path.startswith('/admin/'):
            # Create log entry
            PageLogs.objects.create(
                url=request.path,
                user=request.user if request.user.is_authenticated else None,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 