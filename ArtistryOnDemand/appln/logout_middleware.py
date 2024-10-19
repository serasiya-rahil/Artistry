from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin

class SessionExpiryMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
                logout(request)