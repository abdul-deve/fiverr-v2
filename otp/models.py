from django.db import models
from django.contrib.auth import get_user_model
from lib.models import TimeStamp

User = get_user_model()
class OTPManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="otp")
    secret_key = models.CharField(max_length=32, null=True, blank=True)
    attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(null=True, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    resend_attempts = models.IntegerField(default=0)
    blocked_until = models.DateTimeField(null=True, blank=True)


