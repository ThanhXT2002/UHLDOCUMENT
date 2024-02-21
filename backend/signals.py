from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from .models import Notification

@receiver(pre_save, sender=Notification)
def set_sender_on_notification(sender, instance, **kwargs):
    # Nếu sender chưa được thiết lập, và có một người dùng đăng nhập, hãy thiết lập sender là người dùng đó.
    if not instance.sender and hasattr(instance, 'request') and instance.request.user.is_authenticated:
        instance.sender = instance.request.user

# middleware.py
class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request.user = request.user
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        setattr(request, 'user', request.user)