from .models import set_current_user
from django.urls import reverse
# middleware.py
class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_user(request.user)
        response = self.get_response(request)
        return response
    
from django.contrib import messages
class WarningMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not request.user.is_authenticated and (request.path == reverse('dashboard') or  request.path == reverse('user') or request.path == reverse('add_user') or request.path == reverse('home') ):
            messages.warning(request, 'Bạn cần đăng nhập để vào trang này')

        return response
    
    
    
# myapp/middleware.py
class SaveIPAddressMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lấy địa chỉ IP từ header 'X-Forwarded-For' hoặc 'REMOTE_ADDR'
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', None) or request.META.get('REMOTE_ADDR', None)

        # Lưu địa chỉ IP vào request để sử dụng trong views hoặc các middleware khác
        request.ip_address = ip_address

        response = self.get_response(request)
        return response
    
    
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import render

class CustomPermissionDeniedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied):
            return render(request, 'error_page/403_page.html', status=403)

