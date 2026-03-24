from django.utils.deprecation import MiddlewareMixin

class ThemeMiddleware(MiddlewareMixin):
    """
    Middleware to handle theme preference persistence
    Reads theme from cookies and makes it available to all views
    """
    
    def process_request(self, request):
        # Get theme from cookies or set default
        theme = request.COOKIES.get('theme', 'dark')
        request.theme = theme
        return None
    
    def process_response(self, request, response):
        # If theme was set in the request, ensure it's in the cookie
        if hasattr(request, 'theme'):
            response.set_cookie('theme', request.theme, max_age=31536000)  # 1 year
        return response
