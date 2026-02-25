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


class PasswordRestOTPManager(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_otp"
    )
    is_verified = models.BooleanField(default=False)
    issued_at = models.DateTimeField(null=True, blank=True)

    def reset(self):
        self.is_verified = False
        self.issued_at = None
        self.save(update_fields=["is_verified", "issued_at"])

    def is_valid(self):
        from datetime import timedelta
        from django.utils import timezone
        from otp.service import OTP_Expiry
        if not self.is_verified or not self.issued_at:
            return False
        return self.is_verified and self.issued_at + timedelta(seconds=OTP_Expiry) > timezone.now()

    class Meta:
        abstract = True
