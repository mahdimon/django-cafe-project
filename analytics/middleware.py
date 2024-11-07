from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class StaffOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the URL of the login page, defaulting to LOGIN_URL in settings
        login_url = reverse(settings.LOGIN_URL) if settings.LOGIN_URL else '/login/'
        
        # Define paths that should be accessible to everyone (e.g., login page)
        allowed_paths = [login_url]

        # Check if user is authenticated and is_staff, and if path is not allowed
        if not request.user.is_authenticated or not request.user.is_staff:
            if request.path not in allowed_paths:
                return redirect(settings.LOGIN_URL)  # Redirect to login if user is not staff
        
        # Continue to the view if user meets the requirements or on an allowed path
        return self.get_response(request)